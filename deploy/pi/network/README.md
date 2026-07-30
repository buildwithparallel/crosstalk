# Aspen Pi network fallback

The Pi prefers saved station networks by NetworkManager autoconnect priority:

1. Home Wi-Fi
2. The saved mobile hotspot
3. The `Aspen-Iridium-Pi` access point when no station obtains an IPv4 address

The supervisor intentionally requires NetworkManager state `100 (connected)`
and an IPv4 address. A named profile that is still connecting is not considered
usable.

The Pi Zero's BCM43438 firmware does not interoperate reliably with an iPhone
when NetworkManager's supplicant advertises mixed WPA key-management modes.
For fallback mode, the supervisor disconnects NetworkManager and starts a
strict WPA2-PSK/CCMP access point with `hostapd`, plus local DHCP through
`dnsmasq`. NetworkManager remains the station manager and starts normally
after every reboot.

Required packages:

```sh
sudo apt-get install hostapd dnsmasq
sudo systemctl disable --now hostapd.service dnsmasq.service
```

Trail access:

- SSID: `Aspen-Iridium-Pi`
- Pi address: `10.42.0.1`
- CrossTalk: `http://10.42.0.1:8000`
- SSH: `parallel@10.42.0.1`

The WPA password is provisioned directly in NetworkManager and is not stored
in this repository.
