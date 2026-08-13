# Chat path status

The Chats list shows a small indicator next to each conversation name:

- A filled green dot means Crosstalk currently has a Reticulum path to that LXMF destination.
- An empty circle means no path is in the local Transport table.

This is a send-now hint, not a true online/offline signal. A path can linger after a peer goes quiet, and a live peer can show an empty circle until an announce or path request fills the table.

## How it updates

`GET /api/v1/lxmf/conversations` includes `has_path` for each chat. That value comes from `RNS.Transport.has_path()`, which is a local lookup and does not request a path from the network.

The messages page already reloads conversations about every five seconds, so the dots can lag by that much.

## What it does not do

- It does not ping the other client.
- It does not call `request_path()` while listing chats.
- It does not replace hop count or signal details in an open conversation.
