"""Refresh Reticulum routes that are still in the table but no longer usable.

expire_path only zeros a path's timestamp, so has_path stays true. Callers
have to treat that entry as unusable and remove it before requesting again.
"""
import asyncio
import time

import RNS

from src.backend.interfaces.PrnsHopspotInterface import DEFAULT_LORA_BITRATE

DEFAULT_PATH_MAX_AGE_SECONDS = 15 * 60
PATH_REQUEST_BUDGET = 8
MIN_AUTO_ANNOUNCE_INTERVAL_SECONDS = 60
MAX_AUTO_ANNOUNCE_INTERVAL_SECONDS = 7 * 24 * 60 * 60


def normalize_auto_announce_interval_seconds(value):
    """0 turns automatic announces off. A positive interval is whole minutes, from 1 minute to 7 days."""
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return 0
    if seconds <= 0:
        return 0
    seconds = max(MIN_AUTO_ANNOUNCE_INTERVAL_SECONDS, min(MAX_AUTO_ANNOUNCE_INTERVAL_SECONDS, seconds))
    return (seconds // 60) * 60


def route_max_age_seconds(announce_interval_seconds):
    try:
        interval = int(announce_interval_seconds or 0)
    except (TypeError, ValueError):
        interval = 0
    if interval > 0:
        return interval
    return DEFAULT_PATH_MAX_AGE_SECONDS


def path_entry(destination_hash):
    table = getattr(RNS.Transport, "path_table", None) or {}
    return table.get(destination_hash)


def path_is_stale(destination_hash, max_age_seconds):
    entry = path_entry(destination_hash)
    if entry is None:
        return False
    timestamp = entry[0] if entry else None
    if not timestamp:
        return True
    interface = entry[5] if len(entry) > 5 else None
    connected_at = getattr(interface, "connected_at", None) if interface is not None else None
    if connected_at is not None and timestamp < connected_at:
        return True
    if max_age_seconds and max_age_seconds > 0 and (time.time() - timestamp) > max_age_seconds:
        return True
    return False


def path_is_usable(destination_hash, max_age_seconds):
    return path_entry(destination_hash) is not None and not path_is_stale(destination_hash, max_age_seconds)


def forget_path(destination_hash):
    table = getattr(RNS.Transport, "path_table", None)
    if not table or destination_hash not in table:
        return
    lock = getattr(RNS.Transport, "path_table_lock", None)
    if lock is None:
        table.pop(destination_hash, None)
        return
    with lock:
        table.pop(destination_hash, None)


def path_retry_seconds(bitrate=None):
    try:
        rate = int(bitrate or 0)
    except (TypeError, ValueError):
        rate = 0
    if rate <= 0:
        rate = DEFAULT_LORA_BITRATE
    mtu = getattr(RNS.Reticulum, "MTU", 500)
    return max(1.0, (mtu * 8) / rate)


def slowest_online_bitrate(default=DEFAULT_LORA_BITRATE):
    rates = []
    for interface in getattr(RNS.Transport, "interfaces", []) or []:
        if not getattr(interface, "online", False):
            continue
        try:
            rate = int(getattr(interface, "bitrate", 0) or 0)
        except (TypeError, ValueError):
            continue
        if rate > 0:
            rates.append(rate)
    return min(rates) if rates else default


async def ensure_fresh_path(destination_hash, timeout_seconds, max_age_seconds, bitrate=None):
    """Request a path until one is usable, repeating after one airtime.

    A timeout of zero sends a single request when the current path is missing
    or stale and returns without waiting.
    """
    deadline = time.time() + max(float(timeout_seconds or 0), 0)
    retry_after = path_retry_seconds(bitrate if bitrate is not None else slowest_online_bitrate())
    next_request = 0
    while True:
        if path_is_usable(destination_hash, max_age_seconds):
            return True
        now = time.time()
        if now >= next_request:
            if path_entry(destination_hash) is not None:
                forget_path(destination_hash)
            RNS.Transport.request_path(destination_hash)
            next_request = now + retry_after
        if not timeout_seconds or time.time() >= deadline:
            return path_is_usable(destination_hash, max_age_seconds)
        await asyncio.sleep(0.05)
