"""Original clinic jazz arrangement and synthesized native MPlay voices."""
from clinic_instruments import clinic_samples


def clinic_tracks(score):
    if score['ticks_per_quarter'] != 24 or not 60 <= score['tempo'] <= 140:
        raise ValueError('Clinic score needs the reviewed native clock and tempo.')
    revision = score.get('arrangement_revision', 1)
    if type(revision) is not int or revision not in (1,2):
        raise ValueError('Unsupported clinic arrangement revision.')
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
            rests=[]
            dynamics = score['phrasing'][section][bar] if revision == 2 else 82
            if type(dynamics) is not int or not 24 <= dynamics <= 110:
                raise ValueError('Clinic phrase dynamics must retain usable headroom.')
            for pitch, length in melody:
                if type(length) is not int or length < 6:
                    raise ValueError('Clinic note/rest must last at least six ticks.')
                if pitch is not None:
                    velocity=dynamics if offset % 24 == 0 else dynamics-10
                    note(0, start + offset, length - 3, pitch, velocity)
                else: rests.append((offset,length))
                offset += length
            if offset != 96:
                raise ValueError('Clinic melody must fill a four-beat bar.')
            root, chord, quality = harmony[bar]
            if quality not in ['major7', 'minor7']:
                raise ValueError('Clinic voicing needs a supported seventh chord.')
            minor = quality == 'minor7'
            tracks[3].append((start, 1, bytes([0xc3, 3 if minor else 2])))
            # Voiced chord samples keep the seven tracks monophonic on GBA.
            comp = score['accompaniment'][section] if revision == 2 else None
            keys = comp['keys'][bar%4] if comp else ([12,60] if bridge else [12,48,78])
            if any(type(t) is not int or not 0 <= t <= 81 for t in keys) or \
               any(b-a<15 for a,b in zip(keys,keys[1:])):
                raise ValueError('Clinic key strikes must fit the bar without overlapping.')
            for tick in keys:
                note(3, start + tick, 15, chord, 60 if tick == 12 else 50)
            approach=comp and bar in comp['bass_approach_bars']
            note(2,start,39,root,76)
            note(2,start+48,19 if approach else 39,root+7,62)
            if approach:
                next_section=score['sections'][(section_index+1)%len(score['sections'])]
                next_root=(harmony[bar+1] if bar<7 else score['harmony'][next_section][0])[0]
                note(2,start+72,18,next_root-1,54)
            if not bridge or bar >= 4:
                if revision == 1:
                    for tick, interval in [(24, 7), (66, 10 if minor else 11)]:
                        note(1, start + tick, 18, chord + interval, 54)
                else:
                    # Answer only in written rests, leaving the melody's space intact.
                    for tick,length in rests:
                        for i,relative in enumerate(range(1,length-9,12)):
                            note(1,start+tick+relative,9,chord+(7 if i%2==0 else 10 if minor else 11),46-i*4)
            # Let the bridge breathe; percussion returns halfway through.
            if not bridge or bar >= 4:
                for tick in [0, 48]: note(4, start + tick, 8, 60, 56)
                for tick in [24, 72]: note(5, start + tick, 10, 60, 50)
                division=comp['shaker_division'] if comp else 12
                if division not in (12,24):raise ValueError('Unsupported clinic shaker division.')
                for tick in range(0,96,division):
                    # One-tick offbeat displacement adds a restrained lilt.
                    offbeat=tick%24!=0
                    shifted=tick+(1 if revision==2 and offbeat else 0)
                    note(6,start+shifted,5,60,42 if offbeat else 30)
    return tracks, 32 * 96
