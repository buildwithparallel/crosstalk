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
                <div class="text-lg font-bold text-[var(--ct-text)]">Hash Inspector</div>
                <div class="text-sm text-[var(--ct-dim)]">Paste any destination hash to see everything this node knows about it.</div>
                </div>
            </div>

            <!-- input -->
            <div class="ct-card p-2.5 space-y-2">
                <div class="text-sm font-medium text-[var(--ct-text)]">Destination Hash</div>
                <input v-model="destinationHash" type="text" placeholder="e.g: a39610c89d18bb48c73e429582423c24" class="ct-hash block w-full rounded-lg border p-2.5" @keyup.enter="inspect">
                <button @click="inspect" :disabled="!cleanedDestinationHash" type="button" class="ct-brand-button rounded-lg px-2.5 py-1.5 text-sm font-semibold disabled:opacity-50">Inspect</button>
            </div>

            <!-- result -->
            <div v-if="info" class="ct-card">
                <div class="flex border-b border-[var(--ct-border)] p-2.5 font-semibold text-[var(--ct-text)]">Result</div>
                <div class="divide-y divide-[var(--ct-border)] text-sm text-[var(--ct-muted)]">

                    <div class="flex p-2.5"><span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Display Name</span><span>{{ info.announce?.display_name ?? "unknown" }}<span v-if="info.custom_display_name"> (saved as {{ info.custom_display_name }})</span></span></div>
                    <div class="flex p-2.5"><span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Blocked</span><span>{{ info.is_blocked ? "yes" : "no" }}</span></div>

                    <template v-if="info.announce">
                        <div class="flex p-2.5"><span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Aspect</span><span>{{ info.announce.aspect }}</span></div>
                        <div class="flex p-2.5"><span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Identity Hash</span><span class="ct-hash break-all">{{ info.announce.identity_hash }}</span></div>
                        <div class="flex p-2.5"><span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Last Announced</span><span>{{ info.announce.last_announced_at }}</span></div>
                        <div v-if="info.announce.rssi != null" class="flex p-2.5"><span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Signal</span><span>RSSI {{ info.announce.rssi }}dBm<span v-if="info.announce.snr != null">, SNR {{ info.announce.snr }}dB</span><span v-if="info.announce.quality != null">, Quality {{ info.announce.quality }}%</span></span></div>
                    </template>
                    <div v-else class="p-2.5">Never heard an announce from this destination.</div>

                    <div v-if="info.path" class="flex p-2.5"><span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Path</span><span>{{ info.path.hops }} {{ info.path.hops === 1 ? "hop" : "hops" }} via {{ info.path.next_hop_interface }}</span></div>
                    <div v-else class="flex p-2.5"><span class="w-44 shrink-0 font-medium text-[var(--ct-text)]">Path</span><span>no path known</span></div>

                </div>
            </div>

        </div>
    </div>
</template>

<script>
export default {
    name: 'HashInspectorPage',
    data() {
        return {
            destinationHash: "",
            info: null,
        };
    },
    computed: {
        cleanedDestinationHash() {
            // strip whitespace and angle brackets so pasted "<hash>" values work
            return this.destinationHash.replace(/[<>\s]/g, "");
        },
    },
    methods: {
        async inspect() {
            this.info = null;
            try {
                const response = await window.axios.get(`/api/v1/destination/${this.cleanedDestinationHash}/info`);
                this.info = response.data.destination_info;
            } catch(e) {
                console.log(e);
            }
        },
    },
}
</script>
