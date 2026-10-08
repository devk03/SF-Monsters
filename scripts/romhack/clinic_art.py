"""Original clinic furniture on the existing save-compatible service layout."""
import hashlib
import json
from pathlib import Path
import struct
from collections import Counter, deque
from office_art import encode_card_atlas, install_interior_tileset
from park_art import pack_park_cells
from street_art import rotate_pixels

ASSET = 'assets/tiles/south-park-clinic'
REVISION = 'v4'
SOURCE_FILE = 'source-neutral-v4.png'
CARD_BANKS = (6,6,6,6,7,7,8,7,6,9,7,6,9,9,6,6)


def encode_clinic(root):
    encode_card_atlas(root, ASSET, SOURCE_FILE, REVISION, CARD_BANKS, 'clinic')


def paving(palette):
    """A faint eight-pixel material repeat, independent of collision cells."""
    colors = struct.unpack('<16H',palette[:32])
    light = lambda i:sum((colors[i]>>(5*c))&31 for c in range(3))
    grout,base,highlight = sorted((1,2,3),key=light)
    return bytes(grout if x%8==7 or y%8==7 else base
                 for y in range(16) for x in range(16))


def align_ground(pixels,width,height,floor):
    """Stitch edge-connected ground; enclosing prop outlines protect white props."""
    output=bytearray(pixels)
    pending=deque((x,y) for y in range(height) for x in range(width)
                  if (x in (0,width-1) or y in (0,height-1)) and pixels[y*width+x] in (1,2,3))
    visited=set()
    while pending:
        x,y=pending.popleft()
        if (x,y) in visited:continue
        visited.add((x,y));output[y*width+x]=floor[(y%16)*16+x%16]
        for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=xx<width and 0<=yy<height and pixels[yy*width+xx] in (1,2,3):
                pending.append((xx,yy))
    return bytes(output)


def joined_wall(floor,band,edges,north=None):
    """Join authored half-cell wall strips with a continuous miter at corners."""
    output=bytearray(floor)
    for y in range(16):
        for x in range(16):
            choices=[]
            for edge in edges:
                depth={'N':y,'S':15-y,'W':x,'E':15-x}[edge]
                limit=16 if edge=='N' and north is not None else 8
                if depth<limit:
                    along=x if edge in 'NS' else y
                    material=north if limit==16 else band
                    choices.append((depth*(16//limit),material[depth*16+along]))
            if choices:output[y*16+x]=min(choices,key=lambda v:v[0])[1]
    return bytes(output)


def clinic_resources(root):
    from PIL import Image
    path = root / ASSET
    metadata = json.loads((path/f'conversion-{REVISION}.json').read_text())
    if tuple(metadata['card_banks']) != CARD_BANKS:
        raise ValueError('Clinic palette ownership changed after conversion.')
    for name,digest in dict(metadata['files'],**{SOURCE_FILE:metadata['source_sha256']}).items():
        if hashlib.sha256((path/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Regenerate clinic art after changing '+name)
    raw = (path/f'cards-{REVISION}.indices').read_bytes()
    if len(raw) != 16*1024 or not all(0 < pixel < 16 for pixel in raw):
        raise ValueError('Clinic requires sixteen opaque four-bit 32x32 cards.')
    palette=(path/f'clinic-{REVISION}.gbapal').read_bytes()
    floor=paving(palette)
    cards = [align_ground(raw[i*1024:(i+1)*1024],32,32,floor)
             if i in (4,5,6,7,9,10,12,13,14) else raw[i*1024:(i+1)*1024] for i in range(16)]
    def small(index):
        return bytes(cards[index][y*64+x*2] for y in range(16) for x in range(16))
    # Preserve old record indices/exit behavior while removing framed floor art.
    carpet=bytes([Counter(cards[1]).most_common(1)[0][0]])*256
    cells = ([(bytes([4])*256,6),(floor,6),(floor,6),(carpet,6)]+
             [(align_ground(small(i),16,16,floor) if i in (5,6,12) else small(i),CARD_BANKS[i])
              for i in (2,3,5,12,6,13,15,11)])
    flags = [0x1000]*len(cells)
    flags[1] = 0x1065 # south-arrow exit warp at the existing (6,12)
    for card,bank in zip(cards,CARD_BANKS):
        for yy,xx in ((0,0),(0,16),(16,0),(16,16)):
            pixels=bytes(pixel for y in range(yy,yy+16) for pixel in card[y*32+xx:y*32+xx+16])
            foreground = card==cards[10] and yy==0
            if foreground:pixels=bytes(0 if pixel in (1,2,3) else pixel for pixel in pixels)
            cells.append((pixels,bank));flags.append(0 if foreground else 0x1000)
    # Keep the two-cell supplies counter within its existing collision footprint.
    counter = Image.frombytes('L',(32,32),cards[10]).resize((32,16),Image.Resampling.NEAREST).tobytes()
    counter=align_ground(counter,32,16,floor)
    for xx in (0,16):
        cells.append((bytes(pixel for y in range(16) for pixel in counter[y*32+xx:y*32+xx+16]),7))
        flags.append(0x1000)
    for turns in (1,2,3):
        cells.append((rotate_pixels(small(2),turns),6)); flags.append(0x1000)
    # Strip height is independent of the 16-pixel movement/collision grid.
    band=Image.frombytes('L',(32,32),cards[2]).crop((2,0,30,32)).resize((16,8),Image.Resampling.NEAREST).tobytes()
    north=small(2);window=small(3)
    for edges in ('N','S','W','E','NW','NE','SW','SE'):
        cells.append((joined_wall(floor,band,edges,north),6));flags.append(0x1000)
    cells.append((window,6));flags.append(0x1000)
    mat=Image.frombytes('L',(32,32),cards[14]).resize((32,16),Image.Resampling.NEAREST).tobytes()
    mat=align_ground(mat,32,16,floor)
    for xx in (0,16):
        cells.append((bytes(pixel for y in range(16) for pixel in mat[y*32+xx:y*32+xx+16]),6))
        flags.append(0x1000)
    notes=Image.frombytes('L',(32,32),cards[12]).resize((32,16),Image.Resampling.NEAREST).tobytes()
    for xx in (0,16):
        cells.append((align_ground(bytes(pixel for y in range(16) for pixel in notes[y*32+xx:y*32+xx+16]),16,16,floor),9))
        flags.append(0x1000)
    graphics,records,attributes = pack_park_cells(cells,flags)
    # A proper front layer hides only the counter's opaque prop pixels;
    # ground stays behind actors, avoiding the former all-floor occlusion bug.
    records=bytearray(records)
    ground=records[2*16+8:3*16]
    for index in (52,53):records[index*16:index*16+8]=ground
    return graphics,bytes(records),attributes,bytes(192)+palette+bytes(192)


def clinic_tile(plan,x,y):
    token = plan['rows'][y][x]
    last_x,last_y=len(plan['rows'][y])-1,len(plan['rows'])-1
    if y==0:return 512
    if (x,y) in ((0,1),(last_x,1),(0,last_y),(last_x,last_y)):
        return 512+{(0,1):85,(last_x,1):86,(0,last_y):87,(last_x,last_y):88}[(x,y)]
    if token == '#':return 512+(83 if x==0 else 84 if x==last_x else 82)
    if token == 'W':return 512+(89 if x in (3,7,10) else 81)
    single = {'.':514,'r':514,'E':513,'p':520,'=':602,'>':603,'U':604,'T':605}
    if token in single:return single[token]
    if token in 'abcC':return 512+12+5*4+'abcC'.index(token)
    if token in 'efgh':return 512+12+13*4+'efgh'.index(token)
    if token in 'HKuv':return 512+12+10*4+'HKuv'.index(token)
    for letters,card in (('klmn',4),('ijst',7)):
        if token in letters:
            # Upper waiting area has chairs; lower area offers supplies storage.
            if letters=='ijst' and y>=8:card=9
            return 512+12+card*4+letters.index(token)
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
