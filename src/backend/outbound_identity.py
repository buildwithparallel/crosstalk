"""Outbound LXMF send helpers.

A reply is a new delivery. Crosstalk must not require the inbound Reticulum
path or link to still exist after a long pause. Identity can be restored from
a saved announce when RNS has culled ``known_destinations``.
"""

import base64

import RNS


# Do not block the send HTTP call waiting for a path. LXMF retries after
# handle_outbound. Callers that want the old 10s wait can pass path_timeout.
DEFAULT_SEND_PATH_TIMEOUT_SECONDS = 0


def parse_path_timeout(raw_value, default=DEFAULT_SEND_PATH_TIMEOUT_SECONDS):
    """Parse a send path-wait in seconds. Negative values are treated as 0."""
    if raw_value is None or raw_value == "":
        return default
    timeout = float(raw_value)
    if timeout < 0:
        return 0
    return timeout


def identity_from_public_key_bytes(public_key):
    if not public_key:
        return None
    identity = RNS.Identity(create_keys=False)
    identity.load_public_key(public_key)
    return identity


def identity_from_public_key_b64(public_key_b64):
    if not public_key_b64:
        return None
    return identity_from_public_key_bytes(base64.b64decode(public_key_b64))


def remember_destination_identity(destination_hash, identity, packet_hash=None):
    """Re-seed RNS known destinations so a later recall succeeds."""
    if identity is None or destination_hash is None:
        return
    RNS.Identity.remember(
        packet_hash or destination_hash,
        destination_hash,
        identity.get_public_key(),
        getattr(identity, "app_data", None),
    )


def recall_send_identity(destination_hash, announce_public_key_b64=None):
    """Return an identity for sending, from RNS recall or a saved announce key."""
    identity = RNS.Identity.recall(destination_hash)
    if identity is not None:
        return identity

    identity = identity_from_public_key_b64(announce_public_key_b64)
    if identity is not None:
        remember_destination_identity(destination_hash, identity)
        return identity

    return None
