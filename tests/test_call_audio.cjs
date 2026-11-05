const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const root = path.resolve(__dirname, '..');
const playerSource = fs.readFileSync(path.join(root, 'src/frontend/js/CallAudioPlayer.js'), 'utf8');
const playerModule = import('data:text/javascript;base64,' + Buffer.from(playerSource).toString('base64'));
const assets = path.join(root, 'src/frontend/public/assets/js/codec2-emscripten');
const pcm = () => new Uint8Array(3840 * 2);

class AudioContextStub {
    constructor() {
        this.currentTime = 0;
        this.state = 'running';
        this.destination = {};
        this.scheduled = [];
    }
    createBuffer(channels, samples, rate) {
        const channel = new Float32Array(samples);
        return { duration: samples / rate, getChannelData: () => channel };
    }
    createBufferSource() {
        const context = this;
        return {
            connect() {}, disconnect() {},
            start(time) { this.startTime = time; context.scheduled.push(this); },
            stop() { this.stopped = true; },
        };
    }
    async resume() {}
    async close() { this.state = 'closed'; }
}

test('irregular arrivals play adjacent chunks on one timeline', async () => {
    const { default: Player } = await playerModule;
    const context = new AudioContextStub();
    const player = new Player(context, async () => pcm());
    for(const arrival of [0, 0.53, 1.01]) {
        context.currentTime = arrival;
        await player.enqueue('1200', new Uint8Array([1]));
    }
    const starts = context.scheduled.map(source => source.startTime);
    assert.equal(starts[0], 0.12);
    for(let i = 1; i < starts.length; i++) assert.ok(Math.abs(starts[i] - starts[i-1] - 0.48) < 1e-9);
    player.close();
});

test('a real underrun starts a fresh short buffer instead of playing in the past', async () => {
    const { default: Player } = await playerModule;
    const context = new AudioContextStub();
    const player = new Player(context, async () => pcm());
    player.playPcm16(pcm());
    context.currentTime = 2;
    player.playPcm16(pcm());
    assert.equal(context.scheduled[1].startTime, 2.12);
    player.close();
});

test('slow decoding stays in packet order', async () => {
    const { default: Player } = await playerModule;
    const context = new AudioContextStub();
    let release;
    const decoded = [];
    const player = new Player(context, async (_, encoded) => {
        decoded.push(encoded[0]);
        if(encoded[0] === 1) await new Promise(resolve => { release = resolve; });
        return pcm();
    });
    const done = player.enqueue('1200', new Uint8Array([1]));
    player.enqueue('1200', new Uint8Array([2]));
    assert.deepEqual(decoded, [1]);
    release();
    await done;
    assert.deepEqual(decoded, [1, 2]);
    assert.equal(context.scheduled.length, 2);
    player.close();
});

test('hangup cancels queued decoding and closes the audio context', async () => {
    const { default: Player } = await playerModule;
    const context = new AudioContextStub();
    let release;
    const player = new Player(context, async () => {
        await new Promise(resolve => { release = resolve; });
        return pcm();
    });
    player.playPcm16(pcm());
    const done = player.enqueue('1200', new Uint8Array([1]));
    player.enqueue('1200', new Uint8Array([2]));
    player.close();
    release();
    await done;
    assert.equal(context.state, 'closed');
    assert.equal(context.scheduled.length, 1);
    assert.ok(context.scheduled[0].stopped);
});

test('mute discards decoding already in flight and permits fresh audio after unmute', async () => {
    const { default: Player } = await playerModule;
    const context = new AudioContextStub();
    let release;
    let count = 0;
    const player = new Player(context, async () => {
        if(count++ === 0) await new Promise(resolve => { release = resolve; });
        return pcm();
    });
    const done = player.enqueue('1200', new Uint8Array([1]));
    player.clear();
    release();
    await done;
    assert.equal(context.scheduled.length, 0);
    await player.enqueue('1200', new Uint8Array([2]));
    assert.equal(context.scheduled.length, 1);
    player.close();
});

test('excessively early audio cannot build an unlimited playback backlog', async () => {
    const { default: Player } = await playerModule;
    const context = new AudioContextStub();
    const player = new Player(context, async () => pcm());
    for(let i = 0; i < 20; i++) player.playPcm16(pcm());
    assert.ok(player.nextStart - context.currentTime <= 1.5);
    player.close();
});

test('capture preserves every sample across frame boundaries', async () => {
    const { CALL_CAPTURE_SAMPLES } = await playerModule;
    let Processor;
    const chunks = [];
    vm.runInNewContext(fs.readFileSync(path.join(assets, 'processor.js'), 'utf8'), {
        AudioWorkletProcessor: class { constructor() { this.port = { postMessage: data => chunks.push(Array.from(data)) }; } },
        registerProcessor: (_, type) => { Processor = type; },
        Float32Array,
    });
    const processor = new Processor({ processorOptions: { bufferSize: CALL_CAPTURE_SAMPLES } });
    for(let offset = 0; offset < 3840 * 2; offset += 128) {
        processor.process([[Float32Array.from({ length: 128 }, (_, i) => offset + i)]], [], {});
    }
    assert.equal(chunks.length, 2);
    assert.deepEqual(chunks.flat(), Array.from({ length: 7680 }, (_, i) => i));
    assert.equal(new Processor().bufferSize, 4096);
});

async function runCodec(factory, wasm, args, inputName, input, outputName) {
    const options = { wasmBinary: fs.readFileSync(path.join(assets, wasm)),
        arguments: args, noExitRuntime: true, print() {}, printErr() {} };
    options.preRun = () => options.FS.writeFile(inputName, input);
    const module = await factory(options);
    return module.FS.readFile(outputName).slice();
}

test('real Codec2 1200 and 3200 retain every sample with the new capture size', { timeout: 5000 }, async () => {
    const { CALL_CAPTURE_SAMPLES } = await playerModule;
    const encode = require(path.join(assets, 'c2enc.js'));
    const decode = require(path.join(assets, 'c2dec.js'));
    for(const mode of ['1200', '3200']) {
        const input = new Uint8Array(CALL_CAPTURE_SAMPLES * 2);
        const bits = await runCodec(encode, 'c2enc.wasm', [mode, 'input.raw', 'output.bit'], 'input.raw', input, 'output.bit');
        const output = await runCodec(decode, 'c2dec.wasm', [mode, 'input.bit', 'output.raw'], 'input.bit', bits, 'output.raw');
        assert.equal(output.length, input.length, mode + ' lost samples');
    }
});
