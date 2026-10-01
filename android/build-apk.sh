#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
sdk_dir=${ANDROID_SDK_ROOT:-"$HOME/Library/Android/sdk"}
platform=${ANDROID_PLATFORM:-android-29}
build_tools_version=${ANDROID_BUILD_TOOLS:-35.0.1}
android_jar="$sdk_dir/platforms/$platform/android.jar"
build_tools="$sdk_dir/build-tools/$build_tools_version"
output_apk=${OUTPUT_APK:-"$project_dir/build/Crosstalk-Android.apk"}
keystore=${ANDROID_DEBUG_KEYSTORE:-"$HOME/.android/debug.keystore"}
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM

[ -r "$android_jar" ] || { printf 'Missing %s\n' "$android_jar" >&2; exit 1; }
for tool in aapt2 d8 zipalign apksigner; do
    [ -x "$build_tools/$tool" ] || { printf 'Missing build tool: %s\n' "$build_tools/$tool" >&2; exit 1; }
done

mkdir -p "$work_dir/classes" "$work_dir/dex" "$work_dir/generated" "$(dirname -- "$output_apk")"
"$build_tools/aapt2" compile --dir "$project_dir/res" -o "$work_dir/resources.zip"
"$build_tools/aapt2" link -o "$work_dir/unsigned.apk" -I "$android_jar" \
    --manifest "$project_dir/AndroidManifest.xml" --min-sdk-version 26 --target-sdk-version 29 \
    --auto-add-overlay -R "$work_dir/resources.zip" --java "$work_dir/generated"
find "$project_dir/src" "$work_dir/generated" -name '*.java' -print0 | \
    xargs -0 javac --release 8 -classpath "$android_jar" -d "$work_dir/classes"
"$build_tools/d8" --lib "$android_jar" --min-api 26 --output "$work_dir/dex" \
    $(find "$work_dir/classes" -name '*.class' -print)
zip -q -j "$work_dir/unsigned.apk" "$work_dir/dex/classes.dex"
"$build_tools/zipalign" -f 4 "$work_dir/unsigned.apk" "$work_dir/aligned.apk"

if [ ! -r "$keystore" ]; then
    mkdir -p "$(dirname -- "$keystore")"
    keytool -genkeypair -keystore "$keystore" -storepass android -keypass android \
        -alias androiddebugkey -dname "CN=Android Debug,O=Android,C=US" \
        -keyalg RSA -keysize 2048 -validity 10000 >/dev/null 2>&1
fi
"$build_tools/apksigner" sign --ks "$keystore" --ks-pass pass:android --key-pass pass:android \
    --out "$output_apk" "$work_dir/aligned.apk"
"$build_tools/apksigner" verify --verbose "$output_apk"
printf '%s\n' "$output_apk"
