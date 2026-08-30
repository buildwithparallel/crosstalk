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

            <!-- path lookup -->
            <RouterLink :to="{ name: 'path-lookup' }" class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
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

        </div>
    </div>
</template>

<script>

export default {
    name: 'ToolsPage',
}
</script>
