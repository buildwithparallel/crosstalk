<template>
    <div class="inline-flex min-h-11 rounded-lg shadow-sm sm:min-h-0 sm:rounded-md">
        <!-- send button -->
        <button @click="send" :disabled="!canSendMessage" type="button" class="my-auto inline-flex min-h-11 items-center rounded-l-lg px-3 py-1.5 text-sm font-semibold text-white transition sm:min-h-0 sm:px-2.5" :class="[ canSendMessage ? 'bg-[var(--ct-blue)] hover:bg-[var(--ct-blue-hover)]' : 'cursor-not-allowed bg-[rgba(255,255,255,0.12)] text-[var(--ct-dim)]']">
            <span v-if="isSendingMessage">Sending...</span>
            <span v-else class="space-x-1">
                <span>Send</span>
                <span v-if="deliveryMethod === 'direct'">(Direct Link)</span>
                <span v-if="deliveryMethod === 'opportunistic'">(Opportunistic)</span>
                <span v-if="deliveryMethod === 'propagated'">(Propagated)</span>
            </span>
        </button>
        <div class="relative">
            <!-- dropdown button -->
            <button @click="showMenu" :disabled="!canSendMessage" type="button" aria-label="Choose delivery method" class="my-auto relative inline-flex min-h-11 min-w-11 items-center justify-center rounded-r-lg border-l px-2 py-1.5 text-white transition sm:min-h-0 sm:min-w-0" :class="[ canSendMessage ? 'border-[rgba(0,0,0,0.3)] bg-[var(--ct-blue)] hover:bg-[var(--ct-blue-hover)]' : 'cursor-not-allowed border-[rgba(0,0,0,0.2)] bg-[rgba(255,255,255,0.12)] text-[var(--ct-dim)]']">
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true" data-slot="icon">
                    <path fill-rule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
                </svg>
            </button>
            <!-- dropdown menu -->
            <Transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95">
                <div v-if="isShowingMenu" v-click-outside="hideMenu" class="ct-panel absolute bottom-0 right-0 z-10 mb-12 overflow-hidden rounded-lg border border-[var(--ct-border)] sm:mb-10">
                    <div class="py-1">
                        <button @click="setDeliveryMethod(null)" type="button" class="block min-h-11 w-full whitespace-nowrap border-b border-[var(--ct-border)] px-4 py-2 text-left text-sm text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.06)] hover:text-[var(--ct-text)]">Send Automatically</button>
                        <button @click="setDeliveryMethod('direct')" type="button" class="block min-h-11 w-full whitespace-nowrap px-4 py-2 text-left text-sm text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.06)] hover:text-[var(--ct-text)]">Send over Direct Link</button>
                        <button @click="setDeliveryMethod('opportunistic')" type="button" class="block min-h-11 w-full whitespace-nowrap px-4 py-2 text-left text-sm text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.06)] hover:text-[var(--ct-text)]">Send Opportunistically</button>
                        <button @click="setDeliveryMethod('propagated')" type="button" class="block min-h-11 w-full whitespace-nowrap px-4 py-2 text-left text-sm text-[var(--ct-muted)] transition hover:bg-[rgba(255,255,255,0.06)] hover:text-[var(--ct-text)]">Send to Propagation Node</button>
                    </div>
                </div>
            </Transition>
        </div>
    </div>
</template>

<script>
export default {
    name: 'SendMessageButton',
    props: {
        deliveryMethod: String,
        canSendMessage: Boolean,
        isSendingMessage: Boolean,
    },
    data() {
        return {
            isShowingMenu: false,
        };
    },
    methods: {
        showMenu() {
            this.isShowingMenu = true;
        },
        hideMenu() {
            this.isShowingMenu = false;
        },
        setDeliveryMethod(deliveryMethod) {
            this.$emit("delivery-method-changed", deliveryMethod);
            this.hideMenu();
        },
        send() {
            this.$emit("send");
        },
    },
}
</script>
