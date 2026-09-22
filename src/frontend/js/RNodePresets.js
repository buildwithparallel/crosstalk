/**
 * Starting LoRa presets for RNode interfaces.
 *
 * These are common community starters for regional ISM bands, not legal
 * requirements and not universal radio defaults. Peers on a mesh must still
 * match frequency, bandwidth, spreading factor, and coding rate exactly.
 * Transmit power may differ per device within hardware and local rules.
 */

/** @typedef {{ id: string, label: string, description: string, frequency: number, bandwidth: number, spreadingfactor: number, codingrate: number, txpower: number }} RNodePreset */

/** @type {RNodePreset[]} */
export const RNODE_REGIONAL_PRESETS = [
    {
        id: "us-915",
        label: "US 915 MHz (starter)",
        description: "Common US ISM starting point around 915 MHz. Match your mesh if it uses a different center frequency.",
        frequency: 915_000_000,
        bandwidth: 125_000,
        spreadingfactor: 7,
        codingrate: 5,
        txpower: 22,
    },
    {
        id: "eu-868",
        label: "EU 868 MHz (starter)",
        description: "Common EU ISM starting point at 867.2 MHz from Reticulum examples. Confirm local rules and mesh settings.",
        frequency: 867_200_000,
        bandwidth: 125_000,
        spreadingfactor: 8,
        codingrate: 5,
        txpower: 14,
    },
    {
        id: "au-915",
        label: "AU/NZ 915 MHz (starter)",
        description: "Common starting point in the AU/NZ 915 MHz ISM band. Confirm local rules and mesh settings.",
        frequency: 915_000_000,
        bandwidth: 125_000,
        spreadingfactor: 7,
        codingrate: 5,
        txpower: 22,
    },
    {
        id: "ism-433",
        label: "433 MHz (starter)",
        description: "For 433 MHz-capable RNodes where that band is allowed. Not all Heltec boards support this.",
        frequency: 433_000_000,
        bandwidth: 125_000,
        spreadingfactor: 7,
        codingrate: 5,
        txpower: 12,
    },
];

/**
 * Find a preset whose radio parameters match the given values.
 * @param {{ frequency?: number|null, bandwidth?: number|null, spreadingfactor?: number|null, codingrate?: number|null, txpower?: number|null }} params
 * @returns {RNodePreset|null}
 */
export function findMatchingRNodePreset(params) {
    const frequency = Number(params?.frequency);
    const bandwidth = Number(params?.bandwidth);
    const spreadingfactor = Number(params?.spreadingfactor);
    const codingrate = Number(params?.codingrate);
    const txpower = Number(params?.txpower);

    return RNODE_REGIONAL_PRESETS.find((preset) => (
        preset.frequency === frequency
        && preset.bandwidth === bandwidth
        && preset.spreadingfactor === spreadingfactor
        && preset.codingrate === codingrate
        && preset.txpower === txpower
    )) ?? null;
}

/**
 * Split a frequency in Hz into GHz / MHz / kHz form fields.
 * @param {number} frequencyHz
 * @returns {{ ghz: number, mhz: number, khz: number }}
 */
export function splitFrequencyHz(frequencyHz) {
    const hz = Math.max(0, Math.floor(Number(frequencyHz) || 0));
    return {
        ghz: Math.floor(hz / 1e9),
        mhz: Math.floor((hz % 1e9) / 1e6),
        khz: Math.floor((hz % 1e6) / 1e3),
    };
}

export default {
    RNODE_REGIONAL_PRESETS,
    findMatchingRNodePreset,
    splitFrequencyHz,
};
