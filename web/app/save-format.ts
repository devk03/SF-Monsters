/* Stable version-one cartridge save layout; two checksum-protected SRAM banks. */
export const SRAM_SIZE = 32768;
const RECORD_SIZE = 360;
const BANK_OFFSETS = [0, 2048];
export type Progress = { flags: number; caught: number; coins: number; map: number; party: number; sequence: number };
function validBank(bytes: Uint8Array, offset: number): Progress | null {
  if (bytes.length !== SRAM_SIZE) return null;
  const view = new DataView(bytes.buffer, bytes.byteOffset + offset, RECORD_SIZE);
  if (view.getUint32(0, true) !== 0x53464d4d || view.getUint32(4, true) !== 1) return null;
  let hash = 2166136261;
  for (let i = 0; i < RECORD_SIZE; i++) {
    if (i >= 8 && i < 12) continue;
    hash = Math.imul(hash ^ bytes[offset + i], 16777619) >>> 0;
  }
  if (hash !== view.getUint32(8, true)) return null;
  const count = view.getUint8(34), party = view.getUint8(35);
  if (count < 1 || count > 32 || party < 1 || party > 6 || party > count) return null;
  if (view.getUint8(30) > 2 || view.getUint8(31) >= 24 || view.getUint8(32) >= 18 || view.getUint8(33) > 3) return null;
  for (let i = 0; i < count; i++) {
    const base = 38 + i * 10;
    if (view.getUint8(base) >= 12 || view.getUint8(base + 1) < 1 || view.getUint8(base + 1) > 100) return null;
  }
  return { flags: view.getUint16(20, true), caught: view.getUint16(24, true), coins: view.getUint16(26, true),
    map: view.getUint8(30), party, sequence: view.getUint32(12, true) };
}
export function readProgress(bytes: Uint8Array): Progress | null {
  const a = validBank(bytes, BANK_OFFSETS[0]), b = validBank(bytes, BANK_OFFSETS[1]);
  if (!a) return b;
  if (!b) return a;
  return ((b.sequence - a.sequence) | 0) > 0 ? b : a;
}
export function validateSave(bytes: Uint8Array): void {
  if (!readProgress(bytes)) throw new Error("This isn't a valid SF Mini Monsters v1 .sav file. Your current progress was kept.");
}
export function encodeSave(bytes: Uint8Array): string {
  let value = "";
  for (const byte of bytes) value += String.fromCharCode(byte);
  return btoa(value);
}
export function decodeSave(value: string): Uint8Array {
  const raw = atob(value);
  return Uint8Array.from(raw, c => c.charCodeAt(0));
}
export function countCaught(mask: number): number {
  let count = 0;
  for (let i = 0; i < 12; i++) if (mask & (1 << i)) count++;
  return count;
}
export function nextQuest(flags: number): string {
  if (!(flags & 2)) return "Find the parcel on Ocean Beach.";
  if (!(flags & 4)) return "Return to Roon by the sand.";
  if (!(flags & 8)) return "Take Muni to Cognition in SoMa.";
  if (!(flags & 16)) return "Repair the lab's left relay.";
  if (!(flags & 32)) return "Repair the lab's right relay.";
  if (!(flags & 64)) return "Challenge Scott Wu for the Build Badge.";
  return "Build Badge earned. Collect all 12 mini monsters.";
}
