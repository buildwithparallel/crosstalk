<template>
    <button
        type="button"
        class="inline-flex cursor-pointer items-center gap-2.5 select-none"
        role="switch"
        :aria-checked="modelValue ? 'true' : 'false'"
        @click="$emit('update:modelValue', !modelValue)">
        <span
            class="inline-flex h-5 w-9 shrink-0 rounded-full border p-0.5 transition"
            :class="modelValue
                ? 'border-[var(--ct-blue)] bg-[var(--ct-blue)]'
                : 'border-[var(--ct-border-strong)] bg-[rgba(255,255,255,0.08)]'"
            aria-hidden="true">
            <span
                class="h-3.5 w-3.5 rounded-full shadow transition"
                :class="modelValue ? 'translate-x-3.5 bg-white' : 'translate-x-0 bg-[#d7def2]'"></span>
        </span>
        <span v-if="$slots.default" class="min-w-0 text-sm text-[var(--ct-text)]">
            <slot></slot>
        </span>
    </button>
</template>

<script>
export default {
    name: "BaseToggle",
    emits: ["update:modelValue"],
    props: {
        modelValue: {
            type: Boolean,
            default: false,
        },
    },
};
</script>
