<template>
    <div class="dark ct-app-shell ct-shell ct-dot-grid w-full flex flex-col overflow-hidden text-[var(--ct-text)]">

        <!-- overlay hosts -->
        <ModalHost/>
        <ToastHost/>

        <!-- header -->
        <div class="ct-app-header relative z-30 flex shrink-0 bg-[rgba(9,9,9,0.88)] backdrop-blur-xl px-3 py-2 border-b border-[var(--ct-border)] min-h-14 shadow-[0_12px_42px_rgba(0,0,0,0.28)]">
            <div class="pointer-events-none absolute inset-0 ct-vignette opacity-40"></div>
            <div class="flex w-full items-center">
                <button @click="mobileNavigationOpen = true" type="button" aria-label="Open navigation" class="ct-secondary-button relative mr-2 inline-flex size-10 items-center justify-center rounded-full sm:hidden">
                    <PhosphorIcon name="list" weight="bold" class="size-5"/>
                </button>
                <div class="hidden sm:flex mr-2.5">
                    <img class="size-9 drop-shadow-[0_0_20px_rgba(0,97,253,0.45)]" src="/assets/images/crosstalk-mark.svg" />
                </div>
                <div @click="onAppNameClick" class="relative cursor-pointer">
                    <div class="font-bold leading-5 text-[var(--ct-text)]">Crosstalk</div>
                    <div class="text-xs text-[var(--ct-dim)]">Talk to the World</div>
                </div>

                <!-- contextual actions (messages) -->
                <div class="relative flex ml-auto items-center gap-x-2">
                    <button v-if="isOnMessagesRoute" @click="syncPropagationNode" type="button" class="ct-secondary-button flex items-center gap-x-1.5 rounded-full px-3 py-1.5 text-sm font-semibold transition">
                        <span :class="{ 'animate-spin': isSyncingPropagationNode }">
                            <PhosphorIcon name="arrows-clockwise" weight="bold" class="size-4"/>
                        </span>
                        <span class="hidden sm:inline-block">{{ isSyncingPropagationNode ? 'Syncing…' : 'Sync' }}</span>
                    </button>
                    <button @click="composeNewMessage" type="button" class="ct-brand-button flex items-center gap-x-1.5 rounded-full px-3 py-1.5 text-sm font-semibold text-white transition">
                        <PhosphorIcon name="pencil-simple" weight="bold" class="size-4"/>
                        <span class="hidden sm:inline-block">Compose</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- middle -->
        <div ref="middle" class="relative flex min-h-0 flex-1 w-full overflow-hidden">

            <button
                v-if="mobileNavigationOpen"
                @click="mobileNavigationOpen = false"
                type="button"
                aria-label="Close navigation"
                class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm sm:hidden"></button>

            <!-- sidebar -->
            <div
                class="fixed inset-y-0 left-0 z-50 flex w-72 min-w-72 flex-col bg-[rgba(9,9,9,0.96)] shadow-[20px_0_70px_rgba(0,0,0,0.5)] transition-transform duration-200 sm:static sm:z-auto sm:w-64 sm:min-w-64 sm:translate-x-0 sm:shadow-none"
                :class="mobileNavigationOpen ? 'translate-x-0' : '-translate-x-full'">
                <div class="flex min-h-14 items-center border-b border-[var(--ct-border)] px-3 sm:hidden">
                    <img class="size-8" src="/assets/images/crosstalk-mark.svg" />
                    <span class="ml-2 font-semibold">Crosstalk</span>
                    <button @click="mobileNavigationOpen = false" type="button" aria-label="Close navigation" class="ct-secondary-button ml-auto inline-flex size-10 items-center justify-center rounded-full">
                        <PhosphorIcon name="x" weight="bold" class="size-5"/>
                    </button>
                </div>
                <div class="flex grow flex-col overflow-y-auto border-r border-[var(--ct-border)] bg-[rgba(9,9,9,0.72)] backdrop-blur-xl">

                    <!-- navigation -->
                    <div class="flex-1">

                        <!-- communicate group -->
                        <div class="ct-section-label px-4 pt-4 pb-1.5">Communicate</div>
                        <ul class="pr-2 space-y-0.5">
                            <li>
                                <SidebarLink :to="{ name: 'messages' }" @click="mobileNavigationOpen = false">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="chat-circle" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>
                                        <span>Messages</span>
                                        <span v-if="unreadConversationsCount > 0" class="ml-auto mr-2 inline-flex min-w-5 items-center justify-center rounded-full bg-[var(--ct-blue)] px-1.5 text-xs font-bold text-white">{{ unreadConversationsCount }}</span>
                                    </template>
                                </SidebarLink>
                            </li>
                        </ul>

                        <!-- explore group -->
                        <div class="ct-section-label px-4 pt-4 pb-1.5">Explore</div>
                        <ul class="pr-2 space-y-0.5">
                            <li>
                                <SidebarLink :to="{ name: 'nomadnetwork' }">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="globe-hemisphere-west" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>Nomad Browser</template>
                                </SidebarLink>
                            </li>
                        </ul>

                        <!-- network group -->
                        <div class="ct-section-label px-4 pt-4 pb-1.5">Network</div>
                        <ul class="pr-2 space-y-0.5">
                            <li>
                                <SidebarLink :to="{ name: 'network-visualiser' }">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="graph" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>Map</template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'interfaces' }">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="tree-structure" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>Interfaces</template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'infrastructure' }">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="cell-tower" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>Infrastructure</template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'tools' }">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="wrench" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>Diagnostics</template>
                                </SidebarLink>
                            </li>
                        </ul>

                        <!-- app group -->
                        <div class="ct-section-label px-4 pt-4 pb-1.5">App</div>
                        <ul class="pr-2 space-y-0.5">
                            <li>
                                <SidebarLink :to="{ name: 'settings' }">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="gear" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>Settings</template>
                                </SidebarLink>
                            </li>
                            <li>
                                <SidebarLink :to="{ name: 'about' }">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="info" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>About</template>
                                </SidebarLink>
                            </li>
                        </ul>

                        <!-- advanced group -->
                        <div class="ct-section-label px-4 pt-4 pb-1.5">Advanced</div>
                        <ul class="pr-2 space-y-0.5 pb-2">
                            <li>
                                <SidebarLink :to="{ name: 'bridge-extensions' }" @click="mobileNavigationOpen = false">
                                    <template v-slot:icon>
                                        <PhosphorIcon name="plugs-connected" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>Bridge Extensions</template>
                                </SidebarLink>
                            </li>
                            <li v-for="bridge in runningBridges" :key="`${bridge.extensionId}-${bridge.roleId}`" class="pl-5">
                                <SidebarLink
                                    :to="{ name: 'bridge-extensions.role', params: { id: bridge.extensionId, roleId: bridge.roleId } }"
                                    @click="mobileNavigationOpen = false">
                                    <template v-slot:icon>
                                        <PhosphorIcon :name="bridge.icon" weight="duotone" class="size-5"/>
                                    </template>
                                    <template v-slot:text>
                                        <span class="truncate">{{ bridge.hardware }}</span>
                                        <span class="ml-auto mr-2 size-1.5 shrink-0 rounded-full bg-green-400" title="Running here"></span>
                                    </template>
                                </SidebarLink>
                            </li>
                        </ul>

                    </div>

                    <!-- active calls banner -->
                    <div v-if="activeAudioCalls.length > 0" class="mx-2 mb-2 rounded-xl border border-[rgba(46,231,129,0.4)] bg-[rgba(46,231,129,0.08)] p-2">
                        <div class="flex items-center">
                            <div class="min-w-0">
                                <div class="text-sm font-semibold text-[var(--ct-text)]">
                                    <span v-if="activeInboundAudioCalls.length > 0">{{ activeInboundAudioCalls.length }} Incoming {{ activeInboundAudioCalls.length === 1 ? 'Call' : 'Calls' }}</span>
                                    <span v-else>{{ activeOutboundAudioCalls.length }} Outgoing {{ activeOutboundAudioCalls.length === 1 ? 'Call' : 'Calls' }}</span>
                                </div>
                            </div>
                            <div class="ml-auto flex items-center gap-x-1.5">
                                <a href="../call.html" target="_blank" title="View Calls" class="inline-flex items-center rounded-full bg-green-500 p-1.5 text-white hover:bg-green-400">
                                    <PhosphorIcon name="phone" weight="fill" class="size-4"/>
                                </a>
                                <button title="Hang up all calls" @click="hangupAllCalls" type="button" class="inline-flex items-center rounded-full bg-red-500 p-1.5 text-white hover:bg-red-400">
                                    <PhosphorIcon name="phone-disconnect" weight="fill" class="size-4"/>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- identity card -->
                    <div v-if="config" class="border-t border-[var(--ct-border)] bg-[rgba(13,13,18,0.9)]">

                        <!-- expanded identity settings -->
                        <div v-if="isShowingIdentitySettings" class="border-b border-[var(--ct-border)] p-3 space-y-3">
                            <div>
                                <div class="ct-section-label mb-1">Display Name</div>
                                <div class="flex gap-x-1.5">
                                    <input
                                        v-model="displayName"
                                        @keydown.enter="saveIdentitySettings"
                                        type="text"
                                        placeholder="Display Name"
                                        class="block w-full rounded-lg border p-2 text-sm"
                                    >
                                    <button @click="saveIdentitySettings" type="button" class="ct-brand-button rounded-lg px-3 text-sm font-semibold">Save</button>
                                </div>
                            </div>
                            <div>
                                <div class="ct-section-label mb-1">LXMF Address</div>
                                <div class="flex items-center gap-x-1">
                                    <div class="ct-hash break-all">{{ config.lxmf_address_hash }}</div>
                                    <CopyButton class="ml-auto" :value="config.lxmf_address_hash" label="LXMF Address"/>
                                </div>
                            </div>
                            <div>
                                <div class="ct-section-label mb-1">Identity Hash</div>
                                <div class="flex items-center gap-x-1">
                                    <div class="ct-hash break-all">{{ config.identity_hash }}</div>
                                    <CopyButton class="ml-auto" :value="config.identity_hash" label="Identity Hash"/>
                                </div>
                            </div>
                            <div>
                                <div class="ct-section-label mb-1">Auto Announce</div>
                                <select
                                    v-model="config.auto_announce_interval_seconds"
                                    @change="onAnnounceIntervalSecondsChange"
                                    class="block w-full rounded-lg border p-2 text-sm"
                                >
                                    <option value="0">Disabled</option>
                                    <option value="900">Every 15 Minutes</option>
                                    <option value="1800">Every 30 Minutes</option>
                                    <option value="3600">Every 1 Hour</option>
                                    <option value="10800">Every 3 Hours</option>
                                    <option value="21600">Every 6 Hours</option>
                                    <option value="43200">Every 12 Hours</option>
                                    <option value="86400">Every 24 Hours</option>
                                </select>
                                <div class="mt-1 text-xs text-[var(--ct-dim)]">
                                    <span v-if="config.last_announced_at">Last announced {{ formatSecondsAgo(config.last_announced_at) }}</span>
                                    <span v-else>Never announced</span>
                                </div>
                            </div>
                            <div class="flex gap-x-1.5">
                                <button @click="sendAnnounce" type="button" class="ct-secondary-button flex-1 rounded-lg px-3 py-1.5 text-sm font-semibold">Announce Now</button>
                                <a href="../call.html" target="_blank" class="ct-secondary-button flex items-center gap-x-1 rounded-lg px-3 py-1.5 text-sm font-semibold">
                                    <span>Phone</span>
                                    <PhosphorIcon name="arrow-square-out" weight="bold" class="size-3.5"/>
                                </a>
                            </div>
                        </div>

                        <!-- collapsed identity card row -->
                        <div @click="isShowingIdentitySettings = !isShowingIdentitySettings" class="flex cursor-pointer items-center gap-x-2.5 p-3 transition hover:bg-[rgba(255,255,255,0.04)]">
                            <RouterLink @click.stop :to="{ name: 'profile.icon' }" title="Change profile icon">
                                <LxmfUserIcon
                                    :icon-name="config?.lxmf_user_icon_name"
                                    :icon-foreground-colour="config?.lxmf_user_icon_foreground_colour"
                                    :icon-background-colour="config?.lxmf_user_icon_background_colour"
                                    :destination-hash="config?.lxmf_address_hash"/>
                            </RouterLink>
                            <div class="min-w-0 flex-1">
                                <div class="truncate text-sm font-semibold text-[var(--ct-text)]">{{ config.display_name || 'Anonymous Peer' }}</div>
                                <div class="ct-hash truncate">{{ truncatedAddress }}</div>
                            </div>
                            <PhosphorIcon name="caret-up" weight="bold" class="size-4 shrink-0 text-[var(--ct-dim)] transition" :class="{ 'rotate-180': isShowingIdentitySettings }"/>
                        </div>

                    </div>

                </div>
            </div>

            <RouterView class="min-w-0 flex-1"/>

        </div>
    </div>
</template>


<script>
import SidebarLink from "./SidebarLink.vue";
import DialogUtils from "../js/DialogUtils";
import WebSocketConnection from "../js/WebSocketConnection";
import GlobalState from "../js/GlobalState";
import Utils from "../js/Utils";
import GlobalEmitter from "../js/GlobalEmitter";
import NotificationUtils from "../js/NotificationUtils";
import LxmfUserIcon from "./LxmfUserIcon.vue";
import CopyButton from "./CopyButton.vue";
import ModalHost from "./overlays/ModalHost.vue";
import ToastHost from "./overlays/ToastHost.vue";
import PhosphorIcon from "./PhosphorIcon.vue";
import { runningBridgeShortcuts } from "../js/bridgeExtensions";

export default {
    name: 'App',
    components: {
        CopyButton,
        LxmfUserIcon,
        SidebarLink,
        ModalHost,
        ToastHost,
        PhosphorIcon,
    },
    data() {
        return {

            reloadInterval: null,

            isShowingIdentitySettings: false,
            mobileNavigationOpen: false,

            displayName: "Anonymous Peer",
            config: null,
            appInfo: null,

            audioCalls: [],
            propagationNodeStatus: null,
            hfBridgeProcesses: {},

        };
    },
    beforeUnmount() {

        clearInterval(this.reloadInterval);

        // stop listening for websocket messages
        WebSocketConnection.off("message", this.onWebsocketMessage);

    },
    mounted() {

        // listen for websocket messages
        WebSocketConnection.on("message", this.onWebsocketMessage);

        this.getAppInfo();
        this.updateCallsList();
        this.updatePropagationNodeStatus();
        this.updateRunningBridges();

        // update info every few seconds
        this.reloadInterval = setInterval(() => {
            this.updateCallsList();
            this.updatePropagationNodeStatus();
            this.updateRunningBridges();
        }, 3000);

    },
    methods: {
        async onWebsocketMessage(message) {
            const json = JSON.parse(message.data);
            switch(json.type){
                case 'config': {
                    this.config = json.config;
                    this.displayName = json.config.display_name;
                    break;
                }
                case 'announced': {
                    // we just announced, update config so we can show the new last updated at
                    this.getConfig();
                    break;
                }
                case 'incoming_audio_call': {
                    NotificationUtils.showIncomingCallNotification();
                    break;
                }
            }
        },
        async getAppInfo() {
            try {
                const response = await window.axios.get(`/api/v1/app/info`);
                this.appInfo = response.data.app_info;
                this.warnAboutDisabledStartupInterfaces();
            } catch(e) {
                // do nothing if failed to load app info
                console.log(e);
            }
        },
        warnAboutDisabledStartupInterfaces() {
            const disabled = this.appInfo?.interfaces_disabled_on_startup ?? [];
            if(disabled.length === 0){
                return;
            }
            const names = disabled.map((name) => `"${name}"`).join(", ");
            const verb = disabled.length === 1 ? "was" : "were";
            DialogUtils.alert(
                `${names} failed to start and ${verb} turned off so Crosstalk could keep running. You can turn ${disabled.length === 1 ? "it" : "them"} back on from Network Interfaces after fixing the conflict.`,
                { title: disabled.length === 1 ? "Interface turned off" : "Interfaces turned off" },
            );
        },
        async getConfig() {
            try {
                const response = await window.axios.get(`/api/v1/config`);
                this.config = response.data.config;
            } catch(e) {
                // do nothing if failed to load config
                console.log(e);
            }
        },
        async sendAnnounce() {

            try {
                await window.axios.get(`/api/v1/announce`);
                DialogUtils.toast("Announce sent to the network", "success");
            } catch(e) {
                DialogUtils.toast("Failed to announce", "error");
                console.log(e);
            }

            // fetch config so it updates last announced timestamp
            await this.getConfig();

        },
        async updateConfig(config) {
            try {
                WebSocketConnection.send(JSON.stringify({
                    "type": "config.set",
                    "config": config,
                }));
            } catch(e) {
                console.error(e);
            }
        },
        async saveIdentitySettings() {
            await this.updateConfig({
                "display_name": this.displayName,
            });
            DialogUtils.toast("Display name saved", "success");
        },
        async onAnnounceIntervalSecondsChange() {
            await this.updateConfig({
                "auto_announce_interval_seconds": this.config.auto_announce_interval_seconds,
            });
        },
        async composeNewMessage() {

            // go to messages route
            await this.$router.push({ name: "messages" });

            // emit global event handled by MessagesPage
            GlobalEmitter.emit("compose-new-message");

        },
        async syncPropagationNode() {

            // ask to stop syncing if already syncing
            if(this.isSyncingPropagationNode){
                if(await DialogUtils.confirm("Are you sure you want to stop syncing?")){
                    await this.stopSyncingPropagationNode();
                }
                return;
            }

            // request sync
            try {
                await axios.get("/api/v1/lxmf/propagation-node/sync");
            } catch(e) {
                const errorMessage = e.response?.data?.message ?? "Something went wrong. Try again later.";
                DialogUtils.toast(errorMessage, "error");
                return;
            }

            // update propagation status
            await this.updatePropagationNodeStatus();

            // wait until sync has finished
            const syncFinishedInterval = setInterval(() => {

                // do nothing if still syncing
                if(this.isSyncingPropagationNode){
                    return;
                }

                // finished syncing, stop checking
                clearInterval(syncFinishedInterval);

                // show result
                const status = this.propagationNodeStatus?.state;
                const messagesReceived = this.propagationNodeStatus?.messages_received ?? 0;
                if(status === "complete" || status === "idle"){
                    DialogUtils.toast(`Sync complete. ${messagesReceived} ${messagesReceived === 1 ? 'message' : 'messages'} received.`, "success");
                } else {
                    DialogUtils.toast(`Sync error: ${status}`, "error");
                }

            }, 500);

        },
        async stopSyncingPropagationNode() {

            // stop sync
            try {
                await axios.get("/api/v1/lxmf/propagation-node/stop-sync");
            } catch(e) {
                // do nothing on error
            }

            // update propagation status
            await this.updatePropagationNodeStatus();

        },
        async updatePropagationNodeStatus() {
            try {
                const response = await axios.get("/api/v1/lxmf/propagation-node/status");
                this.propagationNodeStatus = response.data.propagation_node_status;
            } catch(e) {
                // do nothing on error
            }
        },
        formatSecondsAgo: function(seconds) {
            return Utils.formatSecondsAgo(seconds);
        },
        async updateCallsList() {
            try {

                // fetch calls
                const response = await axios.get("/api/v1/calls");

                // update ui
                this.audioCalls = response.data.audio_calls;

            } catch(e) {
                // do nothing on error
            }
        },
        async updateRunningBridges() {
            try {
                const response = await window.axios.get("/api/v1/hf-bridges");
                this.hfBridgeProcesses = response.data.processes || {};
            } catch (error) {
                this.hfBridgeProcesses = {};
            }
        },
        async hangupAllCalls() {

            // confirm user wants to hang up calls
            if(!await DialogUtils.confirm("Are you sure you want to hang up all incoming and outgoing calls?", { danger: true, confirmLabel: "Hang Up All" })){
                return;
            }

            try {

                // hangup all calls
                await axios.get(`/api/v1/calls/hangup-all`);

                // reload calls list
                await this.updateCallsList();

            } catch(e) {
                // ignore error hanging up call
            }

        },
        onAppNameClick() {
            // user may be on mobile, and is unable to scroll back to sidebar, so let them tap app name to do it
            this.$refs["middle"].scrollTo({
                top: 0,
                left: 0,
                behavior: "smooth",
            });
        },
    },
    computed: {
        unreadConversationsCount() {
            return GlobalState.unreadConversationsCount;
        },
        isOnMessagesRoute() {
            return this.$route.name === "messages";
        },
        runningBridges() {
            return runningBridgeShortcuts(this.hfBridgeProcesses);
        },
        truncatedAddress() {
            const hash = this.config?.lxmf_address_hash ?? "";
            if(hash.length > 16){
                return `${hash.slice(0, 8)}…${hash.slice(-8)}`;
            }
            return hash;
        },
        documentTitle() {
            const hash = this.config?.lxmf_address_hash ?? "";
            if(!hash){
                return "Crosstalk";
            }
            return `Crosstalk - …${hash.slice(-5)}`;
        },
        activeAudioCalls() {
            return this.audioCalls.filter(function(audioCall) {
                return audioCall.is_active;
            });
        },
        activeInboundAudioCalls() {
            return this.activeAudioCalls.filter(function(audioCall) {
                return !audioCall.is_outbound;
            });
        },
        activeOutboundAudioCalls() {
            return this.activeAudioCalls.filter(function(audioCall) {
                return audioCall.is_outbound;
            });
        },
        isSyncingPropagationNode() {
            return [
                "path_requested",
                "link_establishing",
                "link_established",
                "request_sent",
                "receiving",
                "response_received",
            ].includes(this.propagationNodeStatus?.state);
        },
    },
    watch: {
        $route() {
            this.mobileNavigationOpen = false;
        },
        documentTitle: {
            immediate: true,
            handler(title) {
                document.title = title;
            },
        },
    },
}
</script>
