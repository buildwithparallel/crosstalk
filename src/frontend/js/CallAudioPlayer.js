// 480 ms at 8 kHz: whole 160-, 320-, and 640-sample Codec2 frames.
export const CALL_CAPTURE_SAMPLES = 3840;

export default class CallAudioPlayer {
    constructor(context, decode, { startupDelay = 0.12, maxBufferedSeconds = 1.5 } = {}) {
        this.context = context;
        this.decode = decode;
        this.startupDelay = startupDelay;
        this.maxBufferedSeconds = maxBufferedSeconds;
        this.nextStart = 0;
        this.pending = [];
        this.sources = new Set();
        this.processing = false;
        this.closed = false;
        this.generation = 0;
    }

    enqueue(mode, encoded) {
        if(this.closed) return;
        // Keep decoding in arrival order without building a long voice backlog.
        if(this.pending.length >= 3) this.pending.shift();
        this.pending.push({ mode, encoded, generation: this.generation });
        return this.drain();
    }

    async drain() {
        if(this.processing || this.closed) return;
        this.processing = true;
        try {
            while(this.pending.length && !this.closed) {
                const packet = this.pending.shift();
                try {
                    const pcm = await this.decode(packet.mode, packet.encoded);
                    if(this.closed || packet.generation !== this.generation) continue;
                    await this.context.resume();
                    if(!this.closed && packet.generation === this.generation) this.playPcm16(pcm);
                } catch(error) {
                    if(!this.closed) console.warn('Call audio decode failed', error);
                }
            }
        } finally {
            this.processing = false;
        }
    }

    playPcm16(pcm) {
        if(this.closed) return false;
        if(!pcm.byteLength || pcm.byteLength % 2 !== 0) throw new Error('Invalid PCM16 audio');
        const buffer = this.context.createBuffer(1, pcm.byteLength / 2, 8000);
        const channel = buffer.getChannelData(0);
        const view = new DataView(pcm.buffer, pcm.byteOffset, pcm.byteLength);
        for(let i = 0; i < channel.length; i++) channel[i] = view.getInt16(i * 2, true) / 32768;

        const now = this.context.currentTime;
        // Rebuffer after an underrun; otherwise join the preceding chunk exactly.
        const start = this.nextStart < now + 0.01 ? now + this.startupDelay : this.nextStart;
        if(start + buffer.duration - now > this.maxBufferedSeconds) return false;
        const source = this.context.createBufferSource();
        source.buffer = buffer;
        source.connect(this.context.destination);
        source.onended = () => {
            this.sources.delete(source);
            source.disconnect();
        };
        this.sources.add(source);
        source.start(start);
        this.nextStart = start + buffer.duration;
        return true;
    }

    clear() {
        this.generation++;
        this.pending.length = 0;
        this.nextStart = 0;
        for(const source of this.sources) {
            source.stop();
            source.disconnect();
        }
        this.sources.clear();
    }

    close() {
        if(this.closed) return;
        this.closed = true;
        this.clear();
        if(this.context.state !== 'closed') this.context.close().catch(console.warn);
    }
}
