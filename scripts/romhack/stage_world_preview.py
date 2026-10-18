"""Stage only a tested normal-world patch; never copy cartridges or QA saves."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft',required=True,type=Path)
    parser.add_argument('--native-proof',required=True,type=Path)
    parser.add_argument('--wasm-proof',required=True,type=Path)
    parser.add_argument('--version',default='0.0.84-world-preview')
    args=parser.parse_args();draft=args.draft.resolve()
    draft.relative_to(ROOT/'.tools/romhack-drafts')
    if not re.fullmatch(r'\d+\.\d+\.\d+-world-preview',args.version):parser.error('Use a versioned world-preview release')
    source=json.loads((draft/'manifest.json').read_text())
    native=json.loads(args.native_proof.read_text());wasm=json.loads(args.wasm_proof.read_text())
    target=source['target_sha256']
    if (source['profile']!='world-blockout' or source['fixture'] is not None
            or source['save_magic']!=0x5743 or source['save_schema']!=1
            or source['patch_roundtrip']!='byte-identical'
            or source['source_contract']['passed'] is not True or source['compiled_maps']['passed'] is not True):
        raise ValueError('Only a validated normal SF world may become an exploration preview')
    if native['passed'] is not True or native['rom_sha256']!=target or any(native[k]!=n for k,n in
            [('maps',58),('connections',76),('gym_warps',16),('room_warps',26)]):
        raise ValueError('Require the complete matching native return circuit')
    if wasm['passed'] is not True or wasm['rom_sha256']!=target or wasm['different_bytes']!=0 or wasm['ram_bytes']!=294912:
        raise ValueError('Require matching whole-world native/WASM guest RAM proof')
    native_dir=args.native_proof.parent;wasm_dir=args.wasm_proof.parent
    session=json.loads((native_dir/'session.json').read_text())
    capture=json.loads((wasm_dir/'capture.json').read_text())
    rows=json.loads((native_dir/'inputs.json').read_text())
    trace=''.join(f'{keys},{frames}\n' for keys,frames in rows).encode()
    frames=sum(row[1] for row in rows)
    if (session['controller_only'] is not True or capture['controller_only'] is not True
            or session['rom_sha256']!=target or capture['rom_sha256']!=target
            or not session['state_input_sha256']
            or session['state_input_sha256']!=capture['state_input_sha256']
            or session['battery_input_sha256']!=capture['battery_input_sha256']
            or session['mgba_revision']!=capture['mgba_revision']
            or capture['input_sha256']!=hashlib.sha256(trace).hexdigest()
            or capture['frames']!=frames or wasm['frames']!=frames or frames<=0):
        raise ValueError('WASM replay must match the complete native circuit inputs, initial state and frame count')
    left=(native_dir/'returned.state').read_bytes();right=(wasm_dir/'capture.state').read_bytes()
    if (len(left)!=0x61000 or len(right)!=len(left) or left[0x19000:]!=right[0x19000:]
            or hashlib.sha256(left[0x19000:]).hexdigest()!=wasm['native_ram_sha256']
            or wasm['wasm_ram_sha256']!=wasm['native_ram_sha256']):
        raise ValueError('Actual final native/WASM guest RAM must match the reported proof')
    base=ROOT/'.tools/romhack-baseline/emerald-matching.gba'
    rom=draft/'target.gba';patch=draft/'sf-world-blockout.bps'
    if (sha(base),sha(rom),sha(patch))!=(source['base_sha256'],target,source['patch_sha256']):
        raise ValueError('Frozen draft or base bytes differ from their receipts')
    run=ROOT/'.tools/world-publication-checks'/uuid.uuid4().hex;run.mkdir(parents=True)
    subprocess.run([str(ROOT/'.tools/flips-macos'),'--apply','--exact',str(patch),str(base),str(run/'verified.gba')],check=True)
    if sha(run/'verified.gba')!=target:raise ValueError('Public patch roundtrip differs')
    manifest=dict(version=args.version,profile='world-preview',fixture=None,
                  base_sha256=source['base_sha256'],base_bytes=base.stat().st_size,
                  target_sha256=target,target_bytes=rom.stat().st_size,
                  patch_sha256=source['patch_sha256'],patch_bytes=patch.stat().st_size,
                  save_magic=0x5743,save_schema=1,game_code='BPEE',
                  source_version=source['version'],human_quality_approval='pending',
                  scope='18-destination exploration preview; temporary loan/access stamps; final gyms and contributor missions unfinished',
                  native_maps=58,connections=76,local_activities=18,service_interiors=13,
                  native_proof_sha256=sha(args.native_proof),wasm_proof_sha256=sha(args.wasm_proof),
                  full_route_frames=frames,controller_input_sha256=capture['input_sha256'],
                  build_source_commit=source['source_commit'],
                  build_inputs_sha256=hashlib.sha256(json.dumps(source['frozen_inputs'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                  staging_base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  provenance_note='Build commit is the checkout base; frozen build inputs are authoritative. Staging base is not a reproducibility assertion.')
    encoded=(json.dumps(manifest,indent=2)+'\n').encode()
    release=ROOT/'romhack/releases'/args.version
    release.mkdir(parents=True,exist_ok=True)
    for name,data in [('manifest.json',encoded),('sf-mini-monsters.bps',patch.read_bytes())]:
        path=release/name
        if path.exists() and path.read_bytes()!=data:raise ValueError('Preserve existing release; use a new version')
        if not path.exists():path.write_bytes(data)
    public=ROOT/'web/public/world-patch';public.mkdir(parents=True,exist_ok=True)
    for name in ('manifest.json','sf-mini-monsters.bps'):shutil.copyfile(release/name,public/name)
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
