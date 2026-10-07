"""Original harmonic/formant creature calls encoded for Emerald's sound engine."""
from pathlib import Path
import json
import math
import random
import re
import struct
import wave

ROOT = Path(__file__).resolve().parents[2]


def synthesize(cry, rate):
    if not re.fullmatch(r'[a-z]+', cry['name']) or not 0.1 <= cry['duration'] <= 2:
        raise ValueError('Cry identity or duration is invalid.')
    if not 8000 <= rate <= 22050: raise ValueError('Cry rate exceeds the native sample budget.')
    length = round(rate * cry['duration'])
    signal = [0.0] * length
    rng = random.Random(0x5346 + sum(cry['name'].encode()))
    for start, duration, high, low in cry['pulses']:
        if start < 0 or duration <= 0 or start + duration > cry['duration']:
            raise ValueError('A cry pulse leaves its sample window.')
        if not 60 <= low <= high <= rate / 4: raise ValueError('Invalid voiced pulse range.')
        phase, breath = 0.0, 0.0
        count = round(duration * rate)
        for index in range(count):
            fraction = index / max(1, count - 1)
            pitch = high + (low - high) * fraction + 7 * math.sin(fraction * math.tau * 3)
            phase += pitch / rate
            envelope = math.sin(math.pi * fraction) ** 1.8
            voiced, weight = 0.0, 0.0
            for harmonic in range(1, min(24, int(rate / (2 * pitch)))):
                frequency = harmonic * pitch
                resonance = sum(math.exp(-((frequency - formant) / 260) ** 2) for formant in cry['formants'])
                amplitude = (0.15 + resonance) / harmonic
                voiced += math.sin(math.tau * phase * harmonic) * amplitude
                weight += amplitude
            breath = breath * 0.65 + (rng.random() * 2 - 1) * 0.35
            sample = envelope * (voiced / max(weight, 0.01) + cry['noise'] * breath)
            position = round(start * rate) + index
            if position < length: signal[position] += sample
    peak = max(abs(value) for value in signal)
    if peak < 0.01: raise ValueError('Cry has no audible signal.')
    samples = [max(-120, min(120, round(value * 112 / peak))) for value in signal]
    samples[0] = samples[-1] = 0
    return bytes(sample & 255 for sample in samples)


def write_assets(cry, rate, directory):
    samples = synthesize(cry, rate)
    directory.mkdir(parents=True, exist_ok=True)
    # WaveData: uncompressed signed PCM, no loop, fixed native frequency units.
    (directory / (cry['name'] + '.bin')).write_bytes(struct.pack('<HHIII', 0, 0, rate * 1024, 0, len(samples)) + samples)
    signed = [value if value < 128 else value - 256 for value in samples]
    with wave.open(str(directory / (cry['name'] + '.wav')), 'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate)
        wav.writeframes(struct.pack('<%dh' % len(signed), *(sample * 256 for sample in signed)))


def apply_creature_audio(content, root, engine, original):
    if 'creature_audio' not in content: return []
    path = (root / content['creature_audio']).resolve()
    path.relative_to(root / 'assets/audio')
    recipes = json.loads(path.read_text())
    tables_path = 'sound/cry_tables.inc'; tables = original(tables_path)
    changed = [tables_path]
    for cry in recipes['cries']:
        if not re.fullmatch('[A-Z][A-Za-z]+', cry['engine_symbol']) or not re.fullmatch('[a-z]+', cry['engine_file']):
            raise ValueError('Unsafe native cry symbol/path.')
        samples = synthesize(cry, recipes['sample_rate'])
        destination = 'sound/direct_sound_samples/cries/' + cry['engine_file'] + '.bin'
        (engine / destination).write_bytes(struct.pack('<HHIII', 0, 0, recipes['sample_rate'] * 1024, 0, len(samples)) + samples)
        changed.append(destination)
        for kind, voice in [('cry', 'voice_directsound'), ('cry_reverse', 'voice_directsound_reverse')]:
            pattern = rf'(?m)^\t{kind} Cry_{cry["engine_symbol"]}$'
            tables, count = re.subn(pattern, f'\t{voice} 60, 0, Cry_{cry["engine_symbol"]}, 255, 0, 255, 0', tables)
            if count != 1: raise ValueError('Pinned cry table anchor changed.')
    (engine / tables_path).write_text(tables)
    return changed


if __name__ == '__main__':
    recipe = json.loads((ROOT / 'assets/audio/creature-cries.json').read_text())
    for cry in recipe['cries']:
        write_assets(cry, recipe['sample_rate'], ROOT / 'assets/audio/cries-v1')
    print('Wrote three original creature-call candidates.')
