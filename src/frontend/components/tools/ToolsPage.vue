<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <!-- page header -->
            <div>
                <div class="text-lg font-bold text-[var(--ct-text)]">Diagnostics</div>
                <div class="text-sm text-[var(--ct-dim)]">Useful utilities for testing and diagnosing your network.</div>
            </div>

            <!-- ping -->
            <RouterLink :to="{ name: 'ping' }" class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
                        <path fill-rule="evenodd" d="M14.615 1.595a.75.75 0 0 1 .359.852L12.982 9.75h7.268a.75.75 0 0 1 .548 1.262l-10.5 11.25a.75.75 0 0 1-1.272-.71l1.992-7.302H3.75a.75.75 0 0 1-.548-1.262l10.5-11.25a.75.75 0 0 1 .913-.143Z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="my-auto mr-auto">
                    <div class="font-bold text-[var(--ct-text)]">Ping</div>
                    <div class="text-sm text-[var(--ct-dim)]">Check if a destination is reachable, and measure round-trip time and signal quality.</div>
                </div>
                <div class="my-auto text-[var(--ct-dim)] group-hover:text-[var(--ct-text)]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                    </svg>
                </div>
            </RouterLink>



            <!-- propagation sync -->
            <RouterLink :to="{ name: 'propagation-health' }" class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
                        <path fill-rule="evenodd" d="M4.755 10.059a7.5 7.5 0 0 1 12.548-3.364l1.903 1.903h-3.183a.75.75 0 1 0 0 1.5h4.992a.75.75 0 0 0 .75-.75V4.356a.75.75 0 0 0-1.5 0v3.18l-1.9-1.9A9 9 0 0 0 3.306 9.67a.75.75 0 1 0 1.45.388Zm15.408 3.352a.75.75 0 0 0-.919.53 7.5 7.5 0 0 1-12.548 3.364l-1.902-1.903h3.183a.75.75 0 0 0 0-1.5H2.984a.75.75 0 0 0-.75.75v4.992a.75.75 0 0 0 1.5 0v-3.18l1.9 1.9a9 9 0 0 0 15.059-4.035.75.75 0 0 0-.53-.918Z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="my-auto mr-auto">
                    <div class="font-bold text-[var(--ct-text)]">Propagation Sync</div>
                    <div class="text-sm text-[var(--ct-dim)]">Health of message syncing with your preferred propagation node, and a manual sync trigger.</div>
                </div>
                <div class="my-auto text-[var(--ct-dim)] group-hover:text-[var(--ct-text)]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                    </svg>
                </div>
            </RouterLink>


            <!-- live activity -->
            <RouterLink :to="{ name: 'rf-activity' }" class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
                        <path d="M3.53 2.47a.75.75 0 0 0-1.06 1.06 18.72 18.72 0 0 0 0 16.94.75.75 0 1 0 1.34-.68 17.22 17.22 0 0 1 0-15.58.75.75 0 0 0-.28-1.02v.28ZM20.47 2.47a.75.75 0 0 1 1.06 1.06 18.72 18.72 0 0 1 0 16.94.75.75 0 1 1-1.34-.68 17.22 17.22 0 0 0 0-15.58.75.75 0 0 1 .28-1.02v.28Z" />
                        <path d="M6.7 5.65a.75.75 0 1 0-1.3-.75 14.22 14.22 0 0 0 0 14.2.75.75 0 0 0 1.3-.75 12.72 12.72 0 0 1 0-12.7ZM18.6 4.9a.75.75 0 1 0-1.3.75 12.72 12.72 0 0 1 0 12.7.75.75 0 0 0 1.3.75 14.22 14.22 0 0 0 0-14.2Z" />
                        <path d="M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" />
                    </svg>
                </div>
                <div class="my-auto mr-auto">
                    <div class="font-bold text-[var(--ct-text)]">Live Activity</div>
                    <div class="text-sm text-[var(--ct-dim)]">Watch announces arrive in real time with signal readings, and monitor interface traffic.</div>
                </div>
                <div class="my-auto text-[var(--ct-dim)] group-hover:text-[var(--ct-text)]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                    </svg>
                </div>
            </RouterLink>

            <!-- advanced tools -->
            <button @click="showAdvanced = !showAdvanced" type="button" class="flex w-full items-center gap-x-1.5 px-1 text-sm font-semibold text-[var(--ct-dim)] hover:text-[var(--ct-text)]">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4 transition-transform" :class="{ 'rotate-90': showAdvanced }">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                </svg>
                Advanced
            </button>


            <!-- path lookup -->
            <RouterLink v-if="showAdvanced" :to="{ name: 'path-lookup' }" class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
                        <path fill-rule="evenodd" d="M8.161 2.58a1.875 1.875 0 0 1 1.678 0l4.993 2.498c.106.052.23.052.336 0l3.869-1.935A1.875 1.875 0 0 1 21.75 4.82v12.485c0 .71-.401 1.36-1.037 1.677l-4.875 2.437a1.875 1.875 0 0 1-1.676 0l-4.994-2.497a.375.375 0 0 0-.336 0l-3.868 1.935A1.875 1.875 0 0 1 2.25 19.18V6.695c0-.71.401-1.36 1.036-1.677l4.875-2.437ZM9 6a.75.75 0 0 1 .75.75V15a.75.75 0 0 1-1.5 0V6.75A.75.75 0 0 1 9 6Zm6.75 3a.75.75 0 0 0-1.5 0v8.25a.75.75 0 0 0 1.5 0V9Z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="my-auto mr-auto">
                    <div class="font-bold text-[var(--ct-text)]">Path Lookup</div>
                    <div class="text-sm text-[var(--ct-dim)]">Check if a path to a destination is known, its hop count, and which interface it uses.</div>
                </div>
                <div class="my-auto text-[var(--ct-dim)] group-hover:text-[var(--ct-text)]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                    </svg>
                </div>
            </RouterLink>

            <!-- path table -->
            <RouterLink v-if="showAdvanced" :to="{ name: 'path-table' }" class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
                        <path fill-rule="evenodd" d="M2.625 6.75a1.125 1.125 0 1 1 2.25 0 1.125 1.125 0 0 1-2.25 0Zm4.875 0A.75.75 0 0 1 8.25 6h12a.75.75 0 0 1 0 1.5h-12a.75.75 0 0 1-.75-.75ZM2.625 12a1.125 1.125 0 1 1 2.25 0 1.125 1.125 0 0 1-2.25 0ZM7.5 12a.75.75 0 0 1 .75-.75h12a.75.75 0 0 1 0 1.5h-12A.75.75 0 0 1 7.5 12Zm-4.875 5.25a1.125 1.125 0 1 1 2.25 0 1.125 1.125 0 0 1-2.25 0Zm4.875 0a.75.75 0 0 1 .75-.75h12a.75.75 0 0 1 0 1.5h-12a.75.75 0 0 1-.75-.75Z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="my-auto mr-auto">
                    <div class="font-bold text-[var(--ct-text)]">Path Table</div>
                    <div class="text-sm text-[var(--ct-dim)]">All destinations this node knows a route to, and which interface each routes via.</div>
                </div>
                <div class="my-auto text-[var(--ct-dim)] group-hover:text-[var(--ct-text)]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                    </svg>
                </div>
            </RouterLink>

            <!-- hash inspector -->
            <RouterLink v-if="showAdvanced" :to="{ name: 'hash-inspector' }" class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
                        <path fill-rule="evenodd" d="M10.5 3.75a6.75 6.75 0 1 0 0 13.5 6.75 6.75 0 0 0 0-13.5ZM2.25 10.5a8.25 8.25 0 1 1 14.59 5.28l4.69 4.69a.75.75 0 1 1-1.06 1.06l-4.69-4.69A8.25 8.25 0 0 1 2.25 10.5Z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="my-auto mr-auto">
                    <div class="font-bold text-[var(--ct-text)]">Hash Inspector</div>
                    <div class="text-sm text-[var(--ct-dim)]">Paste any destination hash to see everything this node knows about it.</div>
                </div>
                <div class="my-auto text-[var(--ct-dim)] group-hover:text-[var(--ct-text)]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                    </svg>
                </div>
            </RouterLink>

            <RouterLink v-if="showAdvanced" :to="{ name: 'log-viewer' }" class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6">
                        <path fill-rule="evenodd" d="M2.25 6a3 3 0 0 1 3-3h13.5a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H5.25a3 3 0 0 1-3-3V6Zm3.97.97a.75.75 0 0 1 1.06 0l2.25 2.25a.75.75 0 0 1 0 1.06l-2.25 2.25a.75.75 0 0 1-1.06-1.06l1.72-1.72-1.72-1.72a.75.75 0 0 1 0-1.06Zm4.28 4.28a.75.75 0 0 0 0 1.5h3a.75.75 0 0 0 0-1.5h-3Z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="my-auto mr-auto">
                    <div class="font-bold text-[var(--ct-text)]">Log Viewer</div>
                    <div class="text-sm text-[var(--ct-dim)]">Recent Reticulum log output for diagnosing interface, sync and delivery problems.</div>
                </div>
                <div class="my-auto text-[var(--ct-dim)] group-hover:text-[var(--ct-text)]">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                    </svg>
                </div>
            </RouterLink>

        </div>
    </div>
</template>

<script>

export default {
    name: 'ToolsPage',
    data() {
        return {
            showAdvanced: false,
        };
    },
}
</script>
