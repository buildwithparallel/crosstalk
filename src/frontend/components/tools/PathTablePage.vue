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
                <div class="text-lg font-bold text-[var(--ct-text)]">Path Table</div>
                <div class="text-sm text-[var(--ct-dim)]">Every destination this node currently knows a route to, how many hops away it is, and which interface it routes via. Drop a path to force it to be rediscovered.</div>
                </div>
            </div>

            <!-- table -->
            <div class="ct-card">
                <div class="flex items-center gap-x-2.5 border-b border-[var(--ct-border)] p-2.5">
                    <span class="mr-auto font-semibold text-[var(--ct-text)]">{{ filteredEntries.length }} paths</span>
                    <input v-model="searchText" type="text" placeholder="Filter by name or hash..." class="rounded-lg border p-1.5 text-sm">
                    <button @click="getPathTable" type="button" class="ct-secondary-button rounded-lg px-2.5 py-1.5 text-sm font-semibold">Refresh</button>
                </div>
                <div class="divide-y divide-[var(--ct-border)] text-sm text-[var(--ct-muted)]">
                    <div v-if="filteredEntries.length === 0" class="p-2.5 text-[var(--ct-dim)]">No paths known. Paths appear as announces are received.</div>
                    <div v-for="entry in filteredEntries" :key="entry.destination_hash" class="flex items-center gap-x-2.5 p-2.5">
                        <div class="min-w-0 mr-auto">
                            <div class="truncate font-medium text-[var(--ct-text)]">{{ entry.display_name ?? "Unknown" }}<span v-if="entry.aspect" class="ml-2 text-xs font-normal text-[var(--ct-dim)]">{{ entry.aspect }}</span></div>
                            <div class="ct-hash truncate text-xs text-[var(--ct-dim)]">{{ entry.destination_hash }}</div>
                        </div>
                        <span class="shrink-0 text-xs">{{ entry.hops }} {{ entry.hops === 1 ? "hop" : "hops" }}</span>
                        <span class="shrink-0 max-w-48 truncate text-xs text-[var(--ct-dim)]" :title="entry.interface">{{ entry.interface }}</span>
                        <button @click="dropPath(entry)" type="button" class="ct-secondary-button shrink-0 rounded-lg px-2 py-1 text-xs font-semibold">Drop</button>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
import DialogUtils from "../../js/DialogUtils";

export default {
    name: 'PathTablePage',
    data() {
        return {
            entries: [],
            searchText: "",
        };
    },
    computed: {
        filteredEntries() {
            const search = this.searchText.toLowerCase().trim();
            if(!search){
                return this.entries;
            }
            return this.entries.filter((entry) => {
                return entry.destination_hash.includes(search)
                    || (entry.display_name ?? "").toLowerCase().includes(search)
                    || (entry.interface ?? "").toLowerCase().includes(search);
            });
        },
    },
    mounted() {
        this.getPathTable();
    },
    methods: {
        async getPathTable() {
            try {

                // fetch path table and announces, so we can show recognisable names for known destinations
                const [pathTableResponse, announcesResponse] = await Promise.all([
                    window.axios.get("/api/v1/path-table"),
                    window.axios.get("/api/v1/announces"),
                ]);

                // map announces by destination hash
                const announces = {};
                for(const announce of announcesResponse.data.announces){
                    announces[announce.destination_hash] = announce;
                }

                // join announce info onto path table entries, nearest destinations first
                this.entries = pathTableResponse.data.path_table.map((entry) => {
                    const announce = announces[entry.hash];
                    return {
                        destination_hash: entry.hash,
                        display_name: announce?.display_name ?? null,
                        aspect: announce?.aspect ?? null,
                        hops: entry.hops,
                        interface: entry.interface,
                    };
                }).sort((a, b) => a.hops - b.hops || a.destination_hash.localeCompare(b.destination_hash));

            } catch(e) {
                console.log(e);
            }
        },
        async dropPath(entry) {
            try {
                await window.axios.post(`/api/v1/destination/${entry.destination_hash}/drop-path`);
                await this.getPathTable();
            } catch(e) {
                DialogUtils.toast("Failed to drop path", "error");
                console.log(e);
            }
        },
    },
}
</script>
