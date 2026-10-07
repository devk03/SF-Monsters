"""Build the browser's core from the same pinned mGBA as native acceptance."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.tools/mgba-native'
BUILD = ROOT / '.tools/mgba-0105-emscripten'
OUTPUT = ROOT / '.tools/mgba-0105-web'
REVISION = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2'
IMAGE = 'emscripten/emsdk@sha256:92c97951b9a6835cb5da9592e9d95226f67e09ecd01a541d817a5b4801f235a4'


def docker(*arguments):
    subprocess.run(['docker', 'run', '--name', 'sf-web-core-' + uuid.uuid4().hex[:10],
                    '--mount', f'type=bind,src={ROOT},dst=/workspace',
                    '--workdir', '/workspace', IMAGE, *arguments], check=True)


def main():
    if not SOURCE.exists():
        subprocess.run(['git', 'clone', '--depth', '1', '--branch', '0.10.5',
                        'https://github.com/mgba-emu/mgba.git', str(SOURCE)], check=True)
    actual = subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != REVISION: raise ValueError('Native/browser mGBA revision must match.')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    docker('emcmake', 'cmake', '-S', '.tools/mgba-native', '-B', '.tools/mgba-0105-emscripten',
           '-DLIBMGBA_ONLY=ON', '-DCMAKE_BUILD_TYPE=Release',
           '-DCMAKE_C_FLAGS=-O3 -D_GNU_SOURCE -DDISABLE_THREADING',
           '-DENABLE_SCRIPTING=OFF', '-DUSE_FFMPEG=OFF', '-DUSE_LIBZIP=OFF',
           '-DUSE_LZMA=OFF', '-DUSE_PNG=OFF', '-DBUILD_GL=OFF', '-DBUILD_GLES2=OFF', '-DBUILD_GLES3=OFF')
    docker('cmake', '--build', '.tools/mgba-0105-emscripten', '-j8')
    flags = (BUILD / 'CMakeFiles/mgba.dir/flags.make').read_text()
    defines = re.search(r'^C_DEFINES = (.*)$', flags, re.M).group(1).split()
    docker('emcc', '-O3', '-std=gnu11', '-D_GNU_SOURCE', '-DDISABLE_THREADING',
           *defines, '-I.tools/mgba-native/include', '-I.tools/mgba-0105-emscripten/include',
           'emulator/mgba_0105_shim.c', '.tools/mgba-0105-emscripten/libmgba.a',
           '--no-entry', '-sMODULARIZE=1', '-sEXPORT_NAME=createMgbaModule',
           '-sENVIRONMENT=web,node', '-sALLOW_MEMORY_GROWTH=1', '-sINITIAL_MEMORY=67108864',
           '-sMAXIMUM_MEMORY=536870912', '-sSTACK_SIZE=1048576',
           '-sEXPORTED_FUNCTIONS=_malloc,_free',
           '-sEXPORTED_RUNTIME_METHODS=HEAPU8,HEAP16,HEAPU32,UTF8ToString,stringToUTF8,lengthBytesUTF8',
           '-o', '.tools/mgba-0105-web/mgba.js')
    artifacts = {name: hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest()
                 for name in ['mgba.js', 'mgba.wasm']}
    (OUTPUT / 'build.json').write_text(json.dumps({'mgba_version': '0.10.5',
        'mgba_revision': REVISION, 'emsdk_image': IMAGE,
        'shim_sha256': hashlib.sha256((ROOT / 'emulator/mgba_0105_shim.c').read_bytes()).hexdigest(),
        'artifacts': artifacts}, indent=2) + '\n')
    print('Built pinned browser core:', OUTPUT)


if __name__ == '__main__': main()
