"""Build an SF content overlay and publish a BPS patch, never the inherited ROM."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import uuid
from bootstrap import ROOT, EMERALD, EMERALD_REVISION, SDK, checkout
from maps import apply_maps
from battle_content import apply_battles
from engine_guards import apply_engine_guards
from monsters import apply_monsters
from creature_audio import apply_creature_audio

FLIPS = ROOT / '.tools/flips'
FLIPS_REVISION = 'ff216a75df0987047a67d7923567dc4482ce07ac'
BASE = ROOT / '.tools/romhack-baseline/emerald-matching.gba'
BASE_HASH = 'a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af'


def docker(*command, directory='/workspace'):
    subprocess.run(['docker', 'run', '--name', 'sf-hack-' + uuid.uuid4().hex[:10],
        '--mount', f'type=bind,src={ROOT},dst=/workspace', '--workdir', directory,
        SDK, *command], check=True)


def original(path):
    return subprocess.check_output(['git', 'show', f'{EMERALD_REVISION}:{path}'],
                                   cwd=EMERALD, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true', help='Keep iteration artifacts in ignored local storage.')
    args = parser.parse_args()
    if not BASE.exists() or hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_HASH:
        raise ValueError('Run bootstrap.py and verify the matching baseline first.')
    content = json.loads((ROOT / 'romhack/content/engine-probe.json').read_text())
    sections_path = 'src/data/region_map/region_map_sections.json'
    sections = json.loads(original(sections_path))
    changed = set()
    for section in sections['map_sections']:
        if section['id'] in content['region_names']:
            section['name'] = content['region_names'][section['id']]
            changed.add(section['id'])
    if changed != set(content['region_names']):
        raise ValueError('A requested region ID does not exist in the pinned engine.')
    (EMERALD / sections_path).write_text(json.dumps(sections, indent=2) + '\n')
    speech_path = 'data/text/birch_speech.inc'
    speech = original(speech_path)
    for symbol, text in content['intro'].items():
        if '"' in text or '\n' in text:
            raise ValueError('Use escaped engine control characters in single-line strings.')
        replacement = f'{symbol}::\n\t.string "{text}"\n'
        speech, count = re.subn(rf'(?m)^{re.escape(symbol)}::\n.*?(?=^\w+::|\Z)',
                               lambda match: replacement + '\n', speech, flags=re.S)
        if count != 1:
            raise ValueError(f'Expected one intro symbol: {symbol}')
    (EMERALD / speech_path).write_text(speech)
    restored = [sections_path, speech_path] + apply_maps(content, ROOT, EMERALD, original)
    restored += apply_battles(content, ROOT, EMERALD, original)
    restored += apply_engine_guards(ROOT, EMERALD, original)
    restored += apply_monsters(content, ROOT, EMERALD, original)
    restored += apply_creature_audio(content, ROOT, EMERALD, original)
    (ROOT / '.tools/romhack-overlay-files.json').write_text(json.dumps(restored) + '\n')
    docker('make', '-j8', 'FILE_NAME=sf-engine-probe', f'TITLE={content["title"]}',
           f'GAME_CODE={content["game_code"]}', directory='/workspace/.tools/pokeemerald')
    target = EMERALD / 'sf-engine-probe.gba'
    checkout(FLIPS, 'https://github.com/Alcaro/Flips.git', FLIPS_REVISION)
    docker('make', 'TARGET=cli', 'CFLAGS=-O2', directory='/workspace/.tools/flips')
    target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    output = ((ROOT / '.tools/romhack-drafts' / content['version'] / target_hash)
              if args.draft else ROOT / 'romhack/releases' / content['version'])
    candidate = ROOT / '.tools' / ('candidate-' + uuid.uuid4().hex[:10] + '.bps')
    mounted = lambda path: '/workspace/' + str(path.relative_to(ROOT))
    docker('.tools/flips/flips', '--create', '--bps', '--exact',
           mounted(BASE), mounted(target), mounted(candidate))
    verification = ROOT / '.tools' / ('patch-roundtrip-' + uuid.uuid4().hex[:10] + '.gba')
    docker('.tools/flips/flips', '--apply', '--exact', mounted(candidate), mounted(BASE), mounted(verification))
    if verification.read_bytes() != target.read_bytes():
        raise ValueError('BPS application did not reproduce the compiled cartridge.')
    output.mkdir(parents=True, exist_ok=True)
    patch = output / 'sf-mini-monsters.bps'
    if patch.exists() and patch.read_bytes() != candidate.read_bytes():
        raise ValueError('Bump the content version instead of replacing a released patch.')
    if not patch.exists():
        shutil.copy2(candidate, patch)
    manifest = {
        'version': content['version'], 'status': content['status'], 'game_code': content['game_code'],
        'base_sha256': BASE_HASH, 'base_bytes': BASE.stat().st_size,
        'target_sha256': target_hash,
        'target_bytes': target.stat().st_size,
        'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(),
        'patch_bytes': patch.stat().st_size,
        'emerald_revision': EMERALD_REVISION, 'flips_revision': FLIPS_REVISION,
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
        'patch_roundtrip': 'byte-identical', 'quality_approval': 'pending'
    }
    manifest_path = output / 'manifest.json'
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'SF patch verified: {patch} ({patch.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
