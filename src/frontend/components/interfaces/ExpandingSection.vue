<template>
    <div class="ct-card divide-y divide-[var(--ct-border)] overflow-hidden">
        <div @click="isExpanded = !isExpanded" class="flex cursor-pointer justify-between p-2.5 transition hover:bg-[rgba(255,255,255,0.04)]">
            <div class="my-auto mr-auto">
                <div class="font-bold text-[var(--ct-text)]">
                    <slot name="title"/>
                </div>
                <div class="text-sm text-[var(--ct-dim)]">
                    <slot name="subtitle"/>
                </div>
            </div>
            <div class="my-auto ml-2">
                <div class="size-5 transform text-[var(--ct-dim)] transition-transform duration-200" :class="{ 'rotate-90': isExpanded }">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" class="size-5">
                        <rect width="256" height="256" fill="none"/>
                        <path d="M181.66,122.34l-80-80A8,8,0,0,0,88,48V208a8,8,0,0,0,13.66,5.66l80-80A8,8,0,0,0,181.66,122.34Z" fill="currentColor"/>
                    </svg>
                </div>
            </div>
        </div>
        <div v-if="isExpanded" class="divide-y divide-[var(--ct-border)] text-[var(--ct-text)]">
            <slot name="content"/>
        </div>
    </div>
</template>
<script>
export default {
    name: 'ExpandingSection',
    data() {
        return {
            isExpanded: false,
        };
    },
}
</script>