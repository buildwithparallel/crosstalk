import sys


def _load_list_ports():
    """Load pySerial's platform-specific port enumerator when available."""
    # pySerial emits an error to stderr before raising ImportError on Android.
    # Avoid importing its unsupported enumerator there in the first place.
    if sys.platform == "android":
        return None

    try:
        from serial.tools import list_ports
    except ImportError:
        # pySerial intentionally raises here on unsupported platforms such as
        # Android. Crosstalk's network interfaces still work without serial
        # port discovery, so startup should not fail with the optional feature.
        return None

    return list_ports


_LIST_PORTS = _load_list_ports()


def available_serial_ports():
    """Return detected serial ports, or an empty list when unsupported."""
    if _LIST_PORTS is None:
        return []

    return list(_LIST_PORTS.comports())
