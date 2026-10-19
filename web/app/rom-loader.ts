import {applyBps} from './bps';

type PatchManifest = {
  version: string; base_sha256: string; base_bytes: number;
  target_sha256: string; target_bytes: number; patch_sha256: string;
  profile?: string; save_magic?: number; save_schema?: number; fixture?: unknown;
};
async function sha256(bytes: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', new Uint8Array(bytes).buffer);
  return Array.from(new Uint8Array(digest), value => value.toString(16).padStart(2, '0')).join('');
}

/** All ROM bytes stay in the browser. Only our manifest and patch are fetched. */
export async function patchLocalRom(base: Uint8Array, edition: 'emerald' | 'world' = 'emerald'): Promise<{rom: Uint8Array; version: string}> {
  const directory = edition === 'world' ? '/world-patch' : '/patch';
  const response = await fetch(`${directory}/manifest.json`, edition === 'world' ? {cache: 'no-store'} : undefined);
  if (!response.ok) throw new Error('The SF patch is unavailable. Try again.');
  const manifest = await response.json() as PatchManifest;
  if (edition === 'world' && (manifest.profile !== 'world-preview' || manifest.save_magic !== 0x5743 || manifest.save_schema !== 1 || manifest.fixture !== null))
    throw new Error('This is not a supported world preview patch. Your current game was kept.');
  if (base.length !== manifest.base_bytes || await sha256(base) !== manifest.base_sha256)
    throw new Error('Use the USA/Europe Emerald .gba ROM specified for this patch. The selected file was kept unchanged.');
  const patchResponse = await fetch(`${directory}/sf-mini-monsters.bps`, edition === 'world' ? {cache: 'no-store'} : undefined);
  if (!patchResponse.ok) throw new Error('The SF patch could not be downloaded.');
  const patch = new Uint8Array(await patchResponse.arrayBuffer());
  if (await sha256(patch) !== manifest.patch_sha256) throw new Error('Patch integrity check failed. Refresh and try again.');
  const rom = applyBps(base, patch);
  if (rom.length !== manifest.target_bytes || await sha256(rom) !== manifest.target_sha256)
    throw new Error('The patched cartridge could not be verified.');
  return {rom, version: manifest.version};
}
