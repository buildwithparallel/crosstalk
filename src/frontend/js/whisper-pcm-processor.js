/**
 * AudioWorklet processor that forwards raw microphone PCM to the main thread.
 *
 * Downsampling to Whisper's 16 kHz input happens after recording stops so this
 * processor stays allocation-light while the user is speaking.
 */
class WhisperPcmProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const input = inputs[0];
        if (input && input.length > 0 && input[0] && input[0].length > 0) {
            // Copy the samples; the AudioWorklet buffer is reused across callbacks.
            this.port.postMessage(new Float32Array(input[0]));
        }
        return true;
    }
}

registerProcessor("whisper-pcm-processor", WhisperPcmProcessor);
