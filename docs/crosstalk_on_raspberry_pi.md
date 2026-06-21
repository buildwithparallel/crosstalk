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
