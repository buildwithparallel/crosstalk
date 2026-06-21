<template>
    <button
        @click.stop="copy"
        type="button"
        :title="buttonTitle"
        :aria-label="buttonTitle"
        :disabled="!hasValue"
        class="inline-flex shrink-0 items-center justify-center rounded-md border border-[var(--ct-border)] bg-[rgba(255,255,255,0.06)] p-1 text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.1)] hover:text-[var(--ct-text)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
    >
        <svg v-if="isCopied" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4 text-green-400">
            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 7.5V6A2.25 2.25 0 0 1 10.5 3.75h6A2.25 2.25 0 0 1 18.75 6v8.25A2.25 2.25 0 0 1 16.5 16.5H15M8.25 7.5h-3A2.25 2.25 0 0 0 3 9.75V18a2.25 2.25 0 0 0 2.25 2.25h6A2.25 2.25 0 0 0 13.5 18V9.75A2.25 2.25 0 0 0 11.25 7.5h-3Z" />
        </svg>
    </button>
</template>

<script>
import DialogUtils from "../js/DialogUtils";
import Utils from "../js/Utils";

export default {
    name: "CopyButton",
    props: {
        value: {
            type: [String, Number, Boolean],
            default: "",
        },
        label: {
            type: String,
            default: "Value",
        },
    },
    data() {
        return {
            isCopied: false,
            copiedTimeout: null,
        };
    },
    beforeUnmount() {
        clearTimeout(this.copiedTimeout);
    },
    methods: {
        async copy() {
            const copied = await Utils.copyTextToClipboard(String(this.value ?? ""));
            if(!copied){
                DialogUtils.alert(`Failed to copy ${this.label}.`);
                return;
            }

            this.isCopied = true;
            clearTimeout(this.copiedTimeout);
            this.copiedTimeout = setTimeout(() => {
                this.isCopied = false;
            }, 1200);
        },
    },
    computed: {
        hasValue() {
            return this.value != null && this.value !== "";
        },
        buttonTitle() {
            return this.isCopied ? `${this.label} copied` : `Copy ${this.label}`;
        },
    },
}
</script>
