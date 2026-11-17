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
finite time limits. One in-flight voice or link packet is kept across a USB
reconnect. Announces and path requests wait for airtime at the saved bitrate.

USB access needs PyUSB and native libusb. On a development Mac, install libusb
with Homebrew and install the project's Python requirements. macOS packaging
includes the discovered native library in the backend's lib directory.

The USB stream, framing/session handling, and Reticulum interface are separate.
Crosstalk does not speak Prns Bluetooth. Selecting Bluetooth as this
interface's transport is rejected. The board itself may still be running
Bluetooth.

USB Auto only carries Reticulum packets. It does not report the board's LoRa
profile, and it does not say which of the board's radios forwarded a packet.
A muzi Base Duo runs LoRa and Bluetooth together. Packets Crosstalk sends over
USB enter that node, and the node picks the path. A nearby Bluetooth peer can
carry the traffic even when the only Crosstalk interface is the Hopspot.

The LoRa profile is set when the board is flashed, or later by a paired Prns
controller. Crosstalk does not enroll as a controller and does not change
radio settings. Link timers use a fixed estimate of 21,875 bps because the
board does not report its profile on this connection. Keep LAN and TCP
interfaces off during an over-the-air test so the two Crosstalk instances
cannot bypass the radios.
