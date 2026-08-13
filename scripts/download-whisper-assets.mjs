#!/usr/bin/env node
/**
 * Download and stage the on-device Whisper assets used by chat dictation.
 *
 * This keeps speech-to-text fully local at runtime:
 * - Whisper Tiny weights are fetched from Hugging Face at *build* time.
 * - ONNX Runtime WASM is bundled by Vite from the local onnxruntime-web install.
 * - The packaged app then loads both from its own static file server.
 *
 * Audio recorded in the UI is never uploaded anywhere.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const assetsRoot = path.join(repoRoot, "src", "frontend", "public", "assets", "whisper");
const modelDir = path.join(assetsRoot, "models", "Xenova", "whisper-tiny");

const MODEL_HOST = "https://huggingface.co";
const MODEL_ID = "Xenova/whisper-tiny";
const MODEL_REVISION = "main";
const USER_AGENT = "crosstalk-whisper-asset-download";

/**
 * Small tokenizer/config files plus the quantized encoder/decoder used with dtype q8.
 * Larger fp16/fp32 ONNX variants are intentionally omitted to keep the app size down.
 */
const MODEL_FILES = [
    "added_tokens.json",
    "config.json",
    "generation_config.json",
    "merges.txt",
    "normalizer.json",
    "preprocessor_config.json",
    "quant_config.json",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "onnx/encoder_model_quantized.onnx",
    "onnx/decoder_model_merged_quantized.onnx",
];

function modelFileUrl(relativePath) {
    return `${MODEL_HOST}/${MODEL_ID}/resolve/${MODEL_REVISION}/${relativePath}`;
}

async function downloadFile(url, destinationPath) {
    await fs.promises.mkdir(path.dirname(destinationPath), { recursive: true });

    const response = await fetch(url, {
        headers: {
            "User-Agent": USER_AGENT,
        },
        redirect: "follow",
    });

    if (!response.ok) {
        throw new Error(`Failed to download ${url} (${response.status} ${response.statusText})`);
    }

    const bytes = Buffer.from(await response.arrayBuffer());
    await fs.promises.writeFile(destinationPath, bytes);
    return bytes.length;
}

function fileLooksComplete(filePath) {
    try {
        return fs.statSync(filePath).size > 0;
    } catch (_error) {
        return false;
    }
}

async function ensureModelFiles() {
    for (const relativePath of MODEL_FILES) {
        const destinationPath = path.join(modelDir, relativePath);
        if (fileLooksComplete(destinationPath)) {
            console.log(`whisper model already present: ${relativePath}`);
            continue;
        }

        const url = modelFileUrl(relativePath);
        console.log(`downloading whisper model file: ${relativePath}`);
        const size = await downloadFile(url, destinationPath);
        console.log(`  saved ${size} bytes`);
    }
}

async function main() {
    console.log("Preparing on-device Whisper assets…");
    await fs.promises.mkdir(assetsRoot, { recursive: true });
    await ensureModelFiles();
    console.log("Whisper assets are ready.");
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
