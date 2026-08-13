# On-device Whisper assets

Chat dictation loads Whisper Tiny weights from this directory. The files are
staged by `npm run download-whisper-assets` during `npm run build-frontend`
and are then served by Crosstalk's local web server. ONNX Runtime WASM is
bundled by Vite from `onnxruntime-web`.

Nothing in this folder is uploaded at runtime. Microphone audio stays in the
browser/Electron process and is transcribed on-device.

Large model and WASM binaries are gitignored. Rebuild the frontend to restore
them after a fresh clone.
