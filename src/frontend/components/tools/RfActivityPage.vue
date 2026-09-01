<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <!-- page header -->
            <div class="flex items-center gap-x-2">
                <RouterLink :to="{ name: 'tools' }" class="flex rounded-md p-1.5 text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.08)] hover:text-[var(--ct-text)]" title="Back to Diagnostics">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5">
                        <path fill-rule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clip-rule="evenodd" />
                    </svg>
                </RouterLink>
                <div>
                <div class="text-lg font-bold text-[var(--ct-text)]">Live Activity</div>
                <div class="text-sm text-[var(--ct-dim)]">Watch traffic on your interfaces. Path requests keep a hub busy even when nobody is announcing. Announces appear here as they are heard, including rebroadcasts of destinations you already know.</div>
                </div>
            </div>

            <!-- interfaces -->
            <div class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Interfaces</div>
                <div class="divide-y divide-[var(--ct-border)] text-sm text-[var(--ct-muted)]">
                    <div v-if="interfaces.length === 0" class="p-2.5 text-[var(--ct-dim)]">No interface stats available.</div>
                    <div v-for="iface in interfaces" :key="iface.name" class="flex flex-wrap items-center gap-x-2.5 gap-y-1 p-2.5">
                        <span class="size-2.5 shrink-0 rounded-full" :class="iface.status ? 'bg-[var(--ct-green)]' : 'border border-[var(--ct-dim)]'"></span>
                        <span class="mr-auto font-medium text-[var(--ct-text)]">{{ iface.name }}</span>
                        <span class="text-[var(--ct-dim)]">RX {{ formatBytes(iface.rxb) }}</span>
                        <span class="text-[var(--ct-dim)]">TX {{ formatBytes(iface.txb) }}</span>
                        <span class="text-[var(--ct-dim)]">Announces {{ formatRate(iface.incoming_announce_frequency) }}</span>
                        <span class="text-[var(--ct-dim)]">Path req {{ formatRate(iface.incoming_pr_frequency) }}</span>
                    </div>
                </div>
            </div>

            <!-- announce feed -->
            <div class="ct-card">
                <div class="flex items-center border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">
                    <span class="mr-auto">Announces</span>
                    <span class="text-sm font-normal text-[var(--ct-dim)]">{{ announces.length }} heard since opening</span>
                </div>
                <div class="divide-y divide-[var(--ct-border)] text-sm text-[var(--ct-muted)]">
                    <div v-if="announces.length === 0" class="p-2.5 text-[var(--ct-dim)]">
                        No announces heard since opening this page. A TCP hub can still show RX growth from path requests. Ask a peer to announce, or wait — peers often re-announce only every few hours.
                    </div>
                    <div v-for="announce in announces" :key="announce.key" class="p-2.5">
                        <div class="flex items-center gap-x-2">
                            <span v-if="announce.origin === 'sent'" class="shrink-0 rounded bg-[rgba(0,97,253,0.15)] px-1.5 py-0.5 text-xs font-semibold text-[#7db0ff]">Sent</span>
                            <span v-else-if="announce.rssi != null" class="shrink-0 rounded bg-[rgba(46,231,129,0.15)] px-1.5 py-0.5 text-xs font-semibold text-[var(--ct-green)]">RF</span>
                            <span class="truncate font-medium text-[var(--ct-text)]">{{ announce.display_name ?? "Anonymous" }}</span>
                            <span class="shrink-0 text-xs text-[var(--ct-dim)]">{{ announce.aspect ?? "unknown" }}</span>
                            <span class="ml-auto shrink-0 text-xs text-[var(--ct-dim)]">{{ announce.time }}</span>
                        </div>
                        <div class="ct-hash truncate text-xs text-[var(--ct-dim)]">{{ announce.destination_hash }}</div>
                        <div class="flex gap-x-3 text-xs text-[var(--ct-dim)]">
                            <span v-if="announce.hops != null">{{ announce.hops }} {{ announce.hops === 1 ? "hop" : "hops" }}</span>
                            <span v-if="announce.interface" class="truncate">{{ announce.interface }}</span>
                            <span v-if="announce.rssi != null">RSSI {{ announce.rssi }}dBm</span>
                            <span v-if="announce.snr != null">SNR {{ announce.snr }}dB</span>
                            <span v-if="announce.quality != null">Quality {{ announce.quality }}%</span>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
import WebSocketConnection from "../../js/WebSocketConnection";
import Utils from "../../js/Utils";

export default {
    name: 'RfActivityPage',
    data() {
        return {
            announces: [],
            interfaces: [],
            statsInterval: null,
        };
    },
    mounted() {
        WebSocketConnection.on("message", this.onWebsocketMessage);
        this.getInterfaceStats();
        this.statsInterval = setInterval(this.getInterfaceStats, 2000);
    },
    beforeUnmount() {
        WebSocketConnection.off("message", this.onWebsocketMessage);
        clearInterval(this.statsInterval);
    },
    methods: {
        onWebsocketMessage(message) {
            let json;
            try {
                json = JSON.parse(message.data);
            } catch(e) {
                return;
            }
            if(json.type !== "heard_announce" || !json.announce){
                return;
            }
            this.announces.unshift({
                key: `${json.announce.destination_hash}-${Date.now()}-${this.announces.length}`,
                time: new Date().toLocaleTimeString(),
                ...json.announce,
            });
            // keep the feed bounded so long sessions don't grow memory forever
            if(this.announces.length > 200){
                this.announces.pop();
            }
        },
        async getInterfaceStats() {
            try {
                const response = await window.axios.get("/api/v1/interface-stats");
                this.interfaces = response.data.interface_stats?.interfaces ?? [];
            } catch(e) {
                // do nothing if failed to load interface stats
                console.log(e);
            }
        },
        formatBytes(bytes) {
            return Utils.formatBytes(bytes ?? 0);
        },
        formatRate(hz) {
            const value = Number(hz) || 0;
            if(value <= 0){
                return "0/s";
            }
            if(value < 0.1){
                return "<0.1/s";
            }
            return `${value.toFixed(1)}/s`;
        },
    },
}
</script>
