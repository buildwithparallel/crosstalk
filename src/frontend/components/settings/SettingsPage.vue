<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <!-- page header -->
            <div>
                <div class="text-lg font-bold text-[var(--ct-text)]">Settings</div>
                <div class="text-sm text-[var(--ct-dim)]">Configure how Crosstalk behaves on the network.</div>
            </div>

            <!-- transport mode -->
            <div class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Transport Mode</div>
                <div class="divide-y divide-[var(--ct-border)] text-[var(--ct-muted)]">

                    <div class="p-2.5">
                        <label class="flex cursor-pointer items-start gap-x-2.5">
                            <input v-model="config.is_transport_enabled" @change="onIsTransportEnabledChange" type="checkbox" class="mt-0.5 size-4 rounded border">
                            <span>
                                <span class="block text-sm font-medium text-[var(--ct-text)]">Enable Transport Mode</span>
                                <span class="block text-sm text-[var(--ct-dim)]">When enabled, Crosstalk will route traffic for other peers, respond to path requests and pass announces over your connections. Changes are applied automatically in the desktop app.</span>
                            </span>
                        </label>
                    </div>

                </div>
            </div>

            <!-- connections -->
            <div class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Connections</div>
                <div class="divide-y divide-[var(--ct-border)] text-[var(--ct-muted)]">

                    <div class="p-2.5">
                        <label class="flex cursor-pointer items-start gap-x-2.5">
                            <input v-model="config.show_suggested_community_interfaces" @change="onShowSuggestedCommunityInterfacesChange" type="checkbox" class="mt-0.5 size-4 rounded border">
                            <span>
                                <span class="block text-sm font-medium text-[var(--ct-text)]">Show Community Suggestions</span>
                                <span class="block text-sm text-[var(--ct-dim)]">When enabled, suggested community nodes will be shown when adding a new connection.</span>
                            </span>
                        </label>
                    </div>

                </div>
            </div>

            <!-- messages -->
            <div class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Messages</div>
                <div class="divide-y divide-[var(--ct-border)] text-[var(--ct-muted)]">

                    <div class="p-2.5">
                        <label class="flex cursor-pointer items-start gap-x-2.5">
                            <input v-model="config.auto_resend_failed_messages_when_announce_received" @change="onAutoResendFailedMessagesWhenAnnounceReceivedChange" type="checkbox" class="mt-0.5 size-4 rounded border">
                            <span>
                                <span class="block text-sm font-medium text-[var(--ct-text)]">Auto Resend</span>
                                <span class="block text-sm text-[var(--ct-dim)]">Failed messages will automatically resend when an announce is received from the intended recipient.</span>
                            </span>
                        </label>
                    </div>

                    <div class="p-2.5">
                        <label class="flex cursor-pointer items-start gap-x-2.5">
                            <input v-model="config.allow_auto_resending_failed_messages_with_attachments" @change="onAllowAutoResendingFailedMessagesWithAttachmentsChange" type="checkbox" class="mt-0.5 size-4 rounded border">
                            <span>
                                <span class="block text-sm font-medium text-[var(--ct-text)]">Allow Resending with Attachments</span>
                                <span class="block text-sm text-[var(--ct-dim)]">Failed messages that have attachments are allowed to auto resend.</span>
                            </span>
                        </label>
                    </div>

                    <div class="p-2.5">
                        <label class="flex cursor-pointer items-start gap-x-2.5">
                            <input v-model="config.auto_send_failed_messages_to_propagation_node" @change="onAutoSendFailedMessagesToPropagationNodeChange" type="checkbox" class="mt-0.5 size-4 rounded border">
                            <span>
                                <span class="block text-sm font-medium text-[var(--ct-text)]">Auto Send to Propagation Node</span>
                                <span class="block text-sm text-[var(--ct-dim)]">Messages that fail to send will be handed to the configured propagation node for later delivery.</span>
                            </span>
                        </label>
                    </div>

                </div>
            </div>

            <!-- message delivery / propagation nodes -->
            <div class="ct-card">
                <div class="flex items-center border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">
                    <div class="mr-auto">Message Delivery</div>
                    <RouterLink :to="{ name: 'propagation-nodes' }" class="ct-secondary-button inline-flex items-center gap-x-1 rounded-lg px-2.5 py-1.5 text-sm font-semibold">
                        Browse Propagation Nodes
                    </RouterLink>
                </div>
                <div class="divide-y divide-[var(--ct-border)] text-[var(--ct-muted)]">

                    <div class="p-2.5 text-sm text-[var(--ct-dim)]">
                        Propagation nodes hold encrypted messages for recipients that are offline, and hand them over when the recipient next syncs. They store messages for up to 30 days by default.
                    </div>

                    <div class="p-2.5 space-y-1">
                        <label class="flex cursor-pointer items-start gap-x-2.5">
                            <input v-model="config.lxmf_local_propagation_node_enabled" @change="onLxmfLocalPropagationNodeEnabledChange" type="checkbox" class="mt-0.5 size-4 rounded border">
                            <span>
                                <span class="block text-sm font-medium text-[var(--ct-text)]">Run a Local Propagation Node</span>
                                <span class="block text-sm text-[var(--ct-dim)]">Crosstalk will run its own propagation node and announce this address for other clients to use.</span>
                            </span>
                        </label>
                        <input disabled v-model="config.lxmf_local_propagation_node_address_hash" type="text" class="ct-hash block w-full cursor-not-allowed rounded-lg border p-2.5 opacity-60">
                    </div>

                    <div class="p-2.5 space-y-1">
                        <div class="text-sm font-medium text-[var(--ct-text)]">Preferred Propagation Node</div>
                        <input v-model="config.lxmf_preferred_propagation_node_destination_hash" @input="onLxmfPreferredPropagationNodeDestinationHashChange" type="text" placeholder="Destination hash, e.g: a39610c89d18bb48c73e429582423c24" class="ct-hash block w-full rounded-lg border p-2.5">
                        <div class="text-sm text-[var(--ct-dim)]">This is the propagation node your messages will be sent to and retrieved from.</div>
                    </div>

                    <div class="p-2.5 space-y-1">
                        <div class="text-sm font-medium text-[var(--ct-text)]">Auto Sync Interval</div>
                        <select v-model="config.lxmf_preferred_propagation_node_auto_sync_interval_seconds" @change="onLxmfPreferredPropagationNodeAutoSyncIntervalSecondsChange" class="block w-full rounded-lg border p-2.5 text-sm">
                            <option value="0">Disabled</option>
                            <option value="900">Every 15 Minutes</option>
                            <option value="1800">Every 30 Minutes</option>
                            <option value="3600">Every 1 Hour</option>
                            <option value="10800">Every 3 Hours</option>
                            <option value="21600">Every 6 Hours</option>
                            <option value="43200">Every 12 Hours</option>
                            <option value="86400">Every 24 Hours</option>
                        </select>
                        <div class="text-sm text-[var(--ct-dim)]">
                            <span v-if="config.lxmf_preferred_propagation_node_last_synced_at">Last synced {{ formatSecondsAgo(config.lxmf_preferred_propagation_node_last_synced_at) }}</span>
                            <span v-else>Never synced</span>
                        </div>
                    </div>

                </div>
            </div>

        </div>
    </div>
</template>

<script>
import Utils from "../../js/Utils";
import WebSocketConnection from "../../js/WebSocketConnection";
import DialogUtils from "../../js/DialogUtils";
import ElectronUtils from "../../js/ElectronUtils";

export default {
    name: 'SettingsPage',
    data() {
        return {
            config: {
                auto_resend_failed_messages_when_announce_received: null,
                allow_auto_resending_failed_messages_with_attachments: null,
                auto_send_failed_messages_to_propagation_node: null,
                show_suggested_community_interfaces: null,
                lxmf_local_propagation_node_enabled: null,
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
                DialogUtils.toast("Failed to save settings", "error");
                console.log(e);
            }
        },
        async onAutoResendFailedMessagesWhenAnnounceReceivedChange() {
            await this.updateConfig({
                "auto_resend_failed_messages_when_announce_received": this.config.auto_resend_failed_messages_when_announce_received,
            });
        },
        async onAllowAutoResendingFailedMessagesWithAttachmentsChange() {
            await this.updateConfig({
                "allow_auto_resending_failed_messages_with_attachments": this.config.allow_auto_resending_failed_messages_with_attachments,
            });
        },
        async onAutoSendFailedMessagesToPropagationNodeChange() {
            await this.updateConfig({
                "auto_send_failed_messages_to_propagation_node": this.config.auto_send_failed_messages_to_propagation_node,
            });
        },
        async onShowSuggestedCommunityInterfacesChange() {
            await this.updateConfig({
                "show_suggested_community_interfaces": this.config.show_suggested_community_interfaces,
            });
        },
        async onLxmfPreferredPropagationNodeDestinationHashChange() {
            await this.updateConfig({
                "lxmf_preferred_propagation_node_destination_hash": this.config.lxmf_preferred_propagation_node_destination_hash,
            });
        },
        async onLxmfLocalPropagationNodeEnabledChange() {
            await this.updateConfig({
                "lxmf_local_propagation_node_enabled": this.config.lxmf_local_propagation_node_enabled,
            });
        },
        async onLxmfPreferredPropagationNodeAutoSyncIntervalSecondsChange() {
            await this.updateConfig({
                "lxmf_preferred_propagation_node_auto_sync_interval_seconds": this.config.lxmf_preferred_propagation_node_auto_sync_interval_seconds,
            });
        },
        async onIsTransportEnabledChange() {
            if(this.config.is_transport_enabled){
                try {
                    await window.axios.post("/api/v1/reticulum/enable-transport");
                    await ElectronUtils.restartBackend("#/settings");
                    return;
                } catch(e) {
                    DialogUtils.toast("Failed to enable transport mode", "error");
                    console.log(e);
                }
            } else {
                try {
                    await window.axios.post("/api/v1/reticulum/disable-transport");
                    await ElectronUtils.restartBackend("#/settings");
                    return;
                } catch(e) {
                    DialogUtils.toast("Failed to disable transport mode", "error");
                    console.log(e);
                }
            }
        },
        formatSecondsAgo: function(seconds) {
            return Utils.formatSecondsAgo(seconds);
        },
    },
}
</script>
