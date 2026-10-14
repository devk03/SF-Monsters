"""Vendor the pinned mGBA runtime, keeping the build reproducible and same-origin."""
from pathlib import Path
import shutil
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'web/node_modules/@wasm-gaming/mgba-wasm/dist/mgba'
out=ROOT/'web/public/emulator';out.mkdir(parents=True,exist_ok=True)
# The tracked frontend is maintained source; never regenerate it from upstream.
owned = {'mgba.sdk.js', 'mgba.audio-worklet.js', 'mgba.performance.js'}
if not (out/'mgba.sdk.js').is_file():
    raise ValueError('Restore the tracked SF SDK before preparing the runtime.')
for path in source.iterdir():
    if path.suffix == '.js' and path.name not in owned | {'mgba.js'}:
        shutil.copy2(path,out/path.name)
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
for name in ['mgba.js','mgba.wasm']:(out/name).chmod(0o644)
(out/'entry.js').write_text("import { load } from './mgba.sdk.js';\nimport { extractRom } from './mgba.zip.js';\nwindow.sfMiniMonstersLoad = load;\nwindow.sfMiniMonstersExtract = bytes => extractRom(bytes, ['.gba']);\n")
print('Prepared pinned same-origin core; preserved the maintained SF frontend.')
