# RNode over Bluetooth (BLE)

Crosstalk can attach an [RNode](https://github.com/markqvist/RNode_Firmware) (including Heltec V3) as a normal **RNode (LoRa Radio)** interface using Bluetooth Low Energy.

Reticulum already supports this with a `ble://` port. Crosstalk’s Add Interface form writes that port for you. The Python `bleak` package must be installed so Reticulum can open the BLE link (see `requirements.txt`).

## Pair the RNode first

1. Put the RNode in Bluetooth pairing mode (firmware / board instructions).
2. Pair and bond it in your OS Bluetooth settings (Linux BlueZ, Windows, or macOS).
3. Confirm it stays listed as paired before starting Crosstalk.

Reticulum only connects to **bonded** devices. An unpaired advertisement will not work.

## Add the interface in Crosstalk

1. Open **Interfaces → Add Interface**.
2. Choose **RNode (LoRa Radio)**.
3. Set **Connection** to **Bluetooth (BLE)**.
4. Pick a target:
   - **First paired RNode** → saves `port = ble://`
   - **Device name** → saves `port = ble://RNode 3B87` (exact advertisement name)
   - **MAC address** → saves `port = ble://AA:BB:CC:DD:EE:FF`
5. Choose a **Regional Preset** starter (US / EU / AU-NZ / 433 MHz) or leave **Custom** and enter your mesh's exact LoRa settings.
6. Review frequency / bandwidth / SF / coding rate / TX power, then save.

Presets are common regional starters only — not legal requirements and not universal for every radio. Peers must match frequency, bandwidth, spreading factor, and coding rate.

USB serial and WiFi (`tcp://host`) remain available on the same form.

## Notes

- Prefer either USB **or** BLE to the same board at once; dual connections can confuse some firmware.
- If the interface fails to start, check Crosstalk / RNS logs for bleak or bonding errors, then re-pair the device.
- Packaged desktop builds include `bleak` so BLE works without a separate pip install when you use the official Crosstalk app.
