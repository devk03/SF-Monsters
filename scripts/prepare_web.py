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
# Ensure a quick keyboard tap is visible to a frame-based handheld input loop.
s=s.replace("    const onKeyDown = (e) => {", "    const keyTimes = new Map();\n    const releaseTimers = new Map();\n    const onKeyDown = (e) => {\n        clearTimeout(releaseTimers.get(e.code));\n        keyTimes.set(e.code, performance.now());")
s=s.replace("    const onKeyUp = (e) => {\n        if (applyKey(e.code, false))\n            e.preventDefault();\n    };", "    const onKeyUp = (e) => {\n        if (!codeToBit.has(e.code)) return;\n        e.preventDefault();\n        const delay = Math.max(0, 70 - (performance.now() - (keyTimes.get(e.code) || 0)));\n        releaseTimers.set(e.code, setTimeout(() => applyKey(e.code, false), delay));\n    };")
s=s.replace("            running = false;", "            for (const timer of releaseTimers.values()) clearTimeout(timer);\n            running = false;")
s='/* Modified for SF Mini Monsters: battery saves and frame-safe input. MPL-2.0. */\n'+s
p.write_text(s)
(out/'entry.js').write_text("import { load } from './mgba.sdk.js';\nwindow.sfMiniMonstersLoad = load;\n")
print('Prepared same-origin mGBA runtime and battery-save extension.')
