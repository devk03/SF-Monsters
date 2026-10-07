"""Original Fogbank Frenzy arrangement and synthesized battle instruments."""
import math
import random


def battle_tracks(score):
    quarter = score['ticks_per_quarter']
    if quarter != 24 or not 40 <= score['tempo'] <= 200:
        raise ValueError('Unsupported native battle clock/tempo.')
    names = ['lead', 'answer', 'bass', 'pad', 'kick', 'snare', 'hat']
    tracks = [[] for _ in names]
    for channel, (name, program) in enumerate(zip(names, [0, 4, 1, 2, 5, 6, 7])):
        mix = score['channels'][name]
        if any(not 0 <= mix[key] <= 127 for key in ['volume', 'pan']):
            raise ValueError('Invalid battle MIDI mix.')
        tracks[channel].extend([(0, -1, bytes([0xc0 + channel, program])),
            (0, -1, bytes([0xb0 + channel, 7, mix['volume']])),
            (0, -1, bytes([0xb0 + channel, 10, mix['pan']]))])
    tempo = round(60_000_000 / score['tempo'])
    tracks[0].append((0, -1, b'\xff\x51\x03' + tempo.to_bytes(3, 'big')))

    def note(channel, tick, duration, pitch, velocity):
        if not 0 <= pitch <= 127 or not 1 <= velocity <= 127 or duration <= 0:
            raise ValueError('Invalid battle note.')
        tracks[channel].extend([(tick, 2, bytes([0x90 + channel, pitch, velocity])),
            (tick + duration, 0, bytes([0x80 + channel, pitch, 0]))])

    for section_index, section in enumerate(score['sections']):
        phrase = score['phrases'][section]
        if len(phrase) != 4 or len(score['harmony']) != 4:
            raise ValueError('A battle phrase needs four bars.')
        for bar, melody in enumerate(phrase):
            start = (section_index * 4 + bar) * 4 * quarter
            offset = 0
            for index, (pitch, length) in enumerate(melody):
                if not isinstance(length, int) or length < 4:
                    raise ValueError('Battle note duration must be at least four ticks.')
                note(0, start + offset, length - 3, pitch,
                     108 if offset % 24 == 0 else 88)
                offset += length
            if offset != 96:
                raise ValueError('Battle melody must fill each four-beat bar.')
            root, chord, quality = score['harmony'][bar]
            if quality not in ['major', 'minor']:
                raise ValueError('Unsupported chord quality.')
            tracks[3].append((start, 1, bytes([0xc3, 3 if quality == 'minor' else 2])))
            note(3, start, 84, chord, 64)
            # The bridge rests its answering line; the last phrase brings it back.
            if section != 'C':
                for tick, interval in [(12, 7), (60, 12), (84, 7)]:
                    note(1, start + tick, 9, chord + interval, 68)
            for tick, length, interval in [(0, 18, 0), (24, 9, 0),
                                            (36, 9, 7), (48, 18, 0), (72, 18, 7)]:
                note(2, start + tick, length, root + interval, 98 if tick == 0 else 82)
            for tick in [0, 36, 48]: note(4, start + tick, 10, 60, 106)
            for tick in [24, 72]: note(5, start + tick, 10, 60, 96)
            if bar == 3:
                for tick in [84, 90]: note(5, start + tick, 4, 60, 72)
            for eighth in range(8):
                note(6, start + eighth * 12, 6, 60, 80 if eighth % 2 else 56)
    return tracks, len(score['sections']) * 96 * 4


def battle_samples():
    rate = 16744
    noise = random.Random(0x464f4742414e4b)

    def pcm(length, function):
        return bytes(max(-120, min(120, round(function(n)))) & 255 for n in range(length))

    def saw(n): return 2 * (n % 64) / 64 - 1

    lead = pcm(4096, lambda n: (math.sin(math.tau * n / 64) + .32 * saw(n)
        + .16 * math.sin(math.tau * n / 32)) * 78 * math.exp(-n / 2600))
    answer = pcm(2048, lambda n: (math.sin(math.tau * n / 64)
        + .24 * math.sin(math.tau * n / 16)) * 80 * math.exp(-n / 650))
    bass = pcm(256, lambda n: (math.sin(math.tau * n / 64) + .28 * saw(n)) * 88)
    major = pcm(256, lambda n: (math.sin(math.tau * n / 64)
        + math.sin(math.tau * n * 5 / 256) + math.sin(math.tau * n * 6 / 256)) * 32)
    minor = pcm(1024, lambda n: (math.sin(math.tau * n / 64)
        + math.sin(math.tau * n * 19 / 1024) + math.sin(math.tau * n * 3 / 128)) * 32)
    kick = pcm(2400, lambda n: math.sin(.032 * n + 9 * (1 - math.exp(-n / 240)))
        * 112 * math.exp(-n / 480))
    snare = pcm(2200, lambda n: ((noise.random() * 2 - 1) * 82
        + 24 * math.sin(.075 * n)) * math.exp(-n / 450))
    hat = pcm(960, lambda n: (noise.random() * 2 - 1) * 68 * math.exp(-n / 160))
    return [(name, data, loop, rate) for name, data, loop in
        [('lead', lead, False), ('bass', bass, True), ('major', major, True),
         ('minor', minor, True), ('answer', answer, False), ('kick', kick, False),
         ('snare', snare, False), ('hat', hat, False)]]
