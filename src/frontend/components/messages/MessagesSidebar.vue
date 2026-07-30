<template>
    <div class="flex-col h-full w-full min-w-0 bg-[rgba(10,10,16,0.94)] sm:w-80 sm:min-w-80">

        <!-- tabs -->
        <div class="border-b border-r border-[var(--ct-border)] bg-[rgba(11,12,20,0.96)] p-1.5">
            <div class="flex gap-x-1 rounded-lg bg-[rgba(255,255,255,0.04)] p-1">
                <button @click="tab = 'conversations'" type="button" class="flex-1 rounded-md py-1.5 text-center text-sm font-semibold transition" :class="[ tab === 'conversations' ? 'bg-[var(--ct-blue)] text-white shadow-[0_4px_16px_rgba(0,97,253,0.3)]' : 'text-[var(--ct-dim)] hover:text-[var(--ct-text)]' ]">Chats</button>
                <button @click="tab = 'announces'" type="button" class="flex-1 rounded-md py-1.5 text-center text-sm font-semibold transition" :class="[ tab === 'announces' ? 'bg-[var(--ct-blue)] text-white shadow-[0_4px_16px_rgba(0,97,253,0.3)]' : 'text-[var(--ct-dim)] hover:text-[var(--ct-text)]' ]">Discover</button>
            </div>
        </div>

        <!-- conversations -->
        <div v-if="tab === 'conversations'" class="flex-1 flex flex-col bg-[rgba(11,12,20,0.96)] border-r border-[var(--ct-border)] overflow-hidden">

            <!-- search -->
            <div v-if="conversations.length > 0" class="border-b border-[var(--ct-border)] p-1.5">
                <div class="relative">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-[var(--ct-dim)]">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                    </svg>
                    <input v-model="conversationsSearchTerm" type="text" placeholder="Search chats…" class="block w-full rounded-lg border !pl-8 p-2 text-sm">
                </div>
            </div>

            <!-- conversation list -->
            <div class="flex h-full overflow-y-auto">
                <div v-if="searchedConversations.length > 0" class="w-full py-1">
                    <button @click="onConversationClick(conversation)" v-for="conversation of searchedConversations" :key="conversation.destination_hash" type="button" class="mx-1.5 my-0.5 flex min-h-14 w-[calc(100%-0.75rem)] cursor-pointer items-center rounded-lg p-2 text-left transition" :class="[ conversation.destination_hash === selectedDestinationHash ? 'bg-[rgba(0,97,253,0.18)] ring-1 ring-inset ring-[rgba(0,97,253,0.4)]' : 'hover:bg-[rgba(255,255,255,0.05)]' ]">
                        <div class="mr-2.5 shrink-0">
                            <LxmfUserIcon
                                :icon-name="conversation.lxmf_user_icon?.icon_name"
                                :icon-foreground-colour="conversation.lxmf_user_icon?.foreground_colour"
                                :icon-background-colour="conversation.lxmf_user_icon?.background_colour"
                                :destination-hash="conversation.destination_hash"/>
                        </div>
                        <div class="min-w-0 flex-1">
                            <div class="truncate text-sm text-[var(--ct-text)]" :class="{ 'font-bold': conversation.is_unread || conversation.failed_messages_count > 0 }">{{ conversation.custom_display_name ?? conversation.display_name }}</div>
                            <div class="text-xs text-[var(--ct-dim)]">{{ formatTimeAgo(conversation.updated_at) }}</div>
                        </div>
                        <div v-if="conversation.is_unread" class="ml-2 shrink-0">
                            <div class="size-2.5 rounded-full bg-[var(--ct-blue)] shadow-[0_0_8px_rgba(0,97,253,0.7)]"></div>
                        </div>
                        <div v-else-if="conversation.failed_messages_count" class="ml-2 shrink-0" title="Some messages failed to send">
                            <div class="size-2.5 rounded-full bg-[var(--ct-red)] shadow-[0_0_8px_rgba(255,59,87,0.6)]"></div>
                        </div>
                    </button>
                </div>
                <div v-else class="mx-auto my-auto w-full">

                    <!-- no conversations at all -->
                    <EmptyState v-if="conversations.length === 0" title="No chats yet" description="Find people on the Discover tab, or compose a message to an LXMF address.">
                        <template v-slot:icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
                            </svg>
                        </template>
                    </EmptyState>

                    <!-- is searching, but no results -->
                    <EmptyState v-if="conversationsSearchTerm !== '' && conversations.length > 0" title="No results" description="Your search didn't match any chats.">
                        <template v-slot:icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                                <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                            </svg>
                        </template>
                    </EmptyState>
                </div>
            </div>
        </div>

        <!-- discover -->
        <div v-if="tab === 'announces'" class="flex-1 flex flex-col bg-[rgba(11,12,20,0.96)] border-r border-[var(--ct-border)] overflow-hidden">

            <!-- search -->
            <div v-if="peersCount > 0" class="border-b border-[var(--ct-border)] p-1.5">
                <div class="relative">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-[var(--ct-dim)]">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                    </svg>
                    <input v-model="peersSearchTerm" type="text" :placeholder="`Search ${peersCount} discovered peers…`" class="block w-full rounded-lg border !pl-8 p-2 text-sm">
                </div>
            </div>

            <!-- peers -->
            <div class="flex h-full overflow-y-auto">
                <div v-if="searchedPeers.length > 0" class="w-full py-1">
                    <button @click="onPeerClick(peer)" v-for="peer of searchedPeers" :key="peer.destination_hash" type="button" class="mx-1.5 my-0.5 flex min-h-14 w-[calc(100%-0.75rem)] cursor-pointer items-center rounded-lg p-2 text-left transition" :class="[ peer.destination_hash === selectedDestinationHash ? 'bg-[rgba(0,97,253,0.18)] ring-1 ring-inset ring-[rgba(0,97,253,0.4)]' : 'hover:bg-[rgba(255,255,255,0.05)]' ]">
                        <div class="mr-2.5 shrink-0">
                            <LxmfUserIcon
                                :icon-name="peer.lxmf_user_icon?.icon_name"
                                :icon-foreground-colour="peer.lxmf_user_icon?.foreground_colour"
                                :icon-background-colour="peer.lxmf_user_icon?.background_colour"
                                :destination-hash="peer.destination_hash"/>
                        </div>
                        <div class="min-w-0">
                            <div class="truncate text-sm text-[var(--ct-text)]">{{ peer.custom_display_name ?? peer.display_name }}</div>
                            <div class="flex space-x-1 text-xs text-[var(--ct-dim)]">

                                <!-- time ago -->
                                <span class="flex my-auto space-x-1">
                                    {{ formatTimeAgo(peer.updated_at) }}
                                </span>

                                <!-- hops away -->
                                <span v-if="peer.hops != null && peer.hops !== 128" class="flex my-auto space-x-1">
                                    <span>•</span>
                                    <span v-if="peer.hops === 0 || peer.hops === 1">Direct</span>
                                    <span v-else>{{ peer.hops }} hops</span>
                                </span>

                                <!-- snr -->
                                <span v-if="peer.snr != null" class="flex my-auto space-x-1">
                                    <span>•</span>
                                    <span>SNR {{ peer.snr }}</span>
                                </span>

                            </div>
                        </div>
                    </button>
                </div>
                <div v-else class="mx-auto my-auto w-full">

                    <!-- no peers at all -->
                    <EmptyState v-if="peersCount === 0" title="No peers discovered yet" description="Peers appear here automatically when they announce on the network. Make sure you have a connection set up.">
                        <template v-slot:icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9.348 14.652a3.75 3.75 0 0 1 0-5.304m5.304 0a3.75 3.75 0 0 1 0 5.304m-7.425 2.121a6.75 6.75 0 0 1 0-9.546m9.546 0a6.75 6.75 0 0 1 0 9.546M5.106 18.894c-3.808-3.807-3.808-9.98 0-13.788m13.788 0c3.808 3.807 3.808 9.98 0 13.788M12 12h.008v.008H12V12Z" />
                            </svg>
                        </template>
                    </EmptyState>

                    <!-- is searching, but no results -->
                    <EmptyState v-if="peersSearchTerm !== '' && peersCount > 0" title="No results" description="Your search didn't match any peers.">
                        <template v-slot:icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                                <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                            </svg>
                        </template>
                    </EmptyState>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Utils from "../../js/Utils";
import LxmfUserIcon from "../LxmfUserIcon.vue";
import EmptyState from "../base/EmptyState.vue";

export default {
    name: 'MessagesSidebar',
    components: {LxmfUserIcon, EmptyState},
    props: {
        peers: Object,
        conversations: Array,
        selectedDestinationHash: String,
    },
    data() {
        return {
            tab: "conversations",
            conversationsSearchTerm: "",
            peersSearchTerm: "",
        };
    },
    methods: {
        onConversationClick(conversation) {
            this.$emit("conversation-click", conversation);
        },
        onPeerClick(peer) {
            this.$emit("peer-click", peer);
        },
        formatTimeAgo: function(datetimeString) {
            return Utils.formatTimeAgo(datetimeString);
        },
    },
    computed: {
        searchedConversations() {
            return this.conversations.filter((conversation) => {
                const search = this.conversationsSearchTerm.toLowerCase();
                const matchesDisplayName = conversation.display_name.toLowerCase().includes(search);
                const matchesCustomDisplayName = conversation.custom_display_name?.toLowerCase()?.includes(search) === true;
                const matchesDestinationHash = conversation.destination_hash.toLowerCase().includes(search);
                return matchesDisplayName || matchesCustomDisplayName || matchesDestinationHash;
            });
        },
        peersCount() {
            return Object.keys(this.peers).length;
        },
        peersOrderedByLatestAnnounce() {
            const peers = Object.values(this.peers);
            return peers.sort(function(peerA, peerB) {
                // order by updated_at desc
                const peerAUpdatedAt = new Date(peerA.updated_at).getTime();
                const peerBUpdatedAt = new Date(peerB.updated_at).getTime();
                return peerBUpdatedAt - peerAUpdatedAt;
            });
        },
        searchedPeers() {
            return this.peersOrderedByLatestAnnounce.filter((peer) => {
                const search = this.peersSearchTerm.toLowerCase();
                const matchesDisplayName = peer.display_name.toLowerCase().includes(search);
                const matchesCustomDisplayName = peer.custom_display_name?.toLowerCase()?.includes(search) === true;
                const matchesDestinationHash = peer.destination_hash.toLowerCase().includes(search);
                return matchesDisplayName || matchesCustomDisplayName || matchesDestinationHash;
            });
        },
    },
}
</script>
