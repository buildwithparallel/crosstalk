import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import RNS
from RNS.Interfaces import RNodeInterface as rnode_module

from src.backend.rnode_ble import (
    RNODE_UART_SERVICE_UUID,
    advertised_names,
    matches_rnode_device,
    scan_rnode_ble_devices,
    install_rnode_ble_dependency_guard,
)


CORE_BLUETOOTH_UUID = "06B073E2-E6F5-522B-E6A7-F68CCD0359B1"


def device(name="RNode 8561", address=CORE_BLUETOOTH_UUID):
    return SimpleNamespace(name=name, address=address)


def advertisement(local_name="RNode 8561", services=None, rssi=-53):
    return SimpleNamespace(
        local_name=local_name,
        service_uuids=services if services is not None else [RNODE_UART_SERVICE_UUID.upper()],
        rssi=rssi,
    )


class FakeScanner:
    results = {}

    @classmethod
    async def discover(cls, timeout, return_adv):
        cls.timeout = timeout
        cls.return_adv = return_adv
        return cls.results


class RNodeBleMatchingTest(unittest.TestCase):
    def test_names_include_local_and_system_names(self):
        self.assertEqual(
            advertised_names(
                device(name="Meshtastic_ed54"),
                advertisement(local_name="RNode 8561"),
            ),
            ["RNode 8561", "Meshtastic_ed54"],
        )

    def test_generic_target_accepts_advertised_rnode_name(self):
        self.assertTrue(
            matches_rnode_device(
                device(name="Meshtastic_ed54"),
                advertisement(local_name="RNode 8561"),
                None,
            )
        )

    def test_core_bluetooth_uuid_is_a_valid_specific_target(self):
        self.assertTrue(
            matches_rnode_device(
                device(),
                advertisement(),
                CORE_BLUETOOTH_UUID.lower(),
            )
        )

    def test_specific_target_can_match_either_name(self):
        self.assertTrue(
            matches_rnode_device(
                device(name="Meshtastic_ed54"),
                advertisement(local_name="RNode 8561"),
                "Meshtastic_ed54",
            )
        )

    def test_unrelated_uart_device_needs_specific_selection(self):
        candidate = device(name="Sensor")
        advert = advertisement(local_name="Telemetry")
        self.assertFalse(matches_rnode_device(candidate, advert, None))
        self.assertTrue(matches_rnode_device(candidate, advert, CORE_BLUETOOTH_UUID))

    def test_device_without_rnode_uart_service_is_rejected(self):
        self.assertFalse(
            matches_rnode_device(
                device(),
                advertisement(services=["0000180f-0000-1000-8000-00805f9b34fb"]),
                CORE_BLUETOOTH_UUID,
            )
        )


class RNodeBleScanTest(unittest.IsolatedAsyncioTestCase):
    async def test_scan_returns_uuid_names_and_signal(self):
        FakeScanner.results = {
            CORE_BLUETOOTH_UUID: (
                device(name="Meshtastic_ed54"),
                advertisement(local_name="RNode 8561", rssi=-53),
            ),
            "ignored": (
                device(name="Headphones", address="ignored"),
                advertisement(
                    local_name="Headphones",
                    services=["0000180f-0000-1000-8000-00805f9b34fb"],
                ),
            ),
        }

        results = await scan_rnode_ble_devices(timeout=3.5, scanner_class=FakeScanner)

        self.assertEqual(FakeScanner.timeout, 3.5)
        self.assertTrue(FakeScanner.return_adv)
        self.assertEqual(results, [{
            "identifier": CORE_BLUETOOTH_UUID,
            "name": "RNode 8561",
            "advertised_name": "RNode 8561",
            "system_name": "Meshtastic_ed54",
            "rssi": -53,
        }])


class RNodeBleRecoveryTest(unittest.TestCase):
    def setUp(self):
        self.initialized = []
        initialized = self.initialized

        class Connection:
            bleak = None

            def __init__(self, owner=None, **kwargs):
                initialized.append(owner)
                self.connected = True
                self.is_open = True
                self.running = True
                self.CONNECT_TIMEOUT = 0

        self.connection = Connection
        self.connection_patch = patch.object(rnode_module, "BLEConnection", Connection)
        self.connection_patch.start()
        self.addCleanup(self.connection_patch.stop)

    def test_missing_ble_support_never_reaches_fatal_constructor(self):
        install_rnode_ble_dependency_guard()
        with patch("src.backend.rnode_ble.importlib.import_module", side_effect=ModuleNotFoundError("bleak")), patch.object(RNS, "panic") as panic:
            for _ in range(3):
                with self.assertRaisesRegex(RuntimeError, "Bluetooth support is unavailable"):
                    self.connection(owner="radio")
        panic.assert_not_called()
        self.assertEqual(self.initialized, [])

    def test_broken_native_dependency_is_a_connection_error(self):
        install_rnode_ble_dependency_guard()
        with patch("src.backend.rnode_ble.importlib.import_module", side_effect=OSError("native library unavailable")):
            with self.assertRaisesRegex(RuntimeError, "Bluetooth support is unavailable"):
                self.connection(owner="radio")

    def test_guard_is_idempotent_and_supplies_frozen_dependency(self):
        self.assertTrue(install_rnode_ble_dependency_guard())
        self.assertFalse(install_rnode_ble_dependency_guard())
        bleak = object()
        with patch("src.backend.rnode_ble.importlib.import_module", return_value=bleak):
            self.connection(owner="radio")
        self.assertEqual(self.initialized, ["radio"])
        self.assertIs(self.connection.bleak, bleak)

    def test_reconnect_survives_failures_then_recovers_without_losing_config(self):
        install_rnode_ble_dependency_guard()
        radio = SimpleNamespace(
            port=None, name="radio", online=False, detached=False,
            reconnecting=False, use_ble=True, use_tcp=False, ble=None,
            ble_name="RNode Test", ble_addr=None,
        )
        radio.open_port = lambda: rnode_module.RNodeInterface.open_port(radio)
        radio.configure_device = Mock(side_effect=lambda: setattr(radio, "online", True))
        with patch("src.backend.rnode_ble.importlib.import_module", side_effect=[ModuleNotFoundError("bleak"), OSError("device rebooting"), object()]), patch.object(rnode_module.time, "sleep"), patch.object(RNS, "log"), patch.object(RNS, "panic") as panic:
            rnode_module.RNodeInterface.reconnect_port(radio)
        panic.assert_not_called()
        self.assertTrue(radio.online)
        self.assertFalse(radio.reconnecting)
        self.assertEqual(radio.ble_name, "RNode Test")
        radio.configure_device.assert_called_once()

    def test_unplugged_usb_radio_enters_reconnect(self):
        serial = SimpleNamespace(
            is_open=True, in_waiting=1,
            read=Mock(side_effect=OSError("device unplugged")), close=Mock(),
        )
        radio = SimpleNamespace(
            serial=serial, online=True, detached=False, reconnecting=False,
            reconnect_port=Mock(),
        )
        with patch.object(RNS.Reticulum, "panic_on_interface_error", False, create=True), patch.object(RNS, "log"), patch.object(RNS, "panic") as panic:
            rnode_module.RNodeInterface.readLoop(radio)
        panic.assert_not_called()
        self.assertFalse(radio.online)
        serial.close.assert_called_once()
        radio.reconnect_port.assert_called_once()


if __name__ == "__main__":
    unittest.main()
