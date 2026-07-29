<p align="center">
<a href="https://github.com/buildwithparallel/crosstalk"><img src="./logo/logo-chat-bubble.png" width="150"></a>
</p>

<h2 align="center">Crosstalk</h2>

## What is Crosstalk?

A simple mesh network communications app powered by the [Reticulum Network Stack](https://github.com/markqvist/Reticulum).

<img src="./example-1.png" alt="Crosstalk app preview">

## What does it do?

- It can send and receive messages, files and audio calls with peers;
    - Over your local network through Ethernet and WiFi, completely automatically.
    - Over the internet by connecting through a server [hosted by yourself](https://reticulum.network/manual/interfaces.html#tcp-server-interface) or [the community](https://reticulum.network/connect.html).
    - Over low-powered, license-free, ISM band LoRa Radio, with an [RNode](https://github.com/markqvist/RNode_Firmware).
    - ...and via [any other interface](https://reticulum.network/manual/interfaces.html) supported by the Reticulum Network Stack.
- It communicates securely. Messages can only be decrypted by the intended destination.
- It can communicate with any other existing [LXMF](https://github.com/markqvist/lxmf) client, such as [Sideband](https://github.com/markqvist/Sideband/) and [Nomadnet](https://github.com/markqvist/nomadnet).
- It can download files and browse micron pages (decentralised websites) hosted on [Nomad Network](https://github.com/markqvist/nomadnet) nodes.

## Features

- Supports sending and receiving messages between [Crosstalk](https://github.com/buildwithparallel/crosstalk), [Sideband](https://github.com/markqvist/Sideband/) and [Nomadnet](https://github.com/markqvist/nomadnet).
- Supports receiving and saving images and attachments sent from Sideband.
- Supports sending images, voice recordings and file attachments.
- Supports optional native Reticulum packet transport through a USB-connected RockBLOCK 9704 and Iridium IMT.
- Supports saving inbound and outbound messages to a local database.
- Supports sending an announce to the network.
- Supports setting a custom display name to send in your announce.
- Supports viewing and searching peers discovered from announces.
- Shows signed Reticulum infrastructure advertisements, including transport nodes, hop distance, radio parameters and last-seen status.
- Supports auto resending undelivered messages when an announce is received from the recipient.
- Supports sending messages to and syncing messages from [LXMF Propagation Nodes](https://github.com/markqvist/lxmf?tab=readme-ov-file#propagation-nodes).
- Supports running a local LXMF Propagation Node so other users can use your device for message storage and retrieval.
- Support for browsing pages, and downloading files hosted on Nomad Network Nodes.

## Recent Crosstalk Enhancements

- Renamed and packaged the app as Crosstalk across the desktop window, dock/app title, bundled executable and project metadata.
- Added a darker, higher-contrast app interface with updated message, network visualiser, menu and interface styling.
- Added public internet node onboarding in the Interfaces section, including rmap.world guidance and a Public Backbone Node setup flow.
- Added a disabled-by-default `RMAP World` TCP client interface so users can enable a public Reticulum entrypoint without hand-writing config.
- Added a suggested Miami Thunder Host community node for quick Reticulum connectivity testing.
- Added parsing for rmap.world `BackboneInterface` config blocks so `remote` and `target_port` are mapped into Crosstalk TCP client fields.
- Added interface delete controls, import/export polish and automatic backend restarts after interface changes.
- Removed the need to manually restart the app after editing interfaces.
- Moved Crosstalk's Reticulum config into `~/.crosstalk/.reticulum` for the desktop app so a broken global Reticulum config does not prevent launch.
- Improved chat by removing unnecessary large-message confirmation friction and allowing attachment-only messages.
- Improved file attachments by previewing image files inline while keeping the original download action.
- Improved network visualiser contrast, graph labels and connected/disconnected styling.

## Beta Features

- Support for Audio Calls to other [Crosstalk](https://github.com/buildwithparallel/crosstalk) users.
  - Audio is encoded with [codec2](https://github.com/drowe67/codec2) to support low bandwidth links.
  - Using a microphone requires using the web ui over localhost or https, due to [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet) secure context.
  - Two-way audio calls over LoRa can work well with a single hop when a [reasonable bitrate](https://unsigned.io/understanding-lora-parameters/) is configured on the RNode.
  - Some browsers such as FireFox don't work as expected. Try using a Chromium based browser if running via the command line.

## Download

You can download the latest version for Windows, Mac and Linux from the [releases](https://github.com/buildwithparallel/crosstalk/releases) page.

Alternatively, you can download the source and run it manually from a command line.

See the ["How to use it?"](#how-to-use-it) section, further down on how to do this.

## Other Installation Methods

- [Running Crosstalk on Docker](./docs/crosstalk_on_docker.md)
- [Running Crosstalk on a Raspberry Pi](./docs/crosstalk_on_raspberry_pi.md)
- [Running Crosstalk on Android with Termux](./docs/crosstalk_on_android_with_termux.md)

## Getting Started

Once you've downloaded, installed and launched Crosstalk, there's a few things you need to do in order to start communicating with other people on the network.

1. Create an Identity
2. Configure your Display Name
3. Send an Announce
4. Discover Peers and start sending messages
5. Configuring additional Network Interfaces

**Create an Identity**

On the Reticulum Network, anyone can have any number of Identities. You may opt to use your real name, or you may decide to be completely anonymous. The choice is yours.

A Reticulum Identity is a public/private key-pair. You control the private key used to generate destination addresses, encrypt content and prove receipt of data with unforgeable delivery acknowledgements.

Your public key is shared with the network when you send an announce, and allows others on the network to automatically discover a route to a destination you control.

At this time, Crosstalk generates a new Identity the first time you launch it. A future update will allow you to create and manage multiple identities.

For now, if you want to change, or reset your identity, you can access the identity file at `~/.crosstalk/identity`.

**Configure your Display Name**

The next thing you should do, is set a display name. Your display name is what everyone else on the network will see when looking for someone to communicate with from the Peers list.

You can do this in the `My Identity` section in the bottom left corner. Enter a new display name, and then press `Save`.

**Send an Announce**

When using the Reticulum Network, in order to be contactable, you need to send an `Announce`. You can send an announce as often, or as infrequently as you like.

Sending an announce allows other peers on the network to discover the next-hop across the network their packets should take to arrive at a destination that your identity controls.

If you never send an announce, you will be invisible and no one will ever be able to send anything to you.

When you move across the network, and change entrypoints, such as moving from your home WiFi network, to plugging in to an Ethernet port in a local library or even climbing a mountain and using an RNode over LoRa radio, other peers on the network will only know the previous path to your destinations.

To allow them to discover the new path their packets should take to reach you, you should send an announce.

**Discover Peers and start sending messages**

In the Reticulum Network, you can control an unlimited number of destination addresses. One of these can be an [LXMF](https://github.com/markqvist/lxmf) delivery address.

Your Reticulum Identity allows you to have an LXMF address. Think of an LXMF address as your very own, secure, end-to-end encrypted, unspoofable, email address routed over a mesh network.

When someone else on the network announces themselves (more specifically, their LXMF address), they will show up in the Peers tab.

You can click on any of these discovered peers to open a messaging interface. From here, you can send text messages, files and inline images. If they respond, their messages will show up there too.

As well as being able to announce your LXMF address and discover others, Crosstalk can also discover [Nomad Network](https://github.com/markqvist/nomadnet) nodes hosted by other users. From the Nodes tab, you are free to explore pages and download files they may be publicly sharing on the network.

A future update is planned to allow you to host your own Node and share pages and files with other peers on the network. For now, you could use the official [Nomad Network](https://github.com/markqvist/nomadnet) client to do this.

Remember, in order to connect with other peers or nodes, they must announce on the network. So don't forget to announce if you want to be discovered!

**Configuring additional Network Interfaces**

> TODO: this section is yet to be written. For now, you can check out the [official documentation for configuring interfaces](https://reticulum.network/manual/interfaces.html) in the Reticulum config file. This file is located at `~/.reticulum/config`

## How does it work?

- A python script ([crosstalk.py](./crosstalk.py)) runs a Reticulum instance and a WebSocket server.
- The web page sends and receives LXMF packets encoded in json via the WebSocket.
- Web Browser -> WebSocket -> Python Reticulum -> (configured interfaces) -> (destination)
- LXMF messages sent and received are saved to a local SQLite database.

## How to use it?

It is recommended that you [download](#download) a standalone application.

If you don't want to, or a release is unavailable for your device, you will need to;

- install [Python 3](https://www.python.org/downloads/)
- install [NodeJS v18+](https://nodejs.org/en)
- clone the source code from this repo
- install all dependencies
- then run `crosstalk.py`.

```
# clone repo
git clone https://github.com/buildwithparallel/crosstalk
cd crosstalk

# install nodejs deps
# if you want to build electron binaries, remove "--omit=dev"
# if you're using termux, add "--ignore-scripts" to fix error with esbuild
npm install --omit=dev

# build frontend vue components
npm run build-frontend

# install python deps
pip install -r requirements.txt

# run crosstalk
python crosstalk.py
```

> NOTE: You should now be able to access the web interface at http://localhost:8000

For a full list of command line options, you can run;

```
python crosstalk.py --help
```

```
usage: crosstalk.py [-h] [--host [HOST]] [--port [PORT]] [--headless] [--identity-file IDENTITY_FILE] [--identity-base64 IDENTITY_BASE64] [--generate-identity-file GENERATE_IDENTITY_FILE] [--generate-identity-base64]
              [--reticulum-config-dir RETICULUM_CONFIG_DIR] [--storage-dir STORAGE_DIR]

Crosstalk

options:
  -h, --help            show this help message and exit
  --host [HOST]         The address the web server should listen on.
  --port [PORT]         The port the web server should listen on.
  --headless            Web browser will not automatically launch when this flag is passed.
  --identity-file IDENTITY_FILE
                        Path to a Reticulum Identity file to use as your LXMF address.
  --identity-base64 IDENTITY_BASE64
                        A base64 encoded Reticulum Identity to use as your LXMF address.
  --generate-identity-file GENERATE_IDENTITY_FILE
                        Generates and saves a new Reticulum Identity to the provided file path and then exits.
  --generate-identity-base64
                        Outputs a randomly generated Reticulum Identity as base64 and then exits.
  --reticulum-config-dir RETICULUM_CONFIG_DIR
                        Path to a Reticulum config directory for the RNS stack to use (e.g: ~/.reticulum)
  --storage-dir STORAGE_DIR
                        Path to a directory for storing databases and config files (default: ./storage)
```

## Using an existing Reticulum Identity

The first time you run this application, a new Reticulum identity is generated and saved to `storage/identity`.

If you want to use an existing identity;

- You can overwrite `storage/identity` with another identity file.
- Or, you can pass in a custom identity file path as a command line argument.

To use a custom identity file, provide the `--identity-file` argument followed by the path to your custom identity file.

```
python crosstalk.py --identity-file ./custom_identity_file
```

If you would like to generate a new identity, you can use the [rnid](https://reticulum.network/manual/using.html#the-rnid-utility) utility provided by Reticulum.

```
rnid --generate ./new_identity_file
```

If you don't have access to the `rnid` command, you can use the following:

```
python crosstalk.py --generate-identity-file ./new_identity_file
```

Alternatively, you can provide a base64 encoded private key, like so;

```
python crosstalk.py --identity-base64 "GCN6mMhVemdNIK/fw97C1zvU17qjQPFTXRBotVckeGmoOwQIF8VOjXwNNem3CUOJZCQQpJuc/4U94VSsC39Phw=="
```

> NOTE: this is a randomly generated identity for example purposes. Do not use it, it has been leaked!

## Build Electron Application

Crosstalk can be run from source via a command line, as explained above, or as a standalone application.

To run as a standalone application, we need to compile the python script and dependencies to an executable with [cxfreeze](https://github.com/marcelotduarte/cx_Freeze) and then build an [Electron](https://www.electronjs.org/) app which includes a bundled browser that can interact with the compiled python executable.

This allows for the entire application to be run by double clicking a single file without the need for a user to manually install python, nor run any commands in a command line application.

To build a `.exe` when running on Windows or a `.dmg` when running on a Mac, run the following;

```
pip install -r requirements.txt
npm install
npm run dist
```

> Note: cxfreeze only supports building an executable for the current platform. You will need a Mac to build for Mac, and a Windows PC to build for Windows.

Once completed, you should have a `.exe` or a `.dmg` in the `dist` folder.

## Local Development

I normally run the following commands to work on the project locally.

**Install dependencies**

```
pip install -r requirements.txt
npm install
```

**Build and run Electron App**

```
npm run electron
```



**or; Build and run Crosstalk Server**

```
npm run build-frontend
python3 crosstalk.py --headless
```

The Vite app is built without hot reload because Crosstalk expects everything over its own port, not the Vite server port.

## TODO

- [ ] button to forget announces

# Notes

**LXMF Router**

- By default, the LXMF router rejects inbound messages larger than 1mb.
- LXMF clients are likely to have [this default limit](https://github.com/markqvist/LXMF/blob/c426c93cc5d63a3dae18ad2264b1299a7ad9e46c/LXMF/LXMRouter.py#L38), and your messages will [fail to send](https://github.com/markqvist/LXMF/blob/c426c93cc5d63a3dae18ad2264b1299a7ad9e46c/LXMF/LXMRouter.py#L1428).
- Crosstalk has increased the receive limit to 10mb to allow for larger attachments.

## License

MIT

## Future Ideas

Proven internet, decentralized-web and crypto concepts that could be useful for Crosstalk, LXMF, NomadNet and wider Reticulum workflows:

- Human-readable names for Reticulum destinations, similar to DNS or ENS, mapping names to destination hashes, public keys and service metadata.
- ENS-style identity records for LXMF addresses, NomadNet nodes, payment addresses, content hashes, contact cards, propagation-node preferences and emergency relay details.
- DID-style identity documents with verification keys, service endpoints, rotation keys, recovery keys and capability declarations.
- DNS-style signed and cached zones for community phonebooks, service directories and local-first name resolution with TTLs.
- Namecoin or Handshake-style scarce-name systems using proof-of-work, fees, auctions, staking, web-of-trust sponsorship or external-chain anchoring for global names.
- LXMF email-style workflows with folders, aliases, mailing lists, forwarding, rules, attachments, receipts and delayed delivery through propagation nodes.
- Usenet, forum and BBS-style threaded discussions replicated through propagation nodes with signed authorship and per-board retention policies.
- IRC-style live chat rooms for presence-based conversation, temporary channels, moderation and optional logs.
- Signed announcement channels for community bulletins, emergency alerts, weather updates, release notices and radio/network status.
- NomadNet directory, search and feed tooling for discovering pages, files, services, nodes and people.
- RSS or Atom-like signed feeds for blogs, node updates, software releases, classifieds, sensor logs and alert streams.
- Local-first search indexes that can be exchanged as signed, compressed snapshots.
- Content-addressed pages and files so caches and mirrors can safely serve verified content by hash.
- Community cache nodes for popular pages, Retipedia archives, maps, documentation, packages and public bulletins.
- Store-carry-forward delivery patterns from delay-tolerant networking, including expiry, custody transfer, scheduled sync and opportunistic transport.
- Bandwidth accounting, quotas, fair queues and priority classes for emergency traffic, announces, messages, file transfers and bulk sync.
- Compression, delta sync and content-defined chunking to avoid resending full files, pages, maps or indexes.
- Adaptive content negotiation for scarce links, such as text-only, low-resolution media, full media, send-later and fast-link-only modes.
- Payment or toll primitives for scarce resources like propagation storage, gateway uptime, file hosting, relay bandwidth and priority delivery.
- Anti-spam economics using proof-of-work stamps, message postage, sender quotas, allowlists, reputation, paid inbox priority and community blocklists.
- Web-of-trust tools for contact verification, signed introductions, community trust roots, signed directories and revocation lists.
- Key rotation and recovery flows using old-key-signed transitions, social recovery, multisig recovery, expiration and revocation bulletins.
- Capability-based access for posting, reading, moderation, uploads, gateway access, private pages and group membership.
- Classifieds and marketplace tools for local listings, wanted/offered posts, services, rides, parts, escrow, reputation and expiration.
- Signed software and package repositories with mirrors, release channels, deltas, reproducible builds and verified updates.
- Git, issue tracker and wiki workflows over Reticulum using signed releases, patches over LXMF, work documents and code review bundles.
- Maps and geospatial tools for gateway maps, radio coverage, local hazards, meetups, APRS-like beacons, offline tiles and emergency overlays.
- Network weather and monitoring tools for reachable nodes, gateway capacity, link quality, propagation delays, announce pressure and service uptime.
- Dynamic gateway discovery for public and private entrypoints, radio access points, I2P/TCP backbones, regions, policies, capacity and cost.
- Bridges to regular internet services, including email, RSS, Matrix, IRC, web-to-NomadNet, DNS, ENS and package mirrors, with clear trust/privacy labels.
- Forms, polls and small signed transactions for surveys, incident reports, check-ins, registrations, local governance and resource requests.
- Emergency and disaster workflows for priority bulletins, missing/found posts, supply requests, shelter status, medical directories and relay schedules.
- Voice, voicemail and push-to-talk workflows over LXST where bandwidth allows, with text fallback on degraded links.
- Personal sovereign cloud features for file sync, notes, contacts, calendar, bookmarks, identity documents, encrypted backups and device sync.
- Moderation primitives for public networks, including signed blocklists, community allowlists, board moderators, spam stamps, identity age and posting quotas.
