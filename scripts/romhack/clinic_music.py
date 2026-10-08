"""Original clinic jazz arrangement and synthesized native MPlay voices."""
import math
import random


def clinic_tracks(score):
    if score['ticks_per_quarter'] != 24 or not 60 <= score['tempo'] <= 140:
        raise ValueError('Clinic score needs the reviewed native clock and tempo.')
    names = ['flute', 'guitar', 'bass', 'piano', 'kick', 'brush', 'shaker']
    tracks = [[] for _ in names]
    for channel, (name, program) in enumerate(zip(names, [0, 4, 1, 2, 5, 6, 7])):
        mix = score['channels'][name]
        if any(type(mix[k]) is not int or not 0 <= mix[k] <= 127 for k in ['volume', 'pan']):
            raise ValueError('Invalid clinic mix.')
        tracks[channel].extend([(0, -1, bytes([0xc0 + channel, program])),
            (0, -1, bytes([0xb0 + channel, 7, mix['volume']])),
            (0, -1, bytes([0xb0 + channel, 10, mix['pan']]))])
    tempo = round(60_000_000 / score['tempo'])
    tracks[0].append((0, -1, b'\xff\x51\x03' + tempo.to_bytes(3, 'big')))

    def note(channel, tick, duration, pitch, velocity):
        if not 0 <= pitch <= 127 or not 1 <= velocity <= 127 or duration <= 0:
            raise ValueError('Invalid clinic note.')
        tracks[channel].extend([(tick, 2, bytes([0x90 + channel, pitch, velocity])),
            (tick + duration, 0, bytes([0x80 + channel, pitch, 0]))])

    if len(score['sections']) != 4:
        raise ValueError('Clinic form needs four eight-bar sections.')
    for section_index, section in enumerate(score['sections']):
        phrase, harmony = score['phrases'][section], score['harmony'][section]
        if len(phrase) != 8 or len(harmony) != 8:
            raise ValueError('Clinic sections need eight complete bars.')
        bridge = section == 'B'
        for bar, melody in enumerate(phrase):
            start, offset = (section_index * 8 + bar) * 96, 0
            for pitch, length in melody:
                if type(length) is not int or length < 6:
                    raise ValueError('Clinic note/rest must last at least six ticks.')
                if pitch is not None:
                    note(0, start + offset, length - 3, pitch, 82 if offset % 24 == 0 else 72)
                offset += length
            if offset != 96:
                raise ValueError('Clinic melody must fill a four-beat bar.')
            root, chord, quality = harmony[bar]
            if quality not in ['major7', 'minor7']:
                raise ValueError('Clinic voicing needs a supported seventh chord.')
            minor = quality == 'minor7'
            tracks[3].append((start, 1, bytes([0xc3, 3 if minor else 2])))
            # Voiced chord samples keep the seven tracks monophonic on GBA.
            for tick in ([12, 60] if bridge else [12, 48, 78]):
                note(3, start + tick, 15, chord, 60 if tick == 12 else 50)
            for tick, interval in [(0, 0), (48, 7)]:
                note(2, start + tick, 39, root + interval, 76 if tick == 0 else 62)
            if not bridge or bar >= 4:
                for tick, interval in [(24, 7), (66, 10 if minor else 11)]:
                    note(1, start + tick, 18, chord + interval, 54)
            # Let the bridge breathe; percussion returns halfway through.
            if not bridge or bar >= 4:
                for tick in [0, 48]: note(4, start + tick, 8, 60, 56)
                for tick in [24, 72]: note(5, start + tick, 10, 60, 50)
                for eighth in range(8):
                    note(6, start + eighth * 12, 5, 60, 42 if eighth % 2 else 30)
    return tracks, 32 * 96


def clinic_samples():
    """No recordings: additive flute/piano/bass, plucked string and soft noise."""
    rate, rng = 16744, random.Random(0x5041524b42454e43)

    def pcm(length, function, transient=False):
        values = []
        for n in range(length):
            value = function(n)
            if transient:
                value *= min(1, n / 24, (length - 1 - n) / 192)
            values.append(max(-120, min(120, round(value))) & 255)
        return bytes(values)

    flute = pcm(256, lambda n: 88 * math.sin(math.tau * n / 64)
        + 14 * math.sin(math.tau * n * 2 / 64) + 6 * math.sin(math.tau * n * 3 / 64))
    bass = pcm(256, lambda n: 82 * math.sin(math.tau * n / 64)
        + 22 * math.sin(math.tau * n * 2 / 64))

    def piano(intervals):
        def sample(n):
            attack = min(1, n / 18)
            return sum((math.sin(math.tau * n * 2 ** (i / 12) / 64)
                + .18 * math.sin(math.tau * n * 2 ** (i / 12) / 32))
                * math.exp(-n / 4200) for i in intervals) * 25 * attack
        return pcm(16384, sample, True)

    # A damped string recurrence gives a softer timbre than a repeating sine.
    string = [rng.uniform(-1, 1) for _ in range(64)]
    pluck = []
    for n in range(12288):
        index = n % 64
        string[index] = .498 * (string[index] + string[(index + 1) % 64])
        fade = min(1, n / 12, (12287 - n) / 192)
        pluck.append(max(-120, min(120, round(string[index] * 100 * fade))) & 255)
    kick = pcm(2400, lambda n: math.sin(.024 * n + 4 * (1 - math.exp(-n / 250)))
        * 76 * math.exp(-n / 450), True)
    brush = pcm(3072, lambda n: (rng.random() * 2 - 1) * 52 * math.exp(-n / 850), True)
    shaker = pcm(960, lambda n: (rng.random() * 2 - 1) * 48 * math.exp(-n / 190), True)
    return [(name, data, loop, rate) for name, data, loop in [
        ('flute', flute, True), ('bass', bass, True),
        ('major7', piano([0, 4, 7, 11]), False),
        ('minor7', piano([0, 3, 7, 10]), False),
        ('guitar', bytes(pluck), False), ('kick', kick, False),
        ('brush', brush, False), ('shaker', shaker, False)]]
