import PcmMicrophoneRecorder, { rootMeanSquare } from "./PcmMicrophoneRecorder";
import WhisperWorker from "./whisper.worker.js?worker";

const MAX_RECORDING_SECONDS = 60;
const MIN_RECORDING_SECONDS = 0.35;
const SILENCE_RMS_THRESHOLD = 0.008;

let sharedInstance = null;

/**
 * On-device speech-to-text for the chat composer.
 *
 * Recording stays in this process. Transcription runs in a Web Worker with
 * Whisper Tiny (WASM). The worker is reused so the model is only loaded once
 * per app session.
 */
class WhisperSpeechToText {

    constructor() {
        this.worker = null;
        this.workerReady = false;
        this.readyPromise = null;
        this.recorder = null;
        this.pending = new Map();
        this.nextRequestId = 1;
        this.loadWaiters = [];
    }

    /**
     * Shared engine so switching conversations does not reload the 40 MB model.
     * @returns {WhisperSpeechToText}
     */
    static getShared() {
        if (!sharedInstance) {
            sharedInstance = new WhisperSpeechToText();
        }
        return sharedInstance;
    }

    /**
     * BCP-47 language from the OS/browser, mapped to a Whisper language code.
     * Short clips transcribe more reliably when the language is known.
     * @returns {string|null}
     */
    static detectLanguage() {
        const locale = (navigator.language || "").trim();
        if (!locale) {
            return null;
        }
        return locale.split("-")[0].toLowerCase() || null;
    }

    ensureWorker() {
        if (this.worker) {
            return;
        }

        this.worker = new WhisperWorker();
        this.worker.onmessage = (event) => {
            const { type, requestId, text, message, progress } = event.data || {};

            if (type === "progress") {
                for (const waiter of this.loadWaiters) {
                    waiter.onProgress?.(progress);
                }
                return;
            }

            if (type === "ready") {
                this.workerReady = true;
                this.resolvePending(requestId, true);
                return;
            }

            if (type === "result") {
                this.resolvePending(requestId, text || "");
                return;
            }

            if (type === "error") {
                this.rejectPending(requestId, new Error(message || "Whisper failed"));
            }
        };

        this.worker.onerror = (error) => {
            const failure = new Error(error?.message || "Whisper worker failed");
            for (const [requestId] of this.pending) {
                this.rejectPending(requestId, failure);
            }
        };
    }

    /**
     * Load Whisper Tiny into the worker. Safe to call more than once.
     * @param {(progress: object) => void} [onProgress]
     * @returns {Promise<void>}
     */
    async ensureReady(onProgress) {
        this.ensureWorker();
        if (this.workerReady) {
            return;
        }

        if (!this.readyPromise) {
            const requestId = this.nextRequestId++;
            this.readyPromise = this.waitForWorker(requestId).catch((error) => {
                this.readyPromise = null;
                throw error;
            });
            this.worker.postMessage({ type: "load", requestId });
        }

        if (onProgress) {
            this.loadWaiters.push({ onProgress });
        }

        try {
            await this.readyPromise;
        } finally {
            this.loadWaiters = this.loadWaiters.filter((waiter) => waiter.onProgress !== onProgress);
        }
    }

    /**
     * Start capturing microphone PCM.
     * @returns {Promise<boolean>}
     */
    async startRecording() {
        if (this.recorder) {
            return true;
        }
        this.recorder = new PcmMicrophoneRecorder();
        const started = await this.recorder.start();
        if (!started) {
            this.recorder = null;
        }
        return started;
    }

    /**
     * Whether the microphone is currently capturing dictation audio.
     * @returns {boolean}
     */
    isRecording() {
        return this.recorder != null;
    }

    /**
     * Seconds captured in the current dictation take.
     * @returns {number}
     */
    getElapsedSeconds() {
        return this.recorder ? this.recorder.getElapsedSeconds() : 0;
    }

    /**
     * Stop the mic without transcribing, for example when leaving a chat.
     */
    cancelRecording() {
        if (this.recorder) {
            this.recorder.cancel();
            this.recorder = null;
        }
    }

    /**
     * Stop the microphone and transcribe the captured audio on-device.
     * @returns {Promise<string>}
     */
    async stopRecordingAndTranscribe() {
        if (!this.recorder) {
            return "";
        }

        const elapsed = this.recorder.getElapsedSeconds();
        const samples = await this.recorder.stop();
        this.recorder = null;

        if (elapsed < MIN_RECORDING_SECONDS || samples.length < WHISPER_MIN_SAMPLES) {
            return "";
        }
        if (rootMeanSquare(samples) < SILENCE_RMS_THRESHOLD) {
            return "";
        }

        await this.ensureReady();
        return await this.transcribe(samples);
    }

    /**
     * @param {Float32Array} audio
     * @returns {Promise<string>}
     */
    async transcribe(audio) {
        this.ensureWorker();
        const requestId = this.nextRequestId++;
        const resultPromise = this.waitForWorker(requestId);
        this.worker.postMessage({
            type: "transcribe",
            requestId,
            audio,
            language: WhisperSpeechToText.detectLanguage(),
        }, [audio.buffer]);
        const text = await resultPromise;
        return typeof text === "string" ? text.trim() : "";
    }

    waitForWorker(requestId) {
        return new Promise((resolve, reject) => {
            this.pending.set(requestId, { resolve, reject });
        });
    }

    resolvePending(requestId, value) {
        const pending = this.pending.get(requestId);
        if (!pending) {
            return;
        }
        this.pending.delete(requestId);
        pending.resolve(value);
    }

    rejectPending(requestId, error) {
        const pending = this.pending.get(requestId);
        if (!pending) {
            return;
        }
        this.pending.delete(requestId);
        pending.reject(error);
    }
}

const WHISPER_MIN_SAMPLES = Math.round(16000 * MIN_RECORDING_SECONDS);

export { MAX_RECORDING_SECONDS };
export default WhisperSpeechToText;
