"""Capture synchronized native mGBA frames/audio without depending on GUI presets."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import re
import shlex
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / '.tools/mgba-native'
BUILD = ROOT / '.tools/mgba-build'
REVISION = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2'
SDK = ('devkitpro/devkitarm@sha256:'
       '116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5')
REFERENCE_HASH = 'a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af'
HOST_BUILD = ROOT / '.tools' / ('mgba-build-' + (
    'macos' if platform.system() == 'Darwin' else platform.system().lower()))


def host_setup():
    """Build the same pinned core locally, without changing the container build."""
    cmake = shutil.which('cmake')
    bundled = ROOT / '.tools/venv/bin/cmake'
    if not cmake and bundled.is_file():
        cmake = str(bundled)
    if not cmake:
        raise ValueError('Host capture needs CMake; the project venv is supported.')
    subprocess.run([cmake, '-S', str(SOURCE), '-B', str(HOST_BUILD),
        '-DLIBMGBA_ONLY=ON', '-DENABLE_SCRIPTING=OFF', '-DUSE_FFMPEG=OFF',
        '-DUSE_LIBZIP=OFF', '-DUSE_LZMA=OFF', '-DUSE_PNG=OFF', '-DUSE_ZLIB=OFF',
        '-DUSE_SQLITE3=OFF', '-DBUILD_GL=OFF', '-DBUILD_GLES2=OFF', '-DBUILD_GLES3=OFF',
        '-DBUILD_SHARED=OFF', '-DBUILD_STATIC=ON', '-DCMAKE_BUILD_TYPE=Release'], check=True)
    # Honor the workspace's no-removal rule before executing generated recipes.
    preserve = shlex.quote(sys.executable) + ' ' + shlex.quote(str(
        ROOT / 'scripts/romhack/preserve_files.py')) + ' -f'
    for recipe in HOST_BUILD.rglob('*.make'):
        source = recipe.read_text()
        adapted = re.sub(r'(?m)^RM = .*$', 'RM = ' + preserve, source)
        if re.search(r'(?<![\w/.$-])(?:rm|rmdir)(?=\s)', adapted):
            raise ValueError('Unexpected generated cleanup command; inspect before building.')
        if source != adapted:
            recipe.write_text(adapted)
    subprocess.run([cmake, '--build', str(HOST_BUILD), '-j8'], check=True)
    library = HOST_BUILD / 'libmgba.a'
    (HOST_BUILD / 'sf-capture-build.json').write_text(json.dumps({
        'revision': REVISION, 'system': platform.system(), 'machine': platform.machine(),
        'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(),
        'cmake_version': subprocess.check_output([cmake, '--version'], text=True).splitlines()[0],
        'configuration': 'static software core; scripting/compression/media dependencies disabled'
    }, indent=2) + '\n')


def verified_host_build():
    marker = HOST_BUILD / 'sf-capture-build.json'
    if not marker.is_file():
        raise ValueError('Add --setup to build and fingerprint the host core first.')
    info = json.loads(marker.read_text())
    if (info['revision'], info['system'], info['machine']) != (
            REVISION, platform.system(), platform.machine()):
        raise ValueError('Host core belongs to a different revision or platform.')
    if hashlib.sha256((HOST_BUILD / 'libmgba.a').read_bytes()).hexdigest() != info['library_sha256']:
        raise ValueError('Host core fingerprint changed; rebuild with --setup.')
    return info


def docker(*command):
    subprocess.run(['docker', 'run', '--name', 'sf-capture-' + uuid.uuid4().hex[:10],
        '--mount', f'type=bind,src={ROOT},dst=/workspace', '--workdir=/workspace',
        SDK, *command], check=True)


def mounted(path):
    return '/workspace/' + str(path.resolve().relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup', action='store_true')
    parser.add_argument('--backend', choices=['docker', 'host'], default='docker',
                        help='Use a separate native host build when Docker is unavailable.')
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--state', type=Path)
    parser.add_argument('--battery', type=Path, help='Resume an actual emulator battery save.')
    parser.add_argument('--telemetry', default='0')
    parser.add_argument('--trace-only', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.name):
        parser.error('Use a short lowercase benchmark name.')
    if not re.fullmatch(r'[0-9a-fA-F]{1,8}', args.telemetry):
        parser.error('Telemetry must be a hexadecimal address, or zero.')
    # All container-visible inputs and all outputs remain inside this checkout.
    if args.state and args.battery:
        parser.error('Choose a savestate or battery save, never both.')
    for path in [args.rom, args.input] + ([args.state] if args.state else []) + ([args.battery] if args.battery else []):
        if not path.is_file():
            parser.error(f'Missing input: {path}')
        mounted(path)
    rom = args.rom.read_bytes()
    digest = hashlib.sha256(rom).hexdigest()
    code = rom[0xac:0xb0]
    if args.battery and args.battery.stat().st_size != (131072 if code == b'BPEE' else 32768):
        parser.error('Battery-save size does not match the cartridge family.')
    if code == b'BPEE' and digest != REFERENCE_HASH:
        manifests = list((ROOT / 'romhack/releases').glob('*/manifest.json'))
        manifests += list((ROOT / '.tools/romhack-drafts').glob('*/*/manifest.json'))
        if not any(json.loads(path.read_text()).get('target_sha256') == digest for path in manifests):
            parser.error('ROM matches neither the approved reference nor a verified SF patch target.')
    if code not in [b'BPEE', b'SFMM']:
        parser.error('Only the approved reference or an SF cartridge is supported.')
    if args.state:
        state_metadata = args.state.with_suffix('.json')
        if not state_metadata.is_file():
            parser.error('State must have its original capture metadata beside it.')
        identity = json.loads(state_metadata.read_text())
        if identity.get('rom_sha256') != digest:
            parser.error('State belongs to a different cartridge build.')
        if identity.get('mgba_revision') != REVISION or identity.get('controller_only') is not True:
            parser.error('State needs controller-only provenance from the pinned core revision.')
    # Raw mGBA snapshots omit Flash contents; restore the same capture's battery.
    companion_battery = args.state.with_suffix('.sav') if args.state else None
    battery = args.battery or (companion_battery if companion_battery and companion_battery.is_file() else None)
    if battery and battery.stat().st_size != (131072 if code == b'BPEE' else 32768):
        parser.error('Capture battery size does not match the cartridge family.')
    output = ROOT / '.tools/benchmarks' / args.name
    if output.exists():
        parser.error('Choose a new name; existing benchmark evidence is preserved.')
    if args.setup and not SOURCE.exists():
        subprocess.run(['git', 'clone', '--depth', '1', '--branch', '0.10.5',
            'https://github.com/mgba-emu/mgba.git', str(SOURCE)], check=True)
    if not SOURCE.exists():
        parser.error('Add --setup to obtain the pinned native core first.')
    revision = subprocess.check_output(
        ['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != REVISION:
        parser.error('Native mGBA source revision mismatch.')
    if args.backend == 'host':
        if args.setup:
            host_setup()
        host_info = verified_host_build()
        build = HOST_BUILD
        execute = lambda *command: subprocess.run(command, cwd=ROOT, check=True)
        visible = lambda path: str(path.resolve())
        runtime = f'native mGBA 0.10.5 core, {platform.system()} {platform.machine()} host'
    else:
        build, execute, visible = BUILD, docker, mounted
        runtime = 'native mGBA 0.10.5 core, Linux ARM64 official devkitARM container'
    if args.setup and args.backend == 'docker':
        docker('cmake', '-S', '.tools/mgba-native', '-B', '.tools/mgba-build',
            '-DLIBMGBA_ONLY=ON', '-DENABLE_SCRIPTING=OFF', '-DUSE_FFMPEG=OFF',
            '-DUSE_LIBZIP=OFF', '-DUSE_LZMA=OFF', '-DUSE_PNG=OFF',
            '-DBUILD_GL=OFF', '-DBUILD_GLES2=OFF', '-DBUILD_GLES3=OFF')
        docker('cmake', '--build', '.tools/mgba-build', '-j8')
    if not (build / 'libmgba.a').exists():
        parser.error('Add --setup to build the pinned native core first.')
    executable = '.tools/core_capture_' + uuid.uuid4().hex[:10]
    framework = ['-framework', 'CoreFoundation'] if args.backend == 'host' and platform.system() == 'Darwin' else []
    execute('cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-D_GNU_SOURCE',
        '-DBUILD_STATIC', '-I.tools/mgba-native/include', '-I' + str(build.relative_to(ROOT) / 'include'),
        'scripts/quality/core_capture.c', str(build.relative_to(ROOT) / 'libmgba.a'),
        '-lm', '-lpthread', *framework, '-o', executable)
    output.mkdir(parents=True)
    prefix = output / 'capture'
    execute(executable, visible(args.rom), visible(prefix), visible(args.input),
        visible(args.state) if args.state else '-', args.telemetry,
        'trace' if args.trace_only else 'video', visible(battery) if battery else '-')
    metadata = json.loads(prefix.with_suffix('.json').read_text())
    metadata.update({
        'rom_sha256': digest, 'game_code': code.decode(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'runtime': runtime,
        'mgba_revision': REVISION, 'input_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
        'controller_only': True, 'trace_only': args.trace_only,
        'battery_input_sha256': hashlib.sha256(battery.read_bytes()).hexdigest() if battery else None,
        'state_input_sha256': hashlib.sha256(args.state.read_bytes()).hexdigest() if args.state else None,
        'user_quality_approval': 'pending', 'host_browser_performance_proven': False
    })
    if args.backend == 'host':
        metadata['host_core_build'] = host_info
    metadata['source_worktree_dirty'] = bool(subprocess.check_output(
        ['git', 'status', '--porcelain'], text=True).strip())
    prefix.with_suffix('.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(f'Native capture saved: {output}')


if __name__ == '__main__':
    main()
