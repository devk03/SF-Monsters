"""Apply reviewed indexed-pixel corrections before packing original cast art."""
import hashlib
import re


def digest(data):
    return hashlib.sha256(data).hexdigest()


def apply_cleanup(frames, document, source, palette):
    """Pin the source, palette, input/output poses and every changed pixel."""
    fields = {'format', 'intent', 'source_sha256', 'palette_sha256',
              'before_frame_sha256', 'after_frame_sha256', 'changes'}
    if not isinstance(document, dict) or set(document) != fields or \
       type(document['format']) is not int or document['format'] != 1 or \
       not isinstance(document['intent'], str) or not document['intent'].strip():
        raise ValueError('Native cleanup needs the reviewed format and intent.')
    if document['source_sha256'] != digest(source) or document['palette_sha256'] != digest(palette):
        raise ValueError('Native cleanup source or palette changed; review the indexed edits.')
    if len(palette) != 32 or len(frames) != 9 or any(
        type(frame) is not bytes or len(frame) != 512 or max(frame) > 15
        or any(frame[30*16:]) for frame in frames):
        raise ValueError('Cleanup requires nine four-bit16x32 poses above the feet baseline.')
    changes = document['changes']
    if not isinstance(changes, list) or not 1 <= len(changes) <= 9*16*30:
        raise ValueError('Declare a nonempty bounded native pixel correction.')
    seen, affected = set(), set()
    for edit in changes:
        if not isinstance(edit, dict) or set(edit) != {'frame', 'x', 'y', 'old', 'new'} or any(
            type(edit[key]) is not int or not 0 <= edit[key] < limit
            for key, limit in (('frame',9),('x',16),('y',30),('old',16),('new',16))):
            raise ValueError('Native pixel correction is outside its frame/palette bounds.')
        point = edit['frame'], edit['x'], edit['y']
        if point in seen or edit['old'] == edit['new']:
            raise ValueError('Duplicate or unchanged native pixel correction.')
        seen.add(point); affected.add(str(edit['frame']))
    for key in ('before_frame_sha256', 'after_frame_sha256'):
        hashes = document[key]
        if not isinstance(hashes, dict) or set(hashes) != affected or any(
            not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value)
            for value in hashes.values()):
            raise ValueError('Every corrected pose needs exact input/output hashes.')
    for key in affected:
        if digest(frames[int(key)]) != document['before_frame_sha256'][key]:
            raise ValueError('Native cleanup input pose changed.')
    output = [bytearray(frame) for frame in frames]
    for edit in changes:
        index = edit['y']*16 + edit['x']; frame = edit['frame']
        if output[frame][index] != edit['old']:
            raise ValueError('Native cleanup old pixel differs from its reviewed value.')
        output[frame][index] = edit['new']
    output = [bytes(frame) for frame in output]
    for key in affected:
        if digest(output[int(key)]) != document['after_frame_sha256'][key]:
            raise ValueError('Native cleanup output differs from its reviewed pose.')
    if any(len(set(output[row*3:row*3+3])) != 3 for row in range(3)):
        raise ValueError('Native cleanup collapsed idle/alternate footsteps.')
    return output
