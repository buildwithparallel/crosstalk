const assert = require('node:assert/strict');
const path = require('node:path');
const test = require('node:test');
const { instanceOptions } = require('../electron/instance-options');

test('normal launch keeps the default port and profile', () => {
    const options = instanceOptions(['/Applications/Crosstalk']);
    assert.equal(options.port, 9337);
    assert.equal(options.userData, null);
});

test('packaged profiles use separate endpoints and desktop storage', () => {
    const first = instanceOptions(['Crosstalk', '--port', '9341', '--storage-dir', '/tmp/duo1']);
    const second = instanceOptions(['Crosstalk', '--port', '9342', '--storage-dir', '/tmp/duo2']);
    assert.equal(first.backendOrigin, 'http://localhost:9341');
    assert.equal(second.backendOrigin, 'http://localhost:9342');
    assert.notEqual(first.userData, second.userData);
    assert.equal(first.userData, path.join('/tmp/duo1', 'desktop'));
    assert.equal(first.label, 'duo1');
});

test('source launches remove the Electron application path', () => {
    const options = instanceOptions(['electron', '/project/crosstalk', '--port', '9341'], true);
    assert.deepEqual(options.args, ['--port', '9341']);
    assert.equal(options.port, 9341);
});

test('equals-style options work and the last port wins', () => {
    const options = instanceOptions(['Crosstalk', '--port=9337', '--port=9342', '--storage-dir=/tmp/duo2']);
    assert.equal(options.port, 9342);
    assert.equal(options.label, 'duo2');
});

test('invalid ports are rejected before starting a backend', () => {
    for(const port of ['0', '65536', 'abc', '9341.5']){
        assert.throws(() => instanceOptions(['Crosstalk', '--port', port]), /--port/);
    }
});
