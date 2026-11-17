import os
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import RNS

from src.backend.audio_call_manager import RECOVERY_LINK_TIMEOUT, RECOVERY_PATH_TIMEOUT, AudioCall


class FakeLink:
    def __init__(self, status=None):
        self.status = RNS.Link.ACTIVE if status is None else status
        self.hash = os.urandom(16)
        self.closed_callback = None
        self.packet_callback = None
        self.identity = None
        self.torn_down = False

    def set_link_closed_callback(self, callback):
        self.closed_callback = callback

    def set_packet_callback(self, callback):
        self.packet_callback = callback

    def set_remote_identified_callback(self, callback):
        self.identified_callback = callback

    def get_remote_identity(self):
        return self.identity

    def identify(self, identity):
        self.identity = identity

    def teardown(self):
        self.torn_down = True
        self.status = RNS.Link.CLOSED
        if self.closed_callback is not None:
            self.closed_callback(self)


class FakePacket:
    sent = []

    def __init__(self, link, data, *args, **kwargs):
        self.link = link
        self.data = data

    def send(self):
        FakePacket.sent.append(self.data)


class AudioCallStabilityTest(unittest.TestCase):
    def setUp(self):
        FakePacket.sent = []

    def test_overlapping_audio_keeps_only_the_latest_payload(self):
        call = AudioCall(FakeLink(), is_outbound=True)
        with patch("src.backend.audio_call_manager.RNS.Packet", FakePacket), patch("src.backend.audio_call_manager.slowest_online_bitrate", return_value=21_875):
            call.send_audio_packet(b"one")
            call.send_audio_packet(b"two")
            call.send_audio_packet(b"three")
            self.assertEqual(FakePacket.sent, [b"one"])
            time.sleep(0.08)
        self.assertEqual(FakePacket.sent, [b"one", b"three"])

    def test_user_hangup_does_not_open_another_link(self):
        link = FakeLink()
        call = AudioCall(link, is_outbound=True)
        heard = []
        call.register_hangup_listener(lambda: heard.append("down"))
        with patch("src.backend.audio_call_manager.RNS.Link") as created:
            call.hangup()
            time.sleep(0.05)
        created.assert_not_called()
        self.assertEqual(heard, ["down"])
        self.assertTrue(call._user_hangup)

    def test_one_lost_link_is_replaced_without_a_hangup(self):
        original = FakeLink()
        call = AudioCall(original, is_outbound=True)
        call.destination_hash = b"\x44" * 16
        call._outbound_destination = object()
        call._local_identity = object()
        replacement = FakeLink()
        heard = []
        call.register_hangup_listener(lambda: heard.append("down"))

        async def fresh(*args, **kwargs):
            return True

        with patch("src.backend.audio_call_manager.ensure_fresh_path", fresh), patch("src.backend.audio_call_manager.RNS.Link", return_value=replacement):
            original.teardown()
            deadline = time.time() + 1
            while call.link is not replacement and time.time() < deadline:
                time.sleep(0.01)
        self.assertIs(call.link, replacement)
        self.assertEqual(call.lookup_hash, original.hash)
        self.assertEqual(heard, [])
        self.assertTrue(call.is_active())
        self.assertLessEqual(RECOVERY_PATH_TIMEOUT + RECOVERY_LINK_TIMEOUT, 20)
