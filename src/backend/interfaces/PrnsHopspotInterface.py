"""Direct Prns Hopspot USB transport for stock Python Reticulum.

USB Auto v2 protocol: https://github.com/KenAKAFrosty/Prns
Only the selected physical USB port is opened. No firmware, bootloader,
controller grants, radio configuration, or private keys are read or written.
"""
import ctypes.util
import hashlib
import os
import re
import sys
import threading
import time

import RNS
from RNS.Interfaces.Interface import Interface

USB_VENDOR = 0x1209
USB_PRODUCT = 0x0001
MAX_MESSAGE = 1 + 8192 + 64
HELLO = b"\x01Prns\x02\x01"
ACK_PREFIX = b"\x02Prns\x02\x01"
DEVICE_PATTERN = re.compile(r"usb:1209:0001:\d+:\d+(?:\.\d+)*\Z")


def validate_device_id(value):
    if not isinstance(value, str) or not DEVICE_PATTERN.fullmatch(value):
        raise ValueError("Select a Prns Hopspot USB device before saving.")
    return value


def frame_message(payload):
    if not payload or len(payload) > MAX_MESSAGE:
        raise ValueError("Invalid Hopspot message size")
    return b"\x7e" + payload.replace(b"\x7d", b"\x7d\x5d").replace(b"\x7e", b"\x7d\x5e") + b"\x7e"


class FrameDecoder:
    """Bounded streaming decoder, including USB transfers split mid-escape."""
    def __init__(self):
        self.buffer = bytearray()
        self.escaped = False
        self.dropping = False

    def feed(self, data):
        frames = []
        for byte in data:
            if byte == 0x7e:
                if self.buffer and not self.dropping and not self.escaped:
                    frames.append(bytes(self.buffer))
                self.buffer.clear()
                self.escaped = self.dropping = False
            elif self.dropping:
                continue
            elif self.escaped:
                self.escaped = False
                if byte not in (0x5d, 0x5e):
                    self.buffer.clear()
                    self.dropping = True
                else:
                    self.buffer.append(byte ^ 0x20)
            elif byte == 0x7d:
                self.escaped = True
            else:
                self.buffer.append(byte)
            if len(self.buffer) > MAX_MESSAGE:
                self.buffer.clear()
                self.dropping = True
        return frames


def decode_message(payload):
    if not payload:
        raise ValueError("Empty Hopspot message")
    kind = payload[0]
    if kind == 3:
        if len(payload) > MAX_MESSAGE:
            raise ValueError("Oversized Hopspot packet")
        return kind, payload[1:]
    if kind not in (1, 2) or len(payload) != (7 if kind == 1 else 15):
        raise ValueError("Invalid Hopspot handshake")
    if payload[1:5] != b"Prns" or payload[5] != 2:
        raise ValueError("Unsupported Hopspot USB protocol")
    return kind, payload[7:] if kind == 2 else b""


def usb_modules():
    try:
        import usb.core
        import usb.util
        import usb.backend.libusb1
    except ImportError as error:
        raise RuntimeError("USB support is unavailable. Install the Crosstalk USB dependencies.") from error
    bundled = os.path.join(os.path.dirname(sys.executable), "lib", "libusb-1.0.dylib")
    backend = usb.backend.libusb1.get_backend(
        find_library=lambda name: bundled if os.path.isfile(bundled) else ctypes.util.find_library(name)
    )
    if backend is None:
        raise RuntimeError("The native libusb library is unavailable.")
    return usb.core, usb.util, backend


def usb_device_id(device):
    ports = tuple(device.port_numbers or ())
    if device.bus is None or not ports:
        raise ValueError("This USB device does not expose a stable physical port.")
    return "usb:1209:0001:" + str(device.bus) + ":" + ".".join(str(p) for p in ports)


def discover_usb_devices():
    core, util, backend = usb_modules()
    found = []
    for device in core.find(find_all=True, idVendor=USB_VENDOR, idProduct=USB_PRODUCT, backend=backend):
        try:
            device.default_timeout = 500
            product = device.product or ""
            if not product.startswith("Personal Hopspot"):
                continue
            selector = usb_device_id(device)
            found.append({
                "device_id": selector,
                "name": product,
                "serial": device.serial_number or "",
                "label": product + " · USB " + selector.split("0001:", 1)[1],
            })
        finally:
            util.dispose_resources(device)
    return sorted(found, key=lambda item: item["device_id"])


class PrnsUsbTransport:
    """USB byte stream. A future Bluetooth transport can supply read/write/close."""
    def __init__(self, device_id):
        self.device_id = validate_device_id(device_id)
        self.device = None
        self.interface_number = None

    def open(self):
        core, self.util, backend = usb_modules()
        self.core = core
        devices = list(core.find(find_all=True, idVendor=USB_VENDOR, idProduct=USB_PRODUCT, backend=backend))
        selected = []
        try:
            for device in devices:
                if usb_device_id(device) == self.device_id:
                    selected.append(device)
            if len(selected) != 1:
                raise OSError("Selected Hopspot is disconnected or its USB port is ambiguous.")
            self.device = selected[0]
            self.device.default_timeout = 500
            if not (self.device.product or "").startswith("Personal Hopspot"):
                raise OSError("Selected USB device is not a Prns Hopspot.")
            config = self.device.get_active_configuration()
            candidates = []
            for interface in config:
                if interface.bInterfaceClass != 0xff:
                    continue
                description = self.util.get_string(self.device, interface.iInterface) if interface.iInterface else ""
                if description != "Personal Hopspot WebUSB Auto":
                    continue
                endpoints = [e for e in interface if self.util.endpoint_type(e.bmAttributes) == 2]
                incoming = [e for e in endpoints if self.util.endpoint_direction(e.bEndpointAddress) == 0x80]
                outgoing = [e for e in endpoints if self.util.endpoint_direction(e.bEndpointAddress) == 0]
                if len(incoming) == len(outgoing) == 1:
                    candidates.append((interface, incoming[0], outgoing[0]))
            if len(candidates) != 1:
                raise OSError("Hopspot USB data endpoints were not found.")
            interface, self.incoming, self.outgoing = candidates[0]
            self.util.claim_interface(self.device, interface.bInterfaceNumber)
            self.interface_number = interface.bInterfaceNumber
        except Exception:
            self.close()
            raise
        finally:
            for device in devices:
                if device is not self.device:
                    self.util.dispose_resources(device)
        return self

    def read(self):
        try:
            return bytes(self.incoming.read(self.incoming.wMaxPacketSize, timeout=200))
        except self.core.USBTimeoutError:
            return b""

    def write(self, data):
        for offset in range(0, len(data), self.outgoing.wMaxPacketSize):
            chunk = data[offset:offset + self.outgoing.wMaxPacketSize]
            if self.outgoing.write(chunk, timeout=500) != len(chunk):
                raise OSError("Incomplete Hopspot USB write")

    def close(self):
        if self.device is not None:
            try:
                if self.interface_number is not None:
                    self.util.release_interface(self.device, self.interface_number)
            finally:
                self.util.dispose_resources(self.device)
                self.device = None
                self.interface_number = None


class HopspotSession:
    """USB Auto framing and handshake, separated from the USB byte stream."""
    def __init__(self, transport, node_tag):
        self.transport = transport
        self.node_tag = bytes(node_tag)
        if len(self.node_tag) != 8:
            raise ValueError("Hopspot node tag must be eight bytes")
        self.decoder = FrameDecoder()
        self.write_lock = threading.Lock()
        self.confirmed = False
        self.peer_tag = None
        self.last_seen = time.monotonic()

    def write_message(self, message):
        with self.write_lock:
            self.transport.write(frame_message(message))

    def hello(self):
        self.write_message(HELLO)

    def receive(self):
        packets = []
        for frame in self.decoder.feed(self.transport.read()):
            try:
                kind, body = decode_message(frame)
            except ValueError:
                continue
            if kind == 1:
                self.write_message(ACK_PREFIX + self.node_tag)
                self.confirmed = True
                self.last_seen = time.monotonic()
            elif kind == 2:
                self.peer_tag = body
                self.confirmed = True
                self.last_seen = time.monotonic()
            elif self.confirmed and body:
                packets.append(body)
        return packets

    def handshake(self, timeout=5, stop=None):
        deadline = time.monotonic() + timeout
        next_probe = 0
        while time.monotonic() < deadline and not (stop and stop.is_set()):
            if time.monotonic() >= next_probe:
                self.hello()
                next_probe = time.monotonic() + 0.5
            packets = self.receive()
            if self.confirmed:
                return packets
        raise TimeoutError("Hopspot USB handshake did not finish within its time limit.")

    def send_packet(self, packet):
        if not self.confirmed:
            raise OSError("Hopspot USB connection is not ready")
        self.write_message(b"\x03" + bytes(packet))


class PrnsHopspotInterface(Interface):
    DEFAULT_IFAC_SIZE = 8
    HW_MTU = 8192
    RECONNECT_INTERVAL = 3

    def __init__(self, owner, configuration):
        super().__init__()
        config = Interface.get_config_obj(configuration)
        self.owner = owner
        self.name = config["name"]
        self.transport_kind = config.get("transport", "usb")
        if self.transport_kind != "usb":
            raise ValueError("Only USB Hopspot connections are available in this version.")
        self.device_id = validate_device_id(config.get("device_id"))
        self.online = False
        self.detached = False
        self.IN = self.OUT = True
        self.bitrate = 6_000_000
        self.HW_MTU = 8192
        self.last_error = ""
        self.session = None
        self._session_lock = threading.Lock()
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._run, name="Hopspot " + self.name, daemon=True)
        self._worker.start()

    def _incoming(self, packets):
        for packet in packets:
            self.rxb += len(packet)
            self.owner.inbound(packet, self)

    def _run(self):
        while not self._stop.is_set():
            transport = None
            try:
                transport = PrnsUsbTransport(self.device_id).open()
                session = HopspotSession(transport, hashlib.sha256((self.name + self.device_id).encode()).digest()[:8])
                pending = session.handshake(timeout=5, stop=self._stop)
                with self._session_lock:
                    self.session = session
                    self.online = True
                self.last_error = ""
                RNS.log(str(self) + " connected over USB", RNS.LOG_NOTICE)
                self._incoming(pending)
                next_probe = time.monotonic() + 2
                while not self._stop.is_set():
                    if not self.online:
                        raise OSError("Hopspot USB write failed; reconnecting")
                    if time.monotonic() >= next_probe:
                        session.hello()
                        next_probe = time.monotonic() + 2
                    self._incoming(session.receive())
                    if time.monotonic() - session.last_seen > 6:
                        raise TimeoutError("Hopspot stopped answering USB heartbeats.")
            except Exception as error:
                self.online = False
                # Keep errors free of packet bodies, private keys and device dumps.
                message = str(error) if isinstance(error, (OSError, RuntimeError)) else type(error).__name__
                if message != self.last_error and not self._stop.is_set():
                    RNS.log(str(self) + " offline: " + message, RNS.LOG_WARNING)
                self.last_error = message
            finally:
                with self._session_lock:
                    self.online = False
                    self.session = None
                    if transport is not None:
                        try:
                            transport.close()
                        except Exception:
                            pass
            self._stop.wait(self.RECONNECT_INTERVAL)

    def process_outgoing(self, data):
        if len(data) > self.HW_MTU:
            RNS.log(str(self) + " dropped an oversized packet", RNS.LOG_WARNING)
            return
        with self._session_lock:
            if self.online and self.session is not None:
                try:
                    self.session.send_packet(data)
                    self.txb += len(data)
                except Exception:
                    self.online = False
                    self.session.confirmed = False

    def should_ingress_limit(self):
        return False

    def detach(self):
        self.detached = True
        self.online = False
        self._stop.set()

    def __str__(self):
        return "PrnsHopspotInterface[" + self.name + "]"


interface_class = PrnsHopspotInterface
