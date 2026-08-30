<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <div>
                <div class="flex flex-wrap items-center gap-x-2 text-xs font-semibold uppercase tracking-wide text-[var(--ct-dim)]">
                    <RouterLink :to="{ name: 'bridge-extensions' }" class="hover:text-[var(--ct-text)]">Bridge Extensions</RouterLink>
                    <span>/</span>
                    <RouterLink :to="{ name: 'bridge-extensions.show', params: { id: resolvedExtension.id } }" class="hover:text-[var(--ct-text)]">{{ resolvedExtension.name }}</RouterLink>
                </div>
                <div class="mt-1 flex flex-wrap items-center gap-2">
                    <div class="text-lg font-bold text-[var(--ct-text)]">{{ role.hardware }}</div>
                    <span class="rounded-full border border-[var(--ct-border)] px-2 py-0.5 text-xs text-[var(--ct-muted)]">{{ role.kind }}</span>
                    <span class="rounded-full border px-2 py-0.5 text-xs" :class="roleTone(role.processRole)">{{ roleLabel(role.processRole) }}</span>
                </div>
                <div class="mt-1 text-sm text-[var(--ct-dim)]">{{ roleDetail }}</div>
            </div>

            <div v-if="error" class="rounded-lg border border-red-400/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
                {{ error }}
            </div>

            <div class="ct-card space-y-3 p-3">
                <div class="font-semibold text-[var(--ct-text)]">Open source software</div>
                <label class="block space-y-1">
                    <span class="text-sm text-[var(--ct-muted)]">Radio software folder</span>
                    <input v-model="repoPath" type="text" class="ct-message-input block w-full rounded-lg border px-2 py-1.5 text-sm" placeholder="/path/to/radio-bridge"/>
                </label>
                <div class="text-xs text-[var(--ct-dim)]">
                    Software {{ repoReady ? "looks ready" : "not found yet" }}. This radio runs as its own program so it stays off Crosstalk's normal connections.
                </div>
                <button type="button" class="ct-secondary-button rounded-lg px-3 py-1.5 text-sm font-semibold" @click="saveSettings">
                    Save settings
                </button>
            </div>

            <div v-if="isReceiveOnly" class="ct-card space-y-3 p-3">
                <div class="text-sm text-[var(--ct-muted)]">
                    <div>{{ processes.ingress.running ? "Listening here" : "Stopped" }}</div>
                    <div v-if="!processes.ingress.running && !announcedRole('ingress')">No receive station on this Crosstalk yet.</div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div class="rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)] px-2.5 py-2">
                        <div class="text-xs text-[var(--ct-dim)]">Messages heard</div>
                        <div class="mt-0.5 text-lg font-semibold text-[var(--ct-text)]">{{ ingressStats.heard }}</div>
                    </div>
                    <div class="rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)] px-2.5 py-2">
                        <div class="text-xs text-[var(--ct-dim)]">Forwarded</div>
                        <div class="mt-0.5 text-lg font-semibold text-[var(--ct-text)]">{{ ingressStats.forwarded }}</div>
                    </div>
                    <div class="rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)] px-2.5 py-2">
                        <div class="text-xs text-[var(--ct-dim)]">Could not decode</div>
                        <div class="mt-0.5 text-lg font-semibold text-[var(--ct-text)]">{{ ingressStats.decode_failed }}</div>
                    </div>
                    <div class="rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)] px-2.5 py-2">
                        <div class="text-xs text-[var(--ct-dim)]">Could not forward</div>
                        <div class="mt-0.5 text-lg font-semibold text-[var(--ct-text)]">{{ ingressStats.inject_failed }}</div>
                    </div>
                </div>
                <div v-if="ingressStats.last_origin" class="text-xs text-[var(--ct-dim)]">
                    Last station {{ ingressStats.last_origin }}
                </div>
                <label class="block space-y-1">
                    <span class="text-sm text-[var(--ct-muted)]">Tuner gain {{ rtlGainLabel }} dB</span>
                    <input v-model.number="rtlGainDb" type="range" min="0" max="49.6" step="0.1" class="w-full accent-[var(--ct-blue)]"/>
                    <span class="text-xs text-[var(--ct-dim)]">Lower if the dongle is next to the transmitter. Higher if you are farther away. Applies the next time you Start.</span>
                </label>
                <div class="flex gap-2">
                    <button type="button" class="ct-brand-button rounded-lg px-3 py-1.5 text-sm font-semibold text-white" :disabled="busy" @click="startRole('ingress')">Start</button>
                    <button type="button" class="ct-secondary-button rounded-lg px-3 py-1.5 text-sm font-semibold" :disabled="busy" @click="stopRole('ingress')">Stop</button>
                </div>
                <p v-if="!processes.ingress.running && ingressErrorLine" class="text-xs text-red-300">{{ ingressErrorLine }}</p>
            </div>

            <div v-else class="ct-card space-y-3 p-3">
                <label class="block space-y-1">
                    <span class="text-sm text-[var(--ct-muted)]">Your callsign</span>
                    <input v-model="callsign" type="text" class="ct-message-input block w-full rounded-lg border px-2 py-1.5 text-sm" placeholder="N0CALL"/>
                </label>
                <div class="space-y-1">
                    <span class="text-sm text-[var(--ct-muted)]">Hermes-Lite 2 address</span>
                    <div class="flex flex-col gap-2 sm:flex-row">
                        <input v-model="hl2Ip" type="text" class="ct-message-input block min-w-0 flex-1 rounded-lg border px-2 py-1.5 text-sm" placeholder="192.168.0.164"/>
                        <button
                            type="button"
                            class="ct-secondary-button rounded-lg px-3 py-1.5 text-sm font-semibold"
                            :disabled="findingRadio"
                            @click="findRadio({ saveIfOne: false })">
                            {{ findingRadio ? "Looking…" : "Find radio" }}
                        </button>
                    </div>
                    <p v-if="hl2FindHint" class="text-xs text-[var(--ct-dim)]">{{ hl2FindHint }}</p>
                    <div v-if="unusedFoundRadios.length" class="flex flex-col gap-1.5">
                        <button
                            v-for="radio in unusedFoundRadios"
                            :key="radio.ip"
                            type="button"
                            class="rounded-lg border border-green-400/40 bg-green-500/10 px-2.5 py-1.5 text-left text-sm text-green-200"
                            @click="useFoundRadio(radio)">
                            Use {{ radio.ip }}
                        </button>
                    </div>
                </div>
                <label class="block space-y-1">
                    <span class="text-sm text-[var(--ct-muted)]">Frequency (MHz)</span>
                    <input v-model.number="frequencyMhz" type="number" min="28.121" max="28.188" step="0.001" class="ct-message-input block w-full rounded-lg border px-2 py-1.5 text-sm"/>
                    <span class="text-xs text-[var(--ct-dim)]">Stay between 28.121 and 28.188 so the signal stays in the legal window.</span>
                </label>
                <label class="block space-y-1">
                    <span class="text-sm text-[var(--ct-muted)]">Transmit power {{ powerPercent }}%</span>
                    <input v-model.number="powerPercent" type="range" min="1" max="100" step="1" class="w-full accent-[var(--ct-blue)]"/>
                    <span class="text-xs text-[var(--ct-dim)]">{{ estimatedPowerLabel }}. Applies the next time you Start.</span>
                </label>
                <div class="space-y-1">
                    <BaseToggle v-model="armTx">
                        Allow this computer to transmit
                    </BaseToggle>
                    <p class="text-xs text-[var(--ct-dim)]">Applies the next time you Start. Saved with the other station settings.</p>
                </div>
                <BaseToggle v-model="allowEnabled">
                    Only let listed people use this station
                </BaseToggle>
                <div v-if="allowEnabled" class="space-y-2">
                    <p class="text-xs text-[var(--ct-dim)]">
                        Enter each person's <span class="text-[var(--ct-text)]">LXMF delivery address</span> (32 hex characters). That is not their identity hash — identity hashes cannot key this station.
                    </p>
                    <div v-if="allowHashes.length" class="flex flex-col gap-1.5">
                        <div
                            v-for="hash in allowHashes"
                            :key="hash"
                            class="flex items-center gap-2 rounded-lg border px-2 py-1.5"
                            :class="hash === justAddedHash
                                ? 'border-green-400/40 bg-green-500/10'
                                : 'border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)]'">
                            <span class="ct-hash min-w-0 flex-1 break-all text-xs">{{ hash }}</span>
                            <span class="shrink-0 text-[10px] font-semibold uppercase tracking-wide text-green-300">Entered</span>
                            <span v-if="hash === localLxmfHash" class="shrink-0 text-[10px] text-[var(--ct-dim)]">this station</span>
                            <button
                                type="button"
                                class="shrink-0 text-xs text-[var(--ct-dim)] hover:text-[var(--ct-text)]"
                                aria-label="Remove delivery address"
                                @click="removeAllowHash(hash)">
                                Remove
                            </button>
                        </div>
                    </div>
                    <div v-else class="rounded-lg border border-dashed border-[var(--ct-border)] px-2 py-2 text-xs text-[var(--ct-dim)]">
                        No delivery addresses entered yet.
                    </div>
                    <div class="flex flex-col gap-2 sm:flex-row">
                        <input
                            v-model="allowHashDraft"
                            type="text"
                            class="ct-message-input block min-w-0 flex-1 rounded-lg border px-2 py-1.5 font-mono text-xs"
                            placeholder="Paste an LXMF delivery address"
                            @keydown.enter.prevent="addAllowHashFromDraft"/>
                        <button type="button" class="ct-secondary-button rounded-lg px-3 py-1.5 text-sm font-semibold" @click="addAllowHashFromDraft">
                            Enter
                        </button>
                    </div>
                    <button type="button" class="ct-secondary-button rounded-lg px-3 py-1.5 text-sm font-semibold" @click="addThisStation">
                        Enter this station's delivery address
                    </button>
                    <p v-if="allowListHint" class="text-xs text-[var(--ct-muted)]">{{ allowListHint }}</p>
                </div>
                <div class="text-sm text-[var(--ct-muted)]">
                    <div>{{ processes.txbridge.running ? (snapshot.armed ? "Running here, allowed to transmit" : "Running here, transmit off") : "Stopped" }}</div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div class="rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)] px-2.5 py-2">
                        <div class="text-xs text-[var(--ct-dim)]">Messages received</div>
                        <div class="mt-0.5 text-lg font-semibold text-[var(--ct-text)]">{{ txbridgeStats.received }}</div>
                    </div>
                    <div class="rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)] px-2.5 py-2">
                        <div class="text-xs text-[var(--ct-dim)]">On the air</div>
                        <div class="mt-0.5 text-lg font-semibold text-[var(--ct-text)]">{{ txbridgeStats.on_air }}</div>
                    </div>
                    <div class="rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)] px-2.5 py-2">
                        <div class="text-xs text-[var(--ct-dim)]">Held (transmit off)</div>
                        <div class="mt-0.5 text-lg font-semibold text-[var(--ct-text)]">{{ txbridgeStats.held }}</div>
                    </div>
                    <div class="rounded-lg border border-[var(--ct-border)] bg-[rgba(255,255,255,0.03)] px-2.5 py-2">
                        <div class="text-xs text-[var(--ct-dim)]">Rejected</div>
                        <div class="mt-0.5 text-lg font-semibold text-[var(--ct-text)]">{{ txbridgeStats.rejected }}</div>
                    </div>
                </div>
                <div v-if="txbridgeStats.tx_failed" class="text-xs text-red-300">
                    Could not transmit {{ txbridgeStats.tx_failed }}
                </div>
                <div v-if="txbridgeStats.last_bytes" class="text-xs text-[var(--ct-dim)]">
                    Last message {{ txbridgeStats.last_bytes }} bytes
                </div>
                <div class="flex gap-2">
                    <button type="button" class="ct-brand-button rounded-lg px-3 py-1.5 text-sm font-semibold text-white" :disabled="busy" @click="startRole('txbridge')">Start</button>
                    <button type="button" class="ct-secondary-button rounded-lg px-3 py-1.5 text-sm font-semibold" :disabled="busy" @click="stopRole('txbridge')">Stop</button>
                </div>
                <p v-if="!processes.txbridge.running && txbridgeErrorLine" class="text-xs text-red-300">{{ txbridgeErrorLine }}</p>
            </div>

        </div>
    </div>
</template>

<script>
import BaseToggle from "../base/BaseToggle.vue";
import { LAST_RESORT_HOP } from "../../js/bridgeExtensions";

const RTL_TUNER_GAINS_DB = [
    0.0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7, 16.6, 19.7, 20.7,
    22.9, 25.4, 28.0, 29.7, 32.8, 33.8, 36.4, 37.2, 38.6, 40.2, 42.1, 43.4,
    43.9, 44.5, 48.0, 49.6,
];

function snapRtlGainDb(value) {
    const gain = Number(value);
    if (!Number.isFinite(gain)) {
        return 20.7;
    }
    return RTL_TUNER_GAINS_DB.reduce((best, step) => (
        Math.abs(step - gain) < Math.abs(best - gain) ? step : best
    ));
}

export default {
    name: "HfBridgesPage",
    components: {
        BaseToggle,
    },
    props: {
        extension: {
            type: Object,
            default: null,
        },
        role: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            repoPath: "",
            callsign: "",
            hl2Ip: "",
            findingRadio: false,
            foundRadios: [],
            hl2FindHint: "",
            frequencyMhz: 28.124,
            powerPercent: 10,
            rtlGainDb: 20.7,
            allowEnabled: false,
            allowListText: "",
            allowHashDraft: "",
            allowListHint: "",
            justAddedHash: "",
            localLxmfHash: "",
            localIdentityHash: "",
            settingsHydrated: false,
            armTx: false,
            repoReady: false,
            announced: [],
            snapshot: { armed: false },
            processes: {
                txbridge: { running: false, pid: null, log: "", stats: null },
                ingress: { running: false, pid: null, log: "", stats: null },
            },
            busy: false,
            error: "",
            refreshTimer: null,
        };
    },
    mounted() {
        this.refresh();
        this.refreshTimer = setInterval(this.refresh, 4000);
    },
    beforeUnmount() {
        clearInterval(this.refreshTimer);
    },
    watch: {
        armTx(value) {
            if (!this.settingsHydrated || this.busy) {
                return;
            }
            window.axios.patch("/api/v1/config", { hfbridge_arm_tx: value }).catch((error) => {
                this.error = error.response?.data?.message || "Failed to save settings";
            });
        },
    },
    computed: {
        resolvedExtension() {
            return this.extension || LAST_RESORT_HOP;
        },
        isReceiveOnly() {
            return this.role.processRole === "ingress";
        },
        roleDetail() {
            if (this.isReceiveOnly) {
                return "Plug an RTL-SDR dongle in over USB. This computer only listens; it never transmits, so it does not need a license. That is useful because you can receive on the cheap, on the other side of the conversation, and turn what you hear into a normal Crosstalk message. Keep this listen path off the sender's network, or the message never uses the radio.";
            }
            return "This is the station that can send a message over the radio. Sending requires a US Technician-class amateur license or higher, and your callsign on the message. Technician is enough at this frequency. That is useful because you can send when mesh, internet, and satellite cannot reach someone — without adding the radio as a normal Crosstalk connection.";
        },
        ingressStats() {
            const fromApi = this.processes.ingress.stats;
            if (fromApi && typeof fromApi.heard === "number") {
                return fromApi;
            }
            return this.parseIngressStats(this.processes.ingress.log);
        },
        ingressErrorLine() {
            return this.lastErrorLine(this.processes.ingress.log, "ingress-stats");
        },
        txbridgeStats() {
            const fromApi = this.processes.txbridge.stats;
            if (fromApi && typeof fromApi.received === "number") {
                return fromApi;
            }
            return this.parseTxbridgeStats(this.processes.txbridge.log);
        },
        txbridgeErrorLine() {
            return this.lastErrorLine(this.processes.txbridge.log, "txbridge-stats");
        },
        estimatedPowerLabel() {
            const percent = Math.max(1, Math.min(100, Number(this.powerPercent) || 10));
            const watts = 5 * (percent / 100);
            let amount;
            if (watts < 1) {
                const milliwatts = watts * 1000;
                const shown = milliwatts >= 10 ? Math.round(milliwatts) : Number(milliwatts.toPrecision(2));
                amount = `${shown} mW`;
            } else {
                amount = `${Number(watts.toPrecision(2))} W`;
            }
            return `About ${amount} at this setting (rough). 100% is about 5 W`;
        },
        frequencyHz() {
            const mhz = Number(this.frequencyMhz);
            if (!Number.isFinite(mhz)) {
                return 28124000;
            }
            return Math.round(mhz * 1e6);
        },
        allowHashes() {
            return this.parseAllowHashes(this.allowListText);
        },
        unusedFoundRadios() {
            const current = (this.hl2Ip || "").trim();
            return this.foundRadios.filter((radio) => radio.ip !== current);
        },
        snappedRtlGainDb() {
            return snapRtlGainDb(this.rtlGainDb);
        },
        rtlGainLabel() {
            const snapped = this.snappedRtlGainDb;
            return Number.isInteger(snapped) ? String(snapped) : snapped.toFixed(1);
        },
    },
    methods: {
        announcedRole(role) {
            return this.announced.find((item) => item.role === role) || null;
        },
        lastErrorLine(log, skipPrefix) {
            const lines = (log || "").split("\n").map((line) => line.trim()).filter(Boolean);
            for (let index = lines.length - 1; index >= 0; index -= 1) {
                const line = lines[index];
                if (skipPrefix && line.includes(skipPrefix)) {
                    continue;
                }
                if (/TCPInterface|Bad file descriptor|\[Warning\]|\[Notice\]/i.test(line)) {
                    continue;
                }
                if (/transmit failed|overrun|i2c|rtl|usb|exited immediately|not found/i.test(line)) {
                    return line;
                }
            }
            return "";
        },
        parseTxbridgeStats(log) {
            const pattern = /txbridge-stats received=(\d+) on_air=(\d+) held=(\d+) rejected=(\d+) tx_failed=(\d+)(?: last_bytes=(\d+))?/g;
            let found = null;
            let match = pattern.exec(log || "");
            while (match) {
                found = match;
                match = pattern.exec(log || "");
            }
            if (!found) {
                return {
                    received: 0,
                    on_air: 0,
                    held: 0,
                    rejected: 0,
                    tx_failed: 0,
                    last_bytes: 0,
                };
            }
            return {
                received: Number(found[1]),
                on_air: Number(found[2]),
                held: Number(found[3]),
                rejected: Number(found[4]),
                tx_failed: Number(found[5]),
                last_bytes: Number(found[6] || 0),
            };
        },
        parseIngressStats(log) {
            const pattern = /ingress-stats heard=(\d+) forwarded=(\d+) decode_failed=(\d+) inject_failed=(\d+)(?: last=(\S+))?/g;
            let found = null;
            let match = pattern.exec(log || "");
            while (match) {
                found = match;
                match = pattern.exec(log || "");
            }
            if (!found) {
                return {
                    heard: 0,
                    forwarded: 0,
                    decode_failed: 0,
                    inject_failed: 0,
                    last_origin: null,
                };
            }
            return {
                heard: Number(found[1]),
                forwarded: Number(found[2]),
                decode_failed: Number(found[3]),
                inject_failed: Number(found[4]),
                last_origin: found[5] || null,
            };
        },
        roleLabel(role) {
            const announced = this.announcedRole(role);
            if (this.processes[role].running) {
                return "running here";
            }
            if (this.role.processRole === role) {
                return "stopped";
            }
            if (announced?.heard_recently) {
                return "heard";
            }
            if (announced) {
                return "last heard earlier";
            }
            return "not seen";
        },
        roleTone(role) {
            const label = this.roleLabel(role);
            if (label === "running here" || label === "heard") {
                return "border-green-400/40 bg-green-500/10 text-green-200";
            }
            if (label === "last heard earlier") {
                return "border-amber-400/40 bg-amber-500/10 text-amber-200";
            }
            return "border-[var(--ct-border)] text-[var(--ct-dim)]";
        },
        applyStatus(data) {
            const justHydrated = !this.settingsHydrated && !!data.settings;
            this.repoReady = !!data.repo_ready;
            this.announced = data.announced || [];
            this.snapshot = data.processes || { armed: false };
            this.processes = {
                txbridge: data.processes?.txbridge || this.processes.txbridge,
                ingress: data.processes?.ingress || this.processes.ingress,
            };
            if (!this.settingsHydrated && data.settings) {
                this.repoPath = data.settings.repo_path || this.repoPath;
                this.callsign = data.settings.callsign || this.callsign;
                this.hl2Ip = data.settings.hl2_ip || this.hl2Ip;
                if (data.settings.frequency_hz) {
                    this.frequencyMhz = Number((data.settings.frequency_hz / 1e6).toFixed(3));
                }
                if (typeof data.settings.power_percent === "number") {
                    this.powerPercent = data.settings.power_percent;
                }
                if (typeof data.settings.rtl_gain_db === "number") {
                    this.rtlGainDb = data.settings.rtl_gain_db;
                }
                this.allowEnabled = !!data.settings.allowlist_enabled;
                if (typeof data.settings.allowlist === "string") {
                    this.allowListText = data.settings.allowlist;
                }
                this.armTx = !!data.settings.arm_tx;
                this.localLxmfHash = data.settings.lxmf_address_hash || "";
                this.localIdentityHash = data.settings.identity_hash || "";
                this.settingsHydrated = true;
            }
            if (!this.repoPath && data.default_repo_path) {
                this.repoPath = data.default_repo_path;
            }
            if (data.settings?.lxmf_address_hash) {
                this.localLxmfHash = data.settings.lxmf_address_hash;
            }
            if (data.settings?.identity_hash) {
                this.localIdentityHash = data.settings.identity_hash;
            }
            if (justHydrated && !this.isReceiveOnly) {
                this.findRadio({ silent: true, saveIfOne: false });
            }
        },
        async refresh() {
            try {
                const response = await window.axios.get("/api/v1/hf-bridges");
                this.applyStatus(response.data);
                this.error = "";
            } catch (error) {
                this.error = error.response?.data?.message || "This radio path is not available. Restart Crosstalk after this update.";
            }
        },
        parseAllowHashes(text) {
            const found = [];
            const seen = new Set();
            for (const raw of (text || "").replaceAll(",", " ").split(/\s+/)) {
                const hash = this.normalizeDeliveryAddress(raw);
                if (!hash || seen.has(hash)) {
                    continue;
                }
                seen.add(hash);
                found.push(hash);
            }
            return found;
        },
        normalizeDeliveryAddress(value) {
            let hash = (value || "").trim().toLowerCase().replace(/^lxmf@/, "");
            hash = [...hash].filter((ch) => "0123456789abcdef".includes(ch)).join("");
            if (hash.length !== 32) {
                return "";
            }
            return hash;
        },
        setAllowHashes(hashes) {
            this.allowListText = hashes.join("\n");
        },
        async addAllowHash(hash, { alreadyMessage, addedMessage } = {}) {
            const normalized = this.normalizeDeliveryAddress(hash);
            if (!normalized) {
                this.allowListHint = "Need a 32-character LXMF delivery address, not an identity hash.";
                return false;
            }
            if (normalized === (this.localIdentityHash || "").toLowerCase()) {
                this.allowListHint = "That is this station's identity hash. Enter the LXMF delivery address instead.";
                return false;
            }
            const hashes = [...this.allowHashes];
            if (hashes.includes(normalized)) {
                this.justAddedHash = normalized;
                this.allowListHint = alreadyMessage || "Already entered.";
                this.allowHashDraft = "";
                return true;
            }
            hashes.push(normalized);
            this.setAllowHashes(hashes);
            this.justAddedHash = normalized;
            this.allowHashDraft = "";
            this.allowListHint = addedMessage || "Entered. Stop and Start for this list to apply.";
            await this.saveSettings();
            return true;
        },
        async addAllowHashFromDraft() {
            await this.addAllowHash(this.allowHashDraft);
        },
        async addThisStation() {
            if (!this.localLxmfHash) {
                this.allowListHint = "This station does not have a delivery address yet.";
                return;
            }
            await this.addAllowHash(this.localLxmfHash, {
                alreadyMessage: "This station's delivery address is already entered.",
                addedMessage: "This station's delivery address is entered. Stop and Start for it to apply.",
            });
        },
        async removeAllowHash(hash) {
            this.setAllowHashes(this.allowHashes.filter((item) => item !== hash));
            if (this.justAddedHash === hash) {
                this.justAddedHash = "";
            }
            this.allowListHint = "Removed. Stop and Start for this list to apply.";
            await this.saveSettings();
        },
        async findRadio({ silent = false, saveIfOne = false } = {}) {
            if (this.findingRadio) {
                return;
            }
            this.findingRadio = true;
            if (!silent) {
                this.hl2FindHint = "";
            }
            try {
                const response = await window.axios.post("/api/v1/hf-bridges/discover");
                const radios = response.data.radios || [];
                this.foundRadios = radios;
                if (!radios.length) {
                    this.hl2FindHint = silent
                        ? ""
                        : "No radio answered. This computer needs to be on the same network as the Hermes.";
                    return;
                }
                const current = (this.hl2Ip || "").trim();
                if (!current && radios.length === 1) {
                    this.hl2Ip = radios[0].ip;
                    this.hl2FindHint = `Found ${radios[0].ip}. Save or Start to use it.`;
                    if (saveIfOne) {
                        await this.saveSettings();
                    }
                    return;
                }
                if (radios.some((radio) => radio.ip === current) && radios.length === 1) {
                    this.hl2FindHint = "This address answered.";
                    return;
                }
                if (radios.some((radio) => radio.ip === current)) {
                    this.hl2FindHint = "This address answered. Other radios on this network are listed below.";
                    return;
                }
                this.hl2FindHint = radios.length === 1
                    ? `Found ${radios[0].ip}.`
                    : `Found ${radios.length} radios. Pick the one to use.`;
            } catch (error) {
                this.foundRadios = [];
                this.hl2FindHint = error.response?.data?.message || "Could not look for a radio.";
            } finally {
                this.findingRadio = false;
            }
        },
        async useFoundRadio(radio) {
            this.hl2Ip = radio.ip;
            this.hl2FindHint = `Using ${radio.ip}. Stop and Start if Hermes is already running.`;
            await this.saveSettings();
        },
        async saveSettings() {
            this.busy = true;
            try {
                await window.axios.patch("/api/v1/config", {
                    hfbridge_repo_path: this.repoPath,
                    hfbridge_callsign: this.callsign,
                    hfbridge_hl2_ip: this.hl2Ip,
                    hfbridge_frequency_hz: this.frequencyHz,
                    hfbridge_power_percent: Math.max(1, Math.min(100, Number(this.powerPercent) || 10)),
                    hfbridge_rtl_gain_db: this.snappedRtlGainDb,
                    hfbridge_allowlist_enabled: this.allowEnabled,
                    hfbridge_allowlist: this.allowListText,
                    hfbridge_arm_tx: this.armTx,
                });
                await this.refresh();
                return true;
            } catch (error) {
                this.error = error.response?.data?.message || "Failed to save settings";
                return false;
            } finally {
                this.busy = false;
            }
        },
        async startRole(role) {
            this.busy = true;
            try {
                const saved = await this.saveSettings();
                if (!saved) {
                    return;
                }
                const response = await window.axios.post("/api/v1/hf-bridges/start", {
                    role,
                    arm_tx: role === "txbridge" ? this.armTx : false,
                });
                this.applyStatus(response.data);
            } catch (error) {
                this.error = error.response?.data?.message || `Failed to start ${role}`;
            } finally {
                this.busy = false;
            }
        },
        async stopRole(role) {
            this.busy = true;
            try {
                const response = await window.axios.post("/api/v1/hf-bridges/stop", { role });
                this.applyStatus(response.data);
            } catch (error) {
                this.error = error.response?.data?.message || `Failed to stop ${role}`;
            } finally {
                this.busy = false;
            }
        },
    },
};
</script>
