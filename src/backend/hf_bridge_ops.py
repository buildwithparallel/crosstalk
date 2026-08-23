"""Operate isolated hfbridge processes from Crosstalk.

Radios stay in those child processes. Crosstalk only starts them, reads
logs, and shows announced bridge hashes. Do not attach Hermes or RTL as
Reticulum interfaces here.
"""

from __future__ import annotations

import os
import re
import socket
import subprocess
import sys
import threading
import time
from collections import deque
from pathlib import Path

from src.backend.hf_airtext import air_text_error

TX_NAMES = ("hf-txbridge", "txbridge", "hf tx bridge")
INGRESS_NAMES = ("hf-ingress", "ingress", "hf rtl", "rtl ingress")
HEARD_RECENTLY_SECONDS = 45
LOG_LINES = 80
HFDEST_PREFIX = "hfdest:"
# Must match hfbridge.frame.MAX_PAYLOAD. Crosstalk does not import that package.
LAST_RESORT_MAX_BYTES = 200
INGRESS_STATS_RE = re.compile(
    r"ingress-stats heard=(\d+) forwarded=(\d+) "
    r"decode_failed=(\d+) inject_failed=(\d+)(?: last=(\S+))?"
)
TXBRIDGE_STATS_RE = re.compile(
    r"txbridge-stats received=(\d+) on_air=(\d+) "
    r"held=(\d+) rejected=(\d+) tx_failed=(\d+)(?: last_bytes=(\d+))?"
)


def parse_ingress_stats(log: str | None) -> dict:
    found = None
    for match in INGRESS_STATS_RE.finditer(log or ""):
        found = match
    if found is None:
        return {
            "heard": 0,
            "forwarded": 0,
            "decode_failed": 0,
            "inject_failed": 0,
            "last_origin": None,
        }
    return {
        "heard": int(found.group(1)),
        "forwarded": int(found.group(2)),
        "decode_failed": int(found.group(3)),
        "inject_failed": int(found.group(4)),
        "last_origin": found.group(5),
    }


def parse_txbridge_stats(log: str | None) -> dict:
    found = None
    for match in TXBRIDGE_STATS_RE.finditer(log or ""):
        found = match
    if found is None:
        return {
            "received": 0,
            "on_air": 0,
            "held": 0,
            "rejected": 0,
            "tx_failed": 0,
            "last_bytes": 0,
        }
    return {
        "received": int(found.group(1)),
        "on_air": int(found.group(2)),
        "held": int(found.group(3)),
        "rejected": int(found.group(4)),
        "tx_failed": int(found.group(5)),
        "last_bytes": int(found.group(6) or 0),
    }


def last_resort_title(destination_hash: str) -> str:
    return f"{HFDEST_PREFIX}{destination_hash.lower()}"


def last_resort_peer_from_title(title: str | None) -> str | None:
    text = (title or "").strip().lower()
    if not text.startswith(HFDEST_PREFIX):
        return None
    peer = text[len(HFDEST_PREFIX) :]
    if len(peer) != 32 or any(ch not in "0123456789abcdef" for ch in peer):
        return None
    return peer


def last_resort_send_error(
    title: str | None,
    content: str | None,
    fields: dict | None = None,
) -> str | None:
    if last_resort_peer_from_title(title) is None:
        return None
    fields = fields or {}
    if fields.get("image") or fields.get("audio") or fields.get("file_attachments"):
        return "OTA Long Haul is text only."
    text = content or ""
    if not text.strip():
        return "OTA Long Haul needs a short text message."
    size = len(text.encode("utf-8"))
    if size > LAST_RESORT_MAX_BYTES:
        return f"OTA Long Haul is limited to {LAST_RESORT_MAX_BYTES} bytes."
    reason = air_text_error(text)
    if reason == "payload is empty":
        return "OTA Long Haul needs a short text message."
    if reason:
        return f"OTA Long Haul: {reason}."
    return None


def pick_tx_bridge(announced: list[dict]) -> dict | None:
    tx_bridges = [item for item in announced if item.get("role") == "txbridge"]
    recent = [item for item in tx_bridges if item.get("heard_recently")]
    if recent:
        return recent[0]
    if tx_bridges:
        return tx_bridges[0]
    return None


def default_repo_path() -> Path:
    return Path(__file__).resolve().parents[3] / "reticulum-hf-bridge"


MIN_FREQUENCY_HZ = 28_121_000
MAX_FREQUENCY_HZ = 28_188_000
DEFAULT_FREQUENCY_HZ = 28_124_000
DEFAULT_POWER_PERCENT = 10
DEFAULT_RTL_GAIN_DB = 20.7
# R820T tuner steps. librtlsdr rejects values that are not on this list.
RTL_TUNER_GAINS_DB = (
    0.0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7, 16.6, 19.7, 20.7,
    22.9, 25.4, 28.0, 29.7, 32.8, 33.8, 36.4, 37.2, 38.6, 40.2, 42.1, 43.4,
    43.9, 44.5, 48.0, 49.6,
)
MAX_AMPLITUDE = 1.0
MAX_DRIVE = 255
MIN_DRIVE = 16
FULL_SCALE_WATTS = 5.0


def snap_rtl_gain_db(value: int | float | None) -> float:
    if value is None:
        return DEFAULT_RTL_GAIN_DB
    gain = float(value)
    return min(RTL_TUNER_GAINS_DB, key=lambda step: abs(step - gain))


def rtl_gain_tenths(value: int | float | None) -> int:
    return int(round(snap_rtl_gain_db(value) * 10))


def rtl_gain_from_tenths(tenths: int | None) -> float:
    if tenths is None:
        return DEFAULT_RTL_GAIN_DB
    return snap_rtl_gain_db(tenths / 10.0)


def parse_allow_hashes(text: str | None) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for raw in (text or "").replace(",", " ").split():
        peer = raw.strip().lower().replace("lxmf@", "")
        peer = "".join(ch for ch in peer if ch in "0123456789abcdef")
        if len(peer) != 32 or peer in seen:
            continue
        seen.add(peer)
        found.append(peer)
    return found


def settings_from_power_percent(percent: int | float | None) -> tuple[float, int]:
    """Map 1–100% to IQ amplitude and HL2 drive so 100% is about 5 W."""
    pct = DEFAULT_POWER_PERCENT if percent is None else int(percent)
    pct = max(1, min(100, pct))
    scale = (pct / 100.0) ** 0.5
    drive = max(MIN_DRIVE, min(MAX_DRIVE, round(MAX_DRIVE * scale)))
    amplitude = round(min(MAX_AMPLITUDE, (scale * MAX_DRIVE) / drive), 4)
    return amplitude, drive


def amplitude_from_power_percent(percent: int | float | None) -> float:
    amplitude, _drive = settings_from_power_percent(percent)
    return amplitude


def estimated_watts(amplitude: float, drive: int) -> float:
    return FULL_SCALE_WATTS * (drive / 255.0) ** 2 * amplitude**2


def estimated_watts_from_percent(percent: int | float | None) -> float:
    amplitude, drive = settings_from_power_percent(percent)
    return estimated_watts(amplitude, drive)


def validate_frequency_hz(frequency_hz: int) -> int:
    if not MIN_FREQUENCY_HZ <= frequency_hz <= MAX_FREQUENCY_HZ:
        raise ValueError("frequency must stay inside 28.121–28.188 MHz")
    return frequency_hz


def classify_bridge_name(display_name: str | None) -> str | None:
    text = (display_name or "").strip().lower()
    if not text:
        return None
    if any(name in text for name in TX_NAMES):
        return "txbridge"
    if any(name in text for name in INGRESS_NAMES):
        return "ingress"
    return None


def python_for_repo(repo: Path) -> Path:
    local = repo / ".venv" / "bin" / "python"
    if local.exists():
        return local
    windows = repo / ".venv" / "Scripts" / "python.exe"
    if windows.exists():
        return windows
    return Path(sys.executable)


def repo_is_ready(repo: Path) -> bool:
    return (repo / "src" / "hfbridge" / "txbridge.py").is_file()


# Same OpenHPSDR discovery query as hfbridge.hl2.discover. UDP only; cannot key RF.
HPSDR_PORT = 1024
HL2_DISCOVERY_PACKET = b"\xef\xfe\x02" + bytes(60)


def parse_hl2_discovery_reply(data: bytes, ip: str) -> dict | None:
    if len(data) <= 10 or data[:2] != b"\xef\xfe":
        return None
    return {
        "ip": ip,
        "mac": ":".join(f"{byte:02x}" for byte in data[3:9]),
        "gateware_version": data[9],
        "board_id": data[10],
    }


def discover_hl2_radios(
    timeout: float = 1.0,
    *,
    _socket_factory=socket.socket,
) -> list[dict]:
    """Ask the LAN which Hermes-Lite 2 boards are present. Cannot generate RF."""
    found: dict[str, dict] = {}
    sock = _socket_factory(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", 0))
        sock.sendto(HL2_DISCOVERY_PACKET, ("255.255.255.255", HPSDR_PORT))
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            sock.settimeout(remaining)
            try:
                data, address = sock.recvfrom(2048)
            except socket.timeout:
                break
            radio = parse_hl2_discovery_reply(data, address[0])
            if radio is not None:
                found[radio["ip"]] = radio
    finally:
        sock.close()
    return list(found.values())


def build_command(
    role: str,
    *,
    repo: Path,
    callsign: str,
    hl2_ip: str,
    arm_tx: bool,
    frequency_hz: int = DEFAULT_FREQUENCY_HZ,
    power_percent: int = DEFAULT_POWER_PERCENT,
    allow_hashes: list[str] | None = None,
    allow_enabled: bool = False,
    rtl_gain_db: float | None = None,
) -> list[str]:
    python = str(python_for_repo(repo))
    if role == "txbridge":
        if not callsign.strip():
            raise ValueError("callsign is required to start the HF TX bridge")
        frequency_hz = validate_frequency_hz(int(frequency_hz))
        amplitude, drive = settings_from_power_percent(power_percent)
        allowed = parse_allow_hashes(" ".join(allow_hashes or []))
        if allow_enabled and not allowed:
            raise ValueError("add at least one LXMF address, or turn the allow list off")
        command = [
            python,
            "-u",
            "-m",
            "hfbridge.txbridge",
            "--config",
            "rns-instances/txbridge",
            "--callsign",
            callsign.strip(),
            "--frequency",
            str(frequency_hz),
            "--amplitude",
            str(amplitude),
            "--drive",
            str(drive),
        ]
        if allow_enabled:
            for hash_hex in allowed:
                command.extend(["--allow", hash_hex])
        if arm_tx:
            if not hl2_ip.strip():
                raise ValueError("Hermes-Lite IP is required to arm transmit")
            command.extend(
                ["--hl2-ip", hl2_ip.strip(), "--filter-confirmed", "--arm-tx"]
            )
        return command
    if role == "ingress":
        gain = snap_rtl_gain_db(rtl_gain_db)
        return [
            python,
            "-u",
            "-m",
            "hfbridge.ingress",
            "--config",
            "rns-instances/ingress",
            "--quiet",
            "--gain",
            str(gain),
        ]
    raise ValueError(f"unknown bridge role {role}")


def ensure_instance_configs(repo: Path) -> None:
    config = repo / "rns-instances" / "txbridge" / "config"
    if config.is_file():
        return
    python = str(python_for_repo(repo))
    completed = subprocess.run(
        [python, "-m", "hfbridge.rnssetup"],
        cwd=str(repo),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "rnssetup failed")


class HfBridgeSupervisor:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._processes: dict[str, subprocess.Popen] = {}
        self._logs: dict[str, deque[str]] = {
            "txbridge": deque(maxlen=LOG_LINES),
            "ingress": deque(maxlen=LOG_LINES),
        }
        self._armed = False

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "txbridge": self._role_snapshot("txbridge"),
                "ingress": self._role_snapshot("ingress"),
                "armed": self._armed,
            }

    def start(
        self,
        role: str,
        *,
        repo: Path,
        callsign: str,
        hl2_ip: str,
        arm_tx: bool,
        frequency_hz: int = DEFAULT_FREQUENCY_HZ,
        power_percent: int = DEFAULT_POWER_PERCENT,
        allow_hashes: list[str] | None = None,
        allow_enabled: bool = False,
        rtl_gain_db: float | None = None,
    ) -> dict:
        if role not in ("txbridge", "ingress"):
            raise ValueError(f"unknown bridge role {role}")
        repo = Path(repo).expanduser()
        if not repo_is_ready(repo):
            raise FileNotFoundError(
                f"hfbridge repo not found at {repo}. Set the repo path."
            )
        ensure_instance_configs(repo)
        command = build_command(
            role,
            repo=repo,
            callsign=callsign,
            hl2_ip=hl2_ip,
            arm_tx=arm_tx,
            frequency_hz=frequency_hz,
            power_percent=power_percent,
            allow_hashes=allow_hashes,
            allow_enabled=allow_enabled,
            rtl_gain_db=rtl_gain_db,
        )
        with self._lock:
            existing = self._processes.get(role)
            if existing is not None and existing.poll() is None:
                raise RuntimeError(f"{role} is already running (pid {existing.pid})")
            process = subprocess.Popen(
                command,
                cwd=str(repo),
                env={**os.environ, "PYTHONPATH": "src"},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            self._logs[role].clear()
            self._processes[role] = process
            if role == "txbridge":
                self._armed = bool(arm_tx)
        threading.Thread(
            target=self._pump_log, args=(role, process), daemon=True
        ).start()
        time.sleep(0.2)
        if process.poll() is not None:
            raise RuntimeError(
                "".join(self._logs[role]) or f"{role} exited immediately"
            )
        return self.snapshot()

    def stop(self, role: str) -> dict:
        if role not in ("txbridge", "ingress"):
            raise ValueError(f"unknown bridge role {role}")
        with self._lock:
            process = self._processes.pop(role, None)
            self._logs[role].clear()
            if role == "txbridge":
                self._armed = False
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        return self.snapshot()

    def stop_all(self) -> None:
        for role in ("txbridge", "ingress"):
            try:
                self.stop(role)
            except Exception:
                pass

    def _role_snapshot(self, role: str) -> dict:
        process = self._processes.get(role)
        running = process is not None and process.poll() is None
        log = "".join(self._logs[role])
        snapshot = {
            "running": running,
            "pid": process.pid if running else None,
            "log": log,
        }
        if role == "ingress":
            snapshot["stats"] = parse_ingress_stats(log)
        elif role == "txbridge":
            snapshot["stats"] = parse_txbridge_stats(log)
        return snapshot

    def _pump_log(self, role: str, process: subprocess.Popen) -> None:
        stream = process.stdout
        if stream is None:
            return
        for line in stream:
            self._logs[role].append(line)


def announced_bridges(announces: list[dict], now: float | None = None) -> list[dict]:
    now = time.time() if now is None else now
    found = []
    for announce in announces:
        role = classify_bridge_name(announce.get("display_name"))
        if role is None:
            continue
        updated = announce.get("updated_at")
        try:
            if hasattr(updated, "timestamp"):
                age = now - updated.timestamp()
            else:
                age = now - float(updated)
        except (TypeError, ValueError):
            age = None
        found.append(
            {
                "role": role,
                "display_name": announce.get("display_name"),
                "destination_hash": announce.get("destination_hash"),
                "hops": announce.get("hops"),
                "updated_at": str(updated) if updated is not None else None,
                "heard_recently": age is not None and age <= HEARD_RECENTLY_SECONDS,
            }
        )
    return found
