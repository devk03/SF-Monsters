/** Emerald's two rotating Flash slots; sizes match the pinned engine structures. */
export const FLASH_SIZE = 131072;
const SECTOR_SIZE = 4096;
const SIGNATURE = 0x08012025;
const PAYLOAD_SIZES = [3884, 3968, 3968, 3968, 3848,
  3968, 3968, 3968, 3968, 3968, 3968, 3968, 3968, 2000];

function slotCounter(bytes: Uint8Array, slot: number): number | null {
  const sectors = new Set<number>();
  let counter: number | null = null;
  for (let index = 0; index < 14; index++) {
    const offset = (slot * 14 + index) * SECTOR_SIZE;
    const view = new DataView(bytes.buffer, bytes.byteOffset + offset, SECTOR_SIZE);
    const id = view.getUint16(4084, true);
    if (id >= 14 || sectors.has(id) || view.getUint32(4088, true) !== SIGNATURE) return null;
    const current = view.getUint32(4092, true);
    if (counter !== null && counter !== current) return null;
    counter = current;
    let sum = 0;
    for (let address = 0; address < PAYLOAD_SIZES[id]; address += 4)
      sum = (sum + view.getUint32(address, true)) >>> 0;
    if (((sum + (sum >>> 16)) & 65535) !== view.getUint16(4086, true)) return null;
    sectors.add(id);
  }
  return counter;
}

export function flashCounter(bytes: Uint8Array): number | null {
  if (bytes.length !== FLASH_SIZE) return null;
  const first = slotCounter(bytes, 0), second = slotCounter(bytes, 1);
  if (first === null) return second;
  if (second === null) return first;
  return ((second - first) | 0) > 0 ? second : first;
}

export function validateFlashSave(bytes: Uint8Array): void {
  if (flashCounter(bytes) === null)
    throw new Error('This is not a valid Emerald-format 128 KiB save. Your current progress was kept.');
}
