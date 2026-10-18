"""Finite loopback-only browser preview of a verified private module cartridge."""
import argparse
import hashlib
import json
import mimetypes
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=ROOT / '.tools/pokeemerald-world-host/sf-module-playtest.gba')
    parser.add_argument('--port', type=int, default=18771)
    parser.add_argument('--seconds', type=int, default=1800)
    parser.add_argument('--battery',type=Path,help='Optional private ordinary Save for cold Continue testing')
    args = parser.parse_args()
    if not 60 <= args.seconds <= 3600 or not 1024 <= args.port <= 65535:
        parser.error('Use a 60–3600 second finite session and a port in 1024..65535')
    args.rom.resolve().relative_to((ROOT / '.tools').resolve())
    rom = args.rom.read_bytes(); digest = hashlib.sha256(rom).hexdigest()
    if len(rom) != 16777216 or rom[0xac:0xb0] != b'BPEE':
        parser.error('Use a built Emerald-family private cartridge')
    builds = [json.loads(p.read_text()) for p in (ROOT / '.tools/romhack-drafts').glob('*/*/manifest.json')]
    receipt = next((m for m in builds if m.get('target_sha256') == digest), None)
    if receipt is None or receipt.get('profile') not in ('module-playtest', 'world-blockout'):
        parser.error('Cartridge has no verified private world/module build receipt')
    routes = {'/': (Path(__file__).with_name('module_preview.html').read_bytes(), 'text/html'),
              '/rom.gba': (rom, 'application/octet-stream')}
    if args.battery:
        args.battery.resolve().relative_to((ROOT/'.tools').resolve())
        battery=args.battery.read_bytes()
        if len(battery)!=131072:parser.error('Private world Continue needs 128 KiB Flash')
        routes['/battery.sav']=(battery,'application/octet-stream')
    runtime = ROOT / 'web/public/emulator'
    for path in runtime.iterdir():
        if path.is_file() and not path.is_symlink() and path.suffix in ('.js', '.wasm', '.json', '.txt'):
            routes['/emulator/'+path.name] = (path.read_bytes(), mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
    deadline = time.monotonic() + args.seconds
    done = {'value': False}

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(3)

        def log_message(self, *_): pass

        def reply(self, data, kind, status=200):
            self.send_response(status); self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(data))); self.send_header('Cache-Control', 'no-store')
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
            self.end_headers(); self.wfile.write(data)

        def do_GET(self):
            path = self.path.split('?', 1)[0]
            if path == '/identity.json':
                info = {'rom_sha256': digest, 'profile': receipt['profile'], 'fixture': receipt.get('fixture'),
                        'remaining_seconds': max(0, int(deadline-time.monotonic())),
                        'has_battery':bool(args.battery),
                        'public_progress_touched': False, 'persist': False}
                self.reply(json.dumps(info).encode(), 'application/json')
            elif path in routes:
                self.reply(*routes[path])
            else:
                self.reply(b'Not found', 'text/plain', 404)

        def do_POST(self):
            if self.path != '/finish':
                self.reply(b'Not found', 'text/plain', 404); return
            done['value'] = True; self.reply(b'Finished', 'text/plain')

    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        server.timeout = 1
        print(f'Private module preview: http://127.0.0.1:{args.port}/ (ends in {args.seconds}s)', flush=True)
        while not done['value'] and time.monotonic() < deadline:
            server.handle_request()


if __name__ == '__main__':
    main()
