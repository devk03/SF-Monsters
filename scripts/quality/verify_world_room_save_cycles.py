"""Verify ordinary in-room Saves and cold Continue using existing native probes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--services', type=Path, required=True,
                        help='Matching verify_town_life --room-checkpoints output')
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,43}', args.name):
        parser.error('Use a fresh benchmark name of at most44characters')
    services = args.services.resolve()
    services.relative_to(ROOT / '.tools/benchmarks')
    proof_path = services / 'town-life-result.json'
    proof = json.loads(proof_path.read_text())
    manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
    rooms = [r['id'] for r in manifest['interiors']]
    if (proof['passed'] is not True or proof['rooms'] != len(rooms)
            or {r['room'] for r in proof['checked']} != set(rooms)
            or any(not r['rest_counter_released'] or not r['shop_cancel_released']
                   for r in proof['checked'])):
        raise ValueError('Require complete native services and paired-exit evidence')
    output = ROOT / '.tools/benchmarks' / args.name
    output.mkdir(exist_ok=False)
    results = []
    deadline = time.monotonic() + 1800
    helpers = ('save_world_checkpoint.py', 'verify_world_guide.py')
    try:
        for room in rooms:
            prefix = args.name + '-' + room.replace('_', '-')
            saved, continued = prefix + '-saved', prefix + '-continued'
            commands = [
                [helpers[0], '--state', str(services / (room + '.state')), '--name', saved],
                [helpers[1], '--saved', str(output.parent / saved), '--name', continued]]
            with (output / (room + '.log')).open('x') as log:
                for command in commands:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError('Room Save cycles exceeded their30minute limit')
                    subprocess.run([sys.executable, str(Path(__file__).with_name(command[0])),
                                    *command[1:]], check=True, stdout=log,
                                   stderr=subprocess.STDOUT, timeout=min(120, remaining))
            save = json.loads((output.parent / saved / 'save-result.json').read_text())
            resume = json.loads((output.parent / continued / 'guide-result.json').read_text())
            if (save['passed'] is not True or resume['passed'] is not True
                    or save['rom_sha256'] != proof['rom_sha256']
                    or resume['rom_sha256'] != proof['rom_sha256']):
                raise ValueError('A room Save cycle differs from its service cartridge')
            results.append(dict(room=room, ordinary_save=save, cold_continue=resume))
            print(room, flush=True)
    finally:
        (output / 'partial.json').write_text(json.dumps(results, indent=2) + '\n')
    result = dict(passed=True, rom_sha256=proof['rom_sha256'], rooms=len(results),
                  service_proof_sha256=hashlib.sha256(proof_path.read_bytes()).hexdigest(),
                  orchestrator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  helpers_sha256={h: hashlib.sha256(Path(__file__).with_name(h).read_bytes()).hexdigest()
                                  for h in helpers}, checks=results,
                  scope='Ordinary in-room Saves/coldContinue with protected-state and guide controls; '
                        'services/exits require the matching input proof. Human quality remains separate.')
    (output / 'room-save-cycles.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'checks'}))


if __name__ == '__main__':
    main()
