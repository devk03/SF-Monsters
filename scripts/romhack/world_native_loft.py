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
# muted masonry, dark blue glazing and shadow. Zero stays transparent.
# These are original index mappings, not source color/pixel arrays.
MATERIALS = {
    8: (0,5,12,3,2,13,2,4,1,3,4,5,10,6,9,0),
    11: (0,5,12,12,3,13,2,4,1,3,4,5,12,3,13,0),
}
ROOF = (0,12,12,3,13,13,2,4,1,3,4,3,3,3,3,0)


def checked_blobs(root, hashes):
    engine = Path(root)/'.tools/pokeemerald'
    if not (engine/'.git').exists():
        raise ValueError('Native architecture requires the pinned local Emerald checkout; '
                         'run scripts/romhack/bootstrap.py before world checks')
    result = {}
    for name, expected in hashes.items():
        raw = subprocess.check_output(['git','show',EMERALD_REVISION+':'+name],cwd=engine)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Native architecture input changed: '+name)
        result[name] = raw
    return result


@lru_cache(maxsize=4)
def loft(root):
    from PIL import Image
    blobs = checked_blobs(root,HASHES)
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


CANOPY_PREFIX = 'data/tilesets/secondary/mauville/'
CANOPY_HASHES = {
    'data/layouts/MauvilleCity/map.bin': 'ec1e2a33d33024c4b029b11ca991bfeee25647e860209a0d9fb65ab3a7db8b68',
    CANOPY_PREFIX+'metatiles.bin': 'cb89f9ae47ac21b01246a7ffedf69d26028dcaa0a75e453ec3841d40022bda89',
    CANOPY_PREFIX+'tiles.png': 'fc7ff5d72e303208245539379ba04f7f7169b402d064d9bcf9281d750098be31',
    'data/tilesets/primary/general/tiles.png': HASHES['data/tilesets/primary/general/tiles.png'],
}


@lru_cache(maxsize=4)
def canopy(root):
    """Mauville canopy depth, original SF studio materials/sign/closed shutter.

    Exact General grass words are excluded; the actual SF composer supplies
    sidewalk. The recessed primary dark graphic is architecture, not grass.
    Neither the source gaming logo nor its door/warp behavior is inherited.
    """
    from PIL import Image
    blobs=checked_blobs(root,CANOPY_HASHES)
    secondary=Image.open(io.BytesIO(blobs[CANOPY_PREFIX+'tiles.png']))
    primary=Image.open(io.BytesIO(blobs['data/tilesets/primary/general/tiles.png']))
    layout=blobs['data/layouts/MauvilleCity/map.bin']
    records=blobs[CANOPY_PREFIX+'metatiles.bin']
    width,height=112,64;pixels=bytearray(width*height)
    roof=(0,12,3,4,4,13,2,1,1,5,3,12,3,2,3,0)
    wall=(0,12,3,4,4,13,2,1,1,5,3,7,8,9,7,0)
    for my in range(4):
        for mx in range(7):
            identifier=struct.unpack_from('<H',layout,((my+10)*40+mx+5)*2)[0]&1023
            if not 512<=identifier<512+len(records)//16:
                raise ValueError('Native canopy selected an unexpected primary record')
            for quadrant,word in enumerate(struct.unpack_from('<8H',records,(identifier-512)*16)):
                if word in (0x2002,0x2003):continue  # Exact native ground dependencies only.
                slot,bank=word&1023,word>>12
                image=secondary if slot>=512 else primary;local=slot%512
                for y in range(8):
                    for x in range(8):
                        index=image.getpixel((local%16*8+(7-x if word&0x400 else x),
                                              local//16*8+(7-y if word&0x800 else y)))
                        if not index:continue
                        dx=mx*16+quadrant%2*8+x;dy=my*16+(quadrant%4//2)*8+y
                        if word==0x30be and index==8:value=1
                        elif slot>=512 and bank==10:
                            value=(roof if dy<26 else wall)[index]
                        else:raise ValueError('Native canopy contains unreviewed ground/palette graphics')
                        if value:pixels[dy*width+dx]=value
    # Original restrained studio nameplate, not the source illuminated logo.
    for y in range(34,43):
        for x in range(44,68):pixels[y*width+x]=1 if y in (34,42) else 5
    # Tiny original WORKS lettering; no imported title or gaming motif.
    letters=((5,5,7,7,5),(7,5,5,5,7),(6,5,6,5,5),(5,6,4,6,5),(7,4,7,1,7))
    for n,rows in enumerate(letters):
        for y,row in enumerate(rows):
            for x in range(3):
                if row&(4>>x):pixels[(36+y)*width+46+n*4+x]=1
    for y in range(47,63):
        for x in range(49,63):
            pixels[y*width+x]=1 if x in (49,62) else 13 if y%4==2 else 2
    return width,height,bytes(pixels)
