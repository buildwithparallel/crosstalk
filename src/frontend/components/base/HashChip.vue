<template>
    <span class="inline-flex min-w-0 items-center gap-x-1.5 rounded-md border border-[var(--ct-border)] bg-[rgba(255,255,255,0.04)] px-1.5 py-0.5">
        <span class="ct-hash truncate" :title="value">{{ displayValue }}</span>
        <CopyButton v-if="copyable" :value="value" :label="label" class="!border-0 !bg-transparent !p-0.5"/>
    </span>
</template>

<script>
import CopyButton from "../CopyButton.vue";

export default {
    name: "HashChip",
    components: {
        CopyButton,
    },
    props: {
        value: {
            type: String,
            default: "",
        },
        label: {
            type: String,
            default: "Hash",
        },
        // number of chars to show at each end when truncating, 0 disables truncation
        truncate: {
            type: Number,
            default: 0,
        },
        copyable: {
            type: Boolean,
            default: true,
        },
    },
    computed: {
        displayValue() {
            const value = this.value ?? "";
            if(this.truncate > 0 && value.length > this.truncate * 2 + 3){
                return `${value.slice(0, this.truncate)}…${value.slice(-this.truncate)}`;
            }
            return value;
        },
    },
};
</script>
