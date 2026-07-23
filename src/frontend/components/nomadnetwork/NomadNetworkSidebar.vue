<template>
    <div class="flex flex-col w-80 min-w-80 bg-[rgba(10,10,16,0.94)]">

        <!-- tabs -->
        <div class="border-b border-r border-[var(--ct-border)] bg-[rgba(11,12,20,0.96)] p-1.5">
            <div class="flex gap-x-1 rounded-lg bg-[rgba(255,255,255,0.04)] p-1">
                <button @click="tab = 'favourites'" type="button" class="flex-1 rounded-md py-1.5 text-center text-sm font-semibold transition" :class="[ tab === 'favourites' ? 'bg-[var(--ct-blue)] text-white shadow-[0_4px_16px_rgba(0,97,253,0.3)]' : 'text-[var(--ct-dim)] hover:text-[var(--ct-text)]' ]">Favourites</button>
                <button @click="tab = 'announces'" type="button" class="flex-1 rounded-md py-1.5 text-center text-sm font-semibold transition" :class="[ tab === 'announces' ? 'bg-[var(--ct-blue)] text-white shadow-[0_4px_16px_rgba(0,97,253,0.3)]' : 'text-[var(--ct-dim)] hover:text-[var(--ct-text)]' ]">Discover</button>
            </div>
        </div>

        <!-- favourites -->
        <div v-if="tab === 'favourites'" class="flex-1 flex flex-col bg-[rgba(11,12,20,0.96)] border-r border-[var(--ct-border)] overflow-hidden">

            <!-- search -->
            <div v-if="favourites.length > 0" class="border-b border-[var(--ct-border)] p-1.5">
                <div class="relative">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-[var(--ct-dim)]">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                    </svg>
                    <input v-model="favouritesSearchTerm" type="text" placeholder="Search favourites…" class="block w-full rounded-lg border !pl-8 p-2 text-sm">
                </div>
            </div>

            <!-- favourite nodes -->
            <div class="flex h-full overflow-y-auto">
                <div v-if="searchedFavourites.length > 0" class="w-full py-1">
                    <div @click="onFavouriteClick(favourite)" v-for="favourite of searchedFavourites" :key="favourite.destination_hash" class="mx-1.5 my-0.5 flex cursor-pointer items-center rounded-lg p-2 transition" :class="[ favourite.destination_hash === selectedDestinationHash ? 'bg-[rgba(0,97,253,0.18)] ring-1 ring-inset ring-[rgba(0,97,253,0.4)]' : 'hover:bg-[rgba(255,255,255,0.05)]' ]">
                        <div class="mr-2.5 shrink-0 overflow-hidden rounded-lg">
                            <Identicon :hash="favourite.destination_hash" class="size-10"/>
                        </div>
                        <div class="min-w-0">
                            <div class="truncate text-sm text-[var(--ct-text)]">{{ favourite.display_name }}</div>
                            <div class="ct-hash truncate">{{ formatDestinationHash(favourite.destination_hash) }}</div>
                        </div>
                        <div class="ml-auto shrink-0">
                            <DropDownMenu>
                                <template v-slot:button>
                                    <IconButton class="bg-transparent">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                                        </svg>
                                    </IconButton>
                                </template>
                                <template v-slot:items>

                                    <!-- rename button -->
                                    <DropDownMenuItem @click="onRenameFavourite(favourite)">
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-5">
                                            <path fill-rule="evenodd" d="M5.25 2.25a3 3 0 0 0-3 3v4.318a3 3 0 0 0 .879 2.121l9.58 9.581c.92.92 2.39 1.186 3.548.428a18.849 18.849 0 0 0 5.441-5.44c.758-1.16.492-2.629-.428-3.548l-9.58-9.581a3 3 0 0 0-2.122-.879H5.25ZM6.375 7.5a1.125 1.125 0 1 0 0-2.25 1.125 1.125 0 0 0 0 2.25Z" clip-rule="evenodd" />
                                        </svg>
                                        <span>Rename Favourite</span>
                                    </DropDownMenuItem>

                                    <!-- remove favourite button -->
                                    <div>
                                        <DropDownMenuItem @click="onRemoveFavourite(favourite)">
                                            <svg class="size-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 1 0 .23 1.482l.149-.022.841 10.518A2.75 2.75 0 0 0 7.596 19h4.807a2.75 2.75 0 0 0 2.742-2.53l.841-10.52.149.023a.75.75 0 0 0 .23-1.482A41.03 41.03 0 0 0 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4ZM8.58 7.72a.75.75 0 0 0-1.5.06l.3 7.5a.75.75 0 1 0 1.5-.06l-.3-7.5Zm4.34.06a.75.75 0 1 0-1.5-.06l-.3 7.5a.75.75 0 1 0 1.5.06l.3-7.5Z" clip-rule="evenodd" />
                                            </svg>
                                            <span class="text-red-500">Remove Favourite</span>
                                        </DropDownMenuItem>
                                    </div>

                                </template>
                            </DropDownMenu>
                        </div>
                    </div>
                </div>
                <div v-else class="mx-auto my-auto w-full">

                    <!-- no favourites at all -->
                    <EmptyState v-if="favourites.length === 0" title="No favourites yet" description="Browse a node and tap the star to save it here for quick access.">
                        <template v-slot:icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z" />
                            </svg>
                        </template>
                    </EmptyState>

                    <!-- is searching, but no results -->
                    <EmptyState v-if="favouritesSearchTerm !== '' && favourites.length > 0" title="No results" description="Your search didn't match any favourites.">
                        <template v-slot:icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                                <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                            </svg>
                        </template>
                    </EmptyState>

                </div>
            </div>
        </div>

        <!-- announces -->
        <div v-if="tab === 'announces'" class="flex-1 flex flex-col bg-[rgba(11,12,20,0.96)] border-r border-[var(--ct-border)] overflow-hidden">

            <!-- search -->
            <div v-if="nodesCount > 0" class="border-b border-[var(--ct-border)] p-1.5">
                <div class="relative">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-[var(--ct-dim)]">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                    </svg>
                    <input v-model="nodesSearchTerm" type="text" :placeholder="`Search ${nodesCount} discovered nodes…`" class="block w-full rounded-lg border !pl-8 p-2 text-sm">
                </div>
            </div>

            <!-- nodes -->
            <div class="flex h-full overflow-y-auto">
                <div v-if="searchedNodes.length > 0" class="w-full py-1">
                    <div @click="onNodeClick(node)" v-for="node of searchedNodes" :key="node.destination_hash" class="mx-1.5 my-0.5 flex cursor-pointer items-center rounded-lg p-2 transition" :class="[ node.destination_hash === selectedDestinationHash ? 'bg-[rgba(0,97,253,0.18)] ring-1 ring-inset ring-[rgba(0,97,253,0.4)]' : 'hover:bg-[rgba(255,255,255,0.05)]' ]">
                        <div class="mr-2.5 shrink-0 overflow-hidden rounded-lg">
                            <Identicon :hash="node.destination_hash" class="size-10"/>
                        </div>
                        <div class="min-w-0">
                            <div class="truncate text-sm text-[var(--ct-text)]">{{ node.display_name }}</div>
                            <div class="text-xs text-[var(--ct-dim)]">{{ formatTimeAgo(node.updated_at) }}</div>
                        </div>
                    </div>
                </div>
                <div v-else class="mx-auto my-auto w-full">

                    <!-- no nodes at all -->
                    <EmptyState v-if="nodesCount === 0" title="No nodes discovered yet" description="Nomad Network nodes appear here automatically when they announce on the network.">
                        <template v-slot:icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-7">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9.348 14.652a3.75 3.75 0 0 1 0-5.304m5.304 0a3.75 3.75 0 0 1 0 5.304m-7.425 2.121a6.75 6.75 0 0 1 0-9.546m9.546 0a6.75 6.75 0 0 1 0 9.546M5.106 18.894c-3.808-3.807-3.808-9.98 0-13.788m13.788 0c3.808 3.807 3.808 9.98 0 13.788M12 12h.008v.008H12V12Z" />
                            </svg>
                        </template>
                    </EmptyState>

                    <!-- is searching, but no results -->
                    <EmptyState v-if="nodesSearchTerm !== '' && nodesCount > 0" title="No results" description="Your search didn't match any nodes.">
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
import DropDownMenu from "../DropDownMenu.vue";
import IconButton from "../IconButton.vue";
import DropDownMenuItem from "../DropDownMenuItem.vue";
import Identicon from "../Identicon.vue";
import EmptyState from "../base/EmptyState.vue";

export default {
    name: 'NomadNetworkSidebar',
    components: {DropDownMenuItem, IconButton, DropDownMenu, Identicon, EmptyState},
    props: {
        nodes: Object,
        favourites: Array,
        selectedDestinationHash: String,
    },
    data() {
        return {
            tab: "favourites",
            favouritesSearchTerm: "",
            nodesSearchTerm: "",
        };
    },
    methods: {
        onNodeClick(node) {
            this.$emit("node-click", node);
        },
        onFavouriteClick(favourite) {
            this.onNodeClick(favourite);
        },
        onRenameFavourite(favourite) {
            this.$emit("rename-favourite", favourite);
        },
        onRemoveFavourite(favourite) {
            this.$emit("remove-favourite", favourite);
        },
        formatTimeAgo: function(datetimeString) {
            return Utils.formatTimeAgo(datetimeString);
        },
        formatDestinationHash: function(destinationHash) {
            return Utils.formatDestinationHash(destinationHash);
        },
    },
    computed: {
        nodesCount() {
            return Object.keys(this.nodes).length;
        },
        nodesOrderedByLatestAnnounce() {
            const nodes = Object.values(this.nodes);
            return nodes.sort(function(nodeA, nodeB) {
                // order by updated_at desc
                const nodeAUpdatedAt = new Date(nodeA.updated_at).getTime();
                const nodeBUpdatedAt = new Date(nodeB.updated_at).getTime();
                return nodeBUpdatedAt - nodeAUpdatedAt;
            });
        },
        searchedNodes() {
            return this.nodesOrderedByLatestAnnounce.filter((node) => {
                const search = this.nodesSearchTerm.toLowerCase();
                const matchesDisplayName = node.display_name.toLowerCase().includes(search);
                const matchesDestinationHash = node.destination_hash.toLowerCase().includes(search);
                return matchesDisplayName || matchesDestinationHash;
            });
        },
        searchedFavourites() {
            return this.favourites.filter((favourite) => {
                const search = this.favouritesSearchTerm.toLowerCase();
                const matchesDisplayName = favourite.display_name.toLowerCase().includes(search);
                const matchesCustomDisplayName = favourite.custom_display_name?.toLowerCase()?.includes(search) === true;
                const matchesDestinationHash = favourite.destination_hash.toLowerCase().includes(search);
                return matchesDisplayName || matchesCustomDisplayName || matchesDestinationHash;
            });
        },
    },
}
</script>
