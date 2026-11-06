import builtins
import unittest
from unittest.mock import patch

from src.backend import serial_ports


class SerialPortDiscoveryTest(unittest.TestCase):
    def test_android_skips_unsupported_port_enumerator(self):
        with patch.object(serial_ports.sys, "platform", "android"):
            self.assertIsNone(serial_ports._load_list_ports())

    def test_unsupported_platform_does_not_prevent_startup(self):
        original_import = builtins.__import__

        def import_without_serial_tools(name, *args, **kwargs):
            if name == "serial.tools":
                raise ImportError("no implementation for this platform")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=import_without_serial_tools):
            self.assertIsNone(serial_ports._load_list_ports())

    def test_unsupported_platform_returns_no_ports(self):
        with patch.object(serial_ports, "_LIST_PORTS", None):
            self.assertEqual(serial_ports.available_serial_ports(), [])

    def test_supported_platform_returns_detected_ports(self):
        detected_ports = [object(), object()]

        class FakeListPorts:
            @staticmethod
            def comports():
                return iter(detected_ports)

        with patch.object(serial_ports, "_LIST_PORTS", FakeListPorts):
            self.assertEqual(serial_ports.available_serial_ports(), detected_ports)


if __name__ == "__main__":
    unittest.main()
