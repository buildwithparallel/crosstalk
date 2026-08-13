# Crosstalk on a Raspberry Pi

A simple guide to install [Crosstalk](https://github.com/buildwithparallel/crosstalk) on a Raspberry Pi.

This would allow you to connect an [RNode](https://github.com/markqvist/RNode_Firmware) (such as a Heltec v3) to the Rasbperry Pi via USB, and then access the Crosstalk Web UI from another machine on your network.

One useful setup is to run a Pi + RNode combo as a small always-on node, then access the Crosstalk Web UI via WiFi.

> Note: This has been tested on a Raspberry Pi 4 Model B

## Install Raspberry Pi OS

If you haven't already done so, the first step is to install Raspberry Pi OS onto an sdcard, and then boot up the Pi. Once booted, follow the below commands.

## Update System

```
sudo apt update
sudo apt upgrade
```

## Install System Dependencies

```
sudo apt install git
sudo apt install python3-pip
```

## Install NodeJS v22

```
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/nodesource.gpg
NODE_MAJOR=22
echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt update
sudo apt install nodejs
```

## Install Crosstalk

```
git clone https://github.com/buildwithparallel/crosstalk
cd crosstalk
pip install -r requirements.txt --break-system-packages
npm install --omit=dev
npm run build-frontend
```

The frontend build downloads Whisper Tiny weights for on-device chat dictation.
That step needs internet once; speaking into the composer does not.

## Run Crosstalk

```
python crosstalk.py --headless --host 0.0.0.0
```

## Configure Service

Adding a `systemd` service will allow Crosstalk to run in the background when you disconnect from the Pi's terminal.

```
sudo nano /etc/systemd/system/crosstalk.service
```

```
[Unit]
Description=crosstalk
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=pi
Group=pi
WorkingDirectory=/home/pi/crosstalk
ExecStart=/usr/bin/env python /home/pi/crosstalk/crosstalk.py --headless --host 0.0.0.0

[Install]
WantedBy=multi-user.target
```

> Note: Make sure to update the usernames in the service file if needed.

```
sudo systemctl enable crosstalk.service
sudo systemctl start crosstalk.service
sudo systemctl status crosstalk.service
```

You should now be able to access Crosstalk via your Pi's IP address.

> Note: Don't forget to include the default port `8000`

## RockBLOCK 9704 / Iridium IMT

Crosstalk includes an optional native Reticulum interface for a USB-connected
RockBLOCK 9704. It sends complete encrypted Reticulum packets as Iridium
Messaging Transport (IMT) RAW messages; it does not translate LXMF into a
different application protocol.

The RockBLOCK dependency is deliberately optional, so desktop and macOS
installations without satellite hardware continue to work normally.

### Install the device-side dependencies

Connect the RockBLOCK over USB and identify its serial port:

```sh
ls -l /dev/ttyUSB*
```

Install Ground Control's Python driver in the same Python environment used to
run Crosstalk:

```sh
python -m pip install rockblock9704
```

On an original Raspberry Pi Zero, build the Vue frontend on a more capable
computer and copy the resulting `public` directory to the Pi. The headless
runtime only needs Crosstalk's runtime Python packages; `cx_Freeze` is not
needed:

```sh
python -m pip install aiohttp lxmf peewee rns websockets rockblock9704
```

### Configure the interface

The interface can be added in Crosstalk under **Interfaces → Add Interface →
RockBLOCK 9704 (Iridium)**. A ready-to-edit configuration is also available at
[`docs/examples/iridium-imt-device.config`](./examples/iridium-imt-device.config).

The important settings are:

- `port`: the RockBLOCK serial port, normally `/dev/ttyUSB0`
- `topic`: the IMT RAW topic used by both ends, default `244`
- `maximum_queued_packets`: the maximum number of packets retained on disk
- `retry_interval`: how soon a failed mobile-originated message is retried
- `persistent_destinations`: optional comma-separated destination hashes whose
  authenticated paths should be restored after a restart
- `persistent_path_max_age`: maximum age in seconds for a restored path;
  defaults to seven days

Path persistence is deliberately allowlisted. It does not enable Reticulum
transport and therefore does not turn the satellite device into a router for
other users. A path is cached only after Reticulum has accepted it through the
Iridium interface, and restoring it is a local operation that sends no IMT
message. The first authenticated announce must still arrive normally before a
destination can be cached.

At startup, Crosstalk installs the bundled external interface module into the
selected Reticulum configuration directory. Outbound packets are stored in a
SQLite queue under the Reticulum storage directory and survive process restarts
or periods without satellite coverage.

Use an antenna position with a broad, unobstructed view of the sky. The
Interfaces screen displays current signal bars and the number of packets
waiting for transmission.

### Run as a service

Copy and edit
[`docs/examples/crosstalk-iridium.service`](./examples/crosstalk-iridium.service),
then install it:

```sh
sudo cp docs/examples/crosstalk-iridium.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now crosstalk-iridium.service
```

Open `http://PI_ADDRESS:8000` from a phone or computer on the same Wi-Fi
network.

On a metered satellite link, announce only the LXMF delivery identity instead
of also announcing Crosstalk's audio-call destination:

```sh
curl http://127.0.0.1:8000/api/v1/announce/lxmf
```

Every Reticulum packet is framed with the five-byte prefix `RNSI` plus version
`1` before being submitted as a RAW IMT message. The remote Cloudloop gateway
must remove that frame and inject the untouched packet into its Reticulum
instance. The reverse path applies the same frame before submitting an IMT
mobile-terminated message. That server-side Cloudloop gateway is separate from
this device-side interface.
