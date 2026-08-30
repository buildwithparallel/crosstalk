import unittest

import RNS.vendor.umsgpack as msgpack

from src.backend.lxmf_app_data import display_name_from_app_data
from src.backend.live_activity import (
    display_name_for_aspect,
    heard_announce_payload,
    local_announce_payload,
)


class LxmfAppDataTest(unittest.TestCase):
    def test_reads_msgpack_string_names(self):
        packed = msgpack.packb(["EastPort Home", 8])
        self.assertEqual(display_name_from_app_data(packed), "EastPort Home")

    def test_reads_msgpack_byte_names(self):
        packed = msgpack.packb([b"EastPort Home", 8])
        self.assertEqual(display_name_from_app_data(packed), "EastPort Home")

    def test_reads_legacy_utf8_app_data(self):
        self.assertEqual(display_name_from_app_data(b"Anonymous Peer"), "Anonymous Peer")

    def test_empty_and_missing_app_data(self):
        self.assertIsNone(display_name_from_app_data(None))
        self.assertIsNone(display_name_from_app_data(b""))


class LiveActivityPayloadTest(unittest.TestCase):
    def test_nomad_node_name_from_bytes(self):
        self.assertEqual(
            display_name_for_aspect("nomadnetwork.node", b"rns.moscow"),
            "rns.moscow",
        )

    def test_heard_announce_payload_uses_hex_hash(self):
        packet = type("Packet", (), {})()
        packet.destination_hash = bytes.fromhex("aabbccdd")
        packet.hops = 2
        packet.rssi = None
        packet.snr = None
        packet.quality = None
        packet.receiving_interface = "TCPInterface[hub]"
        payload = heard_announce_payload(packet)
        self.assertEqual(payload["destination_hash"], "aabbccdd")
        self.assertEqual(payload["hops"], 2)
        self.assertEqual(payload["interface"], "TCPInterface[hub]")
        self.assertEqual(payload["origin"], "heard")

    def test_local_announce_payload_marks_sent(self):
        payload = local_announce_payload("abcd", "lxmf.delivery", "N0CALL")
        self.assertEqual(payload["origin"], "sent")
        self.assertEqual(payload["interface"], "this device")
        self.assertEqual(payload["display_name"], "N0CALL")
