import tempfile
import unittest
from pathlib import Path

from src.backend.interfaces.IridiumIMTInterface import (
    DurablePacketQueue,
    IridiumIMTCodec,
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


if __name__ == "__main__":
    unittest.main()
