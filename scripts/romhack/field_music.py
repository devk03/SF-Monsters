"""Compose original sequenced field music and instruments for native MPlay."""
from pathlib import Path
import json
import math
import random
import re
import shutil
import struct

ROOT = Path(__file__).resolve().parents[2]


def variable_length(value):
    if not 0 <= value <= 0x0fffffff: raise ValueError('MIDI delta is out of range.')
    result = [value & 127]
    while value >> 7:
        value >>= 7; result.insert(0, (value & 127) | 128)
    return bytes(result)


def midi_track(events, end):
    ordered = [(0, -2, b'\xff\x06\x01[')] + events + [(end, 3, b'\xff\x06\x01]'), (end, 4, b'\xff\x2f\x00')]
    output, previous = bytearray(), 0
    for tick, priority, data in sorted(ordered, key=lambda row: (row[0], row[1])):
        if not 0 <= tick <= end: raise ValueError('A note leaves the song loop.')
        output.extend(variable_length(tick - previous)); output.extend(data); previous = tick
    return b'MTrk' + struct.pack('>I', len(output)) + output


def score_tracks(score):
    quarter = score['ticks_per_quarter']
    if quarter != 24 or not 40 <= score['tempo'] <= 200: raise ValueError('Unsupported native clock/tempo.')
    names = ['bell', 'counter', 'bass', 'pad', 'kick', 'snare', 'hat']
    programs = [0, 4, 1, 2, 5, 6, 7]
    tracks = [[] for _ in names]
    for channel, name in enumerate(names):
        settings = score['channels'][name]
        if any(not 0 <= settings[key] <= 127 for key in ['volume', 'pan']): raise ValueError('Invalid MIDI mix value.')
        tracks[channel].extend([(0, -1, bytes([0xc0 + channel, programs[channel]])),
            (0, -1, bytes([0xb0 + channel, 7, settings['volume']])),
            (0, -1, bytes([0xb0 + channel, 10, settings['pan']]))])
    tempo = round(60_000_000 / score['tempo'])
    tracks[0].append((0, -1, b'\xff\x51\x03' + tempo.to_bytes(3, 'big')))

    def note(channel, tick, duration, pitch, velocity):
        if not 0 <= pitch <= 127 or not 1 <= velocity <= 127 or duration <= 0: raise ValueError('Invalid note.')
        tracks[channel].extend([(tick, 2, bytes([0x90 + channel, pitch, velocity])),
                                (tick + duration, 0, bytes([0x80 + channel, pitch, 0]))])

    for section_index, section in enumerate(score['sections']):
        melody = score['melodies'][section]
        if len(melody) != 16 or len(score['harmony']) != 4: raise ValueError('Section must contain four bars.')
        base = section_index * 16 * quarter
        for beat, pitch in enumerate(melody):
            note(0, base + beat * quarter, quarter - 3, pitch, 100 if beat % 4 == 0 else 84)
        for bar, (root, chord, quality) in enumerate(score['harmony']):
            tick = base + bar * 4 * quarter
            tracks[3].append((tick, 1, bytes([0xc3, 3 if quality == 'minor' else 2])))
            note(3, tick, 4 * quarter - 8, chord, 76)
            note(2, tick, 2 * quarter - 4, root, 94)
            note(2, tick + 2 * quarter, 2 * quarter - 4, root + 7, 78)
            for half in range(2):
                pitch = score['counterline'][bar * 2 + half]
                if section == 'B': pitch += 12
                note(1, tick + (half * 2 + 1) * quarter, quarter - 6, pitch, 72)
            note(4, tick, quarter // 2, 60, 100)
            note(4, tick + 2 * quarter, quarter // 2, 60, 84)
            for beat in [1, 3]: note(5, tick + beat * quarter, quarter // 2, 60, 86)
            for eighth in range(8):
                note(6, tick + eighth * quarter // 2, quarter // 3, 60, 66 if eighth % 2 else 86)
    return tracks, len(score['sections']) * 16 * quarter


def instrument_samples():
    rate = 16744  # A 64-sample loop has a C4 fundamental at 261.625 Hz.
    rng = random.Random(0x53464d55534943)
    def pcm(length, function):
        return bytes(max(-120, min(120, round(function(index)))) & 255 for index in range(length))
    bell = pcm(4096, lambda n: (math.sin(math.tau * n / 64) + .26 * math.sin(math.tau * n / 32)) * 82 * math.exp(-n / 1100))
    pluck = pcm(3072, lambda n: (math.sin(math.tau * n / 64) + .18 * math.sin(math.tau * n / 21.333333)) * 85 * math.exp(-n / 750))
    bass = pcm(256, lambda n: (math.sin(math.tau * n / 64) + .18 * math.sin(math.tau * n / 32)) * 88)
    major = pcm(256, lambda n: (math.sin(math.tau * n / 64) + math.sin(math.tau * n * 5 / 256) + math.sin(math.tau * n * 6 / 256)) * 34)
    minor = pcm(1024, lambda n: (math.sin(math.tau * n / 64) + math.sin(math.tau * n * 19 / 1024) + math.sin(math.tau * n * 3 / 128)) * 34)
    kick = pcm(3072, lambda n: math.sin(.035 * n + 7 * (1 - math.exp(-n / 300))) * 112 * math.exp(-n / 520))
    snare = pcm(3072, lambda n: (rng.random() * 2 - 1) * 98 * math.exp(-n / 600))
    hat = pcm(1280, lambda n: (rng.random() * 2 - 1) * 62 * math.exp(-n / 210))
    return [(name, data, loop, rate) for name, data, loop in
            [('bell', bell, False), ('bass', bass, True), ('major', major, True),
             ('minor', minor, True), ('pluck', pluck, False), ('kick', kick, False),
             ('snare', snare, False), ('hat', hat, False)]]


def write_song(score, output):
    tracks, end = score_tracks(score)
    output.mkdir(parents=True, exist_ok=True)
    midi = b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks), 24)
    midi += b''.join(midi_track(track, end) for track in tracks)
    (output / 'ocean_commute.mid').write_bytes(midi)
    waves, voices = [], ['voice_group littleroot']
    for name, data, loop, rate in instrument_samples():
        symbol = 'SF_Ocean_' + name
        (output / (name + '.bin')).write_bytes(struct.pack('<HHIII', 0, 0x4000 if loop else 0, rate * 1024, 0, len(data)) + data)
        waves.extend(['\t.align 2', symbol + '::', f'\t.incbin "sound/sf_ocean/{name}.bin"'])
        voices.append(f'\tvoice_directsound 60, 0, {symbol}, 255, 0, 230, {90 if loop else 40}')
    (output / 'waves.inc').write_text('\n'.join(waves) + '\n')
    (output / 'voices.inc').write_text('\n'.join(voices) + '\n')
    (output / 'score-info.json').write_text(json.dumps({'title': score['title'], 'tempo': score['tempo'],
        'bars': end // 96, 'tracks': len(tracks), 'loop_ticks': end,
        'nominal_loop_seconds': end / 24 * 60 / score['tempo'], 'quality_approval': 'pending'}, indent=2) + '\n')


def apply_field_music(content, root, engine, original):
    if 'field_music' not in content: return []
    plan = (root / content['field_music']).resolve(); plan.relative_to(root / 'assets/audio')
    score = json.loads(plan.read_text())
    if score['native_song'] != 'mus_littleroot' or score['native_voicegroup'] != 'littleroot':
        raise ValueError('Review additional native song bindings before using them.')
    source = root / 'assets/audio/ocean-commute-native-v1'
    write_song(score, source)
    destination = engine / 'sound/sf_ocean'; destination.mkdir(exist_ok=True)
    for file in source.iterdir():
        if file.suffix == '.bin': shutil.copy2(file, destination / file.name)
    midi_path, voice_path, data_path = 'sound/songs/midi/mus_littleroot.mid', 'sound/voicegroups/littleroot.inc', 'sound/direct_sound_data.inc'
    shutil.copy2(source / 'ocean_commute.mid', engine / midi_path)
    (engine / voice_path).write_text((source / 'voices.inc').read_text())
    (engine / 'sound/sf_ocean/waves.inc').write_text((source / 'waves.inc').read_text())
    (engine / data_path).write_text(original(data_path) + '\n.include "sound/sf_ocean/waves.inc"\n')
    return [midi_path, voice_path, data_path]


if __name__ == '__main__':
    write_song(json.loads((ROOT / 'assets/audio/ocean-commute.json').read_text()), ROOT / 'assets/audio/ocean-commute-native-v1')
    print('Wrote original native Ocean Commute score and eight synthesized instruments.')
