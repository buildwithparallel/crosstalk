"""RNode BLE discovery and macOS compatibility helpers.

Reticulum's desktop RNode BLE support currently assumes that a scanner can
read an operating-system bond flag. CoreBluetooth does not expose the BlueZ
``Bonded`` property, and it represents device addresses as UUIDs instead of
Bluetooth MAC addresses. On macOS that makes otherwise reachable RNodes fail
Reticulum's pre-connection filter.

Crosstalk keeps the workaround deliberately narrow: only Darwin uses the
replacement filter, the device must advertise the RNode UART service, and
Bleak/CoreBluetooth still performs the real connection and authentication.
"""

from __future__ import annotations

import asyncio
import importlib
import platform
import time
from functools import wraps
from typing import Any


RNODE_UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def advertised_names(device: Any, advertisement: Any) -> list[str]:
    """Return distinct names exposed by Bleak and the advertisement."""
    names: list[str] = []
    for value in (
        getattr(advertisement, "local_name", None),
        getattr(device, "name", None),
    ):
        name = _text(value)
        if name and name not in names:
            names.append(name)
    return names


def device_identifier(device: Any) -> str:
    """Return Bleak's platform identifier (MAC on most OSes, UUID on macOS)."""
    return _text(getattr(device, "address", None))


def advertises_rnode_uart(advertisement: Any) -> bool:
    service_uuids = getattr(advertisement, "service_uuids", None) or []
    return RNODE_UART_SERVICE_UUID in {
        str(service_uuid).lower() for service_uuid in service_uuids
    }


def matches_rnode_device(device: Any, advertisement: Any, target: str | None) -> bool:
    """Match a UART-capable RNode by UUID/MAC or either advertised name."""
    if not advertises_rnode_uart(advertisement):
        return False

    names = advertised_names(device, advertisement)
    identifier = device_identifier(device)
    wanted = _text(target).casefold()

    if wanted:
        candidates = [identifier, *names]
        return any(candidate.casefold() == wanted for candidate in candidates if candidate)

    # A target-less ``ble://`` entry should not attach to an arbitrary Nordic
    # UART device. The in-app scanner can still select unusual advertisements
    # safely by saving their specific UUID/MAC as the target.
    return any(name.casefold().startswith("rnode ") for name in names)


def _rssi(advertisement: Any) -> int | None:
    value = getattr(advertisement, "rssi", None)
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


async def scan_rnode_ble_devices(timeout: float = 6.0, scanner_class=None) -> list[dict]:
    """Scan for devices advertising the RNode UART service."""
    if scanner_class is None:
        from bleak import BleakScanner

        scanner_class = BleakScanner

    discovered = await scanner_class.discover(timeout=timeout, return_adv=True)
    devices: list[dict] = []

    values = discovered.values() if isinstance(discovered, dict) else discovered
    for entry in values:
        if not isinstance(entry, (tuple, list)) or len(entry) != 2:
            continue
        device, advertisement = entry
        if not advertises_rnode_uart(advertisement):
            continue

        identifier = device_identifier(device)
        if not identifier:
            continue
        names = advertised_names(device, advertisement)
        devices.append({
            "identifier": identifier,
            "name": names[0] if names else "RNode",
            "advertised_name": _text(getattr(advertisement, "local_name", None)) or None,
            "system_name": _text(getattr(device, "name", None)) or None,
            "rssi": _rssi(advertisement),
        })

    # A stable order prevents the buttons jumping between scans.
    return sorted(devices, key=lambda item: (item["name"].casefold(), item["identifier"]))


def install_rnode_ble_dependency_guard() -> bool:
    """Make missing BLE support recoverable on initial connection and retries."""
    from RNS.Interfaces.RNodeInterface import BLEConnection

    original_init = BLEConnection.__init__
    if getattr(original_init, "_crosstalk_dependency_guard", False):
        return False

    @wraps(original_init)
    def guarded_init(self, *args, **kwargs):
        try:
            bleak = importlib.import_module("bleak")
        except (ImportError, OSError) as error:
            # Upstream calls RNS.panic() here, including from its reconnect
            # thread after startup protection has ended. Raise an ordinary
            # connection error instead so that thread can keep retrying.
            raise RuntimeError(
                "Bluetooth support is unavailable. This radio will stay offline "
                "while Crosstalk keeps running; repair the Crosstalk installation "
                "to restore Bluetooth support."
            ) from error

        # Frozen packages can import bleak without exposing a find_spec result.
        # Supply the modules before upstream's dynamic dependency detection.
        BLEConnection.bleak = bleak
        BLEConnection.asyncio = asyncio
        return original_init(self, *args, **kwargs)

    guarded_init._crosstalk_dependency_guard = True
    BLEConnection.__init__ = guarded_init
    return True


def apply_macos_rnode_ble_compatibility() -> bool:
    """Install Reticulum's Darwin BLE target filter workaround once."""
    if platform.system() != "Darwin":
        return False

    from RNS.Interfaces.RNodeInterface import BLEConnection

    if getattr(BLEConnection, "_crosstalk_macos_compat", False):
        return False

    async def discover_target(self):
        target = self.target_bt_addr or self.target_name

        def device_filter(device, advertisement):
            return matches_rnode_device(device, advertisement, target)

        return await self.bleak.BleakScanner.find_device_by_filter(
            device_filter,
            timeout=self.scan_timeout,
        )

    def find_target_device(self):
        import RNS

        target = self.target_bt_addr or self.target_name
        RNS.log(
            f"Searching for macOS RNode BLE target {target or '(first visible RNode)'}...",
            RNS.LOG_DEBUG,
        )

        try:
            return self.asyncio.run(discover_target(self))
        except Exception as error:
            RNS.log(
                f"Error while finding macOS RNode BLE device for {self.owner}: {error}",
                RNS.LOG_ERROR,
            )
            self.should_run = False
            return None

    def connect_device(self):
        """Run CoreBluetooth discovery and the connection on one event loop."""
        import RNS

        async def connect_job():
            self.connect_job_running = True
            self.must_disconnect = False
            try:
                device = await discover_target(self)
                if device is None:
                    return

                self.ble_device = device
                RNS.log(
                    f"Connecting macOS BLE device {device} for {self.owner}...",
                    RNS.LOG_DEBUG,
                )

                async with self.bleak.BleakClient(
                    device,
                    disconnected_callback=self.device_disconnected,
                    timeout=20.0,
                ) as ble_client:
                    def handle_rx(_characteristic, data):
                        if self.owner is not None:
                            self.owner.ble_receive(data)

                    uart_service = ble_client.services.get_service(self.UART_SERVICE_UUID)
                    if uart_service is None:
                        raise RuntimeError("RNode UART service disappeared after connection")
                    rx_characteristic = uart_service.get_characteristic(self.UART_RX_CHAR_UUID)
                    if rx_characteristic is None:
                        raise RuntimeError("RNode UART receive characteristic is unavailable")

                    # ESP32 RNode firmware exposes UART RX as write-with-response,
                    # while other implementations may also offer write without
                    # response. Forcing the latter makes CoreBluetooth silently
                    # discard commands on Heltec devices, so honour the GATT
                    # properties reported by the radio.
                    write_with_response = "write" in rx_characteristic.properties

                    # Accessing the protected UART characteristic is what asks
                    # CoreBluetooth to display the RNode's PIN prompt.
                    await ble_client.start_notify(self.UART_TX_CHAR_UUID, handle_rx)

                    self.last_client = ble_client
                    self.ble_device = ble_client
                    self.owner.port = f"ble://{ble_client.address}"
                    self.device_disappeared = False
                    self.connected = True

                    while self.connected and self.should_run:
                        if self.owner is not None and self.owner.ble_waiting():
                            outbound_data = self.owner.get_ble_waiting(
                                rx_characteristic.max_write_without_response_size
                            )
                            await ble_client.write_gatt_char(
                                rx_characteristic,
                                outbound_data,
                                response=write_with_response,
                            )
                        elif self.must_disconnect:
                            await ble_client.disconnect()
                        else:
                            await self.asyncio.sleep(0.1)
            except Exception as error:
                self.connected = False
                self.ble_device = None
                RNS.log(
                    "Could not connect macOS RNode BLE device for "
                    f"{self.owner}: {type(error).__name__}: {error!r}",
                    RNS.LOG_ERROR,
                )
            finally:
                self.connect_job_running = False

        self.asyncio.run(connect_job())

    def connection_job(self):
        import RNS

        self.running = True
        while self.should_run:
            if not self.connected and not self.connect_job_running:
                self.connect_device()
            if self.should_run:
                time.sleep(1)

        self.cleanup()
        self.running = False
        RNS.log(f"BLE connection job for {self.owner} ended", RNS.LOG_DEBUG)

    # Reticulum's normal five-second window can expire while macOS is showing
    # the PIN prompt. These values apply only after the Darwin guard above.
    BLEConnection.SCAN_TIMEOUT = 8.0
    BLEConnection.CONNECT_TIMEOUT = 35.0
    BLEConnection.find_target_device = find_target_device
    BLEConnection.connect_device = connect_device
    BLEConnection.connection_job = connection_job
    BLEConnection._crosstalk_macos_compat = True
    return True
