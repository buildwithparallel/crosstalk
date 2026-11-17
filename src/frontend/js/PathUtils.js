export function isPrnsHopspotPath(path) {
    return String(path?.next_hop_interface ?? "").includes("PrnsHopspotInterface[");
}

export function formatPathBadge(path) {
    if(!path) return "Unknown route";
    if(isPrnsHopspotPath(path)) return "Hopspot";
    if(path.hops === 0 || path.hops === 1) return "Direct";
    return `${path.hops} hops`;
}

export function pathBadgeTitle(path) {
    if(isPrnsHopspotPath(path)) {
        return "Reachable through a Prns Hopspot. The board chooses the radio, which can be LoRa or Bluetooth. The hop count includes forwarding inside the board.";
    }
    return "Reticulum route distance";
}

export function formatPathDetails(path) {
    const hopWord = path.hops === 1 ? "hop" : "hops";
    if(isPrnsHopspotPath(path)) {
        return [
            `Hopspot route via ${path.next_hop_interface}`,
            "",
            `Reticulum reports ${path.hops} protocol ${hopWord}. Crosstalk only sees the USB connection. The board may forward over LoRa, Bluetooth, or another radio it has enabled.`,
        ].join("\n");
    }
    return `${path.hops} ${hopWord} away via ${path.next_hop_interface}`;
}
