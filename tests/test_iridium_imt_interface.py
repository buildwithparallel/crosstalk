import tempfile
import unittest
from pathlib import Path

from src.backend.interfaces.IridiumIMTInterface import (
    DurablePacketQueue,
    IridiumIMTCodec,
    IridiumIMTInterface,
)


class IridiumIMTCodecTest(unittest.TestCase):

    def test_round_trip_preserves_native_reticulum_packet(self):
        packet = bytes(range(256)) + bytes(range(244))
        message = IridiumIMTCodec.encode(packet)

        self.assertEqual(message[:5], b"RNSI\x01")
        self.assertEqual(IridiumIMTCodec.decode(message), packet)

    def test_rejects_unknown_or_empty_frames(self):
        with self.assertRaises(ValueError):
            IridiumIMTCodec.decode(b"not-reticulum")

        with self.assertRaises(ValueError):
            IridiumIMTCodec.decode(IridiumIMTCodec.HEADER)


class DurablePacketQueueTest(unittest.TestCase):

    def test_queue_survives_reopen_and_completes_in_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite3"
            first_queue = DurablePacketQueue(path)
            self.assertTrue(first_queue.enqueue(b"first"))
            self.assertTrue(first_queue.enqueue(b"second"))

            reopened_queue = DurablePacketQueue(path)
            packet_id, payload, attempts = reopened_queue.next_ready(now=1e20)
            self.assertEqual(payload, b"first")
            self.assertEqual(attempts, 0)

            reopened_queue.complete(packet_id)
            _, payload, _ = reopened_queue.next_ready(now=1e20)
            self.assertEqual(payload, b"second")

    def test_retry_and_capacity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite3"
            queue = DurablePacketQueue(path, maximum_packets=1)
            self.assertTrue(queue.enqueue(b"packet"))
            self.assertFalse(queue.enqueue(b"overflow"))

            packet_id, _, _ = queue.next_ready(now=1e20)
            queue.retry(packet_id, delay=60, error="no signal")
            self.assertIsNone(queue.next_ready(now=0))
            self.assertEqual(queue.count(), 1)


class IridiumIMTReceiveTest(unittest.TestCase):

    class FakeOwner:
        def __init__(self):
            self.received = []

        def inbound(self, packet, interface):
            self.received.append((packet, interface))

    class FakeModem:
        def __init__(self, message):
            self.message = message
            self.acknowledged = False

        def receive_message_async(self):
            return self.message

        def acknowledge_receive_head_async(self):
            self.acknowledged = True
            return True

    def make_interface(self, message):
        interface = object.__new__(IridiumIMTInterface)
        interface.name = "Test Iridium"
        interface.port = "/dev/test"
        interface.owner = self.FakeOwner()
        interface.modem = self.FakeModem(message)
        interface.mt_message_ready = True
        interface.rxb = 0
        return interface

    def test_incoming_frame_is_injected_and_acknowledged(self):
        packet = b"\x01native-reticulum-packet"
        interface = self.make_interface(IridiumIMTCodec.encode(packet))

        interface._drain_incoming()

        self.assertEqual(interface.owner.received, [(packet, interface)])
        self.assertEqual(interface.rxb, len(packet))
        self.assertTrue(interface.modem.acknowledged)
        self.assertFalse(interface.mt_message_ready)

    def test_invalid_frame_is_not_injected_but_is_acknowledged(self):
        interface = self.make_interface(b"not-a-native-frame")

        interface._drain_incoming()

        self.assertEqual(interface.owner.received, [])
        self.assertEqual(interface.rxb, 0)
        self.assertTrue(interface.modem.acknowledged)


if __name__ == "__main__":
    unittest.main()
