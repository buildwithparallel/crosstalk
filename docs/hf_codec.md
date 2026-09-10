# 10 m HF codec (public recipe)

This is the on-air notice for Crosstalk's optional amateur HF hop — including
for anyone listening on 10 meters, and for the FCC.

Crosstalk can send a short conversation over a licensed 10 meter station when
there is no Reticulum path. The radio hop is **plaintext**. Encrypted Reticulum
packets never go on the air. The station decrypts locally and shouts callsign +
destination hash + UTF-8. Anyone with a receiver can read that shout.

Digital station ID counts under Part 97.119 because this recipe is public. The
RF hop is **not encoded to obscure meaning** (Part 97.113(a)(4)). Anyone with a
receiver can read the text. There is no second, hidden layer.

Nothing on 10 meters is a Reticulum packet.

The station software that keys Hermes-Lite 2 or listens on an RTL-SDR lives in
a companion repo. This file is the codec. Publishing Crosstalk publishes the
recipe.

## Modulation

| Item | Value |
| --- | --- |
| Band | 10 m amateur |
| Center | **28.124 MHz** (move if busy; stay in 28.120–28.189 MHz) |
| Mode | USB / IQ, **2-CPFSK** around that center |
| Mark (`1`) | +50 Hz |
| Space (`0`) | −50 Hz |
| Rate | **100 baud**, high bit first (`numpy.unpackbits` order) |
| Occupied bandwidth | ~300 Hz on the data body (limit 2.8 kHz) |
| FEC | LDPC (128, 64) rate 1/2; CRC-16 last |
| Encryption | **none** |
| Station ID | amateur callsign in ORIGIN, every shout |

Tune a receiver to 28.124 MHz USB. A `1` is a tone 50 Hz above that center; a
`0` is 50 Hz below. 100 of those flips per second. Phase is continuous
(constant envelope): integrate `2π f / sample_rate` per sample.

A Technician (or higher) may use data on 10 meters from 28.000–28.300 MHz. An
unattended digital station on 10 m is limited to **28.120–28.189 MHz** (Part
97.221(b)). 28.124 MHz is a working center, not a band plan. Keep occupied
bandwidth under 2.8 kHz. Transmit needs a license and a callsign in ORIGIN.
Listening does not.

## Burst (still those two data tones)

New shouts, in order:

1. **Costas wake-up** — 7 symbols, FT8 order `(3, 1, 4, 0, 6, 5, 2)`, shifted
   off DC. Transmitted offsets from center, at 100 baud:
   **+50, −150, +150, −250, +350, +250, −50 Hz**. About 70 ms. Not in the CRC.
2. **Preamble** — `55 55 55 55 55 55 55 55` (`01010101` click-track).
3. **Unique word** — `FD 59 BB 49 C5 E5 18 40`. 63-bit m-sequence
   (`x^6 + x + 1`, all-ones init) padded with one `0`. Thumbtack
   autocorrelation; detect by correlator, not an exact bit match. Older
   shouts used `2E FC 37 49`.
4. **LDPC wrapper** — three copies of the block count, then the coded payload
   (see below).
5. **Tail** — 16 bytes of `55` (timing pad, not text, not in the CRC).

Receivers may still accept older **300 baud** shouts (±125 Hz and ±250 Hz).
New shouts are 100 baud ±50 Hz.

## Inner frame (plaintext)

After LDPC decode, the inner packet is:

| Offset | Bytes | Field | Meaning |
| --- | --- | --- | --- |
| 0 | 1 | VER/TYPE | high nibble version, low nibble type. `10` = version 1, type 0 (data) |
| 1 | 1 | FLAGS | unused, 0 |
| 2 | 6 | ORIGIN | sending station callsign (radix-40) |
| 8 | 16 | DEST | recipient LXMF delivery hash, not a name |
| 24 | 2 | MSG_ID | sender sequence number, big-endian |
| 26 | 1 | FRAG | high nibble index (0-based), low nibble total. `01` = whole message |
| 27 | 1 | LEN | payload length |
| 28 | n | PAYLOAD | UTF-8 text, max **200** bytes |
| 28+n | 2 | CRC | CRC-16-CCITT, poly `0x1021`, init `0xFFFF`, no reflection, xorout 0 |

CRC covers everything above it, big-endian on the wire. No match → drop. No
decrypt step.

### Callsign (radix-40)

Alphabet, index 0 first:

```
 ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-.
```

(leading space). Pad the callsign on the right to 9 characters with spaces.
Value is a base-40 integer, packed big-endian into 6 bytes:

```
value = 0
for ch in padded:
    value = value * 40 + alphabet_index(ch)
wire = value.to_bytes(6, "big")
```

Example: `N0CALL` → `57 7b 2a 46 f8 00`.

### CRC-16

```
crc = 0xFFFF
for byte in body:
    crc ^= byte << 8
    for _ in range(8):
        if crc & 0x8000:
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF
        else:
            crc = (crc << 1) & 0xFFFF
```

## LDPC wrapper

After the unique word:

```
3 bytes   n_blocks, n_blocks, n_blocks   (uint8, majority vote)
n × 16 B  n_blocks of a (128, 64) codeword, 16-way interleaved
```

Inner CRC frame bits are padded with zeros to a multiple of 64, split into
`n_blocks` information words (`1 … 40`), each encoded to 128 bits. Those
`n_blocks × 128` bits are interleaved 16 ways: write row-major into a matrix
with 16 columns, read column-major (`reshape(rows, 16).T.ravel()`).

Each 64 information bits become 128 bits on the air. Soft min-sum is fine;
CRC still has the last word. Older CRC-only shouts (no repeated `n_blocks`)
may still be heard.

At 100 baud with Costas + LDPC, a short line is ~14–16 s; 200 bytes is ~40 s.

### (128, 64) parity-check matrix

`H` is 64 × 128 over GF(2), column weight 3, row weight about 6, full rank.
The reference built it with NumPy `default_rng(20260823)`. **The matrix below
is normative**, not the generator.

Each line is one row as 128 bits packed big-endian (32 hex digits). A `1` in
bit 127 of the hex value is column 0.

```
00 80000004000020000004000040040000
01 00000820000010008000004000000004
02 00800000002000101000000800040000
03 00008000400010000008000400000400
04 00010000082000000400000200020000
05 02000000040004000400010000010000
06 00100000008200000004000010000080
07 01000000040040001000000000400040
08 40000200000008000000402000002000
09 00000804000008002000000400004000
10 00001000010001000080000020010000
11 00200000020000080000401000020000
12 10000040000080004000004000000001
13 10000000010000020001000100004000
14 00400000400000200080000020200000
15 08000000040002002000000008010000
16 00020010000800000010010000000200
17 00002002001000000800000001000004
18 00200000004004000800000400002000
19 00001100000000400100000080000010
20 01000000080000020000810000000010
21 00004001000200000020000008001000
22 80000020000400008000008000000020
23 20000010000000010100000100000002
24 02000008000001000004008000000200
25 00100000008000800100040000000001
26 00020000008000202000000080000080
27 40000000100000800000100001000040
28 08000000200002000000800000400008
29 08000002000020004000002000000080
30 00040000200080000040040000002000
31 00400008000080000000800000808000
32 00002000020400000200001000001000
33 00004080000800000002000004000040
34 00020000004000400001020000000100
35 00000c00001000000000200000201000
36 04000020000200000000200040000010
37 00010000010400000000400100000100
38 00100000100000010010000004000008
39 00004002000000010000081000000100
40 00800080000000044000000001100000
41 80000001000000080000060000000002
42 00000400800000200000080002000200
43 10000000800100000200020000000004
44 02000000200000040000200080000400
45 00080000800000100010000000200002
46 00040001000800000002000040080000
47 00200100000040001000000000880000
48 00800000400000020080000000400400
49 00008000004100000040000800000020
50 04000080000010000000100004008000
51 00002008000100000400000200040000
52 40000200000001008000000200000800
53 00010000020004000020000010000020
54 00040040001000000008000002000800
55 00080004000000080020002000004000
56 00001010000020000001000000808000
57 20000000002000040200008000000008
58 20000040000002000000104000100000
59 00080400000000100000080008020000
60 01000000080000800800000010000800
61 00008100000008000002000020000001
62 00400000100000400008000002080000
63 04000200000040000040000800100000
```

Systematic encoder: place the 64 information bits in columns
`0…62` and `67`. Solve `H x = 0` for the remaining 64 bits (parity). Decode
with belief propagation on `H` (min-sum is enough); then take those same
information columns.

## Example shout

A status note from a Reticulum client with no internet path, addressed to an
ordinary LXMF inbox. The text is the whole message.

- **Origin:** `N0CALL` (the licensed station keying the transmitter)
- **Dest:** `0123456789abcdef0123456789abcdef`
- **MSG_ID:** 42
- **Message:** `no internet here. all ok. next check 0900` (41 characters)

Inner packet, **71 bytes**:

```
10 00 57 7b 2a 46 f8 00 01 23 45 67 89 ab cd ef
01 23 45 67 89 ab cd ef 00 2a 01 29 6e 6f 20 69
6e 74 65 72 6e 65 74 20 68 65 72 65 2e 20 61 6c
6c 20 6f 6b 2e 20 6e 65 78 74 20 63 68 65 63 6b
20 30 39 30 30 85 98
```

| Offset | Hex | Meaning |
| --- | --- | --- |
| 0 | `10` | version 1, data |
| 1 | `00` | flags off |
| 2 | `57 7b 2a 46 f8 00` | ORIGIN `N0CALL` |
| 8 | `01 23 45 … cd ef` | DEST |
| 24 | `00 2a` | MSG_ID 42 |
| 26 | `01` | fragment 0 of 1 |
| 27 | `29` | 41 bytes of text follow |
| 28 | `6e 6f 20 69 … 30 30` | the UTF-8 note |
| 69 | `85 98` | CRC-16 |

On the air that packet is LDPC-wrapped (9 blocks, header `09 09 09`) plus
Costas, click-track, unique word, and tail: **179 bytes** of FSK plus 7 Costas
symbols, about **14 s** at 100 baud.

## What Crosstalk puts on this hop

The conversation toggle **Send over HF** is opt-in per chat. Crosstalk only
allows short readable UTF-8 (max 200 bytes). It refuses empty text, ciphertext
blobs, and language that must not go on amateur radio. The transmitter is
still the legal gate: it identifies with a callsign on every shout, rate-limits,
and may apply an allow list.

Crosstalk addresses the far inbox with the 16-byte LXMF delivery hash in DEST.
A title such as `hfvia:<callsign>` can mark that the text arrived via this hop;
it is not part of the on-air payload.

Sensitive traffic does not belong here. The control operator is responsible
for every emission.
