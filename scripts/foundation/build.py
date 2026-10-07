"""Build the experimental hardware renderer with pinned, redistributable tools."""
from pathlib import Path
import argparse
import subprocess
import shutil
import uuid

ROOT = Path(__file__).resolve().parents[2]
BUTANO = ROOT / '.tools/butano'
REVISION = 'a9426cf21b8b6372e4f43678464345a1bf4594de'
SDK = ('devkitpro/devkitarm@sha256:'
       '116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5')


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup', action='store_true')
    args = parser.parse_args()
    if args.setup:
        if not BUTANO.exists():
            BUTANO.parent.mkdir(parents=True, exist_ok=True)
            run('git', 'clone', '--depth', '1', '--branch', '21.9.0',
                'https://github.com/GValiente/butano.git', str(BUTANO))
        run('docker', 'pull', SDK)
    if not BUTANO.exists():
        parser.error('Run this command with --setup to install the pinned tools.')
    revision = subprocess.check_output(
        ['git', '-C', str(BUTANO), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != REVISION:
        parser.error(f'Butano revision mismatch: expected {REVISION}, got {revision}')
    run(str(ROOT / '.tools/venv/bin/python'),
        str(ROOT / 'scripts/foundation/pack_graphics.py'))
    run(str(ROOT / '.tools/venv/bin/python'),
        str(ROOT / 'scripts/foundation/pack_maps.py'))
    run('python3', str(ROOT / 'scripts/foundation/compose_music.py'))
    generated = ROOT / 'engine/generated'
    generated.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'game/content.c', generated / 'content.c')
    # Keep the container and its logs. No deletion or clean targets are invoked.
    name = 'sf-foundation-' + uuid.uuid4().hex[:10]
    run('docker', 'run', '--name', name, '--mount',
        f'type=bind,src={ROOT},dst=/workspace', '--workdir=/workspace/engine',
        SDK, 'make', '-j8')
    print(f'Foundation ROM: {ROOT / "engine/sf-foundation.gba"}')
    print(f'Build container retained: {name}')


if __name__ == '__main__':
    main()
