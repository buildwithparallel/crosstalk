export function isPrnsHopspotPath(path) {
    return String(path?.next_hop_interface ?? "").includes("PrnsHopspotInterface[");
}

export function formatPathBadge(path) {
    if(!path) return "Unknown route";
    if(isPrnsHopspotPath(path)) return "LoRa route";
    if(path.hops === 0 || path.hops === 1) return "Direct";
    return `${path.hops} hops`;
}

export function pathBadgeTitle(path) {
    if(isPrnsHopspotPath(path)) {
        return "Reachable through a Prns Hopspot LoRa interface. Reticulum's protocol-hop count includes embedded forwarding and is not RF distance.";
    }
    return "Reticulum route distance";
}

export function formatPathDetails(path) {
    const hopWord = path.hops === 1 ? "hop" : "hops";
    if(isPrnsHopspotPath(path)) {
        return [
            `LoRa route via ${path.next_hop_interface}`,
            "",
            `Reticulum reports ${path.hops} protocol ${hopWord}. This includes forwarding inside the embedded Hopspots and does not mean there are ${path.hops} physical LoRa hops.`,
        ].join("\n");
    }
    return `${path.hops} ${hopWord} away via ${path.next_hop_interface}`;
}
