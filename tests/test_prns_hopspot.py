import time
import unittest
from collections import deque
from types import SimpleNamespace
from unittest.mock import patch

import RNS
from RNS.Interfaces.Interface import Interface
from src.backend.interfaces.PrnsHopspotInterface import (
    ACK_PREFIX, HELLO, MAX_MESSAGE, FrameDecoder, HopspotSession,
    PrnsHopspotInterface, decode_message, frame_message, usb_device_id, validate_device_id,
)


class FakeTransport:
    def __init__(self, chunks=(), answer=True):
        self.chunks = deque(chunks)
        self.writes = []
        self.answer = answer
        self.failed = False
        self.closed = False

    def open(self):
        return self

    def write(self, data):
        self.writes.append(data)
        if self.answer and data == frame_message(HELLO):
            self.chunks.append(frame_message(ACK_PREFIX + b"12345678"))

    def read(self):
        if self.failed:
            raise OSError("device rebooting")
        if self.chunks:
            return self.chunks.popleft()
        time.sleep(0.001)
        return b""

    def close(self):
        self.closed = True


class HopspotProtocolTest(unittest.TestCase):
    def test_hello_matches_upstream_v2_wire_format(self):
        self.assertEqual(frame_message(HELLO), bytes.fromhex("7e0150726e7302017e"))
        self.assertEqual(decode_message(ACK_PREFIX + b"12345678"), (2, b"12345678"))

    def test_all_byte_values_survive_split_usb_transfers(self):
        payload = b"\x03" + bytes(range(256))
        wire = frame_message(payload)
        for size in (1, 2, 3, 7, 64):
            decoder = FrameDecoder()
            frames = []
            for offset in range(0, len(wire), size):
                frames.extend(decoder.feed(wire[offset:offset + size]))
            self.assertEqual(frames, [payload])

    def test_oversized_and_malformed_frames_resynchronize(self):
        decoder = FrameDecoder()
        bad = b"\x7e" + b"x" * (MAX_MESSAGE + 1) + b"\x7e"
        self.assertEqual(decoder.feed(bad + frame_message(HELLO)), [HELLO])
        self.assertEqual(decoder.feed(b"\x7ex\x7d\x00\x7e" + frame_message(HELLO)), [HELLO])
        self.assertLessEqual(len(decoder.buffer), MAX_MESSAGE)

    def test_handshake_and_packets_share_usb_connection(self):
        transport = FakeTransport()
        session = HopspotSession(transport, b"abcdefgh")
        session.handshake(timeout=0.1)
        self.assertTrue(session.confirmed)
        self.assertEqual(session.peer_tag, b"12345678")
        session.send_packet(b"reticulum-packet")
        self.assertEqual(transport.writes[-1], frame_message(b"\x03reticulum-packet"))
        transport.chunks.append(frame_message(b"\x03reply"))
        self.assertEqual(session.receive(), [b"reply"])

    def test_device_initiated_handshake_is_answered(self):
        transport = FakeTransport([frame_message(HELLO)], answer=False)
        session = HopspotSession(transport, b"abcdefgh")
        session.receive()
        self.assertEqual(transport.writes, [frame_message(ACK_PREFIX + b"abcdefgh")])
        self.assertTrue(session.confirmed)

    def test_no_data_is_delivered_before_handshake(self):
        session = HopspotSession(FakeTransport([frame_message(b"\x03packet")]), b"abcdefgh")
        self.assertEqual(session.receive(), [])

    def test_missing_or_incompatible_device_hits_deadline(self):
        for response in (b"", frame_message(b"\x02Prns\x09\x01" + b"12345678")):
            session = HopspotSession(FakeTransport([response], answer=False), b"abcdefgh")
            started = time.monotonic()
            with self.assertRaises(TimeoutError):
                session.handshake(timeout=0.02)
            self.assertLess(time.monotonic() - started, 0.2)

    def test_selection_uses_physical_port_not_changing_usb_address(self):
        device = SimpleNamespace(bus=0, port_numbers=(1, 3), address=12)
        identity = usb_device_id(device)
        device.address = 25
        self.assertEqual(usb_device_id(device), identity)
        self.assertEqual(validate_device_id(identity), "usb:1209:0001:0:1.3")
        for value in (None, "", "/dev/cu.usbmodem1101", "usb:1209:0001:0:1\n"):
            with self.assertRaises(ValueError):
                validate_device_id(value)


class HopspotRecoveryTest(unittest.TestCase):
    def wait_for(self, condition):
        deadline = time.monotonic() + 0.5
        while not condition():
            if time.monotonic() > deadline:
                self.fail("Background interface did not reach the expected state")
            time.sleep(0.002)

    def test_missing_device_reconnects_and_reboot_recovers_same_selector(self):
        import src.backend.interfaces.PrnsHopspotInterface as module
        first, second = FakeTransport(), FakeTransport()
        calls = []
        owner = SimpleNamespace(inbound=lambda *args: None)
        def factory(selector):
            calls.append(selector)
            if len(calls) == 1:
                raise OSError("unplugged")
            return first if len(calls) == 2 else second
        def init(interface):
            interface.rxb = interface.txb = 0
        with patch.object(Interface, "__init__", init), patch.object(module, "PrnsUsbTransport", side_effect=factory), patch.object(PrnsHopspotInterface, "RECONNECT_INTERVAL", 0.005), patch.object(RNS, "log"), patch.object(RNS, "panic") as panic:
            radio = PrnsHopspotInterface(owner, {"name": "duo2", "device_id": "usb:1209:0001:0:1"})
            try:
                self.wait_for(lambda: radio.online)
                first.failed = True
                self.wait_for(lambda: radio.online and len(calls) >= 3)
                self.assertTrue(first.closed)
                self.assertEqual(set(calls), {"usb:1209:0001:0:1"})
                panic.assert_not_called()
            finally:
                radio.detach()
                radio._worker.join(timeout=1)
            self.assertFalse(radio._worker.is_alive())
            self.assertTrue(second.closed)


if __name__ == "__main__":
    unittest.main()
