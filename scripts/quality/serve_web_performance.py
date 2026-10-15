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


def runtime_config(args):
    override = getattr(args, 'private_runtime', None)
    schema = getattr(args, 'report_schema', 1)
    if type(schema) is not int or schema not in (1, 2):
        raise ValueError('Diagnostic schema must be1 or2.')
    directory = ROOT / 'web/public/emulator'
    if override is not None:
        directory = Path(override).resolve()
        directory.relative_to((ROOT / '.tools').resolve())
        if not directory.is_dir():
            raise ValueError('Private runtime directory is missing.')
    elif schema != 1:
        raise ValueError('Schema2 requires an explicit private runtime.')
    return directory, schema


def controlled_stall_page(page):
    """One explicit200ms main-thread interruption; never a recurring timer."""
    def replace(old, new):
        nonlocal page
        if page.count(old) != 1:
            raise ValueError('Private stress-page anchor changed.')
        page = page.replace(old, new, 1)
    replace(b'<p role="status"', b'<button id="stall" disabled>Controlled200ms stall</button>\n<p role="status"')
    replace(b'let fieldObservation,', b'let controlledStalls=[],stallUsed=false,stallReady=false;\nlet fieldObservation,')
    replace(b"button('stop').disabled=!measuring||finished;", b"button('stop').disabled=!measuring||finished;\n  button('stall').disabled=!stallReady||finished||stallUsed;")
    replace(b"button('short').onclick=", b"""button('stall').onclick=()=>{
  if(!stallReady||finished||stallUsed)return;stallUsed=true;controls();
  const startedAtMs=performance.now(),until=startedAtMs+200;
  while(performance.now()<until){}
  const endedAtMs=performance.now();controlledStalls.push({requestedMs:200,startedAtMs,endedAtMs,actualMs:endedAtMs-startedAtMs});
  status.textContent='Controlled stall completed; waiting for the finite report.';
};
button('short').onclick=""")
    replace(b'  onStarted?.();', b'  stallReady=true;controls();\n  onStarted?.();')
    replace(b'measuring=false;controls();}}', b'measuring=false;stallReady=false;controls();}}')
    replace(b'const result={...measured,controllerReplay:', b'const result={...measured,controlledStalls:controlledStalls.filter(s=>s.startedAtMs>=measured.startedAtMs&&s.endedAtMs<=measured.endedAtMs),controllerReplay:')
    return page


def page_source(args):
    """Keep experimental host protocols isolated from the normal SDK harness."""
    private = getattr(args, 'private_page', None)
    if private is None:
        return Path(__file__).with_name('web_performance.html').read_bytes(), False
    if getattr(args, 'private_runtime', None) is None or getattr(args, 'report_schema', 1) != 2:
        raise ValueError('Private page requires an explicit private runtime and schema2.')
    path = Path(private)
    if path.is_symlink():
        raise ValueError('Private page must be a regular workspace file.')
    path = path.resolve()
    path.relative_to((ROOT / '.tools').resolve())
    if not path.is_file() or path.suffix != '.html':
        raise ValueError('Private page must be an HTML file under .tools.')
    page = path.read_bytes()
    if not 0 < len(page) <= 131072:
        raise ValueError('Private page exceeds its finite byte bound.')
    if getattr(args, 'controlled_stall', False):
        raise ValueError('Custom page owns its explicit stress actions.')
    return page, True


def snapshot(args):
    runtime_directory, report_schema = runtime_config(args)
    page, private_page = page_source(args)
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
    replay_source = Path(__file__).with_name('controller_replay.mjs').read_bytes()
    routes['/controller-replay.js'] = replay_source
    observation_source = Path(__file__).with_name('field_observation.mjs').read_bytes()
    routes['/field-observation.js'] = observation_source
    controller_route = None
    if args.input:
        route_bytes = args.input.read_bytes()
        lines = route_bytes.decode('ascii').strip().splitlines()
        if len(route_bytes) > 20000 or not 1 <= len(lines) <= 1000:
            raise ValueError('Controller route must fit its finite row/byte bound')
        frames = 0
        for line in lines:
            if not re.fullmatch(r'\d+,\d+', line):
                raise ValueError('Use headerless keyMask,frames controller rows')
            mask, count = map(int, line.split(','))
            if not 0 <= mask <= 1023 or count < 1:
                raise ValueError('Invalid controller route mask/duration')
            frames += count
        if frames * 280896 / 16777216 > 600:
            raise ValueError('Controller route exceeds ten minutes')
        routes['/route.csv'] = route_bytes
        controller_route = {'rows': len(lines), 'frames': frames,
            'duration_ms': frames * 280896 / 16777216 * 1000,
            'scope': 'Supplied controller sequence; browser timing and scenes require observation'}
    for path in sorted(runtime_directory.iterdir()):
        if path.is_symlink():
            raise ValueError('Runtime snapshots must contain regular local files.')
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
    controlled_stall = getattr(args, 'controlled_stall', False)
    if controlled_stall:
        page = controlled_stall_page(page)
    routes['/'] = page
    identity = {
        'rom_sha256': digest(rom), 'mgba_revision': REVISION,
        'files': {name[1:]: digest(data) for name, data in routes.items() if name != '/'},
        'runtime': runtime, 'page_sha256': digest(page),
        'source_state_metadata_sha256': digest(metadata_bytes),
        'inputs': {str(path.resolve()): digest(data) for path, data in (
            (args.rom, rom), (args.state, state), (battery_path, battery), (metadata_path, metadata_bytes))},
        'server_source_sha256': digest(Path(__file__).read_bytes()),
        'controller_route': controller_route,
        'performance_schema': report_schema,
        'private_runtime_override': getattr(args, 'private_runtime', None) is not None,
        'private_page_override': private_page,
        'controlled_stall_ms': 200 if controlled_stall else None,
        'public_progress_touched': False, 'server_limit_seconds': args.seconds,
        'provenance_scope': 'Controller-only capture metadata and matching native state header; companion Flash hashed separately',
    }
    routes['/identity.json'] = json_bytes(identity)
    if args.input:
        identity['inputs'][str(args.input.resolve())] = digest(route_bytes)
        routes['/identity.json'] = json_bytes(identity)
    output = ROOT / '.tools/benchmarks' / args.name
    output.mkdir()  # An existing name fails; evidence is never overwritten.
    (output / 'runtime').mkdir()
    for name in runtime:
        write_new(output / 'runtime' / name, routes['/emulator/' + name])
    write_new(output / 'web_performance.html', page)
    write_new(output / 'state.metadata.json', metadata_bytes)
    write_new(output / 'server-source.py', Path(__file__).read_bytes())
    write_new(output / 'controller-replay.js', replay_source)
    write_new(output / 'field-observation.js', observation_source)
    if args.input:
        write_new(output / 'route.csv', route_bytes)
    write_new(output / 'identity.json', routes['/identity.json'])
    return output, identity, routes


def serve(args, output, identity, routes):
    authority = '127.0.0.1:' + str(args.port)
    origin = 'http://' + authority
    deadline = time.monotonic() + args.seconds
    max_report_bytes = MAX_REPORT_BYTES * (8 if identity.get('performance_schema', 1) == 2 else 1)

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
            if self.headers.get('Host') != authority:
                return self.respond(404)
            if self.path == '/session.json':
                return self.respond(200, json_bytes({
                    'remaining_ms': max(0, (deadline - time.monotonic()) * 1000)}))
            if self.path not in routes:
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
                if not 0 < size <= max_report_bytes or self.headers.get('Transfer-Encoding'):
                    raise ValueError('Invalid report length')
                if self.headers.get_content_type() != 'application/json':
                    raise ValueError('Require JSON')
                body = self.rfile.read(size)
                if len(body) != size:
                    raise ValueError('Incomplete report')
                report = json.loads(body, parse_constant=reject_constant)
                if not isinstance(report, dict) or type(report.get('schema')) is not int or report.get('schema') != identity.get('performance_schema', 1) or (
                        report.get('context', {}).get('identity') != identity):
                    raise ValueError('Report identity differs from this frozen session')
                data = json_bytes(report)
                if len(data) > max_report_bytes:
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
    parser.add_argument('--input', type=Path, help='Optional finite controller CSV; replay uses approximate wall time')
    parser.add_argument('--name', required=True)
    parser.add_argument('--port', type=int, default=18766)
    parser.add_argument('--seconds', type=int, default=1800)
    parser.add_argument('--private-runtime', type=Path, help='Explicit experimental runtime under this workspace .tools only.')
    parser.add_argument('--private-page', type=Path, help='Explicit experimental HTML under .tools; requires private runtime/schema2.')
    parser.add_argument('--report-schema', type=int, choices=[1, 2], default=1)
    parser.add_argument('--controlled-stall', action='store_true', help='Expose one local200ms stress action during measurement.')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,43}', args.name):
        parser.error('Use a fresh lowercase benchmark name of at most 44 characters')
    if not 1 <= args.port <= 65535 or not 1 <= args.seconds <= 3600:
        parser.error('Port must be 1..65535; finite lifetime must be 1..3600 seconds')
    output, identity, routes = snapshot(args)
    serve(args, output, identity, routes)


if __name__ == '__main__':
    main()
