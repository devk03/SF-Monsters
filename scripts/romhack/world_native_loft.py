"""Build-only Emerald parapet silhouette adapted to the SF industrial kit.

No native pixels/palettes are stored here. Read pristine pinned Git objects,
never the mutable SF overlay, and discard only verified transparent graphics.
This imports architecture, not source map collision, doors, scripts or warps.
"""
import hashlib
import io
import struct
import subprocess
from functools import lru_cache
from pathlib import Path

from bootstrap import EMERALD_REVISION

PREFIX = 'data/tilesets/secondary/rustboro/'
HASHES = {
    'data/layouts/RustboroCity/map.bin': '5d1838e9e5c8f8a3bd519b0f7adaf1f01ef556deb9f8d5b46ec5996b26d51c4d',
    PREFIX+'metatiles.bin': '2e5daf7451ac4a3a003ce569e2132dccefe00b618f3e5763d45b2cef480b3274',
    PREFIX+'tiles.png': '87b3ce4e15674b3ef02b1793df0bc8633b7c49bf4443cb50708293615b048d24',
    'data/tilesets/primary/general/tiles.png': '365ba5482e7564763e614a0009900d1c317790dcd9f7a06c4ab74c363a3ba2f5',
}
# Material-role recipes into the existing SF bank12: neutral zinc roof,
# warm masonry, dark blue glazing and shadow. Zero stays transparent.
# These are original index mappings, not source color/pixel arrays.
MATERIALS = {
    8: (0,5,12,3,2,13,2,4,1,3,4,5,10,6,9,0),
    11: (0,5,5,10,6,13,2,4,1,3,4,5,10,6,9,0),
}
ROOF = (0,12,12,3,13,13,2,4,1,3,4,12,3,13,2,0)


@lru_cache(maxsize=4)
def loft(root):
    from PIL import Image
    engine = Path(root)/'.tools/pokeemerald'
    if not (engine/'.git').exists():
        raise ValueError('Native loft requires the pinned local Emerald checkout; '
                         'run scripts/romhack/bootstrap.py before world checks')
    blobs = {}
    for name, expected in HASHES.items():
        raw = subprocess.check_output(['git','show',EMERALD_REVISION+':'+name],cwd=engine)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Native loft input changed: '+name)
        blobs[name] = raw
    secondary = Image.open(io.BytesIO(blobs[PREFIX+'tiles.png']))
    primary = Image.open(io.BytesIO(blobs['data/tilesets/primary/general/tiles.png']))
    layout = blobs['data/layouts/RustboroCity/map.bin']
    records = blobs[PREFIX+'metatiles.bin']
    width,height = 144,96
    pixels = bytearray(width*height)
    for my in range(6):
        for mx in range(9):
            identifier = struct.unpack_from('<H',layout,((my+25)*40+mx+9)*2)[0]&1023
            if not 512 <= identifier < 512+len(records)//16:
                raise ValueError('Native loft selected an unexpected primary record')
            words = struct.unpack_from('<8H',records,(identifier-512)*16)
            for quadrant,word in enumerate(words):
                slot,bank = word&1023,word>>12
                image = secondary if slot>=512 else primary
                local = slot%512
                for y in range(8):
                    for x in range(8):
                        sx = 7-x if word&0x400 else x
                        sy = 7-y if word&0x800 else y
                        index = image.getpixel((local%16*8+sx,local//16*8+sy))
                        if not index:continue
                        if bank not in MATERIALS or slot<512:
                            raise ValueError('Native loft contains unreviewed ground/palette graphics')
                        dx = mx*16+quadrant%2*8+x
                        dy = my*16+(quadrant%4//2)*8+y
                        material = ROOF if dy<48 else MATERIALS[bank]
                        pixels[dy*width+dx] = material[index]
    # A closed timber door replaces the original apartment-door graphic.
    # No doorway/warp affordance is inherited; the whole scenic card is solid.
    for y in range(80,94):
        for x in range(68,76):
            pixels[y*width+x] = 9 if x in (68,75) or y in (80,93) else 6
    for x in range(69,75):pixels[87*width+x] = 5
    return width,height,bytes(pixels)
