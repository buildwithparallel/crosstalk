const { app, BrowserWindow, dialog, ipcMain, shell, systemPreferences } = require('electron');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('node:path');

// remember main window
var mainWindow = null;

// remember child process for exe so we can kill it when app exits
var exeChildProcess = null;
var exePath = null;
var exeArguments = [];
var isQuitting = false;
var isRestartingBackend = false;

app.setName('Crosstalk');

// allow fetching app version via ipc
ipcMain.handle('app-version', () => {
    return app.getVersion();
});

// add support for showing an alert window via ipc
ipcMain.handle('alert', async(event, message) => {
    return await dialog.showMessageBox(mainWindow, {
        message: message,
    });
});

// add support for showing a confirm window via ipc
ipcMain.handle('confirm', async(event, message) => {

    // show confirm dialog
    const result = await dialog.showMessageBox(mainWindow, {
        type: "question",
        title: "Confirm",
        message: message,
        cancelId: 0, // esc key should press cancel button
        defaultId: 1, // enter key should press ok button
        buttons: [
            "Cancel", // 0
            "OK", // 1
        ],
    });

    // check if user clicked OK
    return result.response === 1;

});

// add support for showing a prompt window via ipc
ipcMain.handle('prompt', async(event, message) => {
    return await showPrompt(message);
});

// allow relaunching app via ipc
ipcMain.handle('relaunch', () => {
    app.relaunch();
    app.exit();
});

// allow restarting only the python backend via ipc
ipcMain.handle('restart-backend', async(event, returnRoute) => {
    await restartBackend(returnRoute);
});

// allow showing a file path in os file manager
ipcMain.handle('showPathInFolder', (event, path) => {
    shell.showItemInFolder(path);
});

// Prompt for microphone access the first time capture is requested.
// macOS needs this TCC dialog; other platforms return true immediately.
ipcMain.handle('ask-for-microphone-access', async() => {
    if(process.platform !== "darwin"){
        return true;
    }
    return await systemPreferences.askForMediaAccess('microphone');
});

function log(message) {

    // log to stdout of this process
    console.log(message);

    // make sure main window exists
    if(!mainWindow){
        return;
    }

    // make sure window is not destroyed
    if(mainWindow.isDestroyed()){
        return;
    }

    // log to web console
    mainWindow.webContents.send('log', message);

}

function getDefaultStorageDir() {

    // if we are running a windows portable exe, we want to use .crosstalk in the portable exe dir
    // e.g if we launch "E:\Some\Path\Crosstalk.exe" we want to use "E:\Some\Path\.crosstalk"
    const portableExecutableDir = process.env.PORTABLE_EXECUTABLE_DIR;
    if(process.platform === "win32" && portableExecutableDir != null){
        return path.join(portableExecutableDir, '.crosstalk');
    }

    // otherwise, we will fall back to putting the storage dir in the users home directory
    // e.g: ~/.crosstalk
    return path.join(app.getPath('home'), '.crosstalk');

}

function getDefaultReticulumConfigDir() {

    // Keep Crosstalk's Reticulum config next to its storage so a broken global
    // ~/.reticulum/config cannot prevent the app from launching.
    const portableExecutableDir = process.env.PORTABLE_EXECUTABLE_DIR;
    if(process.platform === "win32" && portableExecutableDir != null){
        return path.join(portableExecutableDir, '.crosstalk', '.reticulum');
    }

    // otherwise, use ~/.crosstalk/.reticulum
    return path.join(getDefaultStorageDir(), '.reticulum');

}

function showPrompt(message) {
    return new Promise((resolve) => {

        var didResolve = false;
        const responseChannel = `prompt-response-${Date.now()}-${Math.random()}`;

        const promptWindow = new BrowserWindow({
            width: 420,
            height: 160,
            parent: mainWindow,
            modal: true,
            resizable: false,
            minimizable: false,
            maximizable: false,
            title: message,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
            },
        });

        function finish(value) {
            if(didResolve){
                return;
            }
            didResolve = true;
            ipcMain.removeAllListeners(responseChannel);
            resolve(value);
            if(!promptWindow.isDestroyed()){
                promptWindow.close();
            }
        }

        ipcMain.once(responseChannel, (event, value) => {
            finish(value);
        });

        promptWindow.on('closed', () => {
            finish(null);
        });

        const promptHtml = `
            <!doctype html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body { font-family: system-ui, sans-serif; margin: 16px; color: #111827; }
                    label { display: block; font-size: 13px; margin-bottom: 8px; }
                    input { box-sizing: border-box; width: 100%; padding: 7px 8px; font-size: 14px; }
                    .actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 14px; }
                    button { padding: 6px 12px; font-size: 13px; }
                </style>
            </head>
            <body>
                <form id="form">
                    <label>${escapeHtml(message)}</label>
                    <input id="value" type="text" autofocus />
                    <div class="actions">
                        <button type="button" id="cancel">Cancel</button>
                        <button type="submit">OK</button>
                    </div>
                </form>
                <script>
                    const { ipcRenderer } = require('electron');
                    const channel = ${JSON.stringify(responseChannel)};
                    const input = document.getElementById('value');
                    document.getElementById('form').addEventListener('submit', (event) => {
                        event.preventDefault();
                        ipcRenderer.send(channel, input.value);
                    });
                    document.getElementById('cancel').addEventListener('click', () => {
                        ipcRenderer.send(channel, null);
                    });
                    input.focus();
                </script>
            </body>
            </html>
        `;

        promptWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(promptHtml)}`);

    });
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

app.whenReady().then(async () => {

    // use the branded dock icon in dev mode (packaged builds get it from electron-builder)
    if(process.platform === "darwin" && app.dock){
        const dockIconPath = path.join(__dirname, "build/icon.png");
        if(fs.existsSync(dockIconPath)){
            app.dock.setIcon(dockIconPath);
        }
    }

    // get arguments passed to application, and remove the provided application path
    const ignoredArguments = ["--no-sandbox", "--ozone-platform-hint=auto"];
    const userProvidedArguments = process.argv.slice(1).filter((arg) => !ignoredArguments.includes(arg));
    const shouldLaunchHeadless = userProvidedArguments.includes("--headless");

    if(!shouldLaunchHeadless){

        // create browser window
        mainWindow = new BrowserWindow({
            width: 1500,
            height: 800,
            webPreferences: {
                // used to inject logging over ipc
                preload: path.join(__dirname, 'preload.js'),
            },
        });

        // open external links in default web browser instead of electron
        mainWindow.webContents.setWindowOpenHandler(({ url }) => {

            var shouldShowInNewElectronWindow = false;

            // we want to open call.html in a new electron window
            // but all other target="_blank" links should open in the system web browser
            if(url.startsWith("http://localhost") && url.includes("/call.html")){
                shouldShowInNewElectronWindow = true;
            }

            // we want to open blob urls in a new electron window
            else if(url.startsWith("blob:")) {
                shouldShowInNewElectronWindow = true;
            }

            // open in new electron window
            if(shouldShowInNewElectronWindow){
                return {
                    action: "allow",
                };
            }

            // fallback to opening any other url in external browser
            shell.openExternal(url);
            return {
                action: "deny",
            };

        });

        // navigate to loading page
        await mainWindow.loadFile(path.join(__dirname, 'loading.html'));

    }

    // find path to python/cxfreeze reticulum crosstalk executable
    const exeName = process.platform === "win32" ? "Crosstalk.exe" : "Crosstalk";
    exePath = path.join(__dirname, `build/exe/${exeName}`);

    // if dist exe doesn't exist, check local build
    if(!fs.existsSync(exePath)){
        exePath = path.join(__dirname, '..', `build/exe/${exeName}`);
    }

    try {

        // arguments we always want to pass in
        const requiredArguments = [
            '--headless', // reticulum crosstalk usually launches default web browser, we don't want this when using electron
            '--port', '9337', // FIXME: let system pick a random unused port?
            // '--test-exception-message', 'Test Exception Message', // uncomment to test the crash dialog
        ];

        // if user didn't provide reticulum config dir, we should provide it
        if(!userProvidedArguments.includes("--reticulum-config-dir")){
            requiredArguments.push("--reticulum-config-dir", getDefaultReticulumConfigDir());
        }

        // if user didn't provide storage dir, we should provide it
        if(!userProvidedArguments.includes("--storage-dir")){
            requiredArguments.push("--storage-dir", getDefaultStorageDir());
        }

        exeArguments = [
            ...requiredArguments, // always provide required arguments
            ...userProvidedArguments, // also include any user provided arguments
        ];

        await startBackend();

    } catch(e) {
        log(e);
    }

});

async function startBackend() {

    // spawn executable
    exeChildProcess = await spawn(exePath, exeArguments);

    // log stdout
    var stdoutLines = [];
    exeChildProcess.stdout.setEncoding('utf8');
    exeChildProcess.stdout.on('data', function(data) {

        // log
        log(data.toString());

        // keep track of last 10 stdout lines
        stdoutLines.push(data.toString());
        if(stdoutLines.length > 10){
            stdoutLines.shift();
        }

    });

    // log stderr
    var stderrLines = [];
    exeChildProcess.stderr.setEncoding('utf8');
    exeChildProcess.stderr.on('data', function(data) {

        // log
        log(data.toString());

        // keep track of last 10 stderr lines
        stderrLines.push(data.toString());
        if(stderrLines.length > 10){
            stderrLines.shift();
        }

    });

    // log errors
    exeChildProcess.on('error', function(error) {
        log(error);
    });

    // quit electron app if exe dies unexpectedly
    exeChildProcess.on('exit', async function(code) {

        // if we are quitting or restarting the backend, we wanted exit to happen
        if(isQuitting || isRestartingBackend){
            return;
        }

        // if no exit code was provided, or the process exited cleanly,
        // we wanted exit to happen, so do nothing
        if(code == null || code === 0){
            return;
        }

        // tell user that Visual C++ redistributable needs to be installed on Windows
        if(code === 3221225781 && process.platform === "win32"){
            await dialog.showMessageBox(mainWindow, {
                message: "Microsoft Visual C++ redistributable must be installed to run this application.",
            });
            app.quit();
            return;
        }

        // show crash log
        const stdout = stdoutLines.join("");
        const stderr = stderrLines.join("");
        await dialog.showMessageBox(mainWindow, {
            message: [
                "Crosstalk Crashed!",
                "",
                `Exit Code: ${code}`,
                "",
                `----- stdout -----`,
                "",
                stdout,
                `----- stderr -----`,
                "",
                stderr,
            ].join("\n"),
        });

        // quit after dismissing error dialog
        app.quit();

    });

}

async function restartBackend(returnRoute = null) {

    if(isRestartingBackend){
        return;
    }

    isRestartingBackend = true;

    try {

        if(mainWindow && !mainWindow.isDestroyed()){
            await mainWindow.loadFile(path.join(__dirname, 'loading.html'), {
                query: returnRoute ? {
                    returnRoute: returnRoute,
                } : {},
            });
        }

        if(exeChildProcess){
            const processToStop = exeChildProcess;
            exeChildProcess = null;

            await new Promise((resolve) => {
                var didExit = false;
                const forceKillTimeout = setTimeout(() => {
                    if(!didExit && processToStop.exitCode == null){
                        processToStop.kill("SIGKILL");
                    }
                }, 3000);
                const giveUpTimeout = setTimeout(resolve, 6000);

                processToStop.once('exit', () => {
                    didExit = true;
                    clearTimeout(forceKillTimeout);
                    clearTimeout(giveUpTimeout);
                    resolve();
                });
                processToStop.kill();
            });
        }

        await startBackend();

    } finally {
        isRestartingBackend = false;
    }

}

function quit() {

    isQuitting = true;

    // kill python process
    if(exeChildProcess){
        exeChildProcess.kill("SIGKILL");
    }

    // quit electron app
    if(!app.isQuitting){
        app.quit();
    }

}

// quit electron if all windows are closed
app.on('window-all-closed', () => {
    quit();
});

// make sure child process is killed if app is quiting
app.on('before-quit', () => {
    app.isQuitting = true;
    quit();
});
