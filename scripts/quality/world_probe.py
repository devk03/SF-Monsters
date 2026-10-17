"""Controller-only native world evidence; RAM access is strictly read-only."""
import hashlib
import json
import select
import struct
import subprocess
import time
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


class Controller:
    def __init__(self, rom, elf, output, *, state=None, battery=None):
        self.rom, self.output = Path(rom), Path(output)
        self.output.mkdir(parents=True, exist_ok=False)
        self.deadline = time.monotonic() + 1800
        self.inputs, self.observations = [], []
        self.symbols = {}
        for line in subprocess.check_output(
                ['arm-none-eabi-nm', '--defined-only', str(elf)], text=True).splitlines():
            fields = line.split()
            if len(fields) == 3:
                self.symbols[fields[2]] = int(fields[0], 16)
        if state:
            identity = json.loads(Path(state).with_suffix('.json').read_text())
            if identity['rom_sha256'] != self.digest() or not identity['controller_only']:
                raise ValueError('State has no matching controller-only provenance.')
        self.stderr = (self.output / 'driver.stderr').open('wb')
        self.process = subprocess.Popen([str(ROOT / '.tools/world-controller'), str(rom),
                                         str(battery or '-'), str(state or '-')],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.stderr)

    def digest(self):
        return hashlib.sha256(self.rom.read_bytes()).hexdigest()

    def command(self, command):
        if time.monotonic() > self.deadline:
            raise TimeoutError('World probe exceeded its finite 30-minute bound.')
        self.process.stdin.write((command + '\n').encode())
        self.process.stdin.flush()
        if not select.select([self.process.stdout], [], [], 15)[0]:
            raise TimeoutError('Native controller response timeout.')
        response = self.process.stdout.readline().decode().strip()
        if not response:
            raise ValueError('Native controller exited early.')
        return response

    def read(self, address, length):
        return bytes.fromhex(self.command(f'read {address:x} {length}'))

    def position(self):
        pointer, = struct.unpack('<I', self.read(self.symbols['gSaveBlock1Ptr'], 4))
        if not 0x02000000 <= pointer < 0x02040000:
            return None
        x, y, group, number = struct.unpack('<hhBB', self.read(pointer, 6))
        return {'x': x, 'y': y, 'group': group, 'number': number}

    def step(self, keys, frames):
        self.command(f'step {keys} {frames}')
        self.inputs.append([keys, frames])
        return self.position()

    def tap(self, keys, wait=24):
        self.step(keys, 8)
        return self.step(0, wait)

    def picture(self, name):
        raw = self.output / (name + '.rgba')
        self.command('frame ' + str(raw))
        image = Image.frombytes('RGBA', (240, 160), raw.read_bytes())
        image.convert('RGB').resize((960, 640), Image.Resampling.NEAREST).save(
            self.output / (name + '.png'))

    def checkpoint(self, name):
        self.step(0, 60)
        self.command('state ' + str(self.output / (name + '.state')))
        self.command('battery ' + str(self.output / (name + '.sav')))
        (self.output / (name + '.json')).write_text(json.dumps({
            'rom_sha256': self.digest(), 'controller_only': True,
            'game_code': 'BPEE',
            'mgba_revision': '26b7884bc25a5933960f3cdcd98bac1ae14d42e2',
            'position': self.position(), 'scope': 'native controller-derived state'}, indent=2))
        self.picture(name)

    def close(self):
        self.process.stdin.close()
        self.process.wait(timeout=5)
        self.stderr.close()
        (self.output / 'inputs.json').write_text(json.dumps(self.inputs))
        (self.output / 'observations.json').write_text(json.dumps(self.observations, indent=2))
