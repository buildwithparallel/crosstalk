import {
    mdiAccessPointNetwork,
    mdiIncognito,
    mdiLan,
    mdiRadioTower,
    mdiServerNetwork,
} from "@mdi/js";

const iconFamilies = {
    radio: {
        path: mdiRadioTower,
        palettes: [
            ["#0f4c81", "#0ea5e9"],
            ["#164e63", "#22d3ee"],
            ["#1e3a8a", "#3b82f6"],
        ],
    },
    backbone: {
        path: mdiLan,
        palettes: [
            ["#14532d", "#22c55e"],
            ["#065f46", "#2ee781"],
            ["#134e4a", "#14b8a6"],
        ],
    },
    server: {
        path: mdiServerNetwork,
        palettes: [
            ["#713f12", "#f59e0b"],
            ["#7c2d12", "#f97316"],
            ["#78350f", "#fbbf24"],
        ],
    },
    private: {
        path: mdiIncognito,
        palettes: [
            ["#4c1d95", "#a855f7"],
            ["#581c87", "#c084fc"],
            ["#312e81", "#818cf8"],
        ],
    },
    generic: {
        path: mdiAccessPointNetwork,
        palettes: [
            ["#334155", "#64748b"],
            ["#1e3a5f", "#4f7ea8"],
            ["#3f3f46", "#71717a"],
        ],
    },
};

function stableNumber(value) {
    let hash = 2166136261;
    for(const character of String(value ?? "")){
        hash ^= character.charCodeAt(0);
        hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
}

function familyForType(type) {
    const normalized = String(type ?? "").toLowerCase();

    if(normalized.includes("rnode") || normalized.includes("kiss") || normalized.includes("weave")){
        return iconFamilies.radio;
    }
    if(normalized.includes("i2p")){
        return iconFamilies.private;
    }
    if(normalized.includes("backbone")){
        return iconFamilies.backbone;
    }
    if(normalized.includes("tcp") || normalized.includes("server")){
        return iconFamilies.server;
    }

    return iconFamilies.generic;
}

export function infrastructureIconDataUri(infrastructure) {
    const family = familyForType(infrastructure?.type);
    const identity = infrastructure?.discovery_hash
        ?? infrastructure?.destination_hash
        ?? infrastructure?.network_id
        ?? infrastructure?.transport_id
        ?? infrastructure?.name
        ?? infrastructure?.type;
    const [base, accent] = family.palettes[stableNumber(identity) % family.palettes.length];
    const transportMarker = infrastructure?.transport
        ? '<circle cx="38" cy="10" r="4.5" fill="#2ee781" stroke="#eafff3" stroke-width="1.5"/>'
        : "";

    const svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">',
        '<defs>',
        `<linearGradient id="surface" x1="6" y1="4" x2="42" y2="44" gradientUnits="userSpaceOnUse"><stop stop-color="${accent}"/><stop offset="1" stop-color="${base}"/></linearGradient>`,
        '<radialGradient id="glow" cx="0" cy="0" r="1" gradientTransform="translate(13 9) rotate(51) scale(38)"><stop stop-color="#fff" stop-opacity=".24"/><stop offset=".7" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        '</defs>',
        '<rect width="48" height="48" rx="14" fill="url(#surface)"/>',
        '<rect x=".75" y=".75" width="46.5" height="46.5" rx="13.25" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="1.5"/>',
        '<rect width="48" height="48" rx="14" fill="url(#glow)"/>',
        `<path d="${family.path}" fill="#f8fafc" transform="translate(8 8) scale(1.333333)"/>`,
        transportMarker,
        '</svg>',
    ].join("");

    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}
