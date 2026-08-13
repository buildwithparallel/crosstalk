# On-device chat dictation

Crosstalk can fill the chat composer from the microphone using Whisper Tiny.
Speech is transcribed in the local UI process. Audio is not sent to a cloud
speech API, Hugging Face, or any other remote service.

This is separate from **Add Voice**, which attaches Codec2 or Opus audio to an
LXMF message.

## Using dictation

1. Open a conversation.
2. Click **Dictate**.
3. Speak, then click the red **Listening** button to stop.
4. Review the text in the composer and send it as a normal message.

The first use in a session loads the local Whisper model into memory, which can
take a few seconds. Later dictations reuse that in-memory model.

Dictation uses the same microphone permission as audio calls and voice
messages. On macOS the app prompts for microphone access at launch. Windows and
Linux prompt when the microphone is first used.

## Privacy

- Microphone samples stay in RAM on the local machine.
- Transcription runs in a Web Worker with Whisper Tiny (`fp32`) and ONNX Runtime
  WASM. Quantized (`q8`) Whisper graphs are avoided because the current
  Transformers.js / ONNX Runtime combination rejects them.
- `env.allowRemoteModels` is disabled, so the worker will not fetch weights
  from the Hugging Face Hub at runtime.
- The OS/browser language is passed to Whisper as a hint. That value never
  leaves the device.

## Build-time assets

`npm run build-frontend` runs `scripts/download-whisper-assets.mjs`, which
downloads Whisper Tiny fp32 ONNX files from Hugging Face into
`src/frontend/public/assets/whisper/models/`. Vite then bundles ONNX Runtime
WASM from the local `onnxruntime-web` install.

Those files are served by Crosstalk's own HTTP server (including packaged
Electron builds). A network connection is only required while *building*, not
while dictating.

After a fresh clone, run `npm install` and `npm run build-frontend` before
using dictation.

## Limits

- Recordings stop automatically after 60 seconds.
- Very short or silent captures are ignored.
- Whisper Tiny is a small model. Accents, noise and uncommon words may need a
  quick edit before sending.
- A Raspberry Pi can run this path, but the first load and each transcription
  will be slower than on a desktop CPU.
