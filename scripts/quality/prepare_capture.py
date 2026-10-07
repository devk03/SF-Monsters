"""Prepare local, reproducible native mGBA captures without publishing reference ROMs."""
from pathlib import Path
import argparse, hashlib, json, subprocess
from zipfile import ZipFile
ROOT = Path(__file__).resolve().parents[2]
REFERENCE_HASH = 'a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af'
SCENARIOS = ['intro','town-walk','route-walk','interior','dialogue','wild-battle',
             'trainer-battle','move-effects','capture','evolution','menus','story']

def prepare(rom: bytes, name: str, reference: bool) -> Path:
    if len(rom) < 192: raise ValueError('Cartridge is too short')
    digest = hashlib.sha256(rom).hexdigest()
    if reference and digest != REFERENCE_HASH:
        raise ValueError('Reference does not match the approved Emerald hash')
    code = rom[172:176].decode('ascii')
    if not reference and code != 'SFMM': raise ValueError('Expected an SFMM cartridge')
    # Keep all recordings, battery saves, and reference data in ignored local storage.
    destination = ROOT/'.tools'/'benchmarks'/name
    destination.mkdir(parents=True, exist_ok=True)
    for scenario in SCENARIOS: (destination/scenario).mkdir(exist_ok=True)
    cartridge = destination/'cartridge.gba'
    if cartridge.exists() and cartridge.read_bytes() != rom:
        raise ValueError('Use a new capture name when the cartridge changes')
    cartridge.write_bytes(rom)
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    metadata = {'schema':1,'name':name,'reference':reference,'rom_sha256':digest,
                'game_code':code,'source_commit':None if reference else head,
                'reference_identity':'BPEE USA/Europe' if reference else None,
                'emulator':'native mGBA 0.10.5','speed':'normal',
                'capture_status':'prepared, not recorded','audio_status':'not recorded'}
    (destination/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    scenario_table = '{'+','.join(f'["{s}"]=true' for s in SCENARIOS)+'}'
    prelude = (f'BENCH_GAME_CODE = {json.dumps(code)}\n'
               f'BENCH_OUTPUT = {json.dumps(str(destination))}\n'
               f'BENCH_SCENARIOS = {scenario_table}\n')
    script = ROOT/'tests'/'quality'/'native_capture.lua'
    (destination/'capture.lua').write_text(prelude+script.read_text())
    return destination

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sources=parser.add_mutually_exclusive_group(required=True)
    sources.add_argument('--reference-zip',type=Path)
    sources.add_argument('--sf-rom',type=Path)
    parser.add_argument('--name',required=True)
    args=parser.parse_args()
    if not args.name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in args.name):
        parser.error('Name must use lowercase letters, numbers, hyphens or underscores')
    reference=args.reference_zip is not None
    if reference:
        with ZipFile(args.reference_zip) as archive:
            entries=[entry for entry in archive.infolist() if entry.filename.lower().endswith('.gba')]
            if len(entries)!=1: parser.error('Archive must contain exactly one GBA ROM')
            rom=archive.read(entries[0])
    else: rom=args.sf_rom.read_bytes()
    destination=prepare(rom,args.name,reference)
    print(f'Open {destination}/cartridge.gba in mGBA.')
    print(f'Load {destination}/capture.lua through Tools > Scripting > File > Load script.')
    print('Record audio/video through mGBA Audio/Video before beginning a scored comparison.')
    print('Use Bench.play for input and Bench.begin("town-walk",1800) for a frame capture.')

if __name__=='__main__': main()
