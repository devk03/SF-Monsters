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

function latestSlot(bytes: Uint8Array): {slot: number; counter: number} | null {
  if (bytes.length !== FLASH_SIZE) return null;
  const first = slotCounter(bytes, 0), second = slotCounter(bytes, 1);
  if (first === null) return second === null ? null : {slot: 1, counter: second};
  if (second === null) return {slot: 0, counter: first};
  return ((second - first) | 0) > 0 ? {slot: 1, counter: second} : {slot: 0, counter: first};
}

export function flashCounter(bytes: Uint8Array): number | null {
  return latestSlot(bytes)?.counter ?? null;
}

/** SF identity is in native persistent vars F8/F9, inside SaveBlock1 sector 2. */
export function validateSfFlashSave(bytes: Uint8Array): void {
  validateFlashSave(bytes);
  const latest = latestSlot(bytes)!;
  for (let index = 0; index < 14; index++) {
    const offset = (latest.slot * 14 + index) * SECTOR_SIZE;
    const view = new DataView(bytes.buffer, bytes.byteOffset + offset, SECTOR_SIZE);
    if (view.getUint16(4084, true) !== 2) continue;
    // SaveBlock1 vars start at 0x139c; sector 2 begins at its byte 0xf80.
    const marker = view.getUint16(0x60c, true), schema = view.getUint16(0x60e, true);
    if (marker === 0x5346 && schema === 1) return;
    break;
  }
  throw new Error('This is not a supported SF Mini Monsters save. Your current progress was kept.');
}

export function validateFlashSave(bytes: Uint8Array): void {
  if (flashCounter(bytes) === null)
    throw new Error('This is not a valid Emerald-format 128 KiB save. Your current progress was kept.');
}
