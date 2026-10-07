"""Vendor the pinned mGBA runtime, keeping the build reproducible and same-origin."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'web/node_modules/@wasm-gaming/mgba-wasm/dist/mgba'
out=ROOT/'web/public/emulator';out.mkdir(parents=True,exist_ok=True)
for path in source.iterdir():
    if path.suffix in ['.js','.wasm']:shutil.copy2(path,out/path.name)
# Small MPL-covered extension exposes battery saves, not proprietary savestates.
p=out/'mgba.sdk.js';s=p.read_text()
needle='        async saveState() {'
assert needle in s
s=s.replace(needle,'''        exportBattery() {
            const bytes = cloneSram();
            if (!bytes) throw new Error('No cartridge save exists yet. Choose a starter first.');
            return bytes;
        },
        importBattery(bytes) {
            if (!(bytes instanceof Uint8Array) || bytes.length !== 32768)
                throw new Error('Expected a 32 KiB GBA SRAM save.');
            const ptr = heapAlloc(mod, bytes);
            const ok = mod._mgbawasm_sram_load(ptr, bytes.length);
            mod._free(ptr);
            if (!ok) throw new Error('The emulator could not restore this save.');
            mod._mgbawasm_reset();
        },
'''+needle)
s='/* Modified for SF Mini Monsters: battery-save export/import. MPL-2.0. */\n'+s
p.write_text(s)
print('Prepared same-origin mGBA runtime and battery-save extension.')
