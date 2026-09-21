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
                <div class="text-lg font-bold text-[var(--ct-text)]">Path Lookup</div>
                <div class="text-sm text-[var(--ct-dim)]">See if a path to a destination is known, how many hops away it is, and which interface traffic will leave on. Reticulum only reveals the next hop, never the full route.</div>
                </div>
            </div>

            <!-- lookup form -->
            <div class="ct-card p-2.5 space-y-2">
                <div class="text-sm font-medium text-[var(--ct-text)]">Destination Hash</div>
                <input v-model="destinationHash" :disabled="isLoading" type="text" placeholder="e.g: a39610c89d18bb48c73e429582423c24" class="ct-hash block w-full rounded-lg border p-2.5">
                <div class="flex gap-x-2">
                    <button @click="lookupPath(false)" :disabled="isLoading || !cleanedDestinationHash" type="button" class="ct-brand-button rounded-lg px-2.5 py-1.5 text-sm font-semibold disabled:opacity-50">Check Path</button>
                    <button @click="lookupPath(true)" :disabled="isLoading || !cleanedDestinationHash" type="button" class="ct-secondary-button rounded-lg px-2.5 py-1.5 text-sm font-semibold disabled:opacity-50">Request from Network</button>
                </div>
                <div v-if="isLoading" class="text-sm text-[var(--ct-dim)]">{{ isRequesting ? "Requesting path from the network, this can take a while on slow links..." : "Checking..." }}</div>
            </div>

            <!-- result -->
            <div v-if="result" class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Result</div>
                <div class="divide-y divide-[var(--ct-border)] text-sm text-[var(--ct-muted)]">
                    <div v-if="result.path == null" class="p-2.5">
                        No path known to this destination. It may be offline, out of range, or may not have announced yet. Try "Request from Network", or wait for an announce.
                    </div>
                    <template v-else>
                        <div class="flex p-2.5"><span class="w-40 shrink-0 font-medium text-[var(--ct-text)]">Hops</span><span>{{ result.path.hops }}</span></div>
                        <div class="flex p-2.5"><span class="w-40 shrink-0 font-medium text-[var(--ct-text)]">Next Hop</span><span class="ct-hash break-all">{{ result.path.next_hop }}</span></div>
                        <div class="flex p-2.5"><span class="w-40 shrink-0 font-medium text-[var(--ct-text)]">Via Interface</span><span>{{ result.path.next_hop_interface }}</span></div>
                    </template>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
export default {
    name: 'PathLookupPage',
    data() {
        return {
            destinationHash: "",
            isLoading: false,
            isRequesting: false,
            result: null,
        };
    },
    computed: {
        cleanedDestinationHash() {
            // strip whitespace and angle brackets so pasted "<hash>" values work
            return this.destinationHash.replace(/[<>\s]/g, "");
        },
    },
    methods: {
        async lookupPath(requestFromNetwork) {
            this.isLoading = true;
            this.isRequesting = requestFromNetwork;
            this.result = null;
            try {
                const response = await window.axios.get(`/api/v1/destination/${this.cleanedDestinationHash}/path`, {
                    params: requestFromNetwork ? { request: "true", timeout: 30 } : {},
                    timeout: 60000,
                });
                this.result = response.data;
            } catch(e) {
                console.log(e);
                this.result = { path: null };
            } finally {
                this.isLoading = false;
                this.isRequesting = false;
            }
        },
    },
}
</script>
