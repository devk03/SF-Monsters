"""Read native music-player state from a verified, controller-only mGBA snapshot."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import subprocess

REVISION = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2'


def inspect(directory, elf):
    metadata = json.loads((directory / 'capture.json').read_text())
    manifest = json.loads((elf.parent / 'manifest.json').read_text())
    cartridge = elf.parent / 'target.gba'
    digest = hashlib.sha256(cartridge.read_bytes()).hexdigest()
    if digest != metadata['rom_sha256'] or digest != manifest['target_sha256']:
        raise ValueError('Snapshot and ELF companion cartridge identities differ.')
    if metadata['mgba_revision'] != REVISION or metadata.get('controller_only') is not True:
        raise ValueError('Only the pinned controller-only capture format is supported.')
    wanted = {'gMPlayInfo_BGM', 'gMPlayInfo_SE2', 'sFanfareCounter', 'voicegroup_sf_heal'}
    symbols = {}
    for line in subprocess.check_output(['arm-none-eabi-nm', '-S', '--defined-only', str(elf)], text=True).splitlines():
        parts = line.split()
        if parts and parts[-1] in wanted:
            if parts[-1] in symbols:
                raise ValueError('Ambiguous native music symbol.')
            symbols[parts[-1]] = int(parts[0], 16)
    if set(symbols) != wanted:
        raise ValueError('ELF lacks the declared recovery/music state symbols.')
    state = (directory / 'capture.state').read_bytes()

    def offset(address, size):
        region = address >> 24
        if region == 2:
            result = 0x21000 + (address & 0x3ffff)
        elif region == 3:
            result = 0x19000 + (address & 0x7fff)
        else:
            raise ValueError('Music state address is outside native RAM.')
        if result + size > len(state):
            raise ValueError('Snapshot is truncated.')
        return result

    def player(name):
        start = offset(symbols[name], 64)
        status = struct.unpack_from('<I', state, start + 4)[0]
        return {'status': hex(status), 'active_tracks': status & 0xffff,
                'paused': bool(status & 0x80000000), 'track_count': state[start + 8],
                'clock_ticks': struct.unpack_from('<I', state, start + 12)[0],
                'voicegroup': hex(struct.unpack_from('<I', state, start + 48)[0])}

    bgm, cue = player('gMPlayInfo_BGM'), player('gMPlayInfo_SE2')
    counter = struct.unpack_from('<H', state, offset(symbols['sFanfareCounter'], 2))[0]
    return {'rom_sha256': digest, 'core_revision': REVISION, 'fanfare_frames_remaining': counter,
            'bgm': bgm, 'cue': cue, 'recovery_voicegroup': hex(symbols['voicegroup_sf_heal']),
            'cue_uses_recovery_bank': cue['voicegroup'] == hex(symbols['voicegroup_sf_heal'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--elf', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.directory, args.elf), indent=2))


if __name__ == '__main__':
    main()
