<template>
    <Teleport to="body">
        <div v-if="modal" class="ct-anim-fade-in fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm" @mousedown.self="onCancel">
            <div
                ref="dialog"
                role="dialog"
                aria-modal="true"
                class="ct-anim-pop-in mx-4 w-full max-w-md rounded-2xl border border-[var(--ct-border-strong)] bg-[var(--ct-overlay)] p-5 shadow-[0_24px_90px_rgba(0,0,0,0.6)]"
                @keydown.esc.prevent="onCancel"
                @keydown.enter.prevent="onEnter"
            >

                <!-- icon + title -->
                <div class="flex items-start gap-x-3">
                    <div v-if="modal.type === 'confirm' && modal.danger" class="flex size-10 shrink-0 items-center justify-center rounded-full bg-[rgba(255,59,87,0.14)] text-[#ff8298]">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                        </svg>
                    </div>
                    <div v-else class="flex size-10 shrink-0 items-center justify-center rounded-full bg-[rgba(0,97,253,0.12)] text-[#7db0ff]">
                        <svg v-if="modal.type === 'prompt'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
                        </svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
                        </svg>
                    </div>
                    <div class="min-w-0 flex-1 pt-0.5">
                        <div v-if="modal.title" class="text-base font-semibold text-[var(--ct-text)]">{{ modal.title }}</div>
                        <div class="whitespace-pre-wrap break-words text-sm leading-relaxed text-[var(--ct-muted)]" :class="{ 'mt-1': modal.title }">{{ modal.message }}</div>
                    </div>
                </div>

                <!-- prompt input -->
                <div v-if="modal.type === 'prompt'" class="mt-4">
                    <input
                        ref="input"
                        v-model="promptValue"
                        type="text"
                        :placeholder="modal.placeholder"
                        class="block w-full rounded-lg border border-[rgba(130,143,180,0.34)] bg-[rgba(15,18,29,0.94)] p-2.5 text-sm text-[var(--ct-text)] placeholder:text-[#9aa1b8] focus:border-[var(--ct-border-focus)] focus:outline-none focus:ring-0"
                    >
                </div>

                <!-- actions -->
                <div class="mt-5 flex justify-end gap-x-2">
                    <button
                        v-if="modal.type !== 'alert'"
                        type="button"
                        class="ct-secondary-button rounded-lg px-3.5 py-2 text-sm font-semibold"
                        @click="onCancel"
                    >{{ modal.cancelLabel }}</button>
                    <button
                        ref="confirmButton"
                        type="button"
                        class="rounded-lg px-3.5 py-2 text-sm font-semibold"
                        :class="modal.danger ? 'ct-danger-button' : 'ct-brand-button'"
                        @click="onConfirm"
                    >{{ modal.confirmLabel }}</button>
                </div>

            </div>
        </div>
    </Teleport>
</template>

<script>
import Overlays from "../../js/Overlays";

export default {
    name: "ModalHost",
    data() {
        return {
            overlaysState: Overlays.state,
            promptValue: "",
        };
    },
    computed: {
        modal() {
            return this.overlaysState.modal;
        },
    },
    watch: {
        modal(newModal) {
            if(newModal){
                this.promptValue = newModal.defaultValue ?? "";
                this.$nextTick(() => {
                    if(newModal.type === "prompt" && this.$refs.input){
                        this.$refs.input.focus();
                        this.$refs.input.select();
                    } else if(this.$refs.confirmButton){
                        this.$refs.confirmButton.focus();
                    }
                });
            }
        },
    },
    methods: {
        onConfirm() {
            const modal = this.modal;
            if(!modal) return;
            if(modal.type === "prompt"){
                Overlays.closeModal(this.promptValue);
            } else if(modal.type === "confirm"){
                Overlays.closeModal(true);
            } else {
                Overlays.closeModal(undefined);
            }
        },
        onCancel() {
            const modal = this.modal;
            if(!modal) return;
            if(modal.type === "prompt"){
                Overlays.closeModal(null);
            } else if(modal.type === "confirm"){
                Overlays.closeModal(false);
            } else {
                Overlays.closeModal(undefined);
            }
        },
        onEnter() {
            this.onConfirm();
        },
    },
};
</script>
