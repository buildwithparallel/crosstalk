<template>
    <Teleport to="body">
        <div class="pointer-events-none fixed bottom-5 left-1/2 z-[110] flex w-full max-w-sm -translate-x-1/2 flex-col items-center gap-y-2 px-4">
            <div
                v-for="toast in toasts"
                :key="toast.id"
                class="ct-anim-toast-in pointer-events-auto flex w-full items-center gap-x-2.5 rounded-xl border px-3.5 py-2.5 text-sm shadow-[0_16px_60px_rgba(0,0,0,0.5)] backdrop-blur"
                :class="toastClass(toast)"
                @click="dismiss(toast.id)"
            >
                <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4 shrink-0 text-[var(--ct-green)]">
                    <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
                <svg v-else-if="toast.type === 'error'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4 shrink-0 text-[var(--ct-red)]">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m0 3.75h.008v.008H12v-.008Z" />
                    <circle cx="12" cy="12" r="9" stroke-width="1.7"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor" class="size-4 shrink-0 text-[#7db0ff]">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
                </svg>
                <span class="min-w-0 flex-1 break-words text-[var(--ct-text)]">{{ toast.message }}</span>
            </div>
        </div>
    </Teleport>
</template>

<script>
import Overlays from "../../js/Overlays";

export default {
    name: "ToastHost",
    data() {
        return {
            overlaysState: Overlays.state,
        };
    },
    computed: {
        toasts() {
            return this.overlaysState.toasts;
        },
    },
    methods: {
        dismiss(id) {
            Overlays.dismissToast(id);
        },
        toastClass(toast) {
            switch(toast.type){
                case "success": return "border-[rgba(46,231,129,0.4)] bg-[rgba(14,26,20,0.94)]";
                case "error": return "border-[rgba(255,59,87,0.4)] bg-[rgba(28,14,17,0.94)]";
                default: return "border-[var(--ct-border-strong)] bg-[rgba(17,17,24,0.94)]";
            }
        },
    },
};
</script>
