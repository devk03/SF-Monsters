"""Serialize original centered seed-room door art into three native size1 stages."""
import hashlib
import json
from pathlib import Path
import struct
from courier_art import opaque_bands
from door_art import native_frames

ASSET = 'assets/tiles/seed-room-door'
HOUSE = 'assets/tiles/sunset-rowhouse-butter'
MOVING = (4, 12, 12, 26)  # Exclusive right/bottom; jamb and threshold stay still.


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reference(root):
    from PIL import Image
    house = root / HOUSE
    image = Image.open(house / 'native-preview.png')
    card = image.resize((48, 64), Image.Resampling.NEAREST).crop((32, 32, 48, 64))
    if card.mode != 'P' or max(card.tobytes()) > 15:
        raise ValueError('Original butter door must retain native palette indices.')
    return card.tobytes(), (house / 'house.gbapal').read_bytes()


def moving_pixels():
    left, top, right, bottom = MOVING
    return {y * 16 + x for y in range(top, bottom) for x in range(left, right)}


def validate(frames, original):
    encoded = native_frames(frames)
    if len(encoded) != 768 or frames[0][:128] != original[:128]:
        raise ValueError('Door must preserve the original top-eight window rows.')
    moving = moving_pixels()
    for frame in frames:
        if any(frame[i] != frames[0][i] for i in range(512) if i not in moving):
            raise ValueError('Only the approved inset leaf may change during opening.')
        if any(frame[i] == 0 for i in moving):
            raise ValueError('An open portal must be opaque, never a transparent hole.')
    return encoded


def encode(root):
    from PIL import Image
    directory = root / ASSET
    source = Image.open(directory / 'source-v1.png').convert('RGBA')
    mask = source.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    bands = opaque_bands(mask, 0)
    if len(bands) != 3:
        raise ValueError('The generated door source needs exactly three separate cards.')
    original, palette = reference(root)
    if len(palette) != 32:
        raise ValueError('Butter-house palette must contain sixteen RGB555 colors.')
    colors = [tuple(((word >> (c * 5)) & 31) * 255 // 31 for c in range(3))
              for word in struct.unpack('<16H', palette)]
    candidates, boxes = [], []
    for left, right in bands:
        box = mask.crop((left, 0, right, mask.height)).getbbox()
        box = (left + box[0], box[1], left + box[2], box[3])
        boxes.append(list(box))
        card = source.crop(box).resize((16, 32), Image.Resampling.NEAREST)
        candidates.append(bytes(0 if rgba[3] < 128 else min(range(1, 16), key=lambda i:
            sum((rgba[c] - colors[i][c]) ** 2 for c in range(3)))
            for rgba in card.get_flattened_data()))
    closed = bytearray(candidates[0])
    closed[:128] = original[:128]
    frames = [bytes(closed)]
    moving = moving_pixels()
    for candidate in candidates[1:]:
        frame = bytearray(closed)
        for index in moving:
            frame[index] = candidate[index]
        frames.append(bytes(frame))
    encoded = validate(frames, original)
    flat = [c for color in colors for c in color] + [0] * 720
    sheet = Image.new('P', (48, 32), 0)
    sheet.putpalette(flat)
    for index, frame in enumerate(frames):
        card = Image.new('P', (16, 32), 0)
        card.putpalette(flat); card.putdata(frame)
        sheet.paste(card, (index * 16, 0))
    sheet.save(directory / 'frames.png', bits=4, transparency=0)
    (directory / 'frames.indices').write_bytes(b''.join(frames))
    (directory / 'frames.4bpp').write_bytes(encoded)
    files = ['frames.png', 'frames.indices', 'frames.4bpp']
    metadata = {'source': 'source-v1.png', 'source_sha256': digest((directory / 'source-v1.png').read_bytes()),
        'prompt_sha256': digest((directory / 'prompt.md').read_bytes()), 'boxes': boxes,
        'size': [16, 32], 'frames': 3, 'palette_bank': 11,
        'palette_sha256': digest(palette), 'reference_sha256': digest(original),
        'moving_rectangle': list(MOVING), 'fixed_top_rows': 8,
        'files': {name: digest((directory / name).read_bytes()) for name in files},
        'quality_approval': 'pending', 'generator': 'Built-in imagegen; original project artwork only'}
    (directory / 'conversion.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata


def load(root):
    directory = root / ASSET
    metadata = json.loads((directory / 'conversion.json').read_text())
    original, palette = reference(root)
    if metadata['source_sha256'] != digest((directory / metadata['source']).read_bytes()) or \
       metadata['prompt_sha256'] != digest((directory / 'prompt.md').read_bytes()) or \
       metadata['reference_sha256'] != digest(original) or metadata['palette_sha256'] != digest(palette):
        raise ValueError('Regenerate seed-door frames after source/reference/palette changes.')
    if metadata['moving_rectangle'] != list(MOVING) or metadata['size'] != [16, 32] or \
       metadata['frames'] != 3 or metadata['fixed_top_rows'] != 8 or metadata['palette_bank'] != 11:
        raise ValueError('Review the native seed-door frame contract before changing it.')
    for name, expected in metadata['files'].items():
        if digest((directory / name).read_bytes()) != expected:
            raise ValueError('Seed-door serialized asset differs: ' + name)
    raw = (directory / 'frames.indices').read_bytes()
    if len(raw) != 1536:
        raise ValueError('Require three complete native door cards.')
    frames = [raw[i * 512:(i + 1) * 512] for i in range(3)]
    if validate(frames, original) != (directory / 'frames.4bpp').read_bytes():
        raise ValueError('Native door pixels and serialized tile order disagree.')
    return {'frames': frames, 'palette': palette, 'metadata': metadata}


if __name__ == '__main__':
    encode(Path(__file__).resolve().parents[2])
