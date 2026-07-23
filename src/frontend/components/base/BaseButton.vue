<template>
    <button
        :type="type"
        :disabled="disabled"
        :class="[variantClass, sizeClass]"
        class="inline-flex items-center justify-center gap-x-1.5 rounded-lg font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        @click="$emit('click', $event)"
    >
        <slot></slot>
    </button>
</template>

<script>
export default {
    name: "BaseButton",
    emits: ["click"],
    props: {
        variant: {
            type: String,
            default: "primary", // primary | secondary | danger | ghost
        },
        size: {
            type: String,
            default: "md", // sm | md | lg
        },
        type: {
            type: String,
            default: "button",
        },
        disabled: {
            type: Boolean,
            default: false,
        },
    },
    computed: {
        variantClass() {
            switch(this.variant){
                case "secondary": return "ct-secondary-button";
                case "danger": return "ct-danger-button";
                case "ghost": return "ct-ghost-button";
                default: return "ct-brand-button";
            }
        },
        sizeClass() {
            switch(this.size){
                case "sm": return "px-2.5 py-1.5 text-xs";
                case "lg": return "px-5 py-2.5 text-sm";
                default: return "px-3.5 py-2 text-sm";
            }
        },
    },
};
</script>
