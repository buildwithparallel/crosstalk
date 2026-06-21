class ElectronUtils {

    static isElectron() {
        return window.electron != null;
    }

    static async relaunch() {
        if(window.electron){
            return await window.electron.relaunch();
        }
    }

    static async restartBackend(returnRoute = null) {
        if(window.electron){
            return await window.electron.restartBackend(returnRoute);
        }
    }

    static async showPathInFolder(path) {
        if(window.electron){
            return await window.electron.showPathInFolder(path);
        }
    }

}

export default ElectronUtils;
