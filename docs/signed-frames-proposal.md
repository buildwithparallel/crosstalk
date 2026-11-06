# Proposal: sender authentication for the plaintext HF leg

Opened as a docs-only pull request because Issues are disabled on this repository. Nothing in this PR touches code; it is the proposal text and a link to a reference implementation. Decline freely.

At 27:48 in your video you say: "We're not going to solve spoofing in this video, although
cryptographic signatures could still prove mathematically that a message originated from a
specific sender." Your codec doc backs that up: the radio hop is plaintext, so nothing on the
air proves who sent a frame.

We built a piece for that gap: a 73-byte signature envelope, one Python file, MIT.

Byte layout:

    0        version 0x01, 1 byte
    1        key id, first 8 bytes of SHA-256(pubkey), 8 bytes
    9        Ed25519 signature, 64 bytes
    73       payload, any length
    73 + n   total envelope size

No timestamp, no validity window, no clock in the format. python -m unittest: 21 tests, OK
(skipped=1).

Hook points for a bridge extension: seal at the origin station, never the gateway; verify plus
envelope-hash dedup at ingress; a key announce frame carries the key once.

One item on your side: hf_airtext.py's gate blocks control bytes, hex runs and base64, so a
sealed frame needs its own VER/TYPE nibble to ride PAYLOAD. Your call, not ours.

What this does not fix: metadata (call sign, destination, sequence, timing) leaves traffic
analysis open, replay needs the one-line dedup above, and this is authentication, never
encryption; the text stays exactly as readable as before.

Legal reading, ours, unconfirmed by either regulator: in the US, 47 CFR 97.113(a)(4) bars only
codes that obscure meaning, and 97.309(b) covers a novel digital code with no publication duty,
though when a Regional Director deems it necessary the station must cease or restrict the
transmission and maintain a record, convertible to the original information, of all digital
communications transmitted. In Canada, SOR/96-484 s.47(b) permits a code or cipher that
is not secret, and a published byte layout satisfies that on its face. Neither reading is backed
by case law or either regulator's own interpretation.

Happy to open a PR, or you can vendor the file directly.

This comes out of ArrowMem (arrowmem.ca), a private assistant that runs on your own hardware. A
companion node for reaching a home machine, and a survival-content node answering with no model
and no internet, are published alongside it: https://github.com/ArrowMem/arrowmem-envelope, https://github.com/ArrowMem/arrowbridge-companion, https://github.com/ArrowMem/arrowbridge-erp-node.

---

