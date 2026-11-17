import asyncio
import threading
import time
from typing import List

import RNS

from src.backend.path_refresh import ensure_fresh_path, slowest_online_bitrate

# todo optionally identity self over link
# todo allowlist/denylist for incoming calls

RECOVERY_PATH_TIMEOUT = 8
RECOVERY_LINK_TIMEOUT = 12
LINK_ACTIVE = RNS.Link.ACTIVE


class CallFailedException(Exception):
    pass


class AudioCall:

    def __init__(self, link: RNS.Link, is_outbound: bool):
        self.link = link
        # The websocket and call APIs keep this hash. A recovery link gets a
        # new Reticulum hash, and swapping the lookup hash would drop the call.
        self.lookup_hash = link.hash
        self.is_outbound = is_outbound
        self.destination_hash = None
        self._outbound_destination = None
        self.peer_identity_hash = None
        self._local_identity = None
        self._max_age_seconds = 0
        self._user_hangup = False
        self._relink_used = False
        self._awaiting_replacement = False
        self._replacement = threading.Event()
        self._finished = False
        self._pending_audio = None
        self._tx_ready_at = 0
        self._flush_armed = False
        self._tx_lock = threading.Lock()
        self.audio_packet_listeners = []
        self.hangup_listeners = []
        self._attach(link)

    @property
    def awaiting_replacement(self):
        return self._awaiting_replacement

    def _attach(self, link):
        self.link = link
        self.link.set_link_closed_callback(self.on_link_closed)
        self.link.set_packet_callback(self.on_packet)

    def register_audio_packet_listener(self, callback):
        self.audio_packet_listeners.append(callback)

    def unregister_audio_packet_listener(self, callback):
        self.audio_packet_listeners.remove(callback)

    def register_hangup_listener(self, callback):
        self.hangup_listeners.append(callback)

    def on_link_closed(self, link):
        print("[AudioCall] on_link_closed")
        if self._user_hangup or self._finished:
            self._finish()
            return
        if getattr(link, "hash", None) != getattr(self.link, "hash", None):
            return
        if self._relink_used:
            self._finish()
            return
        self._relink_used = True
        self._awaiting_replacement = True
        threading.Thread(target=self._recover, name="AudioCall recover", daemon=True).start()

    def _recover(self):
        try:
            if self.is_outbound and self._outbound_destination is not None and self.destination_hash is not None:
                self._recover_outbound()
                return
            if self._replacement.wait(RECOVERY_PATH_TIMEOUT + RECOVERY_LINK_TIMEOUT):
                if not self._user_hangup and self.is_active():
                    self._awaiting_replacement = False
                    self._flush_pending()
                    return
        except Exception as error:
            print("[AudioCall] relink failed: " + str(error))
        self._awaiting_replacement = False
        if not self._user_hangup:
            self._finish()

    def _recover_outbound(self):
        usable = asyncio.run(ensure_fresh_path(
            self.destination_hash,
            RECOVERY_PATH_TIMEOUT,
            self._max_age_seconds,
            slowest_online_bitrate(),
        ))
        if not usable or self._user_hangup:
            self._finish()
            return
        link = RNS.Link(self._outbound_destination)
        deadline = time.time() + RECOVERY_LINK_TIMEOUT
        while link.status != LINK_ACTIVE and time.time() < deadline and not self._user_hangup:
            time.sleep(0.05)
        if link.status == LINK_ACTIVE and not self._user_hangup:
            self._attach(link)
            try:
                link.identify(self._local_identity)
            except Exception:
                pass
            self._awaiting_replacement = False
            self._flush_pending()
            return
        try:
            link.set_link_closed_callback(None)
            link.teardown()
        except Exception:
            pass
        self._finish()

    def adopt(self, link):
        self._attach(link)
        identity = link.get_remote_identity()
        if identity is not None:
            self.peer_identity_hash = identity.hash
        self._awaiting_replacement = False
        self._replacement.set()

    def on_packet(self, message, packet):
        for audio_packet_listener in self.audio_packet_listeners:
            audio_packet_listener(message)

    def send_audio_packet(self, data):
        # Capture already groups Codec2 frames into one protobuf payload.
        # Do not concatenate those payloads: the decoder reads one message.
        if len(data) > RNS.Link.MDU:
            print("[AudioCall] dropping audio packet " + str(len(data)) + " bytes exceeds the link packet MDU of " + str(RNS.Link.MDU) + " bytes")
            return

        with self._tx_lock:
            if not self.is_active() or time.monotonic() < self._tx_ready_at:
                self._pending_audio = data
                self._arm_flush_locked()
                return
            self._write_locked(data)

    def _write_locked(self, data):
        RNS.Packet(self.link, data).send()
        rate = max(slowest_online_bitrate(), 1)
        self._tx_ready_at = time.monotonic() + max((len(data) * 8) / rate, 0.02)
        self._pending_audio = None

    def _arm_flush_locked(self):
        if self._flush_armed:
            return
        self._flush_armed = True
        delay = max(0.02, self._tx_ready_at - time.monotonic())
        timer = threading.Timer(delay, self._flush_pending)
        timer.daemon = True
        timer.start()

    def _flush_pending(self):
        with self._tx_lock:
            self._flush_armed = False
            data = self._pending_audio
            if data is None:
                return
            if not self.is_active() or time.monotonic() < self._tx_ready_at:
                if self.is_active():
                    self._arm_flush_locked()
                return
            self._write_locked(data)

    def get_remote_identity(self):
        return self.link.get_remote_identity()

    def is_active(self):
        return self.link.status == LINK_ACTIVE

    def hangup(self):
        print("[AudioCall] hangup")
        self._user_hangup = True
        self._awaiting_replacement = False
        self._replacement.set()
        self.link.teardown()

    def _finish(self):
        if self._finished:
            return
        self._finished = True
        self._awaiting_replacement = False
        for hangup_listener in list(self.hangup_listeners):
            try:
                hangup_listener()
            except Exception as error:
                print("[AudioCall] hangup listener failed: " + str(error))


class AudioCallManager:

    def __init__(self, identity: RNS.Identity):

        self.identity = identity
        self.on_incoming_call_callback = None
        self.on_outgoing_call_callback = None
        self.audio_call_receiver = AudioCallReceiver(manager=self)

        # remember audio calls
        self.audio_calls: List[AudioCall] = []

    def announce(self, app_data=None):
        self.audio_call_receiver.destination.announce(app_data)
        print("[AudioCallManager] announced destination: " + RNS.prettyhexrep(self.audio_call_receiver.destination.hash))

    def register_incoming_call_callback(self, callback):
        self.on_incoming_call_callback = callback

    def register_outgoing_call_callback(self, callback):
        self.on_outgoing_call_callback = callback

    def handle_incoming_call(self, audio_call: AudioCall):
        self.audio_calls.append(audio_call)
        if self.on_incoming_call_callback is not None:
            self.on_incoming_call_callback(audio_call)

    def handle_outgoing_call(self, audio_call: AudioCall):
        self.audio_calls.append(audio_call)
        if self.on_outgoing_call_callback is not None:
            self.on_outgoing_call_callback(audio_call)

    def has_awaiting_replacement(self):
        return any(audio_call.awaiting_replacement for audio_call in self.audio_calls)

    def find_audio_call_by_link_hash(self, link_hash: bytes):
        for audio_call in self.audio_calls:
            if audio_call.lookup_hash == link_hash or audio_call.link.hash == link_hash:
                return audio_call
        return None

    def delete_audio_call_by_link_hash(self, link_hash: bytes):
        audio_call = self.find_audio_call_by_link_hash(link_hash)
        if audio_call is not None:
            self.delete_audio_call(audio_call)

    def delete_audio_call(self, audio_call: AudioCall):
        self.audio_calls.remove(audio_call)

    def hangup_all(self):
        for audio_call in self.audio_calls:
            audio_call.hangup()
        return None

    async def initiate(self, destination_hash: bytes, timeout_seconds: int = 15, max_age_seconds: int = 0) -> AudioCall:
        bitrate = slowest_online_bitrate()
        if not await ensure_fresh_path(destination_hash, timeout_seconds, max_age_seconds, bitrate):
            raise CallFailedException("Could not find path to destination.")

        server_identity = RNS.Identity.recall(destination_hash)
        if server_identity is None:
            raise CallFailedException("Could not find path to destination.")

        server_destination = RNS.Destination(
            server_identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            "call",
            "audio"
        )

        link = RNS.Link(server_destination)
        link_deadline = time.time() + timeout_seconds
        while link.status != LINK_ACTIVE and time.time() < link_deadline:
            await asyncio.sleep(0.1)

        if link.status != LINK_ACTIVE:
            try:
                link.teardown()
            except Exception:
                pass
            raise CallFailedException("Could not establish link to destination.")

        audio_call = AudioCall(link, is_outbound=True)
        audio_call.destination_hash = destination_hash
        audio_call._outbound_destination = server_destination
        audio_call.peer_identity_hash = server_identity.hash
        audio_call._local_identity = self.identity
        audio_call._max_age_seconds = max_age_seconds
        self.handle_outgoing_call(audio_call)

        # todo: this can be optional, it's only being sent by default for ui, can be removed
        link.identify(self.identity)

        return audio_call


class AudioCallReceiver:

    def __init__(self, manager: AudioCallManager):

        self.manager = manager

        self.destination = RNS.Destination(
            self.manager.identity,
            RNS.Destination.IN,
            RNS.Destination.SINGLE,
            "call",
            "audio",
        )

        self.destination.set_link_established_callback(self.client_connected)

    def find_audio_call_by_link_hash(self, link_hash: bytes):
        return self.manager.find_audio_call_by_link_hash(link_hash)

    def client_connected(self, link: RNS.Link):
        # todo: this can be optional, it's only being sent by default for ui, can be removed
        link.identify(self.manager.identity)

        if self.manager.has_awaiting_replacement():
            link.set_remote_identified_callback(self._adopt_or_open)
            return

        audio_call = AudioCall(link, is_outbound=False)
        link.set_remote_identified_callback(
            lambda identified_link, identity, call=audio_call: self._remember_peer(call, identity)
        )
        self.manager.handle_incoming_call(audio_call)

    def _remember_peer(self, audio_call: AudioCall, identity):
        if identity is not None:
            audio_call.peer_identity_hash = identity.hash

    def _adopt_or_open(self, link: RNS.Link, identity):
        if identity is not None:
            for audio_call in list(self.manager.audio_calls):
                if audio_call.awaiting_replacement and audio_call.peer_identity_hash == identity.hash:
                    audio_call.adopt(link)
                    return
        audio_call = AudioCall(link, is_outbound=False)
        if identity is not None:
            audio_call.peer_identity_hash = identity.hash
        self.manager.handle_incoming_call(audio_call)
