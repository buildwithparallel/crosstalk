<template>
    <div class="flex flex-col flex-1 min-w-full sm:min-w-[500px] overflow-hidden bg-[rgba(5,6,10,0.86)] text-[var(--ct-text)]">
        <div class="border-b border-blue-400/25 bg-blue-500/10 px-3 py-3">
            <div class="flex items-start gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="mt-0.5 h-6 w-6 shrink-0 text-blue-300">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 21 12 3m0 0 3.75 18M12 3v18M5.25 9.75h13.5M3.75 15.75h16.5" />
                </svg>
                <div class="max-w-4xl">
                    <h1 class="font-semibold text-blue-100">Nearby Reticulum infrastructure</h1>
                    <p class="mt-1 text-sm leading-5 text-[var(--ct-muted)]">
                        Some Reticulum devices exist only to relay network traffic. They do not have an LXMF delivery address, so you cannot message them and they do not appear in Contacts. Crosstalk classifies these relay-only devices—including routers, transport nodes, gateways and radio access points—as infrastructure. You can observe them here.
                    </p>
                    <p class="mt-1 text-sm leading-5 text-[var(--ct-muted)]">
                        This view shows which infrastructure devices are visible to Crosstalk, how many hops away they are, their transport and radio details, and when they were last heard. Devices that can receive LXMF messages appear in Contacts instead.
                    </p>
                </div>
            </div>
        </div>

        <div class="flex flex-wrap items-center gap-2 p-2 border-b border-[var(--ct-border)] bg-[rgba(9,9,9,0.72)]">
            <div class="min-w-56 flex-1">
                <input
                    v-model="searchTerm"
                    type="text"
                    :placeholder="`Search ${discoveredInterfaces.length} discovered interfaces...`"
                    class="w-full rounded-lg border border-[var(--ct-border-strong)] bg-[rgba(255,255,255,0.05)] p-2.5 text-sm text-[var(--ct-text)] focus:border-blue-500 focus:ring-blue-500"
                >
            </div>
            <button @click="loadInfrastructure" type="button" class="ct-secondary-button rounded-md px-3 py-2 text-sm font-semibold">
                Refresh
            </button>
        </div>

        <div class="flex flex-wrap gap-x-5 gap-y-1 border-b border-[var(--ct-border)] px-3 py-2 text-sm text-[var(--ct-muted)]">
            <span><span class="font-semibold text-[var(--ct-text)]">{{ availableCount }}</span> available</span>
            <span><span class="font-semibold text-[var(--ct-text)]">{{ transportCount }}</span> transports</span>
            <span><span class="font-semibold text-[var(--ct-text)]">{{ discoveredInterfaces.length }}</span> remembered</span>
            <span class="text-[var(--ct-dim)]">Entries become unknown after 24 hours and expire after 7 days.</span>
        </div>

        <div class="h-full overflow-y-auto">
            <div v-if="filteredInterfaces.length" class="grid grid-cols-1 gap-2 p-2 xl:grid-cols-2">
                <article v-for="iface in filteredInterfaces" :key="iface.discovery_hash" class="ct-elevated-surface overflow-hidden rounded-lg border border-[var(--ct-border)]">
                    <div class="flex items-start gap-3 p-3">
                        <div class="relative shrink-0">
                            <img
                                :src="infrastructureIconDataUri(iface)"
                                :alt="`${friendlyType(iface.type)} icon`"
                                class="size-11 rounded-xl border border-white/15 shadow-lg"
                            >
                            <span class="absolute -bottom-1 -right-1 h-3 w-3 rounded-full ring-2 ring-[#11131c]" :class="statusDotClass(iface.status)"></span>
                        </div>
                        <div class="min-w-0 flex-1">
                            <div class="flex flex-wrap items-center gap-2">
                                <h2 class="break-all font-semibold text-[var(--ct-text)]">{{ iface.name || "Unnamed infrastructure" }}</h2>
                                <span v-if="iface.transport" class="rounded-full border border-blue-400/40 bg-blue-500/15 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-blue-200">Transport</span>
                                <span class="rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide" :class="statusBadgeClass(iface.status)">{{ iface.status }}</span>
                            </div>
                            <div class="mt-0.5 text-sm text-[var(--ct-muted)]">{{ friendlyType(iface.type) }} · {{ formatHops(iface.hops) }}</div>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-px border-y border-[var(--ct-border)] bg-[var(--ct-border)] text-sm sm:grid-cols-4">
                        <div class="bg-[rgba(9,9,9,0.82)] p-2">
                            <div class="text-[11px] uppercase tracking-wide text-[var(--ct-dim)]">Last heard</div>
                            <div>{{ formatSecondsAgo(iface.last_heard) }}</div>
                        </div>
                        <div class="bg-[rgba(9,9,9,0.82)] p-2">
                            <div class="text-[11px] uppercase tracking-wide text-[var(--ct-dim)]">First seen</div>
                            <div>{{ formatSecondsAgo(iface.discovered) }}</div>
                        </div>
                        <div class="bg-[rgba(9,9,9,0.82)] p-2">
                            <div class="text-[11px] uppercase tracking-wide text-[var(--ct-dim)]">Heard</div>
                            <div>{{ (iface.heard_count ?? 0) + 1 }} {{ (iface.heard_count ?? 0) === 0 ? "time" : "times" }}</div>
                        </div>
                        <div class="bg-[rgba(9,9,9,0.82)] p-2">
                            <div class="text-[11px] uppercase tracking-wide text-[var(--ct-dim)]">Stamp value</div>
                            <div>{{ iface.value ?? "Unknown" }}</div>
                        </div>
                    </div>

                    <div v-if="hasRadioDetails(iface)" class="flex flex-wrap gap-x-4 gap-y-1 border-b border-[var(--ct-border)] px-3 py-2 text-sm">
                        <span v-if="iface.frequency"><span class="text-[var(--ct-dim)]">Frequency:</span> {{ formatFrequency(iface.frequency) }}</span>
                        <span v-if="iface.bandwidth"><span class="text-[var(--ct-dim)]">Bandwidth:</span> {{ formatFrequency(iface.bandwidth) }}</span>
                        <span v-if="iface.sf"><span class="text-[var(--ct-dim)]">SF:</span> {{ iface.sf }}</span>
                        <span v-if="iface.cr"><span class="text-[var(--ct-dim)]">CR:</span> 4/{{ iface.cr }}</span>
                        <span v-if="iface.modulation"><span class="text-[var(--ct-dim)]">Modulation:</span> {{ iface.modulation }}</span>
                    </div>

                    <div class="space-y-2 p-3 text-sm">
                        <div v-if="iface.destination_hash" class="flex items-start gap-2">
                            <div class="min-w-0 flex-1">
                                <div class="text-[11px] uppercase tracking-wide text-[var(--ct-dim)]">Discovery destination</div>
                                <div class="ct-mono break-all text-[11px] text-[var(--ct-muted)]">{{ iface.destination_hash }}</div>
                            </div>
                            <CopyButton :value="iface.destination_hash" label="Discovery Destination"/>
                        </div>
                        <div v-if="iface.transport_id" class="flex items-start gap-2">
                            <div class="min-w-0 flex-1">
                                <div class="text-[11px] uppercase tracking-wide text-[var(--ct-dim)]">Transport identity</div>
                                <div class="ct-mono break-all text-[11px] text-[var(--ct-muted)]">{{ iface.transport_id }}</div>
                            </div>
                            <CopyButton :value="iface.transport_id" label="Transport Identity"/>
                        </div>
                        <div v-if="iface.reachable_on" class="text-[var(--ct-muted)]">
                            <span class="text-[var(--ct-dim)]">Reachable at:</span> {{ iface.reachable_on }}<span v-if="iface.port">:{{ iface.port }}</span>
                        </div>
                        <div v-if="hasLocation(iface)" class="text-[var(--ct-muted)]">
                            <span class="text-[var(--ct-dim)]">Advertised location:</span>
                            {{ Number(iface.latitude).toFixed(5) }}, {{ Number(iface.longitude).toFixed(5) }}<span v-if="iface.height != null"> · {{ iface.height }} m</span>
                        </div>
                    </div>
                </article>
            </div>

            <div v-else class="flex h-full items-center justify-center p-6 text-center">
                <div class="max-w-md">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="mx-auto mb-2 h-9 w-9 text-[var(--ct-muted)]">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 21 12 3m0 0 3.75 18M12 3v18M5.25 9.75h13.5M3.75 15.75h16.5" />
                    </svg>
                    <div class="font-semibold">No infrastructure discovered</div>
                    <div class="mt-1 text-sm text-[var(--ct-muted)]">Crosstalk is listening for signed Reticulum interface advertisements. A newly booted RTNode normally advertises after about one minute.</div>
                    <button @click="loadInfrastructure" type="button" class="ct-secondary-button mt-3 rounded-md px-3 py-2 text-sm font-semibold">Check again</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Utils from "../../js/Utils";
import { infrastructureIconDataUri } from "../../js/InfrastructureIcons";
import CopyButton from "../CopyButton.vue";

export default {
    name: "InfrastructurePage",
    components: { CopyButton },
    data() {
        return {
            searchTerm: "",
            discoveredInterfaces: [],
            refreshInterval: null,
        };
    },
    mounted() {
        this.loadInfrastructure();
        this.refreshInterval = setInterval(this.loadInfrastructure, 10000);
    },
    beforeUnmount() {
        clearInterval(this.refreshInterval);
    },
    methods: {
        infrastructureIconDataUri,
        async loadInfrastructure() {
            try {
                const response = await window.axios.get("/api/v1/discovered-interfaces");
                this.discoveredInterfaces = response.data.discovered_interfaces ?? [];
            } catch(e) {
                console.log(e);
            }
        },
        friendlyType(type) {
            return type?.replace("Interface", " Interface") ?? "Unknown interface";
        },
        formatHops(hops) {
            if(hops == null) return "Unknown distance";
            return `${hops} ${hops === 1 ? "hop" : "hops"} away`;
        },
        formatSecondsAgo(timestamp) {
            return timestamp == null ? "Unknown" : Utils.formatSecondsAgo(timestamp);
        },
        formatFrequency(hz) {
            return Utils.formatFrequency(hz);
        },
        hasRadioDetails(iface) {
            return iface.frequency || iface.bandwidth || iface.sf || iface.cr || iface.modulation;
        },
        hasLocation(iface) {
            return iface.latitude != null && iface.longitude != null;
        },
        statusDotClass(status) {
            if(status === "available") return "bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.7)]";
            if(status === "unknown") return "bg-amber-400";
            return "bg-zinc-500";
        },
        statusBadgeClass(status) {
            if(status === "available") return "border-emerald-400/40 bg-emerald-500/15 text-emerald-200";
            if(status === "unknown") return "border-amber-400/40 bg-amber-500/15 text-amber-200";
            return "border-zinc-500/40 bg-zinc-500/15 text-zinc-300";
        },
    },
    computed: {
        availableCount() {
            return this.discoveredInterfaces.filter((iface) => iface.status === "available").length;
        },
        transportCount() {
            return this.discoveredInterfaces.filter((iface) => iface.transport).length;
        },
        filteredInterfaces() {
            const search = this.searchTerm.trim().toLowerCase();
            return this.discoveredInterfaces.filter((iface) => {
                if(!search) return true;
                return [iface.name, iface.type, iface.transport_id, iface.network_id, iface.destination_hash, iface.discovery_hash, iface.reachable_on]
                    .some((value) => value?.toString().toLowerCase().includes(search));
            });
        },
    },
};
</script>
