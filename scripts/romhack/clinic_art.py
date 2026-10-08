"""Original clinic furniture on the existing save-compatible service layout."""
import hashlib
import json
from pathlib import Path
import struct
from office_art import encode_card_atlas, install_interior_tileset
from park_art import pack_park_cells
from street_art import rotate_pixels

ASSET = 'assets/tiles/south-park-clinic'
REVISION = 'v1'
CARD_BANKS = (6,6,6,6,7,7,8,7,9,9,7,9,9,7,6,7)


def encode_clinic(root):
    encode_card_atlas(root, ASSET, 'source.png', REVISION, CARD_BANKS, 'clinic')


def clinic_resources(root):
    from PIL import Image
    path = root / ASSET
    metadata = json.loads((path/f'conversion-{REVISION}.json').read_text())
    if tuple(metadata['card_banks']) != CARD_BANKS:
        raise ValueError('Clinic palette ownership changed after conversion.')
    for name,digest in dict(metadata['files'],**{'source.png':metadata['source_sha256']}).items():
        if hashlib.sha256((path/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Regenerate clinic art after changing '+name)
    raw = (path/f'cards-{REVISION}.indices').read_bytes()
    if len(raw) != 16*1024 or not all(0 < pixel < 16 for pixel in raw):
        raise ValueError('Clinic requires sixteen opaque four-bit 32x32 cards.')
    cards = [raw[i*1024:(i+1)*1024] for i in range(16)]
    def small(index):
        return bytes(cards[index][y*64+x*2] for y in range(16) for x in range(16))
    cells = [(small(i),CARD_BANKS[i]) for i in (0,14,0,1,2,3,5,12,6,13,15,11)]
    flags = [0x1000]*len(cells)
    flags[1] = 0x1065 # south-arrow exit warp at the existing (6,12)
    for card,bank in zip(cards,CARD_BANKS):
        for yy,xx in ((0,0),(0,16),(16,0),(16,16)):
            cells.append((bytes(pixel for y in range(yy,yy+16)
                          for pixel in card[y*32+xx:y*32+xx+16]),bank))
            flags.append(0x1000)
    # Keep the two-cell supplies counter within its existing collision footprint.
    counter = Image.frombytes('L',(32,32),cards[10]).resize((32,16),Image.Resampling.NEAREST).tobytes()
    for xx in (0,16):
        cells.append((bytes(pixel for y in range(16) for pixel in counter[y*32+xx:y*32+xx+16]),7))
        flags.append(0x1000)
    for turns in (1,2,3):
        cells.append((rotate_pixels(small(2),turns),6)); flags.append(0x1000)
    graphics,records,attributes = pack_park_cells(cells,flags)
    return graphics,records,attributes,bytes(192)+(path/f'clinic-{REVISION}.gbapal').read_bytes()+bytes(192)


def clinic_tile(plan,x,y):
    token = plan['rows'][y][x]
    if token == '#':
        if x==0:return 592 # left-facing wall
        if x==len(plan['rows'][y])-1:return 590 # right-facing wall
        return 591 if y==len(plan['rows'])-1 else 516
    if token == 'W':return 517 if x in (3,7,10) else 516
    single = {'.':514,'r':515,'E':513,'C':518,'T':519,'p':520,'=':515,'>':515}
    if token in single:return single[token]
    for letters,card in (('klmn',4),('ijst',7)):
        if token in letters:
            # Upper waiting area has chairs; lower area offers supplies storage.
            if letters=='ijst' and y>=8:card=9
            return 512+12+card*4+letters.index(token)
    if token in 'uv':return 588+'uv'.index(token)
    raise ValueError('Clinic token has no original art: '+token)


def apply_clinic(root,engine):
    paths = install_interior_tileset(engine,'sf_south_park_clinic','SFSouthParkClinic',clinic_resources(root))
    plan = json.loads((root/'romhack/content/services.json').read_text())
    map_path = 'data/layouts/LittlerootTown_ProfessorBirchsLab/map.bin'
    current = bytearray((engine/map_path).read_bytes())
    for y,row in enumerate(plan['rows']):
        for x in range(len(row)):
            offset = (y*len(row)+x)*2
            value = struct.unpack_from('<H',current,offset)[0]
            struct.pack_into('<H',current,offset,(value&0xfc00)|clinic_tile(plan,x,y))
    (engine/map_path).write_bytes(current)
    return paths+[map_path]


if __name__=='__main__':
    encode_clinic(Path(__file__).resolve().parents[2])
