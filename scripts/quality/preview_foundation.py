"""Serve an isolated local review page for the same experimental GBA cartridge."""
from pathlib import Path
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import shutil

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, default=8765)
args = parser.parse_args()
output = ROOT / '.tools/foundation-preview'
output.mkdir(parents=True, exist_ok=True)
rom = ROOT / 'engine/sf-foundation.gba'
if not rom.is_file():
    parser.error('Build the foundation ROM first.')
shutil.copy2(rom, output / rom.name)
shutil.copy2(ROOT / 'tests/quality/foundation_preview.html', output / 'index.html')
shutil.copytree(ROOT / 'web/public/emulator', output / 'emulator', dirs_exist_ok=True)
handler = partial(SimpleHTTPRequestHandler, directory=str(output))
print(f'Local candidate review: http://127.0.0.1:{args.port}', flush=True)
ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
