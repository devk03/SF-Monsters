"""Original clinic voices with attacks, evolving partials and native sustain loops."""
import math
import random

RATE = 16744
PERIOD = 64
TAU = math.tau


def signed_pcm(values):
    """Keep headroom in native signed eight-bit samples."""
    return bytes(max(-120, min(120, round(value))) & 255 for value in values)


def transient(length, sample):
    return signed_pcm(sample(n) * min(1, n / 18, (length - 1 - n) / 192)
                      for n in range(length))


def flute_voice(rng):
    length = 32768
    noise = [rng.uniform(-1, 1) for _ in range(length)]
    # Wrapped filtering makes the breath bed periodic at the sustain join.
    breath = [sum(noise[(n - j) % length] for j in range(4)) / 4
              for n in range(length)]
    wave = []
    for n in range(length):
        motion = TAU * n / 8192
        phase = TAU * n / PERIOD + 1.1 * math.sin(motion)
        openness = 1 + .035 * math.sin(motion + .6)
        tone = (78 * math.sin(phase) + 18 * math.sin(2 * phase + .12)
                + 8 * math.sin(3 * phase) + 3 * math.sin(5 * phase))
        wave.append(tone * openness + 3 * breath[n])
    # An airy onset precedes a long, gently moving sustain instead of an organ cycle.
    attack = [wave[(n - 1024) % length] * min(1, n / 384)
              + 4 * breath[(n - 1024) % length] * math.exp(-n / 220)
              for n in range(1024)]
    attack[0] = 0
    return signed_pcm(attack + wave), 1024


def bass_voice():
    def sustain(n):
        phase = TAU * n / PERIOD
        return 72 * math.sin(phase) + 20 * math.sin(2 * phase) + 9 * math.sin(3 * phase)
    attack = []
    for n in range(4096):
        phase = TAU * n / PERIOD
        pick = (14 * math.sin(5 * phase) + 8 * math.sin(7 * phase)) * math.exp(-n / 650)
        body = sustain(n) * (1 + .12 * math.exp(-n / 900))
        attack.append((body + pick) * min(1, n / 24))
    return signed_pcm(attack + [sustain(n) for n in range(256)]), 4096


def piano_voice(intervals):
    def sample(n):
        value = 0
        for interval in intervals:
            phase = TAU * n * 2 ** (interval / 12) / PERIOD
            # A short inharmonic tine strike fades into the rounded key body.
            tine = math.sin(phase + .95 * math.exp(-n / 1500) * math.sin(2.01 * phase))
            body = .18 * math.sin(2 * phase + .25) * math.exp(-n / 2200)
            value += (tine * math.exp(-n / 6200) + body) * 24
        return value
    return transient(16384, sample)


def guitar_voice(rng):
    pluck_position = .21
    noise = [rng.uniform(-1, 1) for _ in range(12288)]
    def sample(n):
        phase = TAU * n / PERIOD
        string = sum(math.sin(harmonic * TAU * pluck_position / 2)
            * math.sin(harmonic * phase) / harmonic
            * math.exp(-n / (4500 / harmonic ** .65)) for harmonic in range(1, 9))
        body = 6 * math.sin(.067 * n) * math.exp(-n / 1000)
        pick = 14 * noise[n] * math.exp(-n / 85)
        return 58 * string + body + pick
    return transient(12288, sample)


def clinic_samples():
    """Return name/PCM/loop/rate/loop-start; no imported recordings or samples."""
    rng = random.Random(0x5041524b564f4943)
    flute, flute_start = flute_voice(rng)
    bass, bass_start = bass_voice()
    guitar = guitar_voice(rng)
    kick = transient(2400, lambda n: math.sin(.024 * n + 4 * (1 - math.exp(-n / 250)))
                     * 76 * math.exp(-n / 450))
    brush = transient(3072, lambda n: (rng.random() * 2 - 1) * 52 * math.exp(-n / 850))
    shaker = transient(960, lambda n: (rng.random() * 2 - 1) * 48 * math.exp(-n / 190))
    return [(name, data, loop, RATE, start) for name, data, loop, start in [
        ('flute', flute, True, flute_start), ('bass', bass, True, bass_start),
        ('major7', piano_voice([0, 4, 7, 11]), False, 0),
        ('minor7', piano_voice([0, 3, 7, 10]), False, 0),
        ('guitar', guitar, False, 0), ('kick', kick, False, 0),
        ('brush', brush, False, 0), ('shaker', shaker, False, 0)]]
