"""Vendor the pinned mGBA runtime, keeping the build reproducible and same-origin."""
from pathlib import Path
import shutil
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'web/node_modules/@wasm-gaming/mgba-wasm/dist/mgba'
out=ROOT/'web/public/emulator';out.mkdir(parents=True,exist_ok=True)
for path in source.iterdir():
    if path.suffix == '.js' and path.name != 'mgba.js':shutil.copy2(path,out/path.name)
# Keep the browser at the acceptance emulator's exact revision. Never silently
# replace the pinned core with the package's newer upstream binary.
revision = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2'
shim_hash = hashlib.sha256((ROOT/'emulator/mgba_0105_shim.c').read_bytes()).hexdigest()
def verified_core(directory, manifest):
    if not manifest.is_file(): return False
    data = json.loads(manifest.read_text())
    return data.get('mgba_revision') == revision and data.get('shim_sha256') == shim_hash and all(
        (directory/name).is_file() and hashlib.sha256((directory/name).read_bytes()).hexdigest() == data.get('artifacts',{}).get(name)
        for name in ['mgba.js','mgba.wasm'])
cache = ROOT/'.tools/mgba-0105-web'
if verified_core(cache,cache/'build.json'):
    for name in ['mgba.js','mgba.wasm']:shutil.copy2(cache/name,out/name)
    shutil.copy2(cache/'build.json',out/'core-build.json')
elif not verified_core(out,out/'core-build.json'):
    subprocess.run(['python3',str(ROOT/'scripts/build_web_core.py')],check=True)
    if not verified_core(cache,cache/'build.json'):raise ValueError('Pinned browser core verification failed.')
    for name in ['mgba.js','mgba.wasm']:shutil.copy2(cache/name,out/name)
    shutil.copy2(cache/'build.json',out/'core-build.json')
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
            if (!(bytes instanceof Uint8Array) || ![32768, 131072].includes(bytes.length))
                throw new Error('Expected a supported GBA battery save.');
            const current = cloneSram();
            if (current && current.length !== bytes.length)
                throw new Error('This save uses a different cartridge format.');
            rebootCore();
            // Run startup so the ROM initializes SRAM before restoring it.
            let ready = false;
            for (let frame = 0; frame < 120; frame++) {
                mod._mgbawasm_run_frame();
                if (mod._mgbawasm_sram_save() === bytes.length) { ready = true; break; }
            }
            if (!ready) throw new Error('The cartridge save memory did not initialize.');
            const ptr = heapAlloc(mod, bytes);
            const ok = mod._mgbawasm_sram_load(ptr, bytes.length);
            mod._free(ptr);
            if (!ok) throw new Error('The emulator could not restore this save.');
            const restored = cloneSram();
            if (!restored || restored.length !== bytes.length ||
                restored.some((value, index) => value !== bytes[index]))
                throw new Error('The cartridge save could not be verified.');
            mod._mgbawasm_reset();
            applyLiveSettings();
            mod._mgbawasm_set_keys(0);
            sentMask = -1;
        },
'''+needle)
# Ensure a quick keyboard tap is visible to a frame-based handheld input loop.
s=s.replace("    const onKeyDown = (e) => {", "    const keyTimes = new Map();\n    const releaseTimers = new Map();\n    const onKeyDown = (e) => {\n        clearTimeout(releaseTimers.get(e.code));\n        keyTimes.set(e.code, performance.now());")
s=s.replace("    const onKeyUp = (e) => {\n        if (applyKey(e.code, false))\n            e.preventDefault();\n    };", "    const onKeyUp = (e) => {\n        if (!codeToBit.has(e.code)) return;\n        e.preventDefault();\n        const delay = Math.max(0, 70 - (performance.now() - (keyTimes.get(e.code) || 0)));\n        releaseTimers.set(e.code, setTimeout(() => applyKey(e.code, false), delay));\n    };")
s=s.replace("            running = false;", "            for (const timer of releaseTimers.values()) clearTimeout(timer);\n            running = false;")
s=s.replace("    window.addEventListener('keyup', onKeyUp);", "    window.addEventListener('keyup', onKeyUp);\n    const releaseAllKeys = () => { for (const timer of releaseTimers.values()) clearTimeout(timer); keyMask = 0; padMask = 0; pushInput(); };\n    window.addEventListener('blur', releaseAllKeys);")
s=s.replace("            window.removeEventListener('keyup', onKeyUp);", "            window.removeEventListener('keyup', onKeyUp);\n            window.removeEventListener('blur', releaseAllKeys);")
s=s.replace("        importBattery(bytes) {", "        importBattery(bytes) {\n            releaseAllKeys();")
# Video must continue even when a browser audio worklet stalls after reset.
start=s.index("        if (audioCtx.state === 'running' && audioClockAdvancing(now)) {")
end=s.index("        frames = Math.max",start)
s=s[:start]+"""        // Wall-clock video pacing keeps silent ROMs and restored saves playable.
        if (!wallClockStart) {
            wallClockStart = now;
            wallClockFrames = 0;
        }
        const due = Math.floor(((now - wallClockStart) / 1000) * framerate);
        frames = due - wallClockFrames;
        wallClockFrames = due;
"""+s[end:]
s='/* Modified for SF Mini Monsters: battery saves, frame-safe input, video pacing. MPL-2.0. */\n'+s
p.write_text(s)
(out/'entry.js').write_text("import { load } from './mgba.sdk.js';\nimport { extractRom } from './mgba.zip.js';\nwindow.sfMiniMonstersLoad = load;\nwindow.sfMiniMonstersExtract = bytes => extractRom(bytes, ['.gba']);\n")
print('Prepared same-origin mGBA runtime and battery-save extension.')
