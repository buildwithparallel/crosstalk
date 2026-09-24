# On-device Whisper assets

Chat dictation loads Whisper Tiny fp32 weights from this directory. The files
are staged by `npm run download-whisper-assets` during `npm run build-frontend`
(pinned Hugging Face revision
`5332fcc35e32a33b86612b9a57a89be7906102b1`) and are then served by Crosstalk's
local web server. ONNX Runtime WASM is bundled by Vite from
`onnxruntime-web@1.30.0`.

fp32 is intentional: current Transformers.js / ONNX Runtime rejects the older
quantized Whisper graphs with MatMulNBits missing-scale errors.

Nothing in this folder is uploaded at runtime. Microphone audio stays in the
browser/Electron process and is transcribed on-device.

Large model binaries are gitignored. Rebuild the frontend to restore them after
a fresh clone.
