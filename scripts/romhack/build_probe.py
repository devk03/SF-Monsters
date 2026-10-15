"""Build an SF content overlay and publish a BPS patch, never the inherited ROM."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from bootstrap import ROOT, EMERALD, EMERALD_REVISION, SDK, checkout
from maps import apply_maps
from battle_content import apply_battles
from engine_guards import apply_engine_guards
from field_journal import apply_field_journal
from city_map import apply_city_map
from city_map_audit import audit_city_map
from seed_door_audit import audit_seed_door
from connected_frontage_audit import audit_connected
from city_furniture_audit import audit_furniture
from park_density_audit import audit_density
from service_architecture_audit import audit_services
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
from cast_art import apply_cast, audit_compiled_cast, GROUPS
from trainer_portraits import apply_portrait
from trainer_class_alias import apply_alias
from trainer_portrait_audit import audit_portraits
from intro_art import apply_intro, audit_intro
from courier_battle_art import apply_courier_battle
from office_art import apply_office, office_resources
from clinic_art import apply_clinic, clinic_resources
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
    restored += apply_city_map(content, ROOT, EMERALD, original)
    restored += apply_engine_guards(ROOT, EMERALD, original)
    restored += apply_field_journal(ROOT, EMERALD, original)
    restored += apply_monsters(content, ROOT, EMERALD, original)
    restored += apply_alias(ROOT, EMERALD)
    restored += apply_creature_audio(content, ROOT, EMERALD, original)
    restored += apply_field_music(content, ROOT, EMERALD, original)
    restored += apply_courier(ROOT, EMERALD, original)
    restored += apply_cast(ROOT, EMERALD, original)
    restored += apply_portrait(ROOT, EMERALD, original)
    restored += apply_intro(ROOT, EMERALD, original)
    restored += apply_courier_battle(ROOT, EMERALD, original)
    restored += prepare_sunset_tiles(ROOT, EMERALD, original)
    restored += apply_apartment_art(ROOT, EMERALD, original)
    restored += apply_door_art(ROOT, EMERALD, original)
    restored += apply_coastal_animation(ROOT, EMERALD, original)
    restored += apply_park_map(ROOT, EMERALD)
    restored += apply_park_doors(ROOT, EMERALD)
    restored += apply_office(ROOT, EMERALD)
    restored += apply_clinic(ROOT, EMERALD)
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
    # Validate the final cartridge, not just copied PNGs or generated caches.
    # The portable ELF reader works with host and Docker-produced artifacts.
    sys.path.insert(0, str(ROOT / 'scripts/quality'))
    from check_creature_resources import audit as audit_creatures
    compiled_creatures = audit_creatures(target, EMERALD / 'sf-engine-probe.elf', ROOT,
                                        EMERALD / 'include/constants/species.h')
    validation_bytes = (json.dumps(compiled_creatures, indent=2) + '\n').encode()
    validation_directory = ROOT / '.tools/romhack-validation'
    validation_directory.mkdir(parents=True, exist_ok=True)
    validation_path = validation_directory / ('creatures-' + uuid.uuid4().hex + '.json')
    with validation_path.open('xb') as stream:
        stream.write(validation_bytes)
    if compiled_creatures.get('passed') is not True:
        raise ValueError('Compiled creature resources failed; preserved receipt: ' + str(validation_path))
    print('Compiled creature resources verified: ' + json.dumps(compiled_creatures['counts']))
    compiled_intro = audit_intro(target, EMERALD / 'sf-engine-probe.elf', ROOT)
    intro_bytes = (json.dumps(compiled_intro, indent=2) + '\n').encode()
    intro_path = validation_directory / ('intro-' + uuid.uuid4().hex + '.json')
    with intro_path.open('xb') as stream:
        stream.write(intro_bytes)
    if compiled_intro.get('passed') is not True:
        raise ValueError('Compiled intro figure failed; preserved receipt: ' + str(intro_path))
    print('Compiled original intro verified: ' + json.dumps(compiled_intro['counts']))
    compiled_cast = audit_compiled_cast(target, EMERALD / 'sf-engine-probe.elf', ROOT,
                                       EMERALD / 'include/constants/event_objects.h')
    cast_bytes = (json.dumps(compiled_cast, indent=2) + '\n').encode()
    cast_path = validation_directory / ('field-cast-' + uuid.uuid4().hex + '.json')
    with cast_path.open('xb') as stream:
        stream.write(cast_bytes)
    if compiled_cast.get('passed') is not True:
        raise ValueError('Compiled original field cast failed; preserved receipt: ' + str(cast_path))
    print('Compiled original field cast verified: ' + json.dumps(compiled_cast['counts']))
    compiled_map = audit_city_map(target, EMERALD / 'sf-engine-probe.elf', ROOT, EMERALD)
    map_bytes = (json.dumps(compiled_map, indent=2) + '\n').encode()
    map_path = validation_directory / ('city-map-' + uuid.uuid4().hex + '.json')
    with map_path.open('xb') as stream:
        stream.write(map_bytes)
    if compiled_map.get('passed') is not True:
        raise ValueError('Compiled SF map failed; preserved receipt: ' + str(map_path))
    print('Compiled SF map verified: ' + json.dumps(compiled_map['counts']))
    compiled_seed_door = audit_seed_door(target, EMERALD / 'sf-engine-probe.elf', ROOT)
    seed_door_bytes = (json.dumps(compiled_seed_door, indent=2) + '\n').encode()
    seed_door_path = validation_directory / ('seed-door-' + uuid.uuid4().hex + '.json')
    with seed_door_path.open('xb') as stream:
        stream.write(seed_door_bytes)
    if compiled_seed_door.get('passed') is not True:
        raise ValueError('Compiled seed door failed; preserved receipt: ' + str(seed_door_path))
    print('Compiled seed door verified: ' + json.dumps(compiled_seed_door['counts']))
    compiled_portraits = audit_portraits(target, EMERALD / 'sf-engine-probe.elf', ROOT)
    portrait_bytes = (json.dumps(compiled_portraits, indent=2) + '\n').encode()
    portrait_path = validation_directory / ('trainer-portraits-' + uuid.uuid4().hex + '.json')
    with portrait_path.open('xb') as stream:
        stream.write(portrait_bytes)
    if compiled_portraits.get('passed') is not True:
        raise ValueError('Compiled trainer portraits failed; preserved receipt: ' + str(portrait_path))
    print('Compiled trainer portraits verified: ' + json.dumps(compiled_portraits['counts']))
    compiled_density = audit_density(target, EMERALD / 'sf-engine-probe.elf', ROOT)
    density_bytes = (json.dumps(compiled_density, indent=2) + '\n').encode()
    density_path = validation_directory / ('park-density-' + uuid.uuid4().hex + '.json')
    with density_path.open('xb') as stream:
        stream.write(density_bytes)
    if compiled_density.get('passed') is not True:
        raise ValueError('Compiled park density failed; preserved receipt: ' + str(density_path))
    print('Compiled park density verified: ' + json.dumps(compiled_density['counts']))
    compiled_furniture = audit_furniture(target, EMERALD / 'sf-engine-probe.elf', ROOT, density=True)
    furniture_bytes = (json.dumps(compiled_furniture, indent=2) + '\n').encode()
    furniture_path = validation_directory / ('city-furniture-' + uuid.uuid4().hex + '.json')
    with furniture_path.open('xb') as stream:
        stream.write(furniture_bytes)
    if compiled_furniture.get('passed') is not True:
        raise ValueError('Compiled city furniture failed; preserved receipt: ' + str(furniture_path))
    print('Compiled city furniture verified: ' + json.dumps(compiled_furniture['counts']))
    compiled_connected = audit_connected(target, EMERALD / 'sf-engine-probe.elf', ROOT, furniture=True, density=True)
    infill_bytes = (json.dumps(compiled_connected, indent=2) + '\n').encode()
    infill_path = validation_directory / ('connected-frontage-' + uuid.uuid4().hex + '.json')
    with infill_path.open('xb') as stream:
        stream.write(infill_bytes)
    if compiled_connected.get('passed') is not True:
        raise ValueError('Compiled connected frontage failed; preserved receipt: ' + str(infill_path))
    print('Compiled connected frontage verified: ' + json.dumps(compiled_connected['counts']))
    compiled_services = audit_services(target, EMERALD / 'sf-engine-probe.elf', ROOT)
    service_bytes = (json.dumps(compiled_services, indent=2) + '\n').encode()
    service_path = validation_directory / ('service-architecture-' + uuid.uuid4().hex + '.json')
    with service_path.open('xb') as stream:
        stream.write(service_bytes)
    if compiled_services.get('passed') is not True:
        raise ValueError('Compiled service architecture failed; preserved receipt: ' + str(service_path))
    print('Compiled service architecture verified: ' + json.dumps(compiled_services['counts']))
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
    manifest['compiled_city_map'] = {
        'passed': True, 'counts': compiled_map['counts'],
        'receipt_sha256': hashlib.sha256(map_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/city_map_audit.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending', 'scope': compiled_map['scope']
    }
    manifest['compiled_connected_frontage'] = {
        'passed': True, 'counts': compiled_connected['counts'],
        'receipt_sha256': hashlib.sha256(infill_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/connected_frontage_audit.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending', 'scope': compiled_connected['scope'],
        'normalization': compiled_connected.get('normalization')
    }
    manifest['compiled_park_density'] = {
        'passed': True, 'counts': compiled_density['counts'],
        'receipt_sha256': hashlib.sha256(density_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/park_density_audit.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending', 'scope': compiled_density['scope']
    }
    manifest['compiled_city_furniture'] = {
        'passed': True, 'counts': compiled_furniture['counts'],
        'receipt_sha256': hashlib.sha256(furniture_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/city_furniture_audit.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending', 'scope': compiled_furniture['scope'],
        'normalization': compiled_furniture.get('normalization')
    }
    manifest['compiled_service_architecture'] = {
        'passed': True, 'counts': compiled_services['counts'],
        'receipt_sha256': hashlib.sha256(service_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/service_architecture_audit.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending', 'scope': compiled_services['scope']
    }
    manifest['compiled_seed_door'] = {
        'passed': True, 'counts': compiled_seed_door['counts'],
        'receipt_sha256': hashlib.sha256(seed_door_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/seed_door_audit.py').read_bytes()).hexdigest(),
        'resident_tiles': compiled_seed_door['resident_tiles'],
        'quality_approval': 'pending', 'scope': compiled_seed_door['scope']
    }
    manifest['compiled_field_cast'] = {
        'passed': True, 'counts': compiled_cast['counts'],
        'receipt_sha256': hashlib.sha256(cast_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/cast_art.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending', 'scope': compiled_cast['scope']
    }
    manifest['compiled_trainer_portraits'] = {
        'passed': True, 'counts': compiled_portraits['counts'],
        'receipt_sha256': hashlib.sha256(portrait_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/trainer_portrait_audit.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending', 'scope': compiled_portraits['scope']
    }
    manifest['compiled_intro'] = {
        'passed': True, 'counts': compiled_intro['counts'],
        'receipt_sha256': hashlib.sha256(intro_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/romhack/intro_art.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending', 'scope': compiled_intro['scope']
    }
    manifest['normal_compilation_verified'] = True
    manifest['compiled_creatures'] = {
        'passed': True, 'counts': compiled_creatures['counts'],
        'receipt_sha256': hashlib.sha256(validation_bytes).hexdigest(),
        'validator_sha256': hashlib.sha256((ROOT / 'scripts/quality/check_creature_resources.py').read_bytes()).hexdigest(),
        'quality_approval': 'pending',
        'scope': 'Compiled resource identity and bindings; not human art or gameplay approval'
    }
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
    manifest['courier_battle'] = json.loads((ROOT /
        'assets/characters/courier-battle-v1/conversion.json').read_text())
    for asset, *_ in GROUPS:
        manifest[Path(asset).name.replace('-', '_')] = json.loads(
            (ROOT/asset/'conversion.json').read_text())
    office_data = office_resources(ROOT)
    manifest['cognition_office'] = {'native_tiles':len(office_data[0])//32,
        'metatiles':len(office_data[1])//16, 'quality_approval':'pending',
        'resource_sha256':{name:hashlib.sha256(data).hexdigest() for name,data in
            zip(('tiles','metatiles','attributes','palettes'),office_data)}}
    clinic_data = clinic_resources(ROOT)
    manifest['south_park_clinic'] = {'native_tiles':len(clinic_data[0])//32,
        'metatiles':len(clinic_data[1])//16, 'quality_approval':'pending',
        'resource_sha256':{name:hashlib.sha256(data).hexdigest() for name,data in
            zip(('tiles','metatiles','attributes','palettes'),clinic_data)}}
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
        'assets/tiles/service-door-v2/conversion.json').read_text())
    manifest['connected_frontage'] = json.loads((ROOT /
        'assets/tiles/connected-frontage-v3/conversion.json').read_text())
    manifest['south_park_services'] = json.loads((ROOT /
        'assets/tiles/south-park-services-v3/conversion.json').read_text())
    manifest['compact_townhouses'] = json.loads((ROOT /
        'assets/tiles/compact-townhouses-v1/conversion.json').read_text())
    manifest['city_furniture'] = json.loads((ROOT /
        'assets/tiles/city-furniture-v1/conversion.json').read_text())
    if args.fixture:
        manifest['fixture'] = {'name': args.fixture, 'setup': 'native scripted gift and Rare Candy',
                               'campaign_progress_evidence': False}
    manifest_path = output / 'manifest.json'
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'SF patch verified: {patch} ({patch.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
