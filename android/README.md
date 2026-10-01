# Crosstalk for Android

The Android companion provides a native, OLED-friendly shell for a Crosstalk
backend running locally in Termux. The WebView is restricted to
`http://localhost:8000`; normal HTTP links leave the app and cleartext traffic
to non-local hosts is blocked by Android's network security policy.

The Python/Reticulum backend remains in Termux instead of being duplicated in
the APK. This keeps one identity and database, preserves the normal interface
configuration, and avoids shipping a second Python runtime.

## Install the Termux backend

Follow [Crosstalk on Android](../docs/crosstalk_on_android_with_termux.md), then
install the fixed controller command:

```sh
install -m 700 android/termux/crosstalk-android-server \
  "$PREFIX/bin/crosstalk-android-server"
```

The controller searches `$HOME/apps/crosstalk` and `$HOME/crosstalk`. Set
`CROSSTALK_HOME` before launching it when the checkout lives elsewhere. It
stores identity and application data under `$HOME/.local/share/crosstalk` by
default and binds the UI/API only to loopback.

To let the Android companion invoke this one fixed controller, add the
following to `~/.termux/termux.properties` and restart Termux:

```properties
allow-external-apps=true
```

Android will still require the user to grant Crosstalk the Termux
`RUN_COMMAND` permission. The app cannot execute arbitrary commands: it calls
only `$PREFIX/bin/crosstalk-android-server start`.

## Build the APK

The build has no Gradle or third-party Android dependencies. It requires JDK 8+
and Android SDK platform 29 with build-tools 35.0.1:

```sh
./android/build-apk.sh
adb install -r android/build/Crosstalk-Android.apk
```

The generated APK is debug-signed for development. Published releases should
use a project-owned signing key and verify the APK digest before installation.

## Privacy boundary

- The backend listens on `127.0.0.1:8000`, not Wi-Fi or a public interface.
- The WebView accepts navigation only within the local Crosstalk origin.
- External HTTP(S) links open in the user's normal browser.
- File access is disabled inside the WebView; attachments use Android's system
  document picker.
- Microphone access is requested only when the local Crosstalk origin asks for
  audio capture.
- Android backups are disabled for the companion. Reticulum identity material
  remains in Termux storage and is never copied into the APK.
