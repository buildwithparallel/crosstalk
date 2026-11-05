# Prns Hopspot over USB

Choose **Interfaces → Add Interface → Prns Hopspot (USB)**, press **Find
devices**, and explicitly select the board. Save the interface. Crosstalk
connects directly to its WebUSB bulk endpoints using USB Auto protocol v2.
No TCP bridge, Prns daemon, or RNode firmware is required.

The board must already run Prns Hopspot firmware. Meshtastic and RNode devices
do not use this protocol. A successful USB handshake proves the host connection
only; it does not prove LoRa settings, radio delivery, or voice throughput.

Each interface opens only its saved physical USB port. Keep the two test
boards in their assigned ports. It refuses an ambiguous match and never falls
back to another board. An unplugged, busy, rebooting, or unavailable board stays
offline while the app continues and retries. USB operations and handshakes have
finite time limits. Outgoing packets are not stored for later replay while offline.

USB access needs PyUSB and native libusb. On a development Mac, install libusb
with Homebrew and install the project's Python requirements. macOS packaging
includes the discovered native library in the backend's lib directory.

The USB stream, framing/session handling, and Reticulum interface are separate.
Bluetooth is not implemented yet and is rejected if selected in config. A
future Prns Bluetooth transport can reuse the Reticulum packet handling while
implementing its own discovery and framing.

This interface never flashes boards, enrolls controller grants, changes radio
configuration, or accesses private device keys. Configure LoRa and controller
permissions through Prns separately. Keep LAN and TCP interfaces off during an
over-the-air test so the two Crosstalk instances cannot bypass the radios.
