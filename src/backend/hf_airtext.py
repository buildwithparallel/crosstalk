"""Refuse amateur HF text that must not go on the air.

Must stay aligned with hfbridge.airtext in the radio repo. Crosstalk does not
import that package, so this copy exists to reject a message before it leaves
the sender. The transmitter is still the legal gate.
"""

from __future__ import annotations

import math
import re
from collections import Counter

ENCODED_ERROR = "coded or encrypted text cannot go on the air"
LANGUAGE_ERROR = "that language cannot go on the air"

_LEET = str.maketrans(
    {
        "@": "a",
        "4": "a",
        "3": "e",
        "1": "i",
        "!": "i",
        "0": "o",
        "$": "s",
        "5": "s",
        "7": "t",
    }
)

_BLOCKED = frozenset(
    {
        "asshole",
        "assholes",
        "bastard",
        "bitch",
        "bitches",
        "blowjob",
        "cock",
        "cocks",
        "cunt",
        "dick",
        "dicks",
        "faggot",
        "fuck",
        "fucked",
        "fucker",
        "fucking",
        "handjob",
        "motherfucker",
        "motherfucking",
        "nigga",
        "nigger",
        "porn",
        "porno",
        "pussy",
        "shit",
        "shitty",
        "slut",
        "whore",
    }
)

_PEM = re.compile(
    r"-----BEGIN|BEGIN PGP|BEGIN AGE|age-encryption\.org|\bssh-(?:ed25519|rsa|dss)\b",
    re.IGNORECASE,
)
_HEX_BLOB = re.compile(r"\b[0-9a-fA-F]{40,}\b")
_LETTERS = re.compile(r"[a-z]+")


def air_text_error(text: str) -> str | None:
    """Return a reason the text cannot go on amateur HF, or None."""
    if not text or not text.strip():
        return "payload is empty"
    if _has_disallowed_chars(text):
        return ENCODED_ERROR
    if _looks_encoded(text):
        return ENCODED_ERROR
    if _has_blocked_language(text):
        return LANGUAGE_ERROR
    return None


def _has_disallowed_chars(text: str) -> bool:
    for char in text:
        code = ord(char)
        if char in "\t\n\r":
            continue
        if code < 32 or code == 127 or 0x80 <= code <= 0x9F:
            return True
        if char == "\ufffd":
            return True
    return False


def _looks_encoded(text: str) -> bool:
    if _PEM.search(text):
        return True
    if _HEX_BLOB.search(text):
        return True
    compact = "".join(text.split())
    if _is_base64_blob(compact):
        return True
    for token in re.findall(r"[A-Za-z0-9+/=]{28,}", text):
        if _is_base64_blob(token):
            return True
    if (
        len(compact) >= 40
        and " " not in text.strip()
        and all(ord(char) < 128 for char in compact)
        and _entropy(compact) >= 4.8
    ):
        return True
    return False


def _is_base64_blob(token: str) -> bool:
    if len(token) < 28:
        return False
    if not re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", token):
        return False
    has_digit = any(char.isdigit() for char in token)
    has_symbol = "+" in token or "/" in token or token.endswith("=")
    return has_digit or has_symbol


def _entropy(text: str) -> float:
    counts = Counter(text)
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def _has_blocked_language(text: str) -> bool:
    folded = re.sub(r"(.)\1{2,}", r"\1", text.casefold().translate(_LEET))
    words = _LETTERS.findall(folded)
    candidates = set(words)
    candidates.update(_joined_singles(words))
    candidates.update(words[index] + words[index + 1] for index in range(len(words) - 1))
    for word in candidates:
        if word in _BLOCKED or word.rstrip("s") in _BLOCKED:
            return True
    return False


def _joined_singles(words: list[str]) -> list[str]:
    joined: list[str] = []
    run: list[str] = []
    for word in words:
        if len(word) == 1:
            run.append(word)
            continue
        if len(run) >= 4:
            joined.append("".join(run))
        run = []
    if len(run) >= 4:
        joined.append("".join(run))
    return joined
