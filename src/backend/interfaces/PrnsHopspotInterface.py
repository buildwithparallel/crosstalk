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
from collections import deque

import RNS
from RNS.Interfaces.Interface import Interface

USB_VENDOR = 0x1209
USB_PRODUCT = 0x0001
MAX_MESSAGE = 1 + 8192 + 64
# SF7 at 500 kHz with coding rate 4/5 carries about 21.875 kbps. Reticulum
# uses interface bitrate when sizing link timeouts, so advertising the USB bus
# speed here makes multi-hop LoRa links expire before their replies arrive.
DEFAULT_LORA_BITRATE = 21_875
DEFERRED_LIMIT = 8
HELLO = b"\x01Prns\x02\x01"
_PATH_REQUEST_HASH = None
ACK_PREFIX = b"\x02Prns\x02\x01"
DEVICE_PATTERN = re.compile(r"usb:1209:0001:\d+:\d+(?:\.\d+)*\Z")


def validate_device_id(value):
    if not isinstance(value, str) or not DEVICE_PATTERN.fullmatch(value):
        raise ValueError("Select a Prns Hopspot USB device before saving.")
    return value


def lora_phy_bitrate(spreading_factor, bandwidth_hz, coding_rate):
    """Bitrate for a LoRa profile. Coding rate 5 means 4/5."""
    sf = int(spreading_factor)
    bandwidth = int(bandwidth_hz)
    rate = int(coding_rate)
    if bandwidth < 10_000:
        bandwidth *= 1000
    if not (5 <= sf <= 12 and bandwidth > 0 and 5 <= rate <= 8):
        raise ValueError("LoRa profile must use spreading factor 5–12, a positive bandwidth, and coding rate 4/5 through 4/8.")
    return max(1, (sf * bandwidth * 4) // ((1 << sf) * rate))


def configured_bitrate(config):
    def present(key):
        return config.get(key) not in (None, "")

    if present("spreadingfactor") or present("bandwidth") or present("codingrate"):
        try:
            return lora_phy_bitrate(
                config.get("spreadingfactor", 7),
                config.get("bandwidth", 500_000),
                config.get("codingrate", 5),
            )
        except (TypeError, ValueError):
            pass
    raw = config.get("bitrate")
    if raw not in (None, ""):
        try:
            value = int(raw)
            if value > 0:
                return value
        except (TypeError, ValueError):
            pass
    return DEFAULT_LORA_BITRATE


def hopspot_usb_product(value):
    """USB product string from discovery. Empty when it is not a Hopspot name."""
    if not isinstance(value, str):
        return ""
    text = " ".join(value.split())
    if not text.startswith("Personal Hopspot") or len(text) > 80:
        return ""
    return text


def hopspot_profile_from_request(data):
    raw_sf = data.get("spreadingfactor")
    raw_bandwidth = data.get("bandwidth")
    raw_rate = data.get("codingrate")
    if raw_sf in (None, "") and raw_bandwidth in (None, "") and raw_rate in (None, ""):
        raw_sf, raw_bandwidth, raw_rate = 7, 500_000, 5
    bitrate = lora_phy_bitrate(raw_sf or 7, raw_bandwidth or 500_000, raw_rate or 5)
    bandwidth = int(raw_bandwidth or 500_000)
    if bandwidth < 10_000:
        bandwidth *= 1000
    return int(raw_sf or 7), bandwidth, int(raw_rate or 5), bitrate


def path_request_destination_hash():
    global _PATH_REQUEST_HASH
    if _PATH_REQUEST_HASH is None:
        _PATH_REQUEST_HASH = RNS.Destination.hash(None, RNS.Transport.APP_NAME, "path", "request")
    return _PATH_REQUEST_HASH


def packet_should_wait(data):
    """Announces and path requests wait for airtime. Voice and link packets do not."""
    if not data or len(data) < 2:
        return False
    packet_type = data[0] & 0b11
    if packet_type == RNS.Packet.ANNOUNCE:
        return True
    if packet_type != RNS.Packet.DATA:
        return False
    header_type = (data[0] & 0b01000000) >> 6
    destination_length = RNS.Reticulum.TRUNCATED_HASHLENGTH // 8
    hash_at = 2 + destination_length if header_type == RNS.Packet.HEADER_2 else 2
    if len(data) < hash_at + destination_length:
        return False
    return data[hash_at:hash_at + destination_length] == path_request_destination_hash()


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
        self.bitrate = configured_bitrate(config)
        self.HW_MTU = 8192
        self.last_error = ""
        self.session = None
        self.connected_at = None
        self._held_priority = None
        self._deferred = deque()
        self._deferred_allowed_at = 0
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
                    self.connected_at = time.time()
                self.last_error = ""
                RNS.log(str(self) + " connected over USB", RNS.LOG_NOTICE)
                self._flush_held()
                self._drain_deferred()
                self._incoming(pending)
                next_probe = time.monotonic() + 2
                while not self._stop.is_set():
                    if not self.online:
                        raise OSError("Hopspot USB write failed; reconnecting")
                    if time.monotonic() >= next_probe:
                        session.hello()
                        next_probe = time.monotonic() + 2
                    self._drain_deferred()
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

    def _airtime(self, data):
        return max(0.05, (len(data) * 8) / max(int(self.bitrate or 1), 1))

    def _keep(self, raw):
        if packet_should_wait(raw):
            self._deferred.appendleft(raw)
            while len(self._deferred) > DEFERRED_LIMIT:
                self._deferred.pop()
            return
        self._held_priority = raw

    def _write(self, raw):
        with self._session_lock:
            session = self.session
            if not self.online or session is None:
                self._keep(raw)
                return
            try:
                session.send_packet(raw)
                self.txb += len(raw)
                self._deferred_allowed_at = time.monotonic() + self._airtime(raw)
            except Exception:
                self.online = False
                session.confirmed = False
                self._keep(raw)

    def _defer(self, raw):
        send_now = None
        with self._session_lock:
            self._deferred.append(raw)
            while len(self._deferred) > DEFERRED_LIMIT:
                self._deferred.popleft()
            if (self.online and self.session is not None and self._held_priority is None
                    and time.monotonic() >= self._deferred_allowed_at and self._deferred):
                send_now = self._deferred.popleft()
        if send_now is not None:
            self._write(send_now)

    def _flush_held(self):
        with self._session_lock:
            raw = self._held_priority
            if raw is None or not self.online or self.session is None:
                return
            self._held_priority = None
        self._write(raw)

    def _drain_deferred(self):
        with self._session_lock:
            if self._held_priority is not None or not self.online or self.session is None:
                return
            if time.monotonic() < self._deferred_allowed_at or not self._deferred:
                return
            raw = self._deferred.popleft()
        self._write(raw)

    def process_outgoing(self, data):
        if len(data) > self.HW_MTU:
            RNS.log(str(self) + " dropped an oversized packet", RNS.LOG_WARNING)
            return
        raw = bytes(data)
        if packet_should_wait(raw):
            self._defer(raw)
            return
        with self._session_lock:
            if not (self.online and self.session is not None):
                self._held_priority = raw
                return
        self._write(raw)

    def detach(self):
        self.detached = True
        self.online = False
        self._stop.set()

    def __str__(self):
        return "PrnsHopspotInterface[" + self.name + "]"


interface_class = PrnsHopspotInterface
