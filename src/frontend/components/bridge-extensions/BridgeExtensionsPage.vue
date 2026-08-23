<template>
    <div class="flex flex-col flex-1 overflow-hidden min-w-full sm:min-w-[500px]">
        <div class="overflow-y-auto space-y-3 p-3">

            <div>
                <div class="text-lg font-bold text-[var(--ct-text)]">Bridge Extensions</div>
                <div class="text-sm text-[var(--ct-dim)]">
                    Paths that cannot be added as a normal connection. Crosstalk talks to a helper program instead of to the radio itself. A new kind of path is a new card here, with its own id. Radios for each kind live on that page.
                </div>
            </div>

            <RouterLink
                v-for="extension in extensions"
                :key="extension.id"
                :to="{ name: 'bridge-extensions.show', params: { id: extension.id } }"
                class="ct-card ct-card-hover group flex items-center gap-x-3 p-3">
                <div class="flex size-11 shrink-0 items-center justify-center rounded-lg border border-[rgba(0,97,253,0.3)] bg-[rgba(0,97,253,0.1)] text-[#7db0ff]">
                    <PhosphorIcon name="broadcast" weight="duotone" class="size-6"/>
                </div>
                <div class="my-auto mr-auto min-w-0">
                    <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                        <div class="font-bold text-[var(--ct-text)]">{{ extension.name }}</div>
                        <span class="ct-hash">{{ extension.id }}</span>
                    </div>
                    <div class="text-sm text-[var(--ct-dim)]">{{ extension.summary }}</div>
                    <div class="mt-1.5 flex flex-wrap items-center gap-1">
                        <span v-if="extension.frequency" class="rounded-full border border-[var(--ct-border)] px-2 py-0.5 text-xs text-[var(--ct-muted)]">{{ extension.frequency }}</span>
                        <span v-for="capability in capabilitiesFor(extension)" :key="capability" class="rounded-full border border-[var(--ct-border)] px-2 py-0.5 text-xs text-[var(--ct-muted)]">{{ capability }}</span>
                        <a
                            v-if="extension.repoUrl"
                            :href="extension.repoUrl"
                            target="_blank"
                            rel="noopener noreferrer"
                            @click.stop
                            class="inline-flex items-center gap-x-1 rounded-full border border-[var(--ct-border)] px-2 py-0.5 text-xs text-[var(--ct-muted)] hover:text-[var(--ct-text)]">
                            <span>{{ extension.repoPublic === false ? "Source (not public yet)" : repoLabel(extension.repoUrl) }}</span>
                            <PhosphorIcon name="arrow-square-out" weight="bold" class="size-3"/>
                        </a>
                    </div>
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
import PhosphorIcon from "../PhosphorIcon.vue";
import { BRIDGE_EXTENSIONS, extensionCapabilities, repoHostLabel } from "../../js/bridgeExtensions";

export default {
    name: "BridgeExtensionsPage",
    components: {
        PhosphorIcon,
    },
    data() {
        return {
            extensions: BRIDGE_EXTENSIONS,
        };
    },
    methods: {
        capabilitiesFor(extension) {
            return extensionCapabilities(extension);
        },
        repoLabel(url) {
            return repoHostLabel(url);
        },
    },
};
</script>
