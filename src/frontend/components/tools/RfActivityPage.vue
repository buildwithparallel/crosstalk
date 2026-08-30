<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <!-- page header -->
            <div>
                <div class="text-lg font-bold text-[var(--ct-text)]">Live Activity</div>
                <div class="text-sm text-[var(--ct-dim)]">Watch announces arrive in real time. Entries with signal readings were heard over radio. Leave this page open to confirm your interfaces are receiving.</div>
            </div>

            <!-- interfaces -->
            <div class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Interfaces</div>
                <div class="divide-y divide-[var(--ct-border)] text-sm text-[var(--ct-muted)]">
                    <div v-if="interfaces.length === 0" class="p-2.5 text-[var(--ct-dim)]">No interface stats available.</div>
                    <div v-for="iface in interfaces" :key="iface.name" class="flex items-center gap-x-2.5 p-2.5">
                        <span class="size-2.5 shrink-0 rounded-full" :class="iface.status ? 'bg-[var(--ct-green)]' : 'border border-[var(--ct-dim)]'"></span>
                        <span class="mr-auto font-medium text-[var(--ct-text)]">{{ iface.name }}</span>
                        <span class="text-[var(--ct-dim)]">RX {{ formatBytes(iface.rxb) }}</span>
                        <span class="text-[var(--ct-dim)]">TX {{ formatBytes(iface.txb) }}</span>
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
                        Nothing heard yet. Announces will appear here as they arrive. Ask a peer to announce, or wait.
                    </div>
                    <div v-for="announce in announces" :key="announce.key" class="p-2.5">
                        <div class="flex items-center gap-x-2">
                            <span v-if="announce.rssi != null" class="shrink-0 rounded bg-[rgba(46,231,129,0.15)] px-1.5 py-0.5 text-xs font-semibold text-[var(--ct-green)]">RF</span>
                            <span class="truncate font-medium text-[var(--ct-text)]">{{ announce.display_name ?? "Anonymous" }}</span>
                            <span class="shrink-0 text-xs text-[var(--ct-dim)]">{{ announce.aspect }}</span>
                            <span class="ml-auto shrink-0 text-xs text-[var(--ct-dim)]">{{ announce.time }}</span>
                        </div>
                        <div class="ct-hash truncate text-xs text-[var(--ct-dim)]">{{ announce.destination_hash }}</div>
                        <div class="flex gap-x-3 text-xs text-[var(--ct-dim)]">
                            <span v-if="announce.hops != null">{{ announce.hops }} {{ announce.hops === 1 ? "hop" : "hops" }}</span>
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
            const json = JSON.parse(message.data);
            if(json.type !== "announce"){
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
    },
}
</script>
