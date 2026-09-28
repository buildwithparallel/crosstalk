<template>
    <div class="inline-flex rounded-md shadow-sm">

        <button
            v-if="isActive"
            @click="toggle"
            type="button"
            :aria-label="ariaLabel"
            class="my-auto mr-1 inline-flex min-h-11 items-center gap-x-1 rounded-lg bg-red-500 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-red-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-500 sm:min-h-0 sm:rounded-md">
            <MaterialDesignIcon icon-name="microphone-message" class="size-5"/>
            <span class="ml-1">{{ activeLabel }}</span>
        </button>

        <button
            v-else
            @click="toggle"
            type="button"
            :disabled="isBusy"
            :aria-label="ariaLabel"
            class="my-auto mr-1 inline-flex min-h-11 min-w-11 items-center justify-center gap-x-1 rounded-lg ct-secondary-button px-2.5 py-1.5 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 sm:min-h-0 sm:min-w-0 sm:rounded-md disabled:opacity-50">
            <MaterialDesignIcon icon-name="microphone-message" class="size-5"/>
            <span class="ml-1 hidden xl:inline-block whitespace-nowrap">{{ idleLabel }}</span>
        </button>

    </div>
</template>

<script>
import MaterialDesignIcon from "../MaterialDesignIcon.vue";

/**
 * Composer control that records speech and fills the chat text field.
 * Distinct from Add Voice, which attaches encoded audio to the LXMF message.
 */
export default {
    name: "DictateButton",
    components: {
        MaterialDesignIcon,
    },
    props: {
        /**
         * idle | loading | recording | transcribing
         */
        state: {
            type: String,
            default: "idle",
        },
        duration: {
            type: String,
            default: "00:00",
        },
    },
    computed: {
        isActive() {
            return this.state === "recording";
        },
        isBusy() {
            return this.state === "loading" || this.state === "transcribing";
        },
        idleLabel() {
            if (this.state === "loading") {
                return "Loading…";
            }
            if (this.state === "transcribing") {
                return "Transcribing…";
            }
            return "Dictate";
        },
        activeLabel() {
            return `Listening: ${this.duration}`;
        },
        ariaLabel() {
            if (this.state === "recording") {
                return "Stop dictation";
            }
            if (this.state === "loading") {
                return "Loading on-device speech model";
            }
            if (this.state === "transcribing") {
                return "Transcribing speech";
            }
            return "Dictate message";
        },
    },
    methods: {
        toggle() {
            if (this.isBusy) {
                return;
            }
            this.$emit("toggle");
        },
    },
}
</script>
