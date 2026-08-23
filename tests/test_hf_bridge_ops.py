import socket
import unittest
from pathlib import Path

from src.backend.hf_bridge_ops import (
    DEFAULT_FREQUENCY_HZ,
    DEFAULT_RTL_GAIN_DB,
    amplitude_from_power_percent,
    announced_bridges,
    build_command,
    classify_bridge_name,
    discover_hl2_radios,
    last_resort_peer_from_title,
    last_resort_send_error,
    last_resort_title,
    parse_allow_hashes,
    parse_hl2_discovery_reply,
    parse_ingress_stats,
    parse_txbridge_stats,
    pick_tx_bridge,
    settings_from_power_percent,
    snap_rtl_gain_db,
)


class HfBridgeOpsTest(unittest.TestCase):
    def test_classifies_bridge_display_names(self):
        self.assertEqual(classify_bridge_name("hf-txbridge"), "txbridge")
        self.assertEqual(classify_bridge_name("hf-ingress"), "ingress")
        self.assertIsNone(classify_bridge_name("Tim's Mom"))

    def test_txbridge_stays_dry_run_until_armed(self):
        command = build_command(
            "txbridge",
            repo=Path("/tmp/hf"),
            callsign="KR4NNP",
            hl2_ip="169.254.19.221",
            arm_tx=False,
        )
        self.assertIn("hfbridge.txbridge", command)
        self.assertNotIn("--arm-tx", command)
        self.assertEqual(
            command[command.index("--frequency") + 1], str(DEFAULT_FREQUENCY_HZ)
        )
        amplitude, drive = settings_from_power_percent(10)
        self.assertEqual(command[command.index("--amplitude") + 1], str(amplitude))
        self.assertEqual(command[command.index("--drive") + 1], str(drive))
        self.assertNotIn("--allow", command)

    def test_txbridge_allow_list_and_power(self):
        peer = "aa" * 16
        command = build_command(
            "txbridge",
            repo=Path("/tmp/hf"),
            callsign="KR4NNP",
            hl2_ip="169.254.19.221",
            arm_tx=False,
            frequency_hz=28_130_000,
            power_percent=100,
            allow_enabled=True,
            allow_hashes=[peer],
        )
        self.assertEqual(command[command.index("--frequency") + 1], "28130000")
        self.assertEqual(command[command.index("--amplitude") + 1], "1.0")
        self.assertEqual(command[command.index("--drive") + 1], "255")
        self.assertEqual(command[command.index("--allow") + 1], peer)

    def test_txbridge_allow_list_requires_someone(self):
        with self.assertRaises(ValueError):
            build_command(
                "txbridge",
                repo=Path("/tmp/hf"),
                callsign="KR4NNP",
                hl2_ip="169.254.19.221",
                arm_tx=False,
                allow_enabled=True,
                allow_hashes=[],
            )

    def test_frequency_must_stay_legal(self):
        with self.assertRaises(ValueError):
            build_command(
                "txbridge",
                repo=Path("/tmp/hf"),
                callsign="KR4NNP",
                hl2_ip="169.254.19.221",
                arm_tx=False,
                frequency_hz=28_120_000,
            )

    def test_parse_allow_hashes_and_power_percent(self):
        peer = "b9ab2399f5d00df37b705684ea010af3"
        self.assertEqual(parse_allow_hashes(f"lxmf@{peer.upper()}\n, {peer}"), [peer])
        self.assertEqual(settings_from_power_percent(100), (1.0, 255))
        amplitude, drive = settings_from_power_percent(10)
        self.assertEqual(amplitude_from_power_percent(10), amplitude)
        self.assertGreater(drive, 16)
        self.assertLess(drive, 255)

    def test_ingress_uses_tuner_gain(self):
        command = build_command(
            "ingress",
            repo=Path("/tmp/hf"),
            callsign="",
            hl2_ip="",
            arm_tx=False,
        )
        self.assertEqual(command[command.index("--gain") + 1], str(DEFAULT_RTL_GAIN_DB))
        command = build_command(
            "ingress",
            repo=Path("/tmp/hf"),
            callsign="",
            hl2_ip="",
            arm_tx=False,
            rtl_gain_db=41.9,
        )
        self.assertEqual(command[command.index("--gain") + 1], "42.1")
        self.assertEqual(snap_rtl_gain_db(20.5), 20.7)

    def test_arming_requires_radio_ip(self):
        with self.assertRaises(ValueError):
            build_command(
                "txbridge",
                repo=Path("/tmp/hf"),
                callsign="KR4NNP",
                hl2_ip="",
                arm_tx=True,
            )

    def test_announced_bridges_keep_recent_tx_and_ingress(self):
        found = announced_bridges(
            [
                {
                    "display_name": "hf-txbridge",
                    "destination_hash": "aa" * 16,
                    "hops": 1,
                    "updated_at": 100.0,
                },
                {
                    "display_name": "someone",
                    "destination_hash": "bb" * 16,
                    "updated_at": 100.0,
                },
            ],
            now=110.0,
        )
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["role"], "txbridge")
        self.assertTrue(found[0]["heard_recently"])

    def test_last_resort_title_round_trip(self):
        dest = "b9ab2399f5d00df37b705684ea010af3"
        self.assertEqual(last_resort_title(dest), f"hfdest:{dest}")
        self.assertEqual(last_resort_peer_from_title(last_resort_title(dest)), dest)
        self.assertIsNone(last_resort_peer_from_title("hello"))

    def test_last_resort_send_rejects_attachments_and_oversize(self):
        dest = last_resort_title("b9ab2399f5d00df37b705684ea010af3")
        self.assertIsNone(last_resort_send_error(dest, "hello"))
        self.assertIsNone(last_resort_send_error("ordinary", "x" * 500, {"image": True}))
        self.assertIsNotNone(last_resort_send_error(dest, "hello", {"image": {"image_type": "png"}}))
        self.assertIsNotNone(last_resort_send_error(dest, "x" * 201))
        self.assertIsNotNone(last_resort_send_error(dest, "   "))
        self.assertIn("language", last_resort_send_error(dest, "what the fuck") or "")
        self.assertIn("coded", last_resort_send_error(dest, "-----BEGIN PGP MESSAGE-----\nww") or "")

    def test_pick_tx_bridge_prefers_recent(self):
        chosen = pick_tx_bridge(
            [
                {
                    "role": "ingress",
                    "destination_hash": "11" * 16,
                    "heard_recently": True,
                },
                {
                    "role": "txbridge",
                    "destination_hash": "22" * 16,
                    "heard_recently": False,
                },
                {
                    "role": "txbridge",
                    "destination_hash": "33" * 16,
                    "heard_recently": True,
                },
            ]
        )
        self.assertEqual(chosen["destination_hash"], "33" * 16)

    def test_parse_hl2_discovery_reply(self):
        payload = b"\xef\xfe\x02" + bytes.fromhex("001cc0a213dd") + bytes([74, 6]) + bytes(20)
        self.assertEqual(
            parse_hl2_discovery_reply(payload, "192.168.0.164"),
            {
                "ip": "192.168.0.164",
                "mac": "00:1c:c0:a2:13:dd",
                "gateware_version": 74,
                "board_id": 6,
            },
        )
        self.assertIsNone(parse_hl2_discovery_reply(b"nope", "192.168.0.164"))

    def test_discover_hl2_radios_collects_unique_replies(self):
        payload = b"\xef\xfe\x02" + bytes.fromhex("001cc0a213dd") + bytes([74, 6]) + bytes(20)

        class FakeSocket:
            def __init__(self, *_args):
                self.replies = [(payload, ("192.168.0.164", 1024))]

            def setsockopt(self, *_args):
                return None

            def bind(self, *_args):
                return None

            def sendto(self, *_args):
                return None

            def settimeout(self, *_args):
                return None

            def recvfrom(self, *_args):
                if not self.replies:
                    raise socket.timeout()
                return self.replies.pop(0)

            def close(self):
                return None

        radios = discover_hl2_radios(timeout=0.05, _socket_factory=lambda *_args: FakeSocket())
        self.assertEqual(radios[0]["ip"], "192.168.0.164")
        self.assertEqual(radios[0]["mac"], "00:1c:c0:a2:13:dd")

    def test_parse_ingress_stats_uses_the_latest_line(self):
        log = (
            "ingress abc\n"
            "ingress-stats heard=0 forwarded=0 decode_failed=0 inject_failed=0\n"
            "decoded KR4NNP 8B\n"
            "ingress-stats heard=2 forwarded=1 decode_failed=1 inject_failed=0 last=KR4NNP\n"
        )
        self.assertEqual(
            parse_ingress_stats(log),
            {
                "heard": 2,
                "forwarded": 1,
                "decode_failed": 1,
                "inject_failed": 0,
                "last_origin": "KR4NNP",
            },
        )
        self.assertEqual(parse_ingress_stats(""), {"heard": 0, "forwarded": 0, "decode_failed": 0, "inject_failed": 0, "last_origin": None})

    def test_parse_txbridge_stats_uses_the_latest_line(self):
        log = (
            "txbridge abc\n"
            "txbridge-stats received=0 on_air=0 held=0 rejected=0 tx_failed=0\n"
            "txbridge-stats received=4 on_air=1 held=2 rejected=1 tx_failed=0 last_bytes=12\n"
        )
        self.assertEqual(
            parse_txbridge_stats(log),
            {
                "received": 4,
                "on_air": 1,
                "held": 2,
                "rejected": 1,
                "tx_failed": 0,
                "last_bytes": 12,
            },
        )


if __name__ == "__main__":
    unittest.main()
