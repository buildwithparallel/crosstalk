import unittest
from unittest.mock import patch

import RNS

from src.backend.reticulum_startup import (
    disable_interface_in_config,
    defer_initial_radio_connection,
    recover_failed_interfaces,
)


class FakeConfig(dict):
    def __init__(self, interfaces):
        super().__init__()
        self["interfaces"] = interfaces
        self.writes = 0

    def write(self):
        self.writes += 1


class FakeReticulum:
    def __init__(self, interfaces):
        self.config = FakeConfig(interfaces)


class ReticulumStartupTest(unittest.TestCase):
    def test_disable_sets_existing_enabled_keys(self):
        config = {
            "interfaces": {
                "LAN": {
                    "type": "AutoInterface",
                    "enabled": "yes",
                    "interface_enabled": "true",
                },
            },
        }

        self.assertTrue(disable_interface_in_config(config, "LAN"))
        self.assertEqual(config["interfaces"]["LAN"]["enabled"], "false")
        self.assertEqual(config["interfaces"]["LAN"]["interface_enabled"], "false")

    def test_disable_adds_interface_enabled_when_missing(self):
        config = {"interfaces": {"LAN": {"type": "AutoInterface"}}}

        self.assertTrue(disable_interface_in_config(config, "LAN"))
        self.assertEqual(config["interfaces"]["LAN"]["interface_enabled"], "false")

    def test_disable_ignores_unknown_interface(self):
        config = {"interfaces": {}}
        self.assertFalse(disable_interface_in_config(config, "LAN"))

    def test_failed_synthesize_disables_interface_instead_of_exiting(self):
        real_synthesize = RNS.Reticulum._synthesize_interface
        real_panic = RNS.panic

        def boom(self, config, name, instance_init=False):
            RNS.panic()

        RNS.Reticulum._synthesize_interface = boom
        disabled_names = []
        reticulum = FakeReticulum({
            "LAN": {
                "type": "AutoInterface",
                "interface_enabled": "true",
            },
        })

        try:
            with recover_failed_interfaces(disabled_names):
                RNS.Reticulum._synthesize_interface(
                    reticulum,
                    reticulum.config["interfaces"]["LAN"],
                    "LAN",
                    instance_init=True,
                )
        finally:
            RNS.Reticulum._synthesize_interface = real_synthesize

        self.assertEqual(disabled_names, ["LAN"])
        self.assertEqual(
            reticulum.config["interfaces"]["LAN"]["interface_enabled"],
            "false",
        )
        self.assertEqual(reticulum.config.writes, 1)
        self.assertIs(RNS.panic, real_panic)

    def test_successful_synthesize_leaves_interface_enabled(self):
        real_synthesize = RNS.Reticulum._synthesize_interface
        calls = []

        def ok(self, config, name, instance_init=False):
            calls.append(name)
            return "started"

        RNS.Reticulum._synthesize_interface = ok
        disabled_names = []
        reticulum = FakeReticulum({
            "LAN": {
                "type": "AutoInterface",
                "interface_enabled": "true",
            },
        })

        try:
            with recover_failed_interfaces(disabled_names):
                result = RNS.Reticulum._synthesize_interface(
                    reticulum,
                    reticulum.config["interfaces"]["LAN"],
                    "LAN",
                    instance_init=True,
                )
        finally:
            RNS.Reticulum._synthesize_interface = real_synthesize

        self.assertEqual(result, "started")
        self.assertEqual(calls, ["LAN"])
        self.assertEqual(disabled_names, [])
        self.assertEqual(
            reticulum.config["interfaces"]["LAN"]["interface_enabled"],
            "true",
        )
        self.assertEqual(reticulum.config.writes, 0)

    def test_legacy_panic_setting_is_disabled_before_devices_start(self):
        reticulum = FakeReticulum({"radio": {"type": "RNodeInterface"}})
        observed = []

        def synthesize(self, config, name, instance_init=False):
            observed.append(RNS.Reticulum.panic_on_interface_error)

        with patch.object(RNS.Reticulum, "_synthesize_interface", synthesize), patch.object(RNS.Reticulum, "panic_on_interface_error", True, create=True):
            with recover_failed_interfaces([]):
                RNS.Reticulum._synthesize_interface(reticulum, reticulum.config["interfaces"]["radio"], "radio")
        self.assertEqual(observed, [False])
        self.assertEqual(reticulum.config.writes, 0)

    def test_initial_radio_connection_is_deferred_and_can_connect_later(self):
        class Radio:
            def __init__(self):
                self.settings = {"port": "configured-radio"}
                self.online = False
                self.retry_scheduled = False
                try:
                    self.open_port()
                except ConnectionError:
                    self.retry_scheduled = True

            def open_port(self):
                self.online = True

        self.assertTrue(defer_initial_radio_connection(Radio))
        self.assertFalse(defer_initial_radio_connection(Radio))
        radio = Radio()
        self.assertTrue(radio.retry_scheduled)
        self.assertFalse(radio.online)
        radio.open_port()
        self.assertTrue(radio.online)
        self.assertEqual(radio.settings, {"port": "configured-radio"})


if __name__ == "__main__":
    unittest.main()
