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

        </div>
    </div>
</template>

<script>

export default {
    name: 'ToolsPage',
}
</script>
