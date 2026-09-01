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
                <div class="text-lg font-bold text-[var(--ct-text)]">Log Viewer</div>
                <div class="text-sm text-[var(--ct-dim)]">Recent Reticulum log output. Useful for diagnosing interface problems, sync activity and delivery issues without a terminal.</div>
                </div>
            </div>

            <!-- logs -->
            <div class="ct-card">
                <div class="flex items-center gap-x-2.5 border-b border-[var(--ct-border)] p-2.5">
                    <span class="mr-auto font-semibold text-[var(--ct-text)]">{{ filteredLogs.length }}<span v-if="searchText"> of {{ logs.length }}</span> lines</span>
                    <input v-model="searchText" type="text" placeholder="Search logs..." class="rounded-lg border p-1.5 text-sm">
                    <label class="flex cursor-pointer items-center gap-x-1.5 text-sm text-[var(--ct-dim)]">
                        <input v-model="colorize" type="checkbox" class="size-4 rounded border">
                        Color by level
                    </label>
                    <label class="flex cursor-pointer items-center gap-x-1.5 text-sm text-[var(--ct-dim)]">
                        <input v-model="autoRefresh" type="checkbox" class="size-4 rounded border">
                        Auto refresh
                    </label>
                </div>
                <div class="max-h-[70vh] overflow-y-auto p-2.5">
                    <div v-if="filteredLogs.length === 0" class="text-sm text-[var(--ct-dim)]">{{ searchText ? "No log lines match your search." : "No log lines yet." }}</div>
                    <div v-for="(line, index) in filteredLogs" :key="index" class="ct-hash whitespace-pre-wrap break-all border-b border-[var(--ct-border)] py-0.5 text-xs text-[var(--ct-muted)] last:border-b-0" :style="colorize ? levelStyle(line) : null">{{ line }}</div>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
export default {
    name: 'LogViewerPage',
    data() {
        return {
            logs: [],
            searchText: "",
            colorize: true,
            autoRefresh: true,
            refreshInterval: null,
        };
    },
    computed: {
        filteredLogs() {
            // newest lines first, filtered by search text
            const search = this.searchText.toLowerCase().trim();
            const reversed = [...this.logs].reverse();
            if(!search){
                return reversed;
            }
            return reversed.filter((line) => line.toLowerCase().includes(search));
        },
    },
    mounted() {
        this.getLogs();
        this.refreshInterval = setInterval(() => {
            if(this.autoRefresh){
                this.getLogs();
            }
        }, 2000);
    },
    beforeUnmount() {
        clearInterval(this.refreshInterval);
    },
    methods: {
        levelStyle(line) {
            // rns log lines carry their level like "[2026-09-01 12:00:00] [Error] ..."
            // inline style so the colors are not overridden by the ct-hash class
            if(line.includes("[Critical]") || line.includes("[Error]")){
                return { color: "#f87171" };
            }
            if(line.includes("[Warning]")){
                return { color: "#fbbf24" };
            }
            if(line.includes("[Verbose]") || line.includes("[Debug]") || line.includes("[Extreme]")){
                return { color: "var(--ct-dim)" };
            }
            return null;
        },
        async getLogs() {
            try {
                const response = await window.axios.get("/api/v1/logs");
                this.logs = response.data.logs;
            } catch(e) {
                console.log(e);
            }
        },
    },
}
</script>
