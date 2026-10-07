/** BPS decoder from the public-domain format specification; no third-party code. */
const MAX_CARTRIDGE_BYTES = 32 * 1024 * 1024;
const crcTable = new Uint32Array(256);
for (let value = 0; value < 256; value++) {
  let crc = value;
  for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
  crcTable[value] = crc >>> 0;
}

export function crc32(bytes: Uint8Array): number {
  let crc = 0xffffffff;
  for (const value of bytes) crc = (crc >>> 8) ^ crcTable[(crc ^ value) & 255];
  return (crc ^ 0xffffffff) >>> 0;
}

export function applyBps(source: Uint8Array, patch: Uint8Array): Uint8Array {
  const fail = (message: string): never => { throw new Error(`SF patch: ${message}`); };
  if (patch.length < 19 || String.fromCharCode(...patch.subarray(0, 4)) !== 'BPS1')
    fail('invalid BPS header.');
  const view = new DataView(patch.buffer, patch.byteOffset, patch.byteLength);
  const footer = patch.length - 12;
  if (crc32(patch.subarray(0, patch.length - 4)) !== view.getUint32(patch.length - 4, true))
    fail('patch checksum mismatch. Download it again.');
  if (crc32(source) !== view.getUint32(footer, true))
    fail('base ROM checksum mismatch. Use the specified Emerald version.');
  let position = 4;
  const number = (): number => {
    let value = 0, shift = 1;
    for (;;) {
      if (position >= footer) fail('truncated command.');
      const byte = patch[position++];
      value += (byte & 127) * shift;
      if (!Number.isSafeInteger(value)) fail('integer overflow.');
      if (byte & 128) return value;
      shift *= 128;
      value += shift;
      if (!Number.isSafeInteger(value) || !Number.isSafeInteger(shift)) fail('integer overflow.');
    }
  };
  if (number() !== source.length) fail('base ROM size mismatch.');
  const size = number();
  if (size < 1 || size > MAX_CARTRIDGE_BYTES) fail('unsupported cartridge size.');
  const metadataLength = number();
  if (metadataLength > footer - position) fail('truncated metadata.');
  position += metadataLength;
  const output = new Uint8Array(size);
  let written = 0, sourceOffset = 0, targetOffset = 0;
  const relative = (): number => {
    const value = number();
    return Math.floor(value / 2) * (value & 1 ? -1 : 1);
  };
  while (written < size) {
    const command = number();
    const action = command % 4;
    const length = Math.floor(command / 4) + 1;
    if (length > size - written) fail('command exceeds output size.');
    if (action === 0) {
      if (written + length > source.length) fail('source read is out of range.');
      output.set(source.subarray(written, written + length), written);
    } else if (action === 1) {
      if (length > footer - position) fail('truncated literal data.');
      output.set(patch.subarray(position, position + length), written);
      position += length;
    } else if (action === 2) {
      sourceOffset += relative();
      if (sourceOffset < 0 || sourceOffset + length > source.length) fail('source copy is out of range.');
      output.set(source.subarray(sourceOffset, sourceOffset + length), written);
      sourceOffset += length;
    } else {
      targetOffset += relative();
      if (targetOffset < 0 || targetOffset >= written) fail('target copy references unwritten data.');
      // Forward overlapping copies intentionally expand repeated target patterns.
      for (let index = 0; index < length; index++) output[written + index] = output[targetOffset++];
    }
    written += length;
  }
  if (position !== footer) fail('unexpected trailing commands.');
  if (crc32(output) !== view.getUint32(footer + 4, true)) fail('output checksum mismatch.');
  return output;
}
