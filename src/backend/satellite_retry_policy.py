"""Bounded LXMF delivery retries for high-latency satellite interfaces."""

import threading
import time

import LXMF
import RNS
import RNS.vendor.umsgpack as msgpack


class SatelliteMessageRejected(ValueError):
    """Raised when a message must not be sent over a paid satellite link."""


class SatelliteRetryPolicy:
    """Supervise LXMF sends without changing normal router retry behaviour."""

    DEFAULT_RETRY_DELAY_SECONDS = 10 * 60
    MINIMUM_RETRY_DELAY_SECONDS = 8 * 60
    DEFAULT_MAX_ATTEMPTS = 1
    MAXIMUM_ATTEMPTS = 2
    POLL_INTERVAL_SECONDS = 1

    # A message whose packed content exceeds this fits only in a multi-packet
    # direct-link transfer, which cannot work over minutes-long satellite
    # round trips and would create several billable packets.
    SINGLE_PACKET_CONTENT_LIMIT = LXMF.LXMessage.ENCRYPTED_PACKET_MAX_CONTENT

    def __init__(
        self,
        retry_delay_seconds=DEFAULT_RETRY_DELAY_SECONDS,
        max_attempts=DEFAULT_MAX_ATTEMPTS,
        interface_name=None,
        minimum_retry_delay_seconds=MINIMUM_RETRY_DELAY_SECONDS,
        poll_interval_seconds=POLL_INTERVAL_SECONDS,
    ):
        self.retry_delay_seconds = max(
            float(retry_delay_seconds),
            float(minimum_retry_delay_seconds),
        )
        self.max_attempts = min(
            max(int(max_attempts), 1),
            self.MAXIMUM_ATTEMPTS,
        )
        self.interface_name = interface_name
        self.poll_interval_seconds = float(poll_interval_seconds)
        self._guarded_messages = {}
        self._guarded_messages_lock = threading.Lock()

    @staticmethod
    def _interface_is_enabled(interface_config):
        raw_value = interface_config.get(
            "enabled",
            interface_config.get("interface_enabled"),
        )
        if raw_value is None:
            return True
        return str(raw_value).lower() in ("on", "yes", "true", "1")

    @classmethod
    def from_reticulum_config(cls, reticulum_config):
        interfaces = reticulum_config.get("interfaces", {})
        for interface_name, interface_config in interfaces.items():
            if interface_config.get("type") != "IridiumIMTInterface":
                continue
            if not cls._interface_is_enabled(interface_config):
                continue

            return cls(
                retry_delay_seconds=interface_config.get(
                    "lxmf_retry_interval",
                    cls.DEFAULT_RETRY_DELAY_SECONDS,
                ),
                max_attempts=interface_config.get(
                    "lxmf_max_attempts",
                    cls.DEFAULT_MAX_ATTEMPTS,
                ),
                interface_name=interface_name,
            )

        return None

    @classmethod
    def packed_content_size(cls, content, fields=None, title=""):
        """Mirror LXMF.LXMessage.pack() sizing without creating a message."""

        if isinstance(content, str):
            content = content.encode("utf-8")
        if isinstance(title, str):
            title = title.encode("utf-8")

        payload = [time.time(), title, content, fields or {}]
        packed_payload = msgpack.packb(payload)
        return (
            len(packed_payload)
            - LXMF.LXMessage.TIMESTAMP_SIZE
            - LXMF.LXMessage.STRUCT_OVERHEAD
        )

    def validate_outbound(self, content, has_attachments, has_path):
        """Reject messages that cannot travel as one opportunistic packet."""

        if has_attachments:
            raise SatelliteMessageRejected(
                "Attachments are disabled over the satellite link because "
                "they require multi-packet direct transfers."
            )

        content_size = self.packed_content_size(content)
        if content_size > self.SINGLE_PACKET_CONTENT_LIMIT:
            raise SatelliteMessageRejected(
                f"Message is too large for one satellite packet "
                f"({content_size} > {self.SINGLE_PACKET_CONTENT_LIMIT} "
                "bytes). Shorten the message."
            )

        if not has_path:
            raise SatelliteMessageRejected(
                "No Reticulum route to this peer over the satellite link "
                "yet. Ask the peer to announce (for example tap Announce "
                "in Columba), wait for the announce to arrive, then send "
                "again."
            )

    @staticmethod
    def _is_terminal(lxmessage):
        return lxmessage.state in (
            LXMF.LXMessage.DELIVERED,
            LXMF.LXMessage.FAILED,
            LXMF.LXMessage.CANCELLED,
            LXMF.LXMessage.REJECTED,
        )

    def _wait_for_terminal_state(self, lxmessage):
        deadline = time.monotonic() + self.retry_delay_seconds
        while time.monotonic() < deadline:
            if self._is_terminal(lxmessage):
                return True
            remaining = deadline - time.monotonic()
            time.sleep(min(self.poll_interval_seconds, max(remaining, 0)))
        return self._is_terminal(lxmessage)

    def _register_message(self, lxmessage):
        message_id = getattr(lxmessage, "message_id", None)
        if message_id is None:
            return

        with self._guarded_messages_lock:
            self._guarded_messages[message_id] = lxmessage

    def _forget_message(self, lxmessage):
        message_id = getattr(lxmessage, "message_id", None)
        if message_id is None:
            return

        with self._guarded_messages_lock:
            if self._guarded_messages.get(message_id) is lxmessage:
                del self._guarded_messages[message_id]

    def cancel_message(self, message_id, message_router):
        """Cancel a guarded message after it has left LXMF's fast queue."""

        with self._guarded_messages_lock:
            lxmessage = self._guarded_messages.get(message_id)

        if lxmessage is None:
            return None

        # Let LXMF cancel any representation that is still in its queue.
        message_router.cancel_outbound(message_id)

        # Opportunistic satellite messages are removed from pending_outbound
        # immediately after their first send. Marking the retained object is
        # therefore required to stop the proof wait and any bounded retry.
        if not self._is_terminal(lxmessage):
            lxmessage.state = LXMF.LXMessage.CANCELLED

        self._forget_message(lxmessage)
        return lxmessage

    def supervise(self, lxmessage, message_router, original_send):
        try:
            while lxmessage._satellite_send_attempts < self.max_attempts:
                if self._wait_for_terminal_state(lxmessage):
                    return

                try:
                    lxmessage._satellite_send_attempts += 1
                    lxmessage.delivery_attempts = max(
                        lxmessage.delivery_attempts,
                        lxmessage._satellite_send_attempts,
                    )
                    RNS.log(
                        "Satellite LXMF retry "
                        f"{lxmessage._satellite_send_attempts}/"
                        f"{self.max_attempts} for {lxmessage}",
                        RNS.LOG_NOTICE,
                    )
                    original_send()
                except Exception as error:
                    RNS.log(
                        f"Satellite LXMF retry failed for {lxmessage}: {error}",
                        RNS.LOG_ERROR,
                    )
                    break

            if self._wait_for_terminal_state(lxmessage):
                return

            RNS.log(
                "Satellite LXMF proof window expired after "
                f"{lxmessage._satellite_send_attempts} attempt(s) for {lxmessage}",
                RNS.LOG_WARNING,
            )
            message_router.fail_message(lxmessage)
        finally:
            self._forget_message(lxmessage)

    def guard_message(self, lxmessage, message_router):
        """Replace this message's fast router retries with bounded retries."""

        if hasattr(lxmessage, "_satellite_original_send"):
            return

        original_send = lxmessage.send
        lxmessage._satellite_original_send = original_send
        lxmessage._satellite_send_attempts = 0
        supervisor_started = threading.Event()

        def guarded_send():
            if self._is_terminal(lxmessage):
                return None

            if lxmessage._satellite_send_attempts >= self.max_attempts:
                message_router.fail_message(lxmessage)
                return None

            lxmessage._satellite_send_attempts += 1
            try:
                result = original_send()
            except Exception as error:
                RNS.log(
                    f"Initial satellite LXMF send failed for {lxmessage}: {error}",
                    RNS.LOG_ERROR,
                )
                message_router.fail_message(lxmessage)
                return None

            self._register_message(lxmessage)

            # LXMF normally leaves opportunistic messages in its outbound
            # queue and retries them after only a few seconds. The receipt's
            # proof callback remains attached after removing the message.
            if lxmessage in message_router.pending_outbound:
                message_router.pending_outbound.remove(lxmessage)

            if not supervisor_started.is_set():
                supervisor_started.set()
                thread = threading.Thread(
                    target=self.supervise,
                    args=(lxmessage, message_router, original_send),
                    name="satellite-lxmf-retry",
                    daemon=True,
                )
                thread.start()

            return result

        lxmessage.send = guarded_send
