"""Serve a frozen, private browser timing checkpoint for one finite local session."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import struct
import time
import uuid
import zlib

ROOT = Path(__file__).resolve().parents[2]
REVISION = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2'
MAX_REPORT_BYTES = 1048576


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_new(path, data):
    with path.open('xb') as target:
        target.write(data)


def json_bytes(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()


def reject_constant(value):
    raise ValueError('Nonfinite JSON value: ' + value)


def snapshot(args):
    rom = args.rom.read_bytes()
    state = args.state.read_bytes()
    battery_path, metadata_path = args.state.with_suffix('.sav'), args.state.with_suffix('.json')
    battery, metadata_bytes = battery_path.read_bytes(), metadata_path.read_bytes()
    metadata = json.loads(metadata_bytes)
    if len(rom) != 16777216 or rom[0xac:0xb0] != b'BPEE':
        raise ValueError('Require a 16 MiB BPEE cartridge')
    if metadata.get('controller_only') is not True or (
            metadata.get('rom_sha256'), metadata.get('mgba_revision'), metadata.get('game_code')) != (
                digest(rom), REVISION, 'BPEE'):
        raise ValueError('Require controller-only capture metadata for this exact cartridge/core')
    if len(battery) != 131072:
        raise ValueError('Require the capture companion 128 KiB Flash battery')
    if len(state) != 0x61000 or struct.unpack_from('<I', state)[0] != 0x01000007 or (
            struct.unpack_from('<I', state, 8)[0] != zlib.crc32(rom)) or (
            state[16:32] != rom[0xa0:0xb0]):
        raise ValueError('Native checkpoint header, cartridge identity or state layout differs')
    runtime, routes = {}, {'/rom.gba': rom, '/state.bin': state, '/battery.sav': battery}
    for path in sorted((ROOT / 'web/public/emulator').iterdir()):
        if path.is_file() and path.suffix in ('.js', '.wasm', '.txt', '.json'):
            routes['/emulator/' + path.name] = path.read_bytes()
            runtime[path.name] = digest(routes['/emulator/' + path.name])
    build = json.loads(routes['/emulator/core-build.json'])
    if build.get('mgba_revision') != REVISION or build.get('mgba_version') != '0.10.5':
        raise ValueError('Browser core revision differs from the checkpoint')
    for name in ('mgba.js', 'mgba.wasm'):
        if build.get('artifacts', {}).get(name) != runtime.get(name):
            raise ValueError('Browser core artifact differs from its pinned build: ' + name)
    for name in ('mgba.sdk.js', 'mgba.performance.js', 'mgba.audio-worklet.js'):
        if name not in runtime:
            raise ValueError('Missing browser diagnostic runtime: ' + name)
    page = Path(__file__).with_name('web_performance.html').read_bytes()
    routes['/'] = page
    identity = {
        'rom_sha256': digest(rom), 'mgba_revision': REVISION,
        'files': {name[1:]: digest(data) for name, data in routes.items() if name != '/'},
        'runtime': runtime, 'page_sha256': digest(page),
        'source_state_metadata_sha256': digest(metadata_bytes),
        'inputs': {str(path.resolve()): digest(data) for path, data in (
            (args.rom, rom), (args.state, state), (battery_path, battery), (metadata_path, metadata_bytes))},
        'server_source_sha256': digest(Path(__file__).read_bytes()),
        'public_progress_touched': False, 'server_limit_seconds': args.seconds,
        'provenance_scope': 'Controller-only capture metadata and matching native state header; companion Flash hashed separately',
    }
    routes['/identity.json'] = json_bytes(identity)
    output = ROOT / '.tools/benchmarks' / args.name
    output.mkdir()  # An existing name fails; evidence is never overwritten.
    (output / 'runtime').mkdir()
    for name in runtime:
        write_new(output / 'runtime' / name, routes['/emulator/' + name])
    write_new(output / 'web_performance.html', page)
    write_new(output / 'state.metadata.json', metadata_bytes)
    write_new(output / 'server-source.py', Path(__file__).read_bytes())
    write_new(output / 'identity.json', routes['/identity.json'])
    return output, identity, routes


def serve(args, output, identity, routes):
    authority = '127.0.0.1:' + str(args.port)
    origin = 'http://' + authority
    deadline = time.monotonic() + args.seconds

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def respond(self, code, data=b'{}', content_type='application/json'):
            self.send_response(code)
            for name, value in [('Content-Type', content_type), ('Content-Length', str(len(data))),
                                ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff')]:
                self.send_header(name, value)
            self.end_headers()
            try:
                self.wfile.write(data)
            except OSError:
                pass

        def do_GET(self):
            if self.headers.get('Host') != authority or self.path not in routes:
                return self.respond(404)
            content_type = 'text/html; charset=utf-8' if self.path == '/' else (
                'application/javascript' if self.path.endswith('.js') else
                'application/wasm' if self.path.endswith('.wasm') else
                mimetypes.guess_type(self.path)[0] or 'application/octet-stream')
            self.respond(200, routes[self.path], content_type)

        def do_POST(self):
            if self.headers.get('Host') != authority or self.headers.get('Origin') != origin or self.path != '/report':
                return self.respond(403)
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= MAX_REPORT_BYTES or self.headers.get('Transfer-Encoding'):
                    raise ValueError('Invalid report length')
                if self.headers.get_content_type() != 'application/json':
                    raise ValueError('Require JSON')
                body = self.rfile.read(size)
                if len(body) != size:
                    raise ValueError('Incomplete report')
                report = json.loads(body, parse_constant=reject_constant)
                if not isinstance(report, dict) or report.get('schema') != 1 or (
                        report.get('context', {}).get('identity') != identity):
                    raise ValueError('Report identity differs from this frozen session')
                data = json_bytes(report)
                if len(data) > MAX_REPORT_BYTES:
                    raise ValueError('Expanded report exceeds storage bound')
            except (ValueError, TypeError, AttributeError, RecursionError, OSError):
                return self.respond(400)
            name = 'report-' + uuid.uuid4().hex + '.json'
            write_new(output / name, data)
            self.respond(200, json_bytes({'name': name, 'sha256': digest(data)}))

    class FiniteServer(ThreadingHTTPServer):
        daemon_threads = True  # A slow client cannot keep this finite process alive.

        def get_request(self):
            connection, address = super().get_request()
            connection.settimeout(max(0.01, min(3, deadline - time.monotonic())))
            return connection, address

    server = FiniteServer(('127.0.0.1', args.port), Handler)
    print(f'Private timing session {origin}/; expires after {args.seconds}s; evidence {output}', flush=True)
    try:
        while time.monotonic() < deadline:
            server.timeout = min(1, deadline - time.monotonic())
            if server.timeout > 0:
                server.handle_request()
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--port', type=int, default=18766)
    parser.add_argument('--seconds', type=int, default=1800)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,43}', args.name):
        parser.error('Use a fresh lowercase benchmark name of at most 44 characters')
    if not 1 <= args.port <= 65535 or not 1 <= args.seconds <= 3600:
        parser.error('Port must be 1..65535; finite lifetime must be 1..3600 seconds')
    output, identity, routes = snapshot(args)
    serve(args, output, identity, routes)


if __name__ == '__main__':
    main()
