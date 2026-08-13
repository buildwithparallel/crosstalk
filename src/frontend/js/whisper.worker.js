/**
 * Web Worker that runs Whisper Tiny entirely on-device.
 *
 * Remote Hugging Face / CDN fetches are disabled. Model weights and ONNX
 * Runtime WASM files are loaded from Crosstalk's local static assets.
 */

import { pipeline, env } from "@huggingface/transformers";
// onnxruntime-web's package exports hide the WASM files, so Vite must load
// them from the installed dist directory instead of the package name.
import asyncifyWasmUrl from "../../../node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.asyncify.wasm?url";
import asyncifyMjsUrl from "../../../node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.asyncify.mjs?url";
import safariWasmUrl from "../../../node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.wasm?url";
import safariMjsUrl from "../../../node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.mjs?url";

const MODEL_ID = "Xenova/whisper-tiny";

function isSafari() {
    if (typeof navigator === "undefined") {
        return false;
    }
    const userAgent = navigator.userAgent;
    const vendor = navigator.vendor || "";
    const isAppleVendor = vendor.indexOf("Apple") > -1;
    const notOtherBrowser = !userAgent.match(/CriOS|FxiOS|EdgiOS|OPiOS|mercury|brave/i)
        && !userAgent.includes("Chrome")
        && !userAgent.includes("Android");
    return isAppleVendor && notOtherBrowser;
}

// Serve weights and WASM from this origin only. Never fall back to the Hub.
env.allowLocalModels = true;
env.allowRemoteModels = false;
env.localModelPath = "/assets/whisper/models/";
env.useBrowserCache = true;
env.backends.onnx.wasm.numThreads = 1;
env.backends.onnx.wasm.proxy = false;
env.backends.onnx.wasm.wasmPaths = isSafari()
    ? {
        mjs: safariMjsUrl,
        wasm: safariWasmUrl,
    }
    : {
        mjs: asyncifyMjsUrl,
        wasm: asyncifyWasmUrl,
    };

let transcriber = null;
let loadPromise = null;

async function getTranscriber() {
    if (transcriber) {
        return transcriber;
    }
    if (!loadPromise) {
        loadPromise = pipeline("automatic-speech-recognition", MODEL_ID, {
            dtype: "q8",
            device: "wasm",
            progress_callback: (progress) => {
                self.postMessage({
                    type: "progress",
                    progress,
                });
            },
        }).then((instance) => {
            transcriber = instance;
            return instance;
        }).catch((error) => {
            loadPromise = null;
            throw error;
        });
    }
    return loadPromise;
}

self.onmessage = async (event) => {
    const { type, requestId, audio, language } = event.data || {};

    try {
        if (type === "load") {
            await getTranscriber();
            self.postMessage({ type: "ready", requestId });
            return;
        }

        if (type === "transcribe") {
            const asr = await getTranscriber();
            const options = {
                task: "transcribe",
                return_timestamps: false,
            };
            if (language) {
                options.language = language;
            }
            const result = await asr(audio, options);
            const text = typeof result?.text === "string" ? result.text : "";
            self.postMessage({
                type: "result",
                requestId,
                text,
            });
            return;
        }
    } catch (error) {
        self.postMessage({
            type: "error",
            requestId,
            message: error?.message || String(error),
        });
    }
};
