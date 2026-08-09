"""Native Reticulum interface for a USB-connected RockBLOCK 9704.

The interface transports complete, unmodified Reticulum packets inside
Iridium Messaging Transport (IMT) RAW messages. It deliberately contains no
LXMF or Crosstalk-specific translation.

This module is loaded by Reticulum as an external interface. The optional
``rockblock9704`` dependency is imported only when the interface is enabled,
so normal Crosstalk installations are unaffected.
"""

import hashlib
import json
import os
import sqlite3
import threading
import time
from collections import OrderedDict, deque

import RNS
from RNS.Interfaces.Interface import Interface


class IridiumIMTCodec:
    """Small versioned frame around one native Reticulum packet."""

    MAGIC = b"RNSI"
    VERSION = 1
    HEADER = MAGIC + bytes((VERSION,))

    @classmethod
    def encode(cls, packet):
        return cls.HEADER + bytes(packet)

    @classmethod
    def decode(cls, message):
        message = bytes(message)
        if not message.startswith(cls.HEADER):
            raise ValueError("IMT payload is not a supported Reticulum frame")
        packet = message[len(cls.HEADER):]
        if not packet:
            raise ValueError("IMT Reticulum frame contains no packet")
        return packet


class DurablePacketQueue:
    """Tiny SQLite spool used while the constellation is unavailable."""

    def __init__(self, path, maximum_packets=512):
        self.path = os.path.abspath(os.path.expanduser(path))
        self.maximum_packets = maximum_packets
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS outbound_packets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload BLOB NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    next_attempt_at REAL NOT NULL DEFAULT 0,
                    last_error TEXT,
                    created_at REAL NOT NULL
                )
                """
            )

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def enqueue(self, payload):
        with self.lock, self._connect() as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM outbound_packets"
            ).fetchone()[0]
            if count >= self.maximum_packets:
                return False
            connection.execute(
                """
                INSERT INTO outbound_packets
                    (payload, attempts, next_attempt_at, created_at)
                VALUES (?, 0, 0, ?)
                """,
                (sqlite3.Binary(bytes(payload)), time.time()),
            )
            return True

    def next_ready(self, now=None):
        now = time.time() if now is None else now
        with self.lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, payload, attempts
                FROM outbound_packets
                WHERE next_attempt_at <= ?
                ORDER BY id ASC
                LIMIT 1
                """,
                (now,),
            ).fetchone()
            if row is None:
                return None
            return row[0], bytes(row[1]), row[2]

    def complete(self, packet_id):
        with self.lock, self._connect() as connection:
            connection.execute(
                "DELETE FROM outbound_packets WHERE id = ?",
                (packet_id,),
            )

    def retry(self, packet_id, delay, error):
        with self.lock, self._connect() as connection:
            connection.execute(
                """
                UPDATE outbound_packets
                SET attempts = attempts + 1,
                    next_attempt_at = ?,
                    last_error = ?
                WHERE id = ?
                """,
                (time.time() + delay, str(error), packet_id),
            )

    def count(self):
        with self.lock, self._connect() as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM outbound_packets"
            ).fetchone()[0]


class DurablePathCache:
    """Allowlisted Reticulum paths that can be rebound after a restart.

    Reticulum only persists its complete path table when transport is enabled.
    A paid edge interface must remain a non-transport instance, so this cache
    stores only destinations explicitly configured by the operator.
    """

    def __init__(self, path):
        self.path = os.path.abspath(os.path.expanduser(path))
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS persistent_paths (
                    destination_hash BLOB PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    next_hop BLOB NOT NULL,
                    hops INTEGER NOT NULL,
                    expires REAL NOT NULL,
                    random_blobs TEXT NOT NULL,
                    packet_hash BLOB NOT NULL,
                    recorded_at REAL NOT NULL
                )
                """
            )

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def save(self, destination_hash, path_entry, recorded_at=None):
        recorded_at = time.time() if recorded_at is None else float(recorded_at)
        random_blobs = json.dumps(
            [bytes(blob).hex() for blob in path_entry[4]],
            separators=(",", ":"),
        )
        with self.lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO persistent_paths (
                    destination_hash, timestamp, next_hop, hops, expires,
                    random_blobs, packet_hash, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(destination_hash) DO UPDATE SET
                    timestamp = excluded.timestamp,
                    next_hop = excluded.next_hop,
                    hops = excluded.hops,
                    expires = excluded.expires,
                    random_blobs = excluded.random_blobs,
                    packet_hash = excluded.packet_hash,
                    recorded_at = excluded.recorded_at
                """,
                (
                    sqlite3.Binary(bytes(destination_hash)),
                    float(path_entry[0]),
                    sqlite3.Binary(bytes(path_entry[1])),
                    int(path_entry[2]),
                    float(path_entry[3]),
                    random_blobs,
                    sqlite3.Binary(bytes(path_entry[6])),
                    recorded_at,
                ),
            )

    def load(self, destination_hash):
        with self.lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT timestamp, next_hop, hops, expires, random_blobs,
                       packet_hash, recorded_at
                FROM persistent_paths
                WHERE destination_hash = ?
                """,
                (sqlite3.Binary(bytes(destination_hash)),),
            ).fetchone()

        if row is None:
            return None

        return {
            "timestamp": float(row[0]),
            "next_hop": bytes(row[1]),
            "hops": int(row[2]),
            "expires": float(row[3]),
            "random_blobs": [bytes.fromhex(blob) for blob in json.loads(row[4])],
            "packet_hash": bytes(row[5]),
            "recorded_at": float(row[6]),
        }

    def delete(self, destination_hash):
        with self.lock, self._connect() as connection:
            connection.execute(
                "DELETE FROM persistent_paths WHERE destination_hash = ?",
                (sqlite3.Binary(bytes(destination_hash)),),
            )


class RecentInboundPacketCache:
    """Bounded replay cache for exact IMT frame duplicates."""

    def __init__(self, ttl=600, maximum_packets=1024):
        self.ttl = float(ttl)
        self.maximum_packets = int(maximum_packets)
        self.packets = OrderedDict()

    def check_and_record(self, payload, now=None):
        now = time.monotonic() if now is None else float(now)
        digest = hashlib.sha256(bytes(payload)).hexdigest()
        cutoff = now - self.ttl

        while self.packets:
            _, oldest_seen_at = next(iter(self.packets.items()))
            if oldest_seen_at >= cutoff:
                break
            self.packets.popitem(last=False)

        duplicate = digest in self.packets
        if duplicate:
            self.packets.move_to_end(digest)
        self.packets[digest] = now

        while len(self.packets) > self.maximum_packets:
            self.packets.popitem(last=False)

        return duplicate, digest


class IridiumIMTInterface(Interface):
    """Reticulum interface backed by a RockBLOCK 9704 serial device."""

    DEFAULT_IFAC_SIZE = 16
    FIXED_MTU = True
    RECONNECT_DELAY = 10

    def __str__(self):
        return f"IridiumIMTInterface[{self.name}/{self.port}]"

    def __init__(self, owner, configuration):
        super().__init__()

        interface_config = Interface.get_config_obj(configuration)
        self.owner = owner
        self.name = interface_config.get("name", "Iridium IMT")
        self.port = interface_config.get("port", None)
        if self.port is None:
            raise ValueError(f"port is required for interface '{self.name}'")

        self.topic = int(interface_config.get("topic", 244))
        self.poll_interval = float(interface_config.get("poll_interval", 0.01))
        self.retry_interval = float(interface_config.get("retry_interval", 600))
        self.maximum_modem_attempts = int(
            interface_config.get("maximum_modem_attempts", 1)
        )
        self.bitrate = int(interface_config.get("bitrate", 300))
        self.HW_MTU = RNS.Reticulum.MTU
        self.IN = True
        self.OUT = True

        default_queue_path = os.path.join(
            RNS.Reticulum.storagepath,
            "iridium_imt",
            "outbound.sqlite3",
        )
        queue_path = interface_config.get("queue_path", default_queue_path)
        maximum_queued_packets = int(
            interface_config.get("maximum_queued_packets", 512)
        )
        self.packet_queue = DurablePacketQueue(
            queue_path,
            maximum_packets=maximum_queued_packets,
        )

        self.persistent_destination_hashes = self._parse_destination_hashes(
            interface_config.get("persistent_destinations", "")
        )
        self.persistent_path_max_age = float(
            interface_config.get("persistent_path_max_age", 60 * 60 * 24 * 7)
        )
        self.persistent_path_cache = None
        if self.persistent_destination_hashes:
            default_path_cache_path = os.path.join(
                RNS.Reticulum.storagepath,
                "iridium_imt",
                "persistent_paths.sqlite3",
            )
            self.persistent_path_cache = DurablePathCache(
                interface_config.get("persistent_path_cache", default_path_cache_path)
            )
        self.persistent_paths_restored = False

        try:
            from rockblock9704 import RockBlock9704
        except ImportError as error:
            raise ImportError(
                "IridiumIMTInterface requires the optional rockblock9704 "
                "package. Install Ground Control's RockBLOCK-9704 Python "
                "library before enabling this interface."
            ) from error

        self.rockblock_class = RockBlock9704
        self.modem = None
        self.current_packet = None
        self.mt_message_ids = deque()
        self.recent_inbound_packets = RecentInboundPacketCache()
        self.signal_bars = -1
        self.stop_event = threading.Event()
        self.state_lock = threading.Lock()

        self.worker = threading.Thread(
            target=self._run,
            name=f"iridium-imt-{self.name}",
            daemon=True,
        )
        self.worker.start()

    @staticmethod
    def _parse_destination_hashes(value):
        if value is None:
            return set()

        values = value if isinstance(value, (list, tuple)) else [value]
        tokens = []
        for item in values:
            tokens.extend(str(item).replace(",", " ").split())

        expected_length = RNS.Reticulum.TRUNCATED_HASHLENGTH // 8
        destination_hashes = set()
        for token in tokens:
            try:
                destination_hash = bytes.fromhex(token)
            except ValueError:
                RNS.log(
                    f"Ignoring invalid persistent Iridium destination {token!r}",
                    RNS.LOG_WARNING,
                )
                continue

            if len(destination_hash) != expected_length:
                RNS.log(
                    f"Ignoring persistent Iridium destination {token!r}; "
                    f"expected {expected_length * 2} hexadecimal characters",
                    RNS.LOG_WARNING,
                )
                continue
            destination_hashes.add(destination_hash)

        return destination_hashes

    def _capture_persistent_paths(self):
        if self.persistent_path_cache is None:
            return

        try:
            with RNS.Transport.path_table_lock:
                paths = {
                    destination_hash: list(RNS.Transport.path_table[destination_hash])
                    for destination_hash in self.persistent_destination_hashes
                    if destination_hash in RNS.Transport.path_table
                    and RNS.Transport.path_table[destination_hash][5] is self
                }

            for destination_hash, path_entry in paths.items():
                self.persistent_path_cache.save(destination_hash, path_entry)
                RNS.log(
                    f"{self} saved allowlisted path to "
                    f"{RNS.prettyhexrep(destination_hash)}",
                    RNS.LOG_DEBUG,
                )
        except Exception as error:
            RNS.log(
                f"{self} could not save persistent path: {error}",
                RNS.LOG_ERROR,
            )

    def _restore_persistent_paths(self):
        if self.persistent_paths_restored:
            return
        if self.persistent_path_cache is None:
            self.persistent_paths_restored = True
            return

        # External interface constructors run before Reticulum finishes adding
        # them to the active interface list. Wait until this interface is fully
        # registered, otherwise the normal path-table cleanup would remove it.
        if self not in RNS.Transport.interfaces:
            return

        now = time.time()
        try:
            for destination_hash in self.persistent_destination_hashes:
                saved_path = self.persistent_path_cache.load(destination_hash)
                if saved_path is None:
                    continue

                stale_after = saved_path["recorded_at"] + self.persistent_path_max_age
                if self.persistent_path_max_age <= 0 or now >= stale_after:
                    self.persistent_path_cache.delete(destination_hash)
                    RNS.log(
                        f"{self} discarded expired persistent path to "
                        f"{RNS.prettyhexrep(destination_hash)}",
                        RNS.LOG_NOTICE,
                    )
                    continue

                with RNS.Transport.path_table_lock:
                    if destination_hash in RNS.Transport.path_table:
                        continue
                    RNS.Transport.path_table[destination_hash] = [
                        saved_path["timestamp"],
                        saved_path["next_hop"],
                        saved_path["hops"],
                        saved_path["expires"],
                        saved_path["random_blobs"],
                        self,
                        saved_path["packet_hash"],
                    ]

                RNS.log(
                    f"{self} restored allowlisted path to "
                    f"{RNS.prettyhexrep(destination_hash)} without transmitting",
                    RNS.LOG_NOTICE,
                )
        except Exception as error:
            RNS.log(
                f"{self} could not restore persistent paths: {error}",
                RNS.LOG_ERROR,
            )
        finally:
            self.persistent_paths_restored = True

    def process_outgoing(self, data):
        if self.detached:
            return

        packet = bytes(data)
        if len(packet) > RNS.Reticulum.MTU:
            RNS.log(
                f"{self} rejected {len(packet)} byte packet; "
                f"Reticulum MTU is {RNS.Reticulum.MTU}",
                RNS.LOG_ERROR,
            )
            return

        if not self.packet_queue.enqueue(IridiumIMTCodec.encode(packet)):
            RNS.log(
                f"{self} outbound queue is full; packet was not queued",
                RNS.LOG_ERROR,
            )
            return

        RNS.log(
            f"{self} queued {len(packet)} byte Reticulum packet "
            f"({self.packet_queue.count()} waiting)",
            RNS.LOG_DEBUG,
        )

    def _run(self):
        while not self.stop_event.is_set():
            if self.modem is None:
                self._connect()
                if self.modem is None:
                    self.stop_event.wait(self.RECONNECT_DELAY)
                    continue

            try:
                self.modem.poll()
                self._restore_persistent_paths()
                self._drain_incoming()
                self._start_next_outbound()
                self.stop_event.wait(self.poll_interval)
            except Exception as error:
                RNS.log(
                    f"{self} modem worker failed: {error}",
                    RNS.LOG_ERROR,
                )
                self._disconnect(retry_current=True, error=error)
                self.stop_event.wait(self.RECONNECT_DELAY)

        self._disconnect(retry_current=False)

    def _connect(self):
        try:
            modem = self.rockblock_class()
            modem.set_mo_message_complete_callback(
                mo_message_complete=self._on_mo_complete
            )
            modem.set_mt_message_complete_callback(
                mt_message_complete=self._on_mt_complete
            )
            modem.set_constellation_state_callback(
                constellation_state=self._on_constellation_state
            )
            modem.set_mo_message_started_callback(
                mo_message_started=self._on_mo_started
            )

            if not modem.begin(self.port):
                raise ConnectionError(
                    f"could not open RockBLOCK 9704 on {self.port}"
                )

            self.modem = modem
            self.online = True
            time.sleep(0.1)
            RNS.log(
                f"{self} connected; {self.packet_queue.count()} packet(s) queued",
                RNS.LOG_NOTICE,
            )
        except Exception as error:
            self.modem = None
            self.online = False
            RNS.log(f"{self} connection failed: {error}", RNS.LOG_ERROR)

    def _disconnect(self, retry_current=False, error="modem disconnected"):
        self.online = False
        if retry_current:
            self._retry_current(error)

        with self.state_lock:
            self.mt_message_ids.clear()

        modem = self.modem
        self.modem = None
        if modem is not None:
            try:
                modem.end()
            except Exception:
                pass

    def _start_next_outbound(self):
        if self.current_packet is not None or self.modem is None:
            return

        queued_packet = self.packet_queue.next_ready()
        if queued_packet is None:
            return

        packet_id, payload, attempts = queued_packet
        if attempts >= self.maximum_modem_attempts:
            self.packet_queue.complete(packet_id)
            RNS.log(
                f"{self} discarded packet {packet_id} after "
                f"{attempts} failed modem attempt(s); LXMF controls any "
                "end-to-end satellite retry",
                RNS.LOG_WARNING,
            )
            return

        with self.state_lock:
            self.current_packet = queued_packet

        try:
            accepted = self.modem.send_message_async(payload, self.topic)
        except Exception as error:
            self._retry_current(error)
            return

        if not accepted:
            self._retry_current("RockBLOCK did not accept the queued message")
            return

        RNS.log(
            f"{self} submitted queued packet {packet_id} to the modem "
            f"(attempt {attempts + 1})",
            RNS.LOG_DEBUG,
        )

    def _retry_current(self, error):
        with self.state_lock:
            current_packet = self.current_packet
            self.current_packet = None

        if current_packet is not None:
            self.packet_queue.retry(
                current_packet[0],
                self.retry_interval,
                error,
            )
            RNS.log(
                f"{self} will retry packet {current_packet[0]}: {error}",
                RNS.LOG_WARNING,
            )

    def _on_mo_started(self, message_id):
        RNS.log(
            f"{self} modem started mobile-originated message {message_id}",
            RNS.LOG_DEBUG,
        )

    def _on_mo_complete(self, message_id, status):
        with self.state_lock:
            current_packet = self.current_packet
            self.current_packet = None

        if current_packet is None:
            return

        packet_id, payload, _ = current_packet
        if status == 1:
            self.packet_queue.complete(packet_id)
            self.txb += len(IridiumIMTCodec.decode(payload))
            RNS.log(
                f"{self} transmitted packet {packet_id} "
                f"as IMT message {message_id}",
                RNS.LOG_NOTICE,
            )
        else:
            self.packet_queue.retry(
                packet_id,
                self.retry_interval,
                f"IMT completion status {status}",
            )
            RNS.log(
                f"{self} failed packet {packet_id} with IMT status {status}",
                RNS.LOG_WARNING,
            )

    def _on_mt_complete(self, message_id, status):
        if status == 1:
            with self.state_lock:
                self.mt_message_ids.append(message_id)
            RNS.log(
                f"{self} received mobile-terminated message {message_id}",
                RNS.LOG_NOTICE,
            )
        else:
            RNS.log(
                f"{self} received unsuccessful MT status {status} "
                f"for message {message_id}",
                RNS.LOG_WARNING,
            )

    def _on_constellation_state(self, state):
        try:
            new_signal = int(state["signalBars"])
        except (KeyError, TypeError, ValueError):
            return

        if new_signal != self.signal_bars:
            self.signal_bars = new_signal
            RNS.log(
                f"{self} constellation signal is {new_signal}/5",
                RNS.LOG_NOTICE,
            )

    def _drain_incoming(self):
        if self.modem is None:
            return

        with self.state_lock:
            if not self.mt_message_ids:
                return
            message_id = self.mt_message_ids.popleft()

        message = self.modem.receive_message_async()
        if message is None:
            with self.state_lock:
                self.mt_message_ids.appendleft(message_id)
            return

        duplicate, digest = self.recent_inbound_packets.check_and_record(message)
        short_digest = digest[:16]

        try:
            packet = IridiumIMTCodec.decode(message)
            if duplicate:
                RNS.log(
                    f"{self} suppressed duplicate MT message {message_id} "
                    f"with SHA-256 {short_digest}",
                    RNS.LOG_NOTICE,
                )
            else:
                self.owner.inbound(packet, self)
                self._capture_persistent_paths()
                self.rxb += len(packet)
                RNS.log(
                    f"{self} injected {len(packet)} byte packet from MT "
                    f"message {message_id} with SHA-256 {short_digest}",
                    RNS.LOG_NOTICE,
                )
        except Exception as error:
            RNS.log(
                f"{self} discarded invalid MT message {message_id} "
                f"with SHA-256 {short_digest}: {error}",
                RNS.LOG_ERROR,
            )
        finally:
            acknowledged = bool(
                self.modem.acknowledge_receive_head_async()
            )
            if acknowledged:
                RNS.log(
                    f"{self} acknowledged MT message {message_id} "
                    f"with SHA-256 {short_digest}",
                    RNS.LOG_NOTICE,
                )
            else:
                RNS.log(
                    f"{self} could not acknowledge MT message {message_id} "
                    f"with SHA-256 {short_digest}",
                    RNS.LOG_WARNING,
                )

    def detach(self):
        self.detached = True
        self.online = False
        self.stop_event.set()
        if (
            self.worker.is_alive()
            and threading.current_thread() is not self.worker
        ):
            self.worker.join(timeout=2)


interface_class = IridiumIMTInterface
