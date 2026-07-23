<template>
    <div class="flex flex-col items-center justify-center px-6 py-12 text-center">
        <div v-if="$slots.icon" class="mb-4 flex size-14 items-center justify-center rounded-2xl border border-[var(--ct-border)] bg-[rgba(0,97,253,0.08)] text-[#7db0ff]">
            <slot name="icon"></slot>
        </div>
        <div class="text-base font-semibold text-[var(--ct-text)]">{{ title }}</div>
        <div v-if="description" class="mt-1 max-w-sm text-sm text-[var(--ct-dim)]">{{ description }}</div>
        <div v-if="$slots.action" class="mt-5">
            <slot name="action"></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: "EmptyState",
    props: {
        title: {
            type: String,
            required: true,
        },
        description: {
            type: String,
            default: null,
        },
    },
};
</script>
