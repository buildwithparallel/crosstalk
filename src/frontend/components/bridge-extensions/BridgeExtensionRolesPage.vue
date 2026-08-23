<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <div>
                <RouterLink :to="{ name: 'bridge-extensions' }" class="text-xs font-semibold uppercase tracking-wide text-[var(--ct-dim)] hover:text-[var(--ct-text)]">Bridge Extensions</RouterLink>
                <div class="mt-1 flex flex-wrap items-center gap-2">
                    <div class="text-lg font-bold text-[var(--ct-text)]">{{ extension.name }}</div>
                    <span class="ct-hash">{{ extension.id }}</span>
                    <CopyButton :value="extension.id" label="Extension ID"/>
                </div>
                <div class="mt-1 text-sm text-[var(--ct-text)]">{{ extension.headline }}</div>
                <div class="text-sm text-[var(--ct-dim)]">
                    Frequency {{ extension.frequency }} ({{ extension.frequencyNote }}). Crosstalk encryption does not go over the radio; anyone with a receiver can read that part.
                </div>
                <a
                    v-if="extension.repoUrl"
                    :href="extension.repoUrl"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="mt-2 inline-flex items-center gap-x-1 text-sm font-semibold text-[#7db0ff] hover:text-white">
                    <span>{{ extension.repoPublic === false ? "Source (not public yet)" : "Source" }}</span>
                    <PhosphorIcon name="arrow-square-out" weight="bold" class="size-3.5"/>
                </a>
            </div>

            <div class="text-sm font-semibold text-[var(--ct-text)]">Choose a radio</div>

            <RouterLink
                v-for="role in extension.roles"
                :key="role.id"
                :to="{ name: 'bridge-extensions.role', params: { id: extension.id, roleId: role.id } }"
                class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <PhosphorIcon :name="role.icon || 'broadcast'" weight="duotone" class="size-6"/>
                </div>
                <div class="my-auto mr-auto min-w-0">
                    <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                        <div class="font-bold text-[var(--ct-text)]">{{ role.hardware }}</div>
                        <span class="rounded-full border border-[var(--ct-border)] px-2 py-0.5 text-xs text-[var(--ct-muted)]">{{ role.kind }}</span>
                        <span v-if="roleStatus(role)" class="rounded-full border px-2 py-0.5 text-xs" :class="roleStatusTone(role)">{{ roleStatus(role) }}</span>
                    </div>
                    <div class="text-sm text-[var(--ct-dim)]">{{ role.summary }}</div>
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
import CopyButton from "../CopyButton.vue";
import PhosphorIcon from "../PhosphorIcon.vue";
import { LAST_RESORT_HOP_ID } from "../../js/bridgeExtensions";

export default {
    name: "BridgeExtensionRolesPage",
    components: {
        CopyButton,
        PhosphorIcon,
    },
    props: {
        extension: {
            type: Object,
            required: true,
        },
    },
    data() {
        return {
            processes: {},
            refreshTimer: null,
        };
    },
    mounted() {
        if (this.extension.id === LAST_RESORT_HOP_ID) {
            this.refresh();
            this.refreshTimer = setInterval(this.refresh, 4000);
        }
    },
    beforeUnmount() {
        clearInterval(this.refreshTimer);
    },
    methods: {
        roleStatus(role) {
            const process = this.processes[role.processRole];
            if (process?.running) {
                return "running here";
            }
            return "";
        },
        roleStatusTone() {
            return "border-green-400/40 bg-green-500/10 text-green-200";
        },
        async refresh() {
            try {
                const response = await window.axios.get("/api/v1/hf-bridges");
                this.processes = response.data.processes || {};
            } catch (error) {
                this.processes = {};
            }
        },
    },
};
</script>
