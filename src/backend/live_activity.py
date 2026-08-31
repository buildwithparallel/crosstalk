"""Surface every validated announce, not only path-table updates.

Reticulum's registered announce handlers run only when a packet is new
enough to replace a path. Hubs often rebroadcast announces the local
path table already knows, so a handler-only live feed stays empty while
RX counters still move. This hook runs after full signature validation,
which happens for those rebroadcasts too.
"""

from __future__ import annotations

import RNS

from src.backend.lxmf_app_data import display_name_from_app_data

KNOWN_ASPECTS = (
    "lxmf.delivery",
    "lxmf.propagation",
    "nomadnetwork.node",
    "call.audio",
)


def aspect_for_destination(destination_hash):
    identity = RNS.Identity.recall(destination_hash, _no_use=True)
    if identity is None:
        return None
    for aspect in KNOWN_ASPECTS:
        try:
            if RNS.Destination.hash_from_name_and_identity(aspect, identity) == destination_hash:
                return aspect
        except Exception:
            continue
    return None


def display_name_for_aspect(aspect, app_data):
    if app_data is None:
        return None
    if aspect == "lxmf.delivery":
        return display_name_from_app_data(app_data)
    if aspect == "nomadnetwork.node":
        if isinstance(app_data, bytes):
            try:
                return app_data.decode("utf-8").strip() or None
            except Exception:
                return None
        if isinstance(app_data, str):
            return app_data.strip() or None
    return None


def app_data_from_announce_packet(packet):
    data = getattr(packet, "data", None)
    if not data:
        destination_hash = getattr(packet, "destination_hash", None)
        if destination_hash is None:
            return None
        return RNS.Identity.recall_app_data(destination_hash, _no_use=True)

    keysize = RNS.Identity.KEYSIZE // 8
    ratchetsize = RNS.Identity.RATCHETSIZE // 8
    name_hash_len = RNS.Identity.NAME_HASH_LENGTH // 8
    sig_len = RNS.Identity.SIGLENGTH // 8
    min_len = keysize + name_hash_len + 10 + sig_len
    if len(data) <= min_len:
        return None

    if getattr(packet, "context_flag", None) == RNS.Packet.FLAG_SET:
        app_data = data[min_len + ratchetsize:]
    else:
        app_data = data[min_len:]
    return app_data or None


def heard_announce_payload(packet, origin="heard"):
    destination_hash = packet.destination_hash
    aspect = aspect_for_destination(destination_hash)
    app_data = app_data_from_announce_packet(packet)
    interface = getattr(packet, "receiving_interface", None)
    return {
        "destination_hash": destination_hash.hex() if isinstance(destination_hash, bytes) else str(destination_hash),
        "aspect": aspect,
        "display_name": display_name_for_aspect(aspect, app_data),
        "hops": getattr(packet, "hops", None),
        "rssi": getattr(packet, "rssi", None),
        "snr": getattr(packet, "snr", None),
        "quality": getattr(packet, "quality", None),
        "interface": str(interface) if interface is not None else None,
        "origin": origin,
    }


def local_announce_payload(destination_hash, aspect, display_name):
    if isinstance(destination_hash, bytes):
        destination_hash = destination_hash.hex()
    return {
        "destination_hash": destination_hash,
        "aspect": aspect,
        "display_name": display_name,
        "hops": 0,
        "rssi": None,
        "snr": None,
        "quality": None,
        "interface": "this device",
        "origin": "sent",
    }


def install_validate_announce_hook(callback):
    original = RNS.Identity.validate_announce
    if getattr(original, "_crosstalk_live_activity", False):
        return

    def wrapped(packet, only_validate_signature=False, *args, **kwargs):
        # RNS 1.5.2+ passes signal_blackholed=True. Swallowing unknown kwargs
        # here TypeErrors and drops every inbound announce.
        result = original(packet, only_validate_signature, *args, **kwargs)
        # Signature-only is the inbound path that still runs for our own
        # destination when a hub echoes the announce back. Full validation
        # is skipped for local destinations, so hooking only that misses
        # the announce button.
        if result and only_validate_signature:
            try:
                callback(packet)
            except Exception:
                pass
        return result

    wrapped._crosstalk_live_activity = True
    RNS.Identity.validate_announce = staticmethod(wrapped)
