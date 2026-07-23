import { reactive } from "vue";

// central reactive state rendered by ModalHost.vue and ToastHost.vue
const state = reactive({
    modal: null, // { type, title, message, placeholder, defaultValue, confirmLabel, cancelLabel, danger, resolve }
    toasts: [], // [{ id, message, type }]
});

let nextToastId = 1;

class Overlays {

    static get state() {
        return state;
    }

    // shows an informational modal, resolves when dismissed
    static alert(message, options = {}) {
        return new Promise((resolve) => {
            state.modal = {
                type: "alert",
                title: options.title ?? null,
                message: String(message ?? ""),
                confirmLabel: options.confirmLabel ?? "OK",
                resolve,
            };
        });
    }

    // resolves true when confirmed, false when cancelled
    static confirm(message, options = {}) {
        return new Promise((resolve) => {
            state.modal = {
                type: "confirm",
                title: options.title ?? null,
                message: String(message ?? ""),
                confirmLabel: options.confirmLabel ?? "Confirm",
                cancelLabel: options.cancelLabel ?? "Cancel",
                danger: options.danger ?? false,
                resolve,
            };
        });
    }

    // resolves the entered string when confirmed, null when cancelled
    static prompt(message, options = {}) {
        return new Promise((resolve) => {
            state.modal = {
                type: "prompt",
                title: options.title ?? null,
                message: String(message ?? ""),
                placeholder: options.placeholder ?? "",
                defaultValue: options.defaultValue ?? "",
                confirmLabel: options.confirmLabel ?? "OK",
                cancelLabel: options.cancelLabel ?? "Cancel",
                resolve,
            };
        });
    }

    static closeModal(result) {
        if(state.modal){
            state.modal.resolve(result);
            state.modal = null;
        }
    }

    // transient notification, type: info | success | error
    static toast(message, type = "info", durationMs = 3500) {
        const id = nextToastId++;
        state.toasts.push({ id, message: String(message ?? ""), type });
        setTimeout(() => Overlays.dismissToast(id), durationMs);
        return id;
    }

    static dismissToast(id) {
        const index = state.toasts.findIndex((toast) => toast.id === id);
        if(index !== -1){
            state.toasts.splice(index, 1);
        }
    }

}

export default Overlays;
