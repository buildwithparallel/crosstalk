# On-device Whisper assets

Chat dictation loads Whisper Tiny fp32 weights from this directory. The files
are staged by `npm run download-whisper-assets` during `npm run build-frontend`
and are then served by Crosstalk's local web server. ONNX Runtime WASM is
bundled by Vite from `onnxruntime-web`.

fp32 is intentional: current Transformers.js / ONNX Runtime rejects the older
quantized Whisper graphs with MatMulNBits missing-scale errors.

Nothing in this folder is uploaded at runtime. Microphone audio stays in the
browser/Electron process and is transcribed on-device.

Large model binaries are gitignored. Rebuild the frontend to restore them after
a fresh clone.
