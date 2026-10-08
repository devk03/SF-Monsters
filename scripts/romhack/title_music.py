"""Original Foglight Overture sequencing for the existing SF instrument bank."""
import hashlib
import json
from pathlib import Path
import struct
from field_music import midi_track

ROOT = Path(__file__).resolve().parents[2]
CHANNELS = ('lead', 'answer', 'arpeggio', 'bass', 'pad', 'kick', 'snare', 'hat')
PROGRAMS = (0, 4, 4, 1, 2, 5, 6, 7)


def title_tracks(score):
    if score['ticks_per_quarter'] != 24 or not 40 <= score['tempo'] <= 200:
        raise ValueError('Use the native 24-tick quarter and supported tempo.')
    if score['native_voicegroup'] != 'vs_wild':
        raise ValueError('Title arrangement uses the reviewed original SF instrument bank.')
    tracks = [[] for _ in CHANNELS]
    for channel, (name, program) in enumerate(zip(CHANNELS, PROGRAMS)):
        mix = score['channels'][name]
        if any(type(mix[key]) is not int or not 0 <= mix[key] <= 127 for key in ('volume', 'pan')):
            raise ValueError('Native title volume/pan must fit MIDI controls.')
        tracks[channel].extend([(0, -1, bytes([0xc0 + channel, program])),
            (0, -1, bytes([0xb0 + channel, 7, mix['volume']])),
            (0, -1, bytes([0xb0 + channel, 10, mix['pan']]))])
    tempo = round(60_000_000 / score['tempo'])
    tracks[0].append((0, -1, b'\xff\x51\x03' + tempo.to_bytes(3, 'big')))

    def note(channel, tick, length, pitch, velocity):
        if type(pitch) is not int or not 0 <= pitch <= 127 or not 1 <= velocity <= 127 or length < 1:
            raise ValueError('Invalid title note.')
        tracks[channel].extend([(tick, 2, bytes([0x90 + channel, pitch, velocity])),
                               (tick + length, 0, bytes([0x80 + channel, pitch, 0]))])

    for section_index, section in enumerate(score['sections']):
        phrase = score['phrases'][section['phrase']]
        harmony = score['harmonies'][section['harmony']]
        if len(phrase) != 4 or len(harmony) != 4 or section['density'] not in ('full', 'airy'):
            raise ValueError('Each title section needs four bars and a declared texture.')
        airy = section['density'] == 'airy'
        for bar, melody in enumerate(phrase):
            start = (section_index * 4 + bar) * 96
            offset = 0
            for pitch, duration in melody:
                if type(duration) is not int or duration < 6:
                    raise ValueError('Title notes need at least six ticks.')
                note(0, start + offset, duration - 3, pitch, 94 if airy else 108 if offset % 24 == 0 else 86)
                offset += duration
            if offset != 96:
                raise ValueError('Every melody bar must fill exactly four beats.')
            root, chord, quality = harmony[bar]
            if quality not in ('major', 'minor'):
                raise ValueError('Declare the native triad quality.')
            tracks[4].append((start, 1, bytes([0xc4, 3 if quality == 'minor' else 2])))
            note(4, start, 84, chord, 68 if airy else 82)
            for tick, length, interval in [(0, 18, 0), (24, 9, 0), (36, 9, 7), (48, 18, 0), (72, 18, 7)]:
                note(3, start + tick, length, root + interval, 94 if tick == 0 else 76)
            intervals = (0, 3 if quality == 'minor' else 4, 7, 12)
            for beat, interval in enumerate(intervals):
                note(2, start + beat * 24, 15, chord + interval, 56 if airy else 68)
            if not airy:
                for tick, interval in [(12, 7), (60, 12)]:
                    note(1, start + tick, 15, chord + interval, 72)
            for tick in ([0, 48] if airy else [0, 36, 48]):
                note(5, start + tick, 10, 60, 94)
            for tick in ([72] if airy else [24, 72]):
                note(6, start + tick, 10, 60, 86)
            if bar == 3 and not airy:
                for tick in (84, 90): note(6, start + tick, 3, 60, 62)
            for tick in range(0, 96, 24 if airy else 12):
                note(7, start + tick, 5, 60, 58 if tick % 24 == 0 else 42)
    return tracks, len(score['sections']) * 384


def write_title_score(root=ROOT):
    score = json.loads((root / 'assets/audio/foglight-overture.json').read_text())
    tracks, end = title_tracks(score)
    directory = root / 'assets/audio/foglight-overture-native-v1'
    directory.mkdir(exist_ok=True)
    midi = b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks), 24)
    midi += b''.join(midi_track(track, end) for track in tracks)
    (directory / 'foglight_overture.mid').write_bytes(midi)
    (directory / 'score-info.json').write_text(json.dumps({'title': score['title'],
        'tracks': len(tracks), 'bars': end // 96, 'loop_ticks': end,
        'tempo': score['tempo'], 'nominal_loop_seconds': end / 24 * 60 / score['tempo'],
        'instruments': 'Original SF battle-bank PCM; no inherited title instrument samples.',
        'midi_sha256': hashlib.sha256(midi).hexdigest(), 'quality_approval': 'pending'}, indent=2) + '\n')
    return directory / 'foglight_overture.mid'


if __name__ == '__main__':
    print(write_title_score())
