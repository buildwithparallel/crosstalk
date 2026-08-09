import tempfile
import threading
import time
import unittest
from collections import deque
from pathlib import Path
from unittest.mock import patch

import RNS

from src.backend.interfaces.IridiumIMTInterface import (
    DurablePacketQueue,
    DurablePathCache,
    IridiumIMTCodec,
    IridiumIMTInterface,
    RecentInboundPacketCache,
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


class DurablePathCacheTest(unittest.TestCase):

    def test_path_survives_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paths.sqlite3"
            destination_hash = bytes.fromhex("11" * 16)
            next_hop = bytes.fromhex("22" * 16)
            packet_hash = bytes.fromhex("33" * 32)
            path_entry = [
                100.0,
                next_hop,
                2,
                700.0,
                [bytes.fromhex("44" * 10)],
                object(),
                packet_hash,
            ]

            DurablePathCache(path).save(
                destination_hash,
                path_entry,
                recorded_at=150.0,
            )
            restored = DurablePathCache(path).load(destination_hash)

            self.assertEqual(restored["timestamp"], 100.0)
            self.assertEqual(restored["next_hop"], next_hop)
            self.assertEqual(restored["hops"], 2)
            self.assertEqual(restored["expires"], 700.0)
            self.assertEqual(restored["random_blobs"], [bytes.fromhex("44" * 10)])
            self.assertEqual(restored["packet_hash"], packet_hash)
            self.assertEqual(restored["recorded_at"], 150.0)

    def test_delete_removes_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paths.sqlite3"
            destination_hash = bytes.fromhex("11" * 16)
            path_entry = [
                100.0,
                bytes.fromhex("22" * 16),
                1,
                700.0,
                [],
                object(),
                bytes.fromhex("33" * 32),
            ]
            cache = DurablePathCache(path)
            cache.save(destination_hash, path_entry)
            cache.delete(destination_hash)

            self.assertIsNone(cache.load(destination_hash))


class PersistentDestinationParsingTest(unittest.TestCase):

    def test_parses_only_complete_destination_hashes(self):
        first = "11" * 16
        second = "22" * 16

        parsed = IridiumIMTInterface._parse_destination_hashes(
            f"{first}, {second} invalid 1234"
        )

        self.assertEqual(parsed, {bytes.fromhex(first), bytes.fromhex(second)})


class PersistentPathLifecycleTest(unittest.TestCase):

    def make_interface(self, cache, destination_hash):
        interface = object.__new__(IridiumIMTInterface)
        interface.name = "Test Iridium"
        interface.port = "/dev/test"
        interface.persistent_path_cache = cache
        interface.persistent_destination_hashes = {destination_hash}
        interface.persistent_path_max_age = 3600
        interface.persistent_paths_restored = False
        return interface

    def test_capture_and_restore_rebinds_only_to_same_interface(self):
        with tempfile.TemporaryDirectory() as directory:
            destination_hash = bytes.fromhex("11" * 16)
            next_hop = bytes.fromhex("22" * 16)
            packet_hash = bytes.fromhex("33" * 32)
            cache = DurablePathCache(Path(directory) / "paths.sqlite3")
            interface = self.make_interface(cache, destination_hash)
            path_entry = [
                time.time(),
                next_hop,
                2,
                time.time() + 3600,
                [bytes.fromhex("44" * 10)],
                interface,
                packet_hash,
            ]

            with patch.object(RNS.Transport, "path_table", {destination_hash: path_entry}):
                interface._capture_persistent_paths()

            with (
                patch.object(RNS.Transport, "interfaces", [interface]),
                patch.object(RNS.Transport, "path_table", {}) as restored_table,
            ):
                interface._restore_persistent_paths()

                self.assertIn(destination_hash, restored_table)
                self.assertEqual(restored_table[destination_hash][1], next_hop)
                self.assertEqual(restored_table[destination_hash][2], 2)
                self.assertIs(restored_table[destination_hash][5], interface)

    def test_restore_discards_stale_allowlisted_path(self):
        with tempfile.TemporaryDirectory() as directory:
            destination_hash = bytes.fromhex("11" * 16)
            cache = DurablePathCache(Path(directory) / "paths.sqlite3")
            interface = self.make_interface(cache, destination_hash)
            interface.persistent_path_max_age = 10
            path_entry = [
                1.0,
                bytes.fromhex("22" * 16),
                1,
                100.0,
                [],
                interface,
                bytes.fromhex("33" * 32),
            ]
            cache.save(destination_hash, path_entry, recorded_at=1.0)

            with (
                patch.object(RNS.Transport, "interfaces", [interface]),
                patch.object(RNS.Transport, "path_table", {}) as restored_table,
            ):
                interface._restore_persistent_paths()

                self.assertNotIn(destination_hash, restored_table)
                self.assertIsNone(cache.load(destination_hash))


class RecentInboundPacketCacheTest(unittest.TestCase):

    def test_suppresses_exact_duplicates_within_ttl(self):
        cache = RecentInboundPacketCache(ttl=10, maximum_packets=2)

        self.assertFalse(cache.check_and_record(b"first", now=1)[0])
        self.assertTrue(cache.check_and_record(b"first", now=2)[0])
        self.assertFalse(cache.check_and_record(b"first", now=12.1)[0])

    def test_evicts_oldest_packet_at_capacity(self):
        cache = RecentInboundPacketCache(ttl=100, maximum_packets=2)

        cache.check_and_record(b"first", now=1)
        cache.check_and_record(b"second", now=2)
        cache.check_and_record(b"third", now=3)

        self.assertFalse(cache.check_and_record(b"first", now=4)[0])


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
        interface.mt_message_ids = deque([7])
        interface.recent_inbound_packets = RecentInboundPacketCache()
        interface.state_lock = threading.Lock()
        interface.rxb = 0
        interface.persistent_path_cache = None
        return interface

    def test_incoming_frame_is_injected_and_acknowledged(self):
        packet = b"\x01native-reticulum-packet"
        interface = self.make_interface(IridiumIMTCodec.encode(packet))

        interface._drain_incoming()

        self.assertEqual(interface.owner.received, [(packet, interface)])
        self.assertEqual(interface.rxb, len(packet))
        self.assertTrue(interface.modem.acknowledged)
        self.assertEqual(list(interface.mt_message_ids), [])

    def test_invalid_frame_is_not_injected_but_is_acknowledged(self):
        interface = self.make_interface(b"not-a-native-frame")

        interface._drain_incoming()

        self.assertEqual(interface.owner.received, [])
        self.assertEqual(interface.rxb, 0)
        self.assertTrue(interface.modem.acknowledged)

    def test_duplicate_frame_is_acknowledged_but_only_injected_once(self):
        packet = b"\x01native-reticulum-packet"
        interface = self.make_interface(IridiumIMTCodec.encode(packet))

        interface._drain_incoming()
        interface.mt_message_ids.append(8)
        interface.modem.acknowledged = False
        interface._drain_incoming()

        self.assertEqual(interface.owner.received, [(packet, interface)])
        self.assertEqual(interface.rxb, len(packet))
        self.assertTrue(interface.modem.acknowledged)


class IridiumIMTTransmitLimitTest(unittest.TestCase):

    class FakeQueue:
        def __init__(self, packet):
            self.packet = packet
            self.completed = []

        def next_ready(self):
            return self.packet

        def complete(self, packet_id):
            self.completed.append(packet_id)

    class FakeModem:
        def __init__(self):
            self.sent = []

        def send_message_async(self, payload, topic):
            self.sent.append((payload, topic))
            return True

    def test_packet_is_not_resubmitted_after_modem_attempt_cap(self):
        interface = object.__new__(IridiumIMTInterface)
        interface.name = "Test Iridium"
        interface.port = "/dev/test"
        interface.modem = self.FakeModem()
        interface.packet_queue = self.FakeQueue((9, b"framed", 1))
        interface.maximum_modem_attempts = 1
        interface.current_packet = None
        interface.state_lock = threading.Lock()
        interface.topic = 244

        interface._start_next_outbound()

        self.assertEqual(interface.packet_queue.completed, [9])
        self.assertEqual(interface.modem.sent, [])
        self.assertIsNone(interface.current_packet)


if __name__ == "__main__":
    unittest.main()
