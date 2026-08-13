# Chat path status

The Chats list shows a small indicator next to each conversation name:

- A filled green dot means Crosstalk currently has a Reticulum path to that LXMF destination.
- An empty circle means no path is in the local Transport table.

This is a send-now hint, not a true online/offline signal. A path can linger after a peer goes quiet, and a live peer can show an empty circle until an announce, a path request, or an on-demand probe fills the table.

## How it updates

`GET /api/v1/lxmf/conversations` includes `has_path` for each chat. That value comes from `RNS.Transport.has_path()`, which is a local lookup and does not request a path from the network.

The messages page already reloads conversations about every five seconds, so unopened chats wait for an announce (or other traffic) to populate the path table.

Opening a conversation is different. If that chat has no local path, Crosstalk sends a silent LXMF delivery ping in the background. A successful proof requests/fills the path and refreshes the chats-list dot without waiting for the peer to announce. Message loading is not blocked, and switching chats ignores a late result. Failures stay silent.

## What it does not do

- It does not ping every chat in the list.
- It does not ping on launch when no conversation is selected.
- It does not call `request_path()` while listing chats.
- It does not replace hop count or signal details in an open conversation.
- It does not show the manual Ping Destination dialog; that remains a separate, explicit action.
