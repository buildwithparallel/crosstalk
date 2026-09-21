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
                <div class="text-lg font-bold text-[var(--ct-text)]">Propagation Sync</div>
                <div class="text-sm text-[var(--ct-dim)]">Health of message syncing with your preferred propagation node, which stores messages for you while you are offline.</div>
                </div>
            </div>

            <!-- health card -->
            <div class="ct-card">
                <div class="flex items-center border-b border-[var(--ct-border)] p-2.5">
                    <span class="mr-auto font-semibold text-[var(--ct-text)]">Status</span>
                    <button @click="syncNow" type="button" class="ct-brand-button rounded-lg px-2.5 py-1.5 text-sm font-semibold">Sync Now</button>
                </div>
                <div class="divide-y divide-[var(--ct-border)] text-sm text-[var(--ct-muted)]">

                    <div v-if="!preferredNode" class="p-2.5">
                        No preferred propagation node is configured. Set one in Settings, or browse propagation nodes to pick one.
                    </div>

                    <template v-else>
                        <div class="flex p-2.5">
                            <span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Preferred Node</span>
                            <span><span v-if="nodeDisplayName">{{ nodeDisplayName }} </span><span class="ct-hash break-all">{{ preferredNode }}</span></span>
                        </div>
                        <div class="flex p-2.5">
                            <span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Path to Node</span>
                            <span>{{ nodePath === null ? "checking..." : (nodePath.path ? `${nodePath.path.hops} ${nodePath.path.hops === 1 ? "hop" : "hops"} via ${nodePath.path.next_hop_interface}` : "no path known") }}</span>
                        </div>
                        <div class="flex p-2.5">
                            <span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Sync State</span>
                            <span>{{ status?.state ?? "unknown" }}<span v-if="status && status.state !== 'idle' && status.progress > 0"> ({{ status.progress.toFixed(0) }}%)</span></span>
                        </div>
                        <div class="flex p-2.5">
                            <span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Last Synced</span>
                            <span>{{ lastSyncedText }}</span>
                        </div>
                        <div class="flex p-2.5">
                            <span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Messages Last Sync</span>
                            <span>{{ status?.messages_received ?? "none" }}</span>
                        </div>
                        <div class="flex p-2.5">
                            <span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Auto Sync</span>
                            <span>{{ autoSyncText }}<span v-if="nextSyncText">, next {{ nextSyncText }}</span></span>
                        </div>
                    </template>

                </div>
            </div>

        </div>
    </div>
</template>

<script>
import Utils from "../../js/Utils";
import DialogUtils from "../../js/DialogUtils";

export default {
    name: 'PropagationHealthPage',
    data() {
        return {
            config: null,
            status: null,
            nodePath: null,
            nodeDisplayName: null,
            statusInterval: null,
        };
    },
    computed: {
        preferredNode() {
            return this.config?.lxmf_preferred_propagation_node_destination_hash;
        },
        lastSyncedText() {
            const lastSyncedAt = this.config?.lxmf_preferred_propagation_node_last_synced_at;
            return lastSyncedAt ? Utils.formatSecondsAgo(lastSyncedAt) : "never";
        },
        autoSyncText() {
            const seconds = parseInt(this.config?.lxmf_preferred_propagation_node_auto_sync_interval_seconds ?? 0);
            if(!seconds){
                return "disabled";
            }
            const minutes = Math.round(seconds / 60);
            return minutes >= 60 ? `every ${minutes / 60} ${minutes === 60 ? "hour" : "hours"}` : `every ${minutes} minutes`;
        },
        nextSyncText() {
            const intervalSeconds = parseInt(this.config?.lxmf_preferred_propagation_node_auto_sync_interval_seconds ?? 0);
            const lastSyncedAt = this.config?.lxmf_preferred_propagation_node_last_synced_at;
            if(!intervalSeconds || !lastSyncedAt){
                return null;
            }
            const secondsUntil = (lastSyncedAt + intervalSeconds) - Math.floor(Date.now() / 1000);
            if(secondsUntil <= 0){
                return "due now";
            }
            const minutesUntil = Math.ceil(secondsUntil / 60);
            return `in ${minutesUntil} ${minutesUntil === 1 ? "minute" : "minutes"}`;
        },
    },
    mounted() {
        this.getConfig();
        this.getStatus();
        this.statusInterval = setInterval(() => {
            this.getStatus();
            this.getConfig();
        }, 2000);
    },
    beforeUnmount() {
        clearInterval(this.statusInterval);
    },
    methods: {
        async getConfig() {
            try {
                const response = await window.axios.get("/api/v1/config");
                this.config = response.data.config;
                // check path and display name for the preferred node once we know it
                if(this.preferredNode && this.nodePath === null){
                    this.getNodePath();
                    this.getNodeDisplayName();
                }
            } catch(e) {
                console.log(e);
            }
        },
        async getStatus() {
            try {
                const response = await window.axios.get("/api/v1/lxmf/propagation-node/status");
                this.status = response.data.propagation_node_status;
            } catch(e) {
                console.log(e);
            }
        },
        async getNodePath() {
            try {
                const response = await window.axios.get(`/api/v1/destination/${this.preferredNode}/path`);
                this.nodePath = response.data;
            } catch(e) {
                this.nodePath = { path: null };
                console.log(e);
            }
        },
        async getNodeDisplayName() {
            try {
                const response = await window.axios.get(`/api/v1/destination/${this.preferredNode}/info`);
                this.nodeDisplayName = response.data.destination_info.announce?.display_name ?? null;
            } catch(e) {
                console.log(e);
            }
        },
        async syncNow() {
            try {
                await window.axios.get("/api/v1/lxmf/propagation-node/sync");
                DialogUtils.toast("Sync started");
            } catch(e) {
                DialogUtils.toast("Failed to start sync", "error");
                console.log(e);
            }
        },
    },
}
</script>
