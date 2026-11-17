import asyncio
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import RNS

from src.backend.path_refresh import (
    ensure_fresh_path,
    forget_path,
    path_is_stale,
    path_is_usable,
    path_retry_seconds,
    normalize_auto_announce_interval_seconds,
    route_max_age_seconds,
)


class PathRefreshTest(unittest.TestCase):
    def setUp(self):
        self.destination = bytes(range(16))
        self.saved = dict(RNS.Transport.path_table)
        RNS.Transport.path_table.clear()

    def tearDown(self):
        RNS.Transport.path_table.clear()
        RNS.Transport.path_table.update(self.saved)

    def entry(self, timestamp, interface=None):
        return [timestamp, b"\x22" * 16, 1, timestamp + 3600, [], interface, b"\x33" * 16]

    def test_announce_interval_is_minutes_or_off(self):
        self.assertEqual(normalize_auto_announce_interval_seconds(0), 0)
        self.assertEqual(normalize_auto_announce_interval_seconds(-5), 0)
        self.assertEqual(normalize_auto_announce_interval_seconds("nope"), 0)
        self.assertEqual(normalize_auto_announce_interval_seconds(60), 60)
        self.assertEqual(normalize_auto_announce_interval_seconds(90), 60)
        self.assertEqual(normalize_auto_announce_interval_seconds(8 * 24 * 60 * 60), 7 * 24 * 60 * 60)

    def test_auto_announce_off_uses_a_quarter_hour(self):
        self.assertEqual(route_max_age_seconds(0), 15 * 60)
        self.assertEqual(route_max_age_seconds(None), 15 * 60)
        self.assertEqual(route_max_age_seconds(120), 120)

    def test_path_learned_before_usb_reconnect_is_stale(self):
        interface = SimpleNamespace(connected_at=time.time())
        RNS.Transport.path_table[self.destination] = self.entry(interface.connected_at - 5, interface)
        self.assertTrue(path_is_stale(self.destination, 0))
        self.assertFalse(path_is_usable(self.destination, 0))

    def test_fresh_path_is_usable_and_zero_timestamp_is_not(self):
        interface = SimpleNamespace(connected_at=time.time() - 30)
        RNS.Transport.path_table[self.destination] = self.entry(time.time(), interface)
        self.assertTrue(path_is_usable(self.destination, 15 * 60))
        RNS.Transport.path_table[self.destination][0] = 0
        self.assertTrue(RNS.Transport.has_path(self.destination))
        self.assertTrue(path_is_stale(self.destination, 0))

    def test_forget_path_removes_the_entry(self):
        RNS.Transport.path_table[self.destination] = self.entry(time.time())
        forget_path(self.destination)
        self.assertNotIn(self.destination, RNS.Transport.path_table)

    def test_request_repeats_after_one_airtime_until_a_usable_path_exists(self):
        requests = []

        def request_path(destination_hash, *args, **kwargs):
            requests.append(destination_hash)
            if len(requests) == 2:
                RNS.Transport.path_table[destination_hash] = self.entry(time.time())

        with patch.object(RNS.Transport, "request_path", request_path):
            found = asyncio.run(ensure_fresh_path(self.destination, timeout_seconds=3, max_age_seconds=60, bitrate=4000))
        self.assertTrue(found)
        self.assertGreaterEqual(len(requests), 2)
        self.assertGreaterEqual(path_retry_seconds(4000), 1.0)
