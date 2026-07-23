import Overlays from "./Overlays";

// All dialogs render as in-app modals (see components/overlays/ModalHost.vue).
// Native window.alert/confirm/prompt and Electron IPC dialogs are intentionally
// no longer used so the experience is consistent and on-brand everywhere.
class DialogUtils {

    static alert(message, options = {}) {
        return Overlays.alert(message, options);
    }

    static confirm(message, options = {}) {
        return Overlays.confirm(message, options);
    }

    static prompt(message, options = {}) {
        return Overlays.prompt(message, options);
    }

    static toast(message, type = "info") {
        return Overlays.toast(message, type);
    }

}

export default DialogUtils;
