/* Actual sink interpolation/output must be unchanged by diagnostics. */
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { WORKLET_SOURCE } from '../web/public/emulator/mgba.audio-worklet.js';

function sink() {
  let Sink;
  class Processor {
    constructor() { this.port = { messages: [], postMessage(value) { this.messages.push(value); } }; }
  }
  const context = { AudioWorkletProcessor: Processor, Float32Array,
    sampleRate: 48000, currentFrame: 0, registerProcessor(name, Constructor) {
      assert.equal(name, 'mgba-sink'); Sink = Constructor;
    } };
  vm.runInNewContext(WORKLET_SOURCE, context);
  const instance = new Sink();
  return {
    send(data) { instance.port.onmessage({ data }); },
    render(count) {
      const left = new Float32Array(count), right = new Float32Array(count);
      instance.process([], [[left, right]]); context.currentFrame += count;
      return [Array.from(left), Array.from(right)];
    },
    messages: instance.port.messages,
  };
}

const normal = sink(), observed = sink();
observed.send({ type: 'diagnostics', enabled: true });
for (const device of [normal, observed]) {
  device.send({ rate: 24000 });
  device.send(new Int16Array([0, 0, 8192, -8192, 16384, -16384, 24576, -24576]));
}
const expected = [[0, .125, .25, .375], [0, -.125, -.25, -.375]];
assert.deepEqual(normal.render(4), expected, 'half-rate linear interpolation');
assert.deepEqual(observed.render(4), expected, 'observer preserves interpolation');
assert.deepEqual(normal.render(12), observed.render(12), 'depleted buffers preserve identical silence');
observed.send({ type: 'diagnostics', enabled: false });
const report = observed.messages.find(message => message?.type === 'diagnostics' && message.final);
assert.equal(report.renderedOutputFrames, 16);
assert.equal(report.underrunOutputFrames, 10, 'six valid interpolation positions, then ten starved output frames');
assert.equal(report.warmupOutputFrames, 0);
assert.equal(report.processQuanta, 2);
assert.equal(report.observedThroughOutputFrame, 16);
assert.equal(normal.messages.filter(value => typeof value === 'object').length, 0);

const startup = sink();
startup.send({ type: 'diagnostics', enabled: true });
startup.render(128);
startup.send({ type: 'diagnostics', enabled: false });
const warmup = startup.messages.at(-1);
assert.equal(warmup.warmupOutputFrames, 128);
assert.equal(warmup.underrunOutputFrames, 0, 'pre-audio startup is reported separately');

const overflow = sink();
overflow.send({ type: 'diagnostics', enabled: true });
overflow.send(new Int16Array((32768 + 4) * 2));
overflow.send({ type: 'diagnostics', enabled: false });
assert.equal(overflow.messages.at(-1).droppedSourceFrames, 4);
assert.equal(overflow.messages.at(-1).queueDepthFrames, 32768);
const count = overflow.messages.length;
overflow.render(4096);
assert.equal(overflow.messages.length, count + 1, 'disabled diagnostics only emit normal consumption');
assert.equal(typeof overflow.messages.at(-1), 'number');
console.log('Audio sink interpolation, silence, warmup, underrun, overflow and observer neutrality passed.');
