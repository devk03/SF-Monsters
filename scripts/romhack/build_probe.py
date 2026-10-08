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
from field_music import apply_field_music
from evolution_fixture import FIXTURES, apply_evolution_fixture
from interface_text import apply_interface_text
from interface_graphics import apply_interface_graphics
from title_art import apply_title_art
from title_creature import apply_title_creature
from title_song_overlay import apply_title_song
from house_art import apply_house_art, prepare_sunset_tiles
from courier_art import apply_courier
from cast_art import apply_cast
from apartment_art import apply_apartment_art
from door_art import apply_door_art
from terrain_art import apply_coastal_animation
from park_map import apply_park_map, park_resources
from park_doors import apply_park_doors

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
    global EMERALD
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=['docker', 'host'], default='docker',
                        help='Use the independently verified native host checkout.')
    parser.add_argument('--draft', action='store_true', help='Keep iteration artifacts in ignored local storage.')
    parser.add_argument('--fixture', choices=FIXTURES, help='Private level/evolution setup, never campaign evidence.')
    args = parser.parse_args()
    if args.fixture and not args.draft:
        parser.error('Fixture cartridges must remain private --draft builds.')
    if args.backend == 'host':
        from host_toolchain import prepare_host, host_make
        EMERALD = prepare_host()
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
    restored += apply_field_music(content, ROOT, EMERALD, original)
    restored += apply_courier(ROOT, EMERALD, original)
    restored += apply_cast(ROOT, EMERALD)
    restored += prepare_sunset_tiles(ROOT, EMERALD, original)
    restored += apply_apartment_art(ROOT, EMERALD, original)
    restored += apply_door_art(ROOT, EMERALD, original)
    restored += apply_coastal_animation(ROOT, EMERALD, original)
    restored += apply_park_map(ROOT, EMERALD)
    restored += apply_park_doors(ROOT, EMERALD)
    if args.fixture:
        apply_evolution_fixture(EMERALD, args.fixture, original)
        content['version'] += '-fixture-' + args.fixture
    (ROOT / '.tools/romhack-overlay-files.json').write_text(json.dumps(restored) + '\n')
    build_args = ('FILE_NAME=sf-engine-probe', f'TITLE={content["title"]}', f'GAME_CODE={content["game_code"]}')
    if args.backend == 'host':
        host_make(EMERALD, *build_args)
    else:
        docker('make', '-j8', *build_args, directory='/workspace/.tools/pokeemerald')
    target = EMERALD / 'sf-engine-probe.gba'
    text_receipt = apply_interface_text(ROOT, EMERALD, target)
    graphics_receipt = apply_interface_graphics(ROOT, EMERALD, target)
    title_receipt = apply_title_art(ROOT, EMERALD, target)
    creature_receipt = apply_title_creature(ROOT, EMERALD, target)
    song_receipt = apply_title_song(ROOT, EMERALD, target)
    house_receipt = apply_house_art(ROOT, EMERALD, target)
    checkout(FLIPS, 'https://github.com/Alcaro/Flips.git', FLIPS_REVISION)
    if args.backend == 'host':
        encoder = ROOT / '.tools/flips-macos'
        host_make(FLIPS, 'TARGET=cli', 'CFLAGS=-O2', 'FNAME_cli=' + str(encoder))
    else:
        docker('make', 'TARGET=cli', 'CFLAGS=-O2', directory='/workspace/.tools/flips')
    target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    output = ((ROOT / '.tools/romhack-drafts' / content['version'] / target_hash)
              if args.draft else ROOT / 'romhack/releases' / content['version'])
    candidate = ROOT / '.tools' / ('candidate-' + uuid.uuid4().hex[:10] + '.bps')
    def patch(*arguments):
        if args.backend == 'host':
            subprocess.run([str(encoder), *[str(value) for value in arguments]], check=True, timeout=300)
        else:
            docker('.tools/flips/flips', *['/workspace/' + str(value.relative_to(ROOT))
                   if isinstance(value, Path) else value for value in arguments])
    patch('--create', '--bps', '--exact', BASE, target, candidate)
    verification = ROOT / '.tools' / ('patch-roundtrip-' + uuid.uuid4().hex[:10] + '.gba')
    patch('--apply', '--exact', candidate, BASE, verification)
    if verification.read_bytes() != target.read_bytes():
        raise ValueError('BPS application did not reproduce the compiled cartridge.')
    output.mkdir(parents=True, exist_ok=True)
    if args.draft:
        # Captures use an immutable cartridge/ELF pair; neither is published.
        for source, name in ((target, 'target.gba'), (EMERALD / 'sf-engine-probe.elf', 'target.elf')):
            destination = output / name
            if destination.exists() and destination.read_bytes() != source.read_bytes():
                raise ValueError('Existing private build evidence changed; preserve and inspect it.')
            if not destination.exists():
                shutil.copy2(source, destination)
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
    manifest['build_backend'] = args.backend
    manifest['normal_compilation_verified'] = True
    if args.backend == 'host':
        manifest['host_toolchain'] = json.loads((EMERALD / 'sf-host-build.json').read_text())
    manifest['interface_text'] = text_receipt
    manifest['interface_graphics'] = graphics_receipt
    manifest['title_art'] = title_receipt
    manifest['title_creature'] = creature_receipt
    manifest['title_song'] = song_receipt
    manifest['sunset_house'] = house_receipt
    manifest['courier_apartment'] = json.loads((ROOT /
        'assets/tiles/courier-apartment/conversion.json').read_text())
    manifest['cognition_cast'] = json.loads((ROOT /
        'assets/characters/cognition-cast/conversion.json').read_text())
    manifest['rowhouse_door'] = json.loads((ROOT /
        'assets/tiles/sunset-door/conversion.json').read_text())
    manifest['coastal_terrain'] = json.loads((ROOT /
        'assets/tiles/sunset-terrain/conversion.json').read_text())
    park_raw, park_records, park_attributes, park_palettes = park_resources(ROOT)
    manifest['south_park'] = {'native_tiles': len(park_raw) // 32,
        'metatiles': len(park_records) // 16, 'quality_approval': 'pending',
        'resource_sha256': {name: hashlib.sha256(data).hexdigest() for name, data in
            zip(('tiles', 'metatiles', 'attributes', 'palettes'),
                (park_raw, park_records, park_attributes, park_palettes))}}
    manifest['south_park_doors'] = json.loads((ROOT /
        'assets/tiles/south-park-doors/conversion.json').read_text())
    if args.fixture:
        manifest['fixture'] = {'name': args.fixture, 'setup': 'native scripted gift and Rare Candy',
                               'campaign_progress_evidence': False}
    manifest_path = output / 'manifest.json'
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'SF patch verified: {patch} ({patch.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
