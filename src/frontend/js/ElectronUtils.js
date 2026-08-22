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

        const restartResponse = await window.axios.post('/api/v1/restart-backend');
        const previousInstanceId = restartResponse.data.instance_id;
        const timeoutAt = Date.now() + 30000;

        while(Date.now() < timeoutAt){
            try {
                const statusResponse = await window.axios.get('/api/v1/status', {
                    params: {
                        restart_check: Date.now(),
                    },
                    timeout: 1000,
                });

                if(statusResponse.data.instance_id !== previousInstanceId){
                    if(returnRoute){
                        window.location.hash = returnRoute;
                    }
                    window.location.reload();
                    return;
                }
            } catch(e) {
                // The backend is expected to be briefly unavailable while restarting.
            }

            await new Promise(resolve => setTimeout(resolve, 250));
        }

        throw new Error("Crosstalk backend did not restart within 30 seconds");
    }

    static async showPathInFolder(path) {
        if(window.electron){
            return await window.electron.showPathInFolder(path);
        }
    }

    /**
     * Ask for microphone access before first capture.
     * In Electron on macOS this shows the TCC prompt. In the browser it is a
     * no-op; getUserMedia will prompt instead. Returns false if denied.
     */
    static async ensureMicrophoneAccess() {
        if(window.electron?.askForMicrophoneAccess){
            return await window.electron.askForMicrophoneAccess();
        }
        return true;
    }

}

export default ElectronUtils;
