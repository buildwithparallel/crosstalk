"""Parse LXMF announce app_data without assuming msgpack strings are bytes.

Newer umsgpack unpacks names as str. LXMF.display_name_from_app_data still
calls .decode() and logs an error for every such announce.
"""

import RNS.vendor.umsgpack as msgpack


def display_name_from_app_data(app_data=None):
    if app_data is None or len(app_data) == 0:
        return None

    first = app_data[0]
    if isinstance(first, int) and ((0x90 <= first <= 0x9F) or first == 0xDC):
        peer_data = msgpack.unpackb(app_data)
        if not isinstance(peer_data, list) or len(peer_data) < 1:
            return None
        return _as_text(peer_data[0])

    return _as_text(app_data)


def _as_text(value):
    if value is None:
        return None
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace")
    elif isinstance(value, str):
        text = value
    else:
        return None
    text = text.replace("\x00", "").strip()
    return text or None
