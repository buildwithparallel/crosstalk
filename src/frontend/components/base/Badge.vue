<template>
    <span :class="variantClass" class="inline-flex items-center gap-x-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset">
        <span v-if="dot" class="ct-status-dot" :class="dotClass" style="width: 6px; height: 6px;"></span>
        <slot></slot>
    </span>
</template>

<script>
export default {
    name: "Badge",
    props: {
        variant: {
            type: String,
            default: "neutral", // green | red | amber | blue | neutral
        },
        dot: {
            type: Boolean,
            default: false,
        },
    },
    computed: {
        variantClass() {
            switch(this.variant){
                case "green": return "bg-[rgba(46,231,129,0.12)] text-[#5df2a4] ring-[rgba(46,231,129,0.35)]";
                case "red": return "bg-[rgba(255,59,87,0.12)] text-[#ff8298] ring-[rgba(255,59,87,0.35)]";
                case "amber": return "bg-[rgba(255,153,0,0.12)] text-[#ffb84d] ring-[rgba(255,153,0,0.35)]";
                case "blue": return "bg-[rgba(0,97,253,0.14)] text-[#7db0ff] ring-[rgba(0,97,253,0.4)]";
                default: return "bg-[rgba(255,255,255,0.06)] text-[var(--ct-muted)] ring-[var(--ct-border-strong)]";
            }
        },
        dotClass() {
            switch(this.variant){
                case "green": return "online";
                case "red": return "error";
                default: return "offline";
            }
        },
    },
};
</script>
