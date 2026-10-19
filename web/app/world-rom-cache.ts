// The original ROM is remembered only on this browser's origin, never uploaded.
// Saves use their existing independent storage keys and are untouched here.
const CACHE = 'sf-world-local-rom-v1';
const KEY = '/__sf_local_world_rom__';

export async function readWorldRom(): Promise<Uint8Array | null> {
  try {
    const response = await (await caches.open(CACHE)).match(KEY);
    return response ? new Uint8Array(await response.arrayBuffer()) : null;
  } catch { return null; }
}

/** Call only after patchLocalRom has verified the original ROM. */
export async function rememberWorldRom(bytes: Uint8Array): Promise<boolean> {
  try {
    await (await caches.open(CACHE)).put(KEY, new Response(new Uint8Array(bytes), {
      headers: {'Content-Type': 'application/octet-stream', 'Cache-Control': 'no-store'},
    }));
    return true;
  } catch { return false; } // Quota/private-mode failures must not prevent play.
}

export async function forgetWorldRom(): Promise<boolean> {
  try { await (await caches.open(CACHE)).delete(KEY); return true; }
  catch { return false; }
}
