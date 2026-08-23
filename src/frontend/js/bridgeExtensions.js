// Catalog of paths that cannot be ordinary network connections in Crosstalk.
// Each implementation has a stable id. New kinds of path are new entries.
// Radios for a kind live on that kind's page as roles.
//
// This card is one hop (custom public long-distance radio), not the whole
// amateur radio service. APRS, Winlink, JS8, packet, pagers, SMS, and other
// meshes should be sibling cards with their own ids when they exist.

export const OTA_LONG_HAUL_ID = "ota-long-haul";
export const LAST_RESORT_HOP_ID = OTA_LONG_HAUL_ID;
const LEGACY_EXTENSION_IDS = {
    "last-resort-hop": OTA_LONG_HAUL_ID,
    "amateur-hf": OTA_LONG_HAUL_ID,
};
// Must match hfbridge.frame.MAX_PAYLOAD.
export const LAST_RESORT_MAX_BYTES = 200;

export function utf8ByteLength(text) {
    return new TextEncoder().encode(text || "").length;
}

export function truncateUtf8Bytes(text, maxBytes = LAST_RESORT_MAX_BYTES) {
    const encoder = new TextEncoder();
    const bytes = encoder.encode(text || "");
    if (bytes.length <= maxBytes) {
        return text || "";
    }
    let end = maxBytes;
    while (end > 0 && (bytes[end] & 0xc0) === 0x80) {
        end -= 1;
    }
    return new TextDecoder().decode(bytes.slice(0, end));
}

export const OTA_LONG_HAUL = {
    id: OTA_LONG_HAUL_ID,
    name: "OTA Long Haul",
    headline: "Crosstalk currently supports an open source over-the-air long-haul hop at 28.124 MHz.",
    summary: "A slow public radio hop across long distance when mesh, internet, and satellite cannot reach someone. Anyone with a receiver can read it. Crosstalk encryption does not go over the radio.",
    frequency: "28.124 MHz",
    frequencyNote: "allowed range 28.120–28.189 MHz",
    repoUrl: "https://github.com/buildwithparallel/reticulum-hf-bridge",
    repoPublic: false,
    roles: [
        {
            id: "rtl-sdr",
            processRole: "ingress",
            kind: "Receive only",
            hardware: "RTL-SDR",
            icon: "usb",
            summary: "USB dongle that only listens. No license. Useful as the cheap far side of a conversation.",
        },
        {
            id: "hermes-lite",
            processRole: "txbridge",
            kind: "Send and receive",
            hardware: "Hermes-Lite 2",
            icon: "broadcast",
            summary: "Radio that can send. Needs a US Technician-class license or higher, and your callsign.",
        },
    ],
};

export const LAST_RESORT_HOP = OTA_LONG_HAUL;

export const BRIDGE_EXTENSIONS = [
    OTA_LONG_HAUL,
];

export function getBridgeExtension(id) {
    const resolved = LEGACY_EXTENSION_IDS[id] || id;
    return BRIDGE_EXTENSIONS.find((item) => item.id === resolved) || null;
}

export function getBridgeExtensionRole(extensionId, roleId) {
    const extension = getBridgeExtension(extensionId);
    return extension?.roles?.find((item) => item.id === roleId) || null;
}

export function runningBridgeShortcuts(processes) {
    const found = [];
    for (const extension of BRIDGE_EXTENSIONS) {
        for (const role of extension.roles || []) {
            if (!processes?.[role.processRole]?.running) {
                continue;
            }
            found.push({
                extensionId: extension.id,
                roleId: role.id,
                hardware: role.hardware,
                icon: role.icon || "broadcast",
            });
        }
    }
    return found;
}

export function extensionCapabilities(extension) {
    return [...new Set((extension.roles || []).map((role) => role.kind))];
}

export function repoHostLabel(url) {
    try {
        const parsed = new URL(url);
        return `${parsed.host}${parsed.pathname.replace(/\.git$/, "").replace(/\/$/, "")}`;
    } catch (error) {
        return url;
    }
}
