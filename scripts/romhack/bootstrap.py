"""Bootstrap a pinned, matching Emerald build without destructive cleanup."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / '.tools'
EMERALD = TOOLS / 'pokeemerald'
AGBCC = TOOLS / 'agbcc'
EMERALD_REVISION = '731ad5bfd6e6f265508d0efcca0ba42f9dcf5881'
AGBCC_REVISION = 'da598c1d918402c42c0c0d7128ba14567f3175e9'
REFERENCE_SHA1 = 'f3ae088181bf583e55daf962a92bb46f4f1d07b7'
SDK = 'sf-monsters-emerald-sdk'
PRESERVE = f'python3 {ROOT / "scripts/romhack/preserve_files.py"}'


def run(*command, cwd=None):
    subprocess.run(command, cwd=cwd or ROOT, check=True)


def checkout(path, remote, revision):
    if not path.exists():
        run('git', 'clone', remote, str(path))
        run('git', 'checkout', '--detach', revision, cwd=path)
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != revision:
        raise ValueError(f'{path.name}: expected pinned revision {revision}, got {actual}')


def preserve_cleanup(directory):
    # Only build automation is adapted. Game/compiler C and assembly stay intact.
    for path in directory.rglob('*'):
        if not path.is_file() or '.git' in path.parts:
            continue
        if path.name in ['configure', 'move-if-change', 'move-if-change.sh'] or \
           path.name.startswith('Makefile') or path.suffix == '.sh':
            original = path.read_text()
            adapted = re.sub(r'(?<![\w/.$-])(?:rm|rmdir)(?=\s)', PRESERVE, original)
            if path.name.startswith('Makefile') and '.SECONDARY:' not in adapted:
                adapted += '\n.SECONDARY:\n'
            if adapted != original:
                path.write_text(adapted)


def make(directory, *targets):
    run('make', '-j1', f'RM={PRESERVE}', *targets, cwd=directory)


def build_compilers():
    installed = EMERALD / 'tools/agbcc'
    marker = installed / 'sf-toolchain.json'
    if marker.exists():
        data = json.loads(marker.read_text())
        if data['agbcc_revision'] != AGBCC_REVISION:
            raise ValueError('Installed compiler revision mismatch.')
        return
    progress = TOOLS / 'agbcc-build-state.json'
    if progress.exists():
        data = json.loads(progress.read_text())
        if data['revision'] != AGBCC_REVISION:
            raise ValueError('Compiler work directory has a different source revision.')
        work = ROOT / data['work']
    else:
        work = TOOLS / ('agbcc-work-' + uuid.uuid4().hex[:10])
        work.mkdir()
        progress.write_text(json.dumps({'revision': AGBCC_REVISION,
                                       'work': str(work.relative_to(ROOT))}) + '\n')
    for name, target in [('old', 'old'), ('normal', 'normal')]:
        source = work / name
        executable = source / ('old_agbcc' if name == 'old' else 'agbcc')
        if not executable.exists():
            if not source.exists():
                shutil.copytree(AGBCC / 'gcc', source)
            preserve_cleanup(source)
            make(source, target)
    sdk = work / 'arm-sdk'
    if not sdk.exists():
        shutil.copytree(AGBCC, sdk, ignore=shutil.ignore_patterns('.git'))
    arm = sdk / 'gcc_arm'
    if not (arm / 'cc1').exists():
        preserve_cleanup(sdk)
        run('sh', './configure', '--target=arm-elf', '--host=i386-linux-gnu', cwd=arm)
        # configure writes the active Makefile; adapt it before executing make.
        preserve_cleanup(arm)
        make(arm, 'cc1')
    libraries = work / 'libraries'
    libraries.mkdir(exist_ok=True)
    for name in ['libgcc', 'libc', 'ginclude']:
        if not (libraries / name).exists():
            shutil.copytree(AGBCC / name, libraries / name)
    shutil.copy2(work / 'old/old_agbcc', libraries / 'old_agbcc')
    preserve_cleanup(libraries)
    make(libraries / 'libgcc')
    make(libraries / 'libc')
    for name in ['bin', 'include', 'lib']:
        (installed / name).mkdir(parents=True, exist_ok=True)
    for source, name in [(work / 'old/old_agbcc', 'old_agbcc'),
                         (work / 'normal/agbcc', 'agbcc'), (arm / 'cc1', 'agbcc_arm')]:
        shutil.copy2(source, installed / 'bin' / name)
    shutil.copytree(libraries / 'libc/include', installed / 'include', dirs_exist_ok=True)
    for source in (libraries / 'ginclude').iterdir():
        if source.is_file():
            shutil.copy2(source, installed / 'include' / source.name)
    for name in ['libgcc', 'libc']:
        shutil.copy2(libraries / name / f'{name}.a', installed / 'lib' / f'{name}.a')
    marker.write_text(json.dumps({'agbcc_revision': AGBCC_REVISION,
        'work': str(work.relative_to(ROOT)), 'cleanup': 'preserved, never deleted'}, indent=2) + '\n')


def inside():
    os.environ['PATH'] = '/opt/devkitpro/devkitARM/bin:' + os.environ['PATH']
    build_compilers()
    # No clean targets: failed/intermediate builds remain inspectable.
    run('make', '-j8', f'RM={PRESERVE}', cwd=EMERALD)
    cartridge = EMERALD / 'pokeemerald.gba'
    digest = hashlib.sha1(cartridge.read_bytes()).hexdigest()
    if digest != REFERENCE_SHA1:
        raise ValueError(f'Original Emerald reproduction mismatch: {digest}')
    output = TOOLS / 'romhack-baseline'
    output.mkdir(exist_ok=True)
    shutil.copy2(cartridge, output / 'emerald-matching.gba')
    (output / 'build.json').write_text(json.dumps({
        'emerald_revision': EMERALD_REVISION, 'agbcc_revision': AGBCC_REVISION,
        'rom_sha1': digest, 'rom_sha256': hashlib.sha256(cartridge.read_bytes()).hexdigest(),
        'bytes': cartridge.stat().st_size, 'matching': True
    }, indent=2) + '\n')
    print('Exact Emerald reproduction verified. Full ROM remains ignored/local.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.inside:
        inside()
        return
    TOOLS.mkdir(exist_ok=True)
    checkout(EMERALD, 'https://github.com/pret/pokeemerald.git', EMERALD_REVISION)
    checkout(AGBCC, 'https://github.com/pret/agbcc.git', AGBCC_REVISION)
    run('docker', 'build', '-f', 'romhack/Dockerfile', '-t', SDK, '.')
    run('docker', 'run', '--name', 'sf-emerald-bootstrap-' + uuid.uuid4().hex[:10],
        '--mount', f'type=bind,src={ROOT},dst=/workspace', '--workdir=/workspace',
        SDK, 'python3', '/workspace/scripts/romhack/bootstrap.py', '--inside')


if __name__ == '__main__':
    main()
