// Curated Phosphor icon paths for Crosstalk UI.
// We import only the icons/weights we use so the bundle stays lean. Profile /
// LXMF user icons still use Material Design names for mesh interoperability.
//
// Note: non-regular weights append the weight to the filename
// (e.g. assets/bold/list-bold.svg), per @phosphor-icons/core.

import questionRegular from "@phosphor-icons/core/assets/regular/question.svg?raw";

import listBold from "@phosphor-icons/core/assets/bold/list-bold.svg?raw";
import arrowsClockwiseBold from "@phosphor-icons/core/assets/bold/arrows-clockwise-bold.svg?raw";
import pencilSimpleBold from "@phosphor-icons/core/assets/bold/pencil-simple-bold.svg?raw";
import xBold from "@phosphor-icons/core/assets/bold/x-bold.svg?raw";
import arrowSquareOutBold from "@phosphor-icons/core/assets/bold/arrow-square-out-bold.svg?raw";
import caretUpBold from "@phosphor-icons/core/assets/bold/caret-up-bold.svg?raw";
import treeStructureBold from "@phosphor-icons/core/assets/bold/tree-structure-bold.svg?raw";

import chatCircleDuotone from "@phosphor-icons/core/assets/duotone/chat-circle-duotone.svg?raw";
import globeHemisphereWestDuotone from "@phosphor-icons/core/assets/duotone/globe-hemisphere-west-duotone.svg?raw";
import graphDuotone from "@phosphor-icons/core/assets/duotone/graph-duotone.svg?raw";
import treeStructureDuotone from "@phosphor-icons/core/assets/duotone/tree-structure-duotone.svg?raw";
import wifiHighDuotone from "@phosphor-icons/core/assets/duotone/wifi-high-duotone.svg?raw";
import wrenchDuotone from "@phosphor-icons/core/assets/duotone/wrench-duotone.svg?raw";
import gearDuotone from "@phosphor-icons/core/assets/duotone/gear-duotone.svg?raw";
import infoDuotone from "@phosphor-icons/core/assets/duotone/info-duotone.svg?raw";
import houseDuotone from "@phosphor-icons/core/assets/duotone/house-duotone.svg?raw";
import broadcastDuotone from "@phosphor-icons/core/assets/duotone/broadcast-duotone.svg?raw";
import cellTowerDuotone from "@phosphor-icons/core/assets/duotone/cell-tower-duotone.svg?raw";
import planetDuotone from "@phosphor-icons/core/assets/duotone/planet-duotone.svg?raw";
import usbDuotone from "@phosphor-icons/core/assets/duotone/usb-duotone.svg?raw";
import plugsConnectedDuotone from "@phosphor-icons/core/assets/duotone/plugs-connected-duotone.svg?raw";
import hardDrivesDuotone from "@phosphor-icons/core/assets/duotone/hard-drives-duotone.svg?raw";
import shareNetworkDuotone from "@phosphor-icons/core/assets/duotone/share-network-duotone.svg?raw";
import detectiveDuotone from "@phosphor-icons/core/assets/duotone/detective-duotone.svg?raw";
import terminalWindowDuotone from "@phosphor-icons/core/assets/duotone/terminal-window-duotone.svg?raw";

import phoneFill from "@phosphor-icons/core/assets/fill/phone-fill.svg?raw";
import phoneDisconnectFill from "@phosphor-icons/core/assets/fill/phone-disconnect-fill.svg?raw";

import broadcastRegular from "@phosphor-icons/core/assets/regular/broadcast.svg?raw";
import shareNetworkRegular from "@phosphor-icons/core/assets/regular/share-network.svg?raw";
import hardDrivesRegular from "@phosphor-icons/core/assets/regular/hard-drives.svg?raw";
import detectiveRegular from "@phosphor-icons/core/assets/regular/detective.svg?raw";
import treeStructureRegular from "@phosphor-icons/core/assets/regular/tree-structure.svg?raw";

const WEIGHTS = ["thin", "light", "regular", "bold", "fill", "duotone"];

// name -> weight -> raw svg
const ICONS = {
    question: { regular: questionRegular },
    list: { bold: listBold },
    "arrows-clockwise": { bold: arrowsClockwiseBold },
    "pencil-simple": { bold: pencilSimpleBold },
    x: { bold: xBold },
    "arrow-square-out": { bold: arrowSquareOutBold },
    "caret-up": { bold: caretUpBold },
    "tree-structure": {
        regular: treeStructureRegular,
        bold: treeStructureBold,
        duotone: treeStructureDuotone,
    },
    "chat-circle": { duotone: chatCircleDuotone },
    "globe-hemisphere-west": { duotone: globeHemisphereWestDuotone },
    graph: { duotone: graphDuotone },
    "wifi-high": { duotone: wifiHighDuotone },
    wrench: { duotone: wrenchDuotone },
    gear: { duotone: gearDuotone },
    info: { duotone: infoDuotone },
    house: { duotone: houseDuotone },
    broadcast: { regular: broadcastRegular, duotone: broadcastDuotone },
    "cell-tower": { duotone: cellTowerDuotone },
    planet: { duotone: planetDuotone },
    usb: { duotone: usbDuotone },
    "plugs-connected": { duotone: plugsConnectedDuotone },
    "hard-drives": { regular: hardDrivesRegular, duotone: hardDrivesDuotone },
    "share-network": { regular: shareNetworkRegular, duotone: shareNetworkDuotone },
    detective: { regular: detectiveRegular, duotone: detectiveDuotone },
    "terminal-window": { duotone: terminalWindowDuotone },
    phone: { fill: phoneFill },
    "phone-disconnect": { fill: phoneDisconnectFill },
};

function normalizeName(name) {
    return String(name ?? "")
        .trim()
        .replace(/^ph[-_]?/i, "")
        .replace(/([a-z0-9])([A-Z])/g, "$1-$2")
        .replace(/[_\s]+/g, "-")
        .toLowerCase();
}

function normalizeWeight(weight) {
    const value = String(weight ?? "regular").toLowerCase();
    return WEIGHTS.includes(value) ? value : "regular";
}

export function getPhosphorSvg(name, weight = "regular") {
    const entry = ICONS[normalizeName(name)];
    if(!entry){
        return ICONS.question.regular;
    }

    const preferred = normalizeWeight(weight);
    return entry[preferred]
        ?? entry.regular
        ?? entry.bold
        ?? entry.duotone
        ?? entry.fill
        ?? ICONS.question.regular;
}

export function getPhosphorPath(name, weight = "regular") {
    const svg = getPhosphorSvg(name, weight);
    if(!svg){
        return "";
    }
    const match = svg.match(/<path\s+d="([^"]+)"/);
    return match?.[1] ?? "";
}

export function listPhosphorIconNames() {
    return Object.keys(ICONS).sort();
}

export const phosphorWeights = WEIGHTS;
