<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">

        <!-- page header -->
        <div class="flex items-center gap-2 border-b border-[var(--ct-border)] p-3">
            <RouterLink :to="{ name: 'settings' }" class="flex rounded-md p-1.5 text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.08)] hover:text-[var(--ct-text)]" title="Back to Settings">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5">
                    <path fill-rule="evenodd" d="M17 10a.75.75 0 0 1-.75.75H5.612l4.158 3.96a.75.75 0 1 1-1.04 1.08l-5.5-5.25a.75.75 0 0 1 0-1.08l5.5-5.25a.75.75 0 1 1 1.04 1.08L5.612 9.25H16.25A.75.75 0 0 1 17 10Z" clip-rule="evenodd" />
                </svg>
            </RouterLink>
            <div>
                <div class="text-lg font-bold text-[var(--ct-text)]">Propagation Nodes</div>
                <div class="text-sm text-[var(--ct-dim)]">Nodes that hold messages for offline recipients. Pick one as your preferred node.</div>
            </div>
        </div>

        <!-- search -->
        <div v-if="propagationNodes.length > 0" class="flex border-b border-[var(--ct-border)] p-2">
            <input v-model="searchTerm" type="text" :placeholder="`Search ${propagationNodes.length} propagation nodes...`" class="block w-full rounded-lg border p-2.5 text-sm">
        </div>

        <!-- propagation nodes -->
        <div class="h-full overflow-y-auto">
            <div v-if="searchedPropagationNodes.length > 0" class="p-2 space-y-2 w-full">
                <div v-for="propagationNode of searchedPropagationNodes" class="ct-card overflow-hidden">
                    <div class="flex p-2.5">
                        <div class="flex min-w-0 items-center gap-x-2.5 pr-2">
                            <div class="shrink-0 overflow-hidden rounded-lg">
                                <Identicon :hash="propagationNode.destination_hash" class="size-10"/>
                            </div>
                            <div class="min-w-0">
                                <div class="truncate font-semibold text-[var(--ct-text)]">{{ propagationNode.operator_display_name ?? "Unknown Operator" }}</div>
                                <div class="flex items-center gap-1 text-sm text-[var(--ct-dim)]">
                                    <span class="ct-hash min-w-0 break-all text-xs">{{ propagationNode.destination_hash }}</span>
                                    <CopyButton :value="propagationNode.destination_hash" label="Propagation Node Address"/>
                                </div>
                            </div>
                        </div>
                        <div class="ml-auto my-auto shrink-0">
                            <button v-if="config.lxmf_preferred_propagation_node_destination_hash === propagationNode.destination_hash" @click="stopUsingPropagationNode" type="button" class="ct-danger-button inline-flex items-center gap-x-1 rounded-lg px-2.5 py-1.5 text-sm font-semibold">
                                Stop Using
                            </button>
                            <button v-else @click="usePropagationNode(propagationNode.destination_hash)" type="button" class="ct-secondary-button inline-flex items-center gap-x-1 rounded-lg px-2.5 py-1.5 text-sm font-semibold">
                                Set as Preferred
                            </button>
                        </div>
                    </div>
                    <div class="border-t border-[var(--ct-border)] bg-[rgba(0,0,0,0.25)] px-2.5 py-1.5">
                        <div class="flex flex-wrap items-center gap-x-2 text-sm text-[var(--ct-dim)]">
                            <span>Announced {{ formatTimeAgo(propagationNode.updated_at) }}</span>
                            <Badge v-if="propagationNode.is_propagation_enabled === false" variant="red">Disabled by Operator</Badge>
                            <Badge v-if="config.lxmf_preferred_propagation_node_destination_hash === propagationNode.destination_hash" variant="green" dot>Preferred</Badge>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="flex h-full">

                <!-- no propagation nodes at all -->
                <EmptyState v-if="propagationNodes.length === 0" title="No Propagation Nodes" description="No propagation nodes have announced yet. Check back later." class="m-auto">
                    <template #icon>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H6.911a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661Z" />
                        </svg>
                    </template>
                    <template #action>
                        <button @click="loadPropagationNodes" type="button" class="ct-secondary-button inline-flex items-center gap-x-1 rounded-lg px-3 py-1.5 text-sm font-semibold">
                            Reload
                        </button>
                    </template>
                </EmptyState>

                <!-- is searching, but no results -->
                <EmptyState v-if="searchTerm !== '' && propagationNodes.length > 0" title="No Search Results" description="Your search didn't match any propagation nodes." class="m-auto">
                    <template #icon>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                        </svg>
                    </template>
                </EmptyState>

            </div>
        </div>

    </div>
</template>

<script>
import Utils from "../../js/Utils";
import WebSocketConnection from "../../js/WebSocketConnection";
import DialogUtils from "../../js/DialogUtils";
import CopyButton from "../CopyButton.vue";
import Identicon from "../Identicon.vue";
import Badge from "../base/Badge.vue";
import EmptyState from "../base/EmptyState.vue";

export default {
    name: 'PropagationNodesPage',
    components: {
        CopyButton,
        Identicon,
        Badge,
        EmptyState,
    },
    data() {
        return {
            searchTerm: "",
            propagationNodes: [],
            config: {
                lxmf_preferred_propagation_node_destination_hash: null,
            },
        };
    },
    beforeUnmount() {

        // stop listening for websocket messages
        WebSocketConnection.off("message", this.onWebsocketMessage);

    },
    mounted() {

        // listen for websocket messages
        WebSocketConnection.on("message", this.onWebsocketMessage);

        this.getConfig();
        this.loadPropagationNodes();

    },
    methods: {
        async onWebsocketMessage(message) {
            const json = JSON.parse(message.data);
            switch(json.type){
                case 'config': {
                    this.config = json.config;
                    break;
                }
            }
        },
        async getConfig() {
            try {
                const response = await window.axios.get("/api/v1/config");
                this.config = response.data.config;
            } catch(e) {
                // do nothing if failed to load config
                console.log(e);
            }
        },
        async updateConfig(config) {
            try {
                const response = await window.axios.patch("/api/v1/config", config);
                this.config = response.data.config;
            } catch(e) {
                DialogUtils.toast("Failed to save config", "error");
                console.log(e);
            }
        },
        async loadPropagationNodes() {
            try {
                const response = await window.axios.get(`/api/v1/lxmf/propagation-nodes`, {
                    params: {
                        limit: 500,
                    },
                });
                this.propagationNodes = response.data.lxmf_propagation_nodes;
            } catch(e) {
                // do nothing if failed to load
            }
        },
        async usePropagationNode(destination_hash) {
            await this.updateConfig({
                lxmf_preferred_propagation_node_destination_hash: destination_hash,
            });
        },
        async stopUsingPropagationNode() {
            await this.updateConfig({
                lxmf_preferred_propagation_node_destination_hash: null,
            });
        },
        formatTimeAgo: function(datetimeString) {
            return Utils.formatTimeAgo(datetimeString);
        },
    },
    computed: {
        searchedPropagationNodes() {
            return this.propagationNodes.filter((propagationNode) => {
                const search = this.searchTerm.toLowerCase();
                const matchesOperatorDisplayName = propagationNode.operator_display_name?.toLowerCase()?.includes(search) ?? false;
                const matchesDestinationHash = propagationNode.destination_hash.toLowerCase().includes(search);
                return matchesOperatorDisplayName || matchesDestinationHash;
            });
        },
    },
}
</script>
