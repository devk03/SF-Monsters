"""Capture synchronized native mGBA frames/audio without depending on GUI presets."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / '.tools/mgba-native'
BUILD = ROOT / '.tools/mgba-build'
REVISION = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2'
SDK = ('devkitpro/devkitarm@sha256:'
       '116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5')
REFERENCE_HASH = 'a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af'


def docker(*command):
    subprocess.run(['docker', 'run', '--name', 'sf-capture-' + uuid.uuid4().hex[:10],
        '--mount', f'type=bind,src={ROOT},dst=/workspace', '--workdir=/workspace',
        SDK, *command], check=True)


def mounted(path):
    return '/workspace/' + str(path.resolve().relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup', action='store_true')
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--state', type=Path)
    parser.add_argument('--telemetry', default='0')
    parser.add_argument('--trace-only', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.name):
        parser.error('Use a short lowercase benchmark name.')
    if not re.fullmatch(r'[0-9a-fA-F]{1,8}', args.telemetry):
        parser.error('Telemetry must be a hexadecimal address, or zero.')
    # All container-visible inputs and all outputs remain inside this checkout.
    for path in [args.rom, args.input] + ([args.state] if args.state else []):
        if not path.is_file():
            parser.error(f'Missing input: {path}')
        mounted(path)
    rom = args.rom.read_bytes()
    digest = hashlib.sha256(rom).hexdigest()
    code = rom[0xac:0xb0]
    if code == b'BPEE' and digest != REFERENCE_HASH:
        parser.error('Reference hash does not match the approved Emerald ROM.')
    if code not in [b'BPEE', b'SFMM']:
        parser.error('Only the approved reference or an SF cartridge is supported.')
    if args.state:
        state_metadata = args.state.with_suffix('.json')
        if not state_metadata.is_file():
            parser.error('State must have its original capture metadata beside it.')
        if json.loads(state_metadata.read_text()).get('rom_sha256') != digest:
            parser.error('State belongs to a different cartridge build.')
    output = ROOT / '.tools/benchmarks' / args.name
    if output.exists():
        parser.error('Choose a new name; existing benchmark evidence is preserved.')
    if args.setup:
        if not SOURCE.exists():
            subprocess.run(['git', 'clone', '--depth', '1', '--branch', '0.10.5',
                'https://github.com/mgba-emu/mgba.git', str(SOURCE)], check=True)
        docker('cmake', '-S', '.tools/mgba-native', '-B', '.tools/mgba-build',
            '-DLIBMGBA_ONLY=ON', '-DENABLE_SCRIPTING=OFF', '-DUSE_FFMPEG=OFF',
            '-DUSE_LIBZIP=OFF', '-DUSE_LZMA=OFF', '-DUSE_PNG=OFF',
            '-DBUILD_GL=OFF', '-DBUILD_GLES2=OFF', '-DBUILD_GLES3=OFF')
        docker('cmake', '--build', '.tools/mgba-build', '-j8')
    if not SOURCE.exists() or not (BUILD / 'libmgba.a').exists():
        parser.error('Add --setup to build the pinned native core first.')
    revision = subprocess.check_output(
        ['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != REVISION:
        parser.error('Native mGBA source revision mismatch.')
    docker('cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-D_GNU_SOURCE',
        '-DBUILD_STATIC', '-I.tools/mgba-native/include', '-I.tools/mgba-build/include',
        'scripts/quality/core_capture.c', '.tools/mgba-build/libmgba.a',
        '-lm', '-lpthread', '-o', '.tools/core_capture')
    output.mkdir(parents=True)
    prefix = output / 'capture'
    docker('.tools/core_capture', mounted(args.rom), mounted(prefix), mounted(args.input),
        mounted(args.state) if args.state else '-', args.telemetry,
        'trace' if args.trace_only else 'video')
    metadata = json.loads(prefix.with_suffix('.json').read_text())
    metadata.update({
        'rom_sha256': digest, 'game_code': code.decode(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'runtime': 'native mGBA 0.10.5 core, Linux ARM64 official devkitARM container',
        'mgba_revision': REVISION, 'input_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
        'controller_only': True, 'trace_only': args.trace_only,
        'user_quality_approval': 'pending', 'host_browser_performance_proven': False
    })
    prefix.with_suffix('.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(f'Native capture saved: {output}')


if __name__ == '__main__':
    main()
