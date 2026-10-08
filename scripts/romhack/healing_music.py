"""Original one-shot recovery cue, sized for the inherited 160-frame service gate."""
import math


def healing_tracks(score):
    if (score['ticks_per_quarter'], score['tempo'], score['playback']) != (24, 192, 'one-shot'):
        raise ValueError('Healing cue must fit the reviewed native fanfare timing.')
    tracks = [[] for _ in range(3)]
    for channel, name in enumerate(['bell', 'bass', 'keys']):
        mix = score['channels'][name]
        if any(type(mix[k]) is not int or not 0 <= mix[k] <= 127 for k in ['volume', 'pan']):
            raise ValueError('Invalid recovery cue mix.')
        tracks[channel].extend([(0, -1, bytes([0xc0 + channel, channel])),
            (0, -1, bytes([0xb0 + channel, 7, mix['volume']])),
            (0, -1, bytes([0xb0 + channel, 10, mix['pan']]))])
    tempo = round(60_000_000 / score['tempo'])
    tracks[0].append((0, -1, b'\xff\x51\x03' + tempo.to_bytes(3, 'big')))

    def note(channel, tick, length, pitch, velocity):
        if not (0 <= tick < tick + length <= 192 and 0 <= pitch <= 127 and 1 <= velocity <= 127):
            raise ValueError('Recovery note exceeds its native one-shot window.')
        tracks[channel].extend([(tick, 2, bytes([0x90 + channel, pitch, velocity])),
                                (tick + length, 0, bytes([0x80 + channel, pitch, 0]))])

    for tick, length, pitch in score['melody']:
        note(0, tick, length, pitch, 96 if tick % 24 == 0 else 80)
    for tick, root, chord, quality in score['cadence']:
        if quality not in ['major7', 'minor7']:
            raise ValueError('Unknown recovery chord.')
        tracks[2].append((tick, 1, bytes([0xc2, 3 if quality == 'minor7' else 2])))
        length = 36 if tick == 144 else 42
        note(1, tick, length, root, 82)
        note(2, tick + 6, length - 6, chord, 64)
    return tracks, 192


def healing_samples():
    rate = 16744
    def pcm(length, function):
        return bytes(max(-120, min(120, round(function(n)
            * min(1, n / 18, (length - 1 - n) / 192)))) & 255 for n in range(length))
    def keys(intervals):
        return pcm(12288, lambda n: sum(math.sin(math.tau * n * 2 ** (i / 12) / 64
            + .7 * math.exp(-n / 1200) * math.sin(math.tau * n * 2 ** (i / 12) / 32))
            for i in intervals) * 25 * math.exp(-n / 5000))
    bell = pcm(12288, lambda n: (76 * math.sin(math.tau * n / 64)
        + 24 * math.sin(math.tau * n * 2.01 / 64) * math.exp(-n / 1500)
        + 10 * math.sin(math.tau * n * 3 / 64)) * math.exp(-n / 3900))
    bass = pcm(16384, lambda n: (84 * math.sin(math.tau * n / 64)
        + 16 * math.sin(math.tau * n / 32)) * math.exp(-n / 9000))
    return [(name, data, False, rate) for name, data in [
        ('bell', bell), ('bass', bass),
        ('major7', keys([0, 4, 7, 11])), ('minor7', keys([0, 3, 7, 10]))]]
