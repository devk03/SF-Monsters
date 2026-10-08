"""Original modular Cognition office art, with stable relay and exit behaviors."""
import hashlib
import json
from pathlib import Path
import struct
from park_art import pack_park_cells
from street_art import rotate_pixels

ASSET = 'assets/tiles/cognition-office'
REVISION = 'v3'
SOURCE_FILE = 'source-bright-v2.png'
CARD_BANKS = (6,6,6,6,7,7,8,7,9,7,7,9,9,9,6,7)


def strong_bands(mask, axis):
    bands = []
    for index in range(mask.size[axis]):
        box = (index,0,index+1,mask.height) if axis == 0 else (0,index,mask.width,index+1)
        count = sum(bool(a) for a in mask.crop(box).get_flattened_data())
        if count >= mask.size[1-axis] // 2:
            if not bands or index > bands[-1][1]:
                bands.append([index,index+1])
            else:
                bands[-1][1] = index+1
    return bands


def encode_card_atlas(root, asset, source_file, revision, card_banks, stem):
    from PIL import Image
    path = root / asset
    source = Image.open(path/source_file).convert('RGBA')
    mask = source.getchannel('A').point(lambda a:255 if a >= 128 else 0)
    rows = strong_bands(mask,1)
    if len(rows) != 4:
        raise ValueError('Interior atlas needs four isolated card rows.')
    boxes = []
    for top,bottom in rows:
        columns = strong_bands(mask.crop((0,top,mask.width,bottom)),0)
        if len(columns) != 4:
            raise ValueError('Every interior atlas row needs four cards.')
        boxes.extend((left,top,right,bottom) for left,right in columns)
    cards = [source.crop(box).resize((32,32),Image.Resampling.NEAREST) for box in boxes]
    def colors_for(pixels,count):
        sample = Image.new('RGB',(len(pixels),1));sample.putdata(pixels)
        values = sample.quantize(colors=count,method=Image.Quantize.MEDIANCUT).getpalette()[:count*3]
        return [tuple(round(c*31/255)*255//31 for c in values[i:i+3]) for i in range(0,len(values),3)]
    floor = colors_for([rgb[:3] for rgb in cards[0].get_flattened_data() if rgb[3]>=128],3)
    palettes = {}
    for bank in range(6,10):
        pixels = [rgb[:3] for card,owner in zip(cards,card_banks) if owner==bank
                  for rgb in card.get_flattened_data() if rgb[3]>=128]
        # Common ground colors keep the floor coherent beneath furniture;
        # eleven remaining colors preserve that group's material/detail range.
        detail = [rgb for rgb in pixels if min(sum((rgb[c]-f[c])**2 for c in range(3)) for f in floor)>432]
        palettes[bank] = [(0,0,0)]+floor+[(24,24,24)]+colors_for(detail or pixels,11)
    native = Image.new('P',(128,128),0)
    flat = [c for bank in range(6,10) for color in palettes[bank] for c in color]
    native.putpalette(flat+[0]*(768-len(flat)))
    indices = []
    for i,card in enumerate(cards):
        colors = palettes[card_banks[i]]
        raw = bytes(min(range(1,16),key=lambda n:sum((rgb[c]-colors[n][c])**2 for c in range(3)))
                    for rgb in card.get_flattened_data())
        indices.append(raw)
        tile = Image.new('P',(32,32));tile.putpalette(native.getpalette())
        tile.putdata(bytes((card_banks[i]-6)*16+p for p in raw))
        native.paste(tile,(i%4*32,i//4*32))
    names = (f'native-atlas-{revision}.png',f'cards-{revision}.indices',f'{stem}-{revision}.gbapal')
    native.save(path/names[0],bits=8)
    (path/names[1]).write_bytes(b''.join(indices))
    palette = b''.join(struct.pack('<H',sum(round(rgb[c]*31/255) << (5*c) for c in range(3)))
                       for bank in range(6,10) for rgb in palettes[bank])
    (path/names[2]).write_bytes(palette)
    metadata = {'source_file':source_file,'source_sha256':hashlib.sha256((path/source_file).read_bytes()).hexdigest(),
                'source_size':list(source.size),'source_cells':boxes,'native_card_size':[32,32],
                'cards':16,'card_banks':card_banks,'palette_banks':[6,7,8,9],'quality_approval':'pending',
                'files':{name:hashlib.sha256((path/name).read_bytes()).hexdigest() for name in names}}
    (path/f'conversion-{revision}.json').write_text(json.dumps(metadata,indent=2)+'\n')


def encode_office(root):
    encode_card_atlas(root, ASSET, SOURCE_FILE, REVISION, CARD_BANKS, 'office')


def office_resources(root):
    from PIL import Image
    path = root / ASSET
    metadata = json.loads((path/f'conversion-{REVISION}.json').read_text())
    if tuple(metadata['card_banks']) != CARD_BANKS:
        raise ValueError('Office palette assignment changed after conversion.')
    for name,digest in dict(metadata['files'],**{metadata['source_file']:metadata['source_sha256']}).items():
        if hashlib.sha256((path/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Regenerate office atlas after changing '+name)
    raw = (path/f'cards-{REVISION}.indices').read_bytes()
    if len(raw) != 16*1024 or not all(0 < p < 16 for p in raw):
        raise ValueError('Office cards need sixteen opaque four-bit 32x32 records.')
    cards = [raw[i*1024:(i+1)*1024] for i in range(16)]
    def small(index):
        return bytes(cards[index][y*2*32+x*2] for y in range(16) for x in range(16))
    # Records 1/2 preserve native exit and scripted gate-open semantics.
    cells = [(small(i),CARD_BANKS[i]) for i in (0,14,0,1,13,2)]
    flags = [0x1000,0x1065,0x1000,0x1000,0x1000,0x1000]
    for card,bank in zip(cards,CARD_BANKS):
        for yy,xx in ((0,0),(0,16),(16,0),(16,16)):
            cells.append((bytes(p for y in range(yy,yy+16) for p in card[y*32+xx:y*32+xx+16]),bank))
            flags.append(0x1000)
    # Two-cell coffee counter keeps the existing one-row collision footprint.
    coffee = Image.frombytes('L',(32,32),cards[10]).resize((32,16),Image.Resampling.NEAREST).tobytes()
    for xx in (0,16):
        cells.append((bytes(p for y in range(16) for p in coffee[y*32+xx:y*32+xx+16]),7));flags.append(0x1000)
    for turns in (1,2,3):
        cells.append((rotate_pixels(small(2),turns),6));flags.append(0x1000)
    for card in (11,12,15,3):
        cells.append((small(card),CARD_BANKS[card]));flags.append(0x1000)
    board = Image.frombytes('L',(32,32),cards[8]).resize((32,16),Image.Resampling.NEAREST).tobytes()
    for xx in (0,16):
        cells.append((bytes(p for y in range(16) for p in board[y*32+xx:y*32+xx+16]),9));flags.append(0x1000)
    graphics,records,attributes = pack_park_cells(cells,flags)
    return graphics,records,attributes,bytes(192)+(path/f'office-{REVISION}.gbapal').read_bytes()+bytes(192)


def office_tile(plan,x,y):
    token = plan['rows'][y][x]
    if token == '.':return 514
    if token == 'r':return 515
    if token == 'E':return 513
    if token == 'Q':return 516
    if token == 'W':return 512+(78 if x%4==0 else 5)
    if token == '#':return 512+({0:74,len(plan['rows'][y])-1:72}.get(x,73 if y==len(plan['rows'])-1 else 5))
    for letters,card in (('abcd',4),('klmn',6),('ijst',9)):
        if token in letters:
            if letters=='abcd':
                if x<3:card=15 if y<5 else 8
                elif y>8:card=5
            if letters=='klmn' and x<3:card=5
            if letters=='ijst':
                if y<6 and x<6:card=7
                elif y>=18 and x>=13:card=15
            return 512+6+card*4+letters.index(token)
    if token in 'uv':return 512+(79 if y==19 else 70)+'uv'.index(token)
    if token == 'B':return 512+75
    if token == 'G':return 512+76
    if token == 'p':return 512+77
    if token == 'T':return 512+6+4*4
    raise ValueError('Office token has no original art: '+token)


def install_interior_tileset(engine, name, symbol, resources):
    from PIL import Image
    graphics,records,attributes,palettes = resources
    directory = engine/('data/tilesets/secondary/'+name);directory.mkdir(parents=True,exist_ok=True)
    count = len(graphics)//32
    image = Image.new('P',(128,((count+15)//16)*8),0)
    palette = []
    for value in struct.unpack('<16H',palettes[192:224]):
        palette.extend(((value&31)*255//31,((value>>5)&31)*255//31,((value>>10)&31)*255//31))
    image.putpalette(palette+[0]*720)
    for i in range(count):
        tile = graphics[i*32:(i+1)*32];pixels = bytes(p for v in tile for p in (v&15,v>>4))
        cell = Image.new('P',(8,8));cell.putdata(pixels);image.paste(cell,(i%16*8,i//16*8))
    image.save(directory/'tiles.png',bits=4)
    for file_name,data in (('metatiles.bin',records),('attributes.bin',attributes),('palettes.gbapal',palettes)):
        (directory/file_name).write_bytes(data)
    prefix = 'data/tilesets/secondary/'+name+'/'
    paths = ['src/data/tilesets/graphics.h','src/data/tilesets/metatiles.h','src/data/tilesets/headers.h']
    additions = [f'\nconst u16 gTilesetPalettes_{symbol}[][16] = INCBIN_U16("'+prefix+'palettes.gbapal");\n'+
                 f'const u32 gTilesetTiles_{symbol}[] = INCGFX_U32("'+prefix+'tiles.png", ".4bpp.lz");\n',
                 f'\nconst u16 gMetatiles_{symbol}[] = INCBIN_U16("'+prefix+'metatiles.bin");\n'+
                 f'const u16 gMetatileAttributes_{symbol}[] = INCBIN_U16("'+prefix+'attributes.bin");\n',
                 f'\nconst struct Tileset gTileset_{symbol} = {{.isCompressed=TRUE, .isSecondary=TRUE,\n'+
                 f' .tiles=gTilesetTiles_{symbol}, .palettes=gTilesetPalettes_{symbol},\n'+
                 f' .metatiles=gMetatiles_{symbol}, .metatileAttributes=gMetatileAttributes_{symbol}, .callback=NULL}};\n']
    for name,extra in zip(paths,additions):(engine/name).write_text((engine/name).read_text()+extra)
    return paths+[prefix+file for file in ('tiles.png','metatiles.bin','attributes.bin','palettes.gbapal')]


def apply_office(root,engine):
    paths = install_interior_tileset(engine, 'sf_cognition_office', 'SFCognitionOffice', office_resources(root))
    plan = json.loads((root/'romhack/content/cognition.json').read_text())
    map_path = 'data/layouts/RustboroCity_Gym/map.bin'
    current = bytearray((engine/map_path).read_bytes())
    for y,row in enumerate(plan['rows']):
        for x in range(len(row)):
            offset = (y*len(row)+x)*2
            value = struct.unpack_from('<H',current,offset)[0]
            struct.pack_into('<H',current,offset,(value&0xfc00)|office_tile(plan,x,y))
    (engine/map_path).write_bytes(current)
    return paths+[map_path]


if __name__ == '__main__':
    encode_office(Path(__file__).resolve().parents[2])
