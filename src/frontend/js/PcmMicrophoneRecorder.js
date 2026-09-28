import processorUrl from "./whisper-pcm-processor.js?url";

const WHISPER_SAMPLE_RATE = 16000;

/**
 * Records microphone audio as 16 kHz mono PCM for on-device Whisper.
 *
 * Audio is kept in memory only. Tracks are stopped when recording ends so the
 * OS microphone indicator is released promptly.
 */
class PcmMicrophoneRecorder {

    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.mediaStreamSource = null;
        this.workletNode = null;
        this.chunks = [];
        this.startedAt = null;
    }

    /**
     * Begin capturing microphone samples.
     * @returns {Promise<boolean>} true when the mic is live
     */
    async start() {
        try {
            this.chunks = [];
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                },
            });

            this.audioContext = new AudioContext();
            await this.audioContext.audioWorklet.addModule(processorUrl);
            this.workletNode = new AudioWorkletNode(this.audioContext, "whisper-pcm-processor");
            this.workletNode.port.onmessage = (event) => {
                this.chunks.push(event.data);
            };

            this.mediaStreamSource = this.audioContext.createMediaStreamSource(this.mediaStream);
            this.mediaStreamSource.connect(this.workletNode);
            this.startedAt = Date.now();
            return true;
        } catch (_error) {
            this.stopTracks();
            return false;
        }
    }

    /**
     * Stop capture and return 16 kHz mono samples for Whisper.
     * @returns {Promise<Float32Array>}
     */
    async stop() {
        const nativeRate = this.audioContext?.sampleRate || WHISPER_SAMPLE_RATE;
        const samples = this.concatenateChunks();
        this.cleanup();
        return downsampleToRate(samples, nativeRate, WHISPER_SAMPLE_RATE);
    }

    /**
     * Stop capture and discard samples, for example when the conversation closes.
     */
    cancel() {
        this.cleanup();
    }

    /**
     * Seconds captured so far, or 0 if recording has not started.
     * @returns {number}
     */
    getElapsedSeconds() {
        if (this.startedAt == null) {
            return 0;
        }
        return (Date.now() - this.startedAt) / 1000;
    }

    concatenateChunks() {
        let length = 0;
        for (const chunk of this.chunks) {
            length += chunk.length;
        }
        const samples = new Float32Array(length);
        let offset = 0;
        for (const chunk of this.chunks) {
            samples.set(chunk, offset);
            offset += chunk.length;
        }
        return samples;
    }

    stopTracks() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach((track) => track.stop());
        }
    }

    cleanup() {
        this.stopTracks();
        if (this.mediaStreamSource) {
            this.mediaStreamSource.disconnect();
        }
        if (this.workletNode) {
            this.workletNode.disconnect();
        }
        if (this.audioContext && this.audioContext.state !== "closed") {
            this.audioContext.close();
        }
        this.audioContext = null;
        this.mediaStream = null;
        this.mediaStreamSource = null;
        this.workletNode = null;
        this.chunks = [];
        this.startedAt = null;
    }
}

/**
 * Average-pool PCM to Whisper's expected 16 kHz rate.
 * @param {Float32Array} samples
 * @param {number} inputRate
 * @param {number} outputRate
 * @returns {Float32Array}
 */
export function downsampleToRate(samples, inputRate, outputRate) {
    if (!samples || samples.length === 0) {
        return new Float32Array(0);
    }
    if (inputRate === outputRate) {
        return samples;
    }

    const ratio = inputRate / outputRate;
    const outputLength = Math.max(1, Math.round(samples.length / ratio));
    const output = new Float32Array(outputLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < output.length) {
        const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
        let accum = 0;
        let count = 0;
        for (let i = offsetBuffer; i < nextOffsetBuffer && i < samples.length; i++) {
            accum += samples[i];
            count++;
        }
        output[offsetResult] = count > 0 ? accum / count : 0;
        offsetResult++;
        offsetBuffer = nextOffsetBuffer;
    }
    return output;
}

/**
 * Mean-square energy used to ignore near-silent recordings.
 * @param {Float32Array} samples
 * @returns {number}
 */
export function rootMeanSquare(samples) {
    if (!samples || samples.length === 0) {
        return 0;
    }
    let sum = 0;
    for (let i = 0; i < samples.length; i++) {
        sum += samples[i] * samples[i];
    }
    return Math.sqrt(sum / samples.length);
}

export default PcmMicrophoneRecorder;
