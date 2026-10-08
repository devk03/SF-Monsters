"""Link original title music into its existing native song allocation."""
import hashlib
import json
import struct
import subprocess
import uuid
from native_resources import replace_resource, named_addresses
from title_music import write_title_score

WAVES = ('lead', 'bass', 'major', 'minor', 'answer', 'kick', 'snare', 'hat')


def song_region(blob, own_header, header_offset, old_header_size, base, group):
    if not 0 <= own_header <= len(blob) - 8 or header_offset < len(blob):
        raise ValueError('Title sequence exceeds its existing track allocation.')
    count = blob[own_header]
    size = 8 + count * 4
    if not 1 <= count <= 10 or size > old_header_size or own_header + size > len(blob):
        raise ValueError('Title header exceeds the existing player/track capacity.')
    header = blob[own_header:own_header + size]
    if struct.unpack_from('<I', header, 4)[0] != group:
        raise ValueError('Title header must use the original SF sample bank.')
    pointers = struct.unpack_from('<' + 'I' * count, header, 8)
    if any(not base <= pointer < base + own_header for pointer in pointers):
        raise ValueError('A title track points outside the original score payload.')
    # Song table keeps its existing header address. Only tracks/header change.
    return blob + bytes(header_offset - len(blob)) + header + bytes(old_header_size - size)


def apply_title_song(root, emerald, target):
    score = json.loads((root / 'assets/audio/foglight-overture.json').read_text())
    volume = score['native_volume']
    if type(volume) is not int or not 1 <= volume <= 100:
        raise ValueError('Native title mix must be 1–100 percent.')
    midi = write_title_score(root)
    work = root / '.tools' / ('title-song-' + uuid.uuid4().hex)
    work.mkdir()
    names = {'mus_title', 'mus_title_1', 'voicegroup_vs_wild'} | {'SF_Wild_' + name for name in WAVES}
    addresses = named_addresses(emerald / 'sf-engine-probe.elf', names)
    linked_path = work / 'linked.bin'
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary',
        str(emerald / 'sf-engine-probe.elf'), str(linked_path)], check=True)
    rom, linked = target.read_bytes(), linked_path.read_bytes()
    group = addresses['voicegroup_vs_wild']
    # Verify every instrument is our declared waveform, not a legacy title voice.
    for index, name in enumerate(WAVES):
        pointer = struct.unpack_from('<I', rom, group - 0x08000000 + index * 12 + 4)[0]
        if pointer != addresses['SF_Wild_' + name]:
            raise ValueError('SF title voicegroup sample pointer changed.')
        owned = (root / 'assets/audio/fogbank-frenzy-native-v1' / (name + '.bin')).read_bytes()
        offset = pointer - 0x08000000
        if rom[offset:offset + len(owned)] != owned:
            raise ValueError('SF title sample bytes do not match our original PCM source.')
    base, header = addresses['mus_title_1'], addresses['mus_title']
    header_offset = header - base
    count = linked[header - 0x08000000]
    if count != 10 or header_offset < 1:
        raise ValueError('Pinned native title allocation changed.')
    old_header_size = 8 + count * 4
    original_pointers = struct.unpack_from('<10I', linked, header - 0x08000000 + 8)
    if min(original_pointers) != base or any(not base <= pointer < header for pointer in original_pointers):
        raise ValueError('Native title allocation is not the expected contiguous song.')
    tool, converter = emerald / 'tools/mid2agb', work / 'mid2agb'
    subprocess.run(['c++', '-std=c++11', '-O2', '-Wall', '-Wno-switch', '-Werror',
        *[str(tool / name) for name in ('agb.cpp', 'error.cpp', 'main.cpp', 'midi.cpp', 'tables.cpp')],
        '-o', str(converter)], check=True)
    assembly, obj, elf, binary = [work / ('foglight.' + suffix) for suffix in ('s', 'o', 'elf', 'bin')]
    subprocess.run([str(converter), str(midi), str(assembly), '-Lfoglight_overture',
        '-G_vs_wild', '-V' + str(volume), '-R50', '-E'], check=True)
    subprocess.run(['arm-none-eabi-as', '-I', str(emerald / 'sound'), str(assembly), '-o', str(obj)], check=True)
    linker = work / 'song.ld'
    linker.write_text(f'SECTIONS {{ .rodata 0x{base:x} : {{ *(.rodata) }} }}\n')
    subprocess.run(['arm-none-eabi-ld', '-T', str(linker),
        '--defsym', f'voicegroup_vs_wild=0x{group:x}', str(obj), '-o', str(elf)], check=True)
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', str(elf), str(binary)], check=True)
    new_header = named_addresses(elf, {'foglight_overture'})['foglight_overture'] - base
    blob = binary.read_bytes()
    replacement = song_region(blob, new_header, header_offset, old_header_size, base, group)
    target.write_bytes(replace_resource(rom, linked, base - 0x08000000,
        header_offset + old_header_size, replacement))
    return {'title': score['title'], 'region_address': base, 'header_address': header,
        'allocated_bytes': header_offset + old_header_size, 'score_bytes': len(blob),
        'tracks': blob[new_header], 'voicegroup_address': group, 'native_volume': volume,
        'midi_sha256': hashlib.sha256(midi.read_bytes()).hexdigest(),
        'score_sha256': hashlib.sha256(blob).hexdigest(),
        'waveform_sources_verified': True, 'quality_approval': 'pending'}
