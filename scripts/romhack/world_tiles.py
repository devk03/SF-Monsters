"""Compile the original SF street kit into one bounded native secondary tileset."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIRST_TILE = 512
FIRST_METATILE = 512
LAYER_COVERED = 0x1000
PROFILES = {'residential':'gTileset_Petalburg','industrial':'gTileset_SFIndustrial',
            'civic':'gTileset_SFCivic','nature':'gTileset_SFNature',
            'culture':'gTileset_SFCulture','stadium':'gTileset_SFStadium',
            'neighborhood':'gTileset_SFNeighborhood','mixed_use':'gTileset_SFMixedUse',
            'ridge_town':'gTileset_SFRidgeTown','park_edge':'gTileset_SFParkEdge'}


def checked(directory, name, receipt):
    data = (directory / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != receipt['files'][name]:
        raise ValueError('Original SF asset changed: ' + str(directory / name))
    return data


def crop(pixels, width, x, y, w, h):
    return bytes(pixels[(y+dy)*width+x+dx] for dy in range(h) for dx in range(w))


def compile_kit(root=ROOT, profile='residential'):
    """Two native layers: opaque ground and original transparent architecture."""
    styles = {'residential':{'coral','cafe','cream','lilac','pair'},
              'industrial':{'coral','cafe'},'civic':{'cream','cafe'},'nature':set(),
              'culture':{'coral','cafe','cream'},'stadium':{'coral','cream','cafe'},
              'neighborhood':{'coral','cafe'},
              'mixed_use':{'coral','cafe'},'ridge_town':{'coral','cafe'},
              'park_edge':{'coral','cafe'}}
    if profile not in styles:raise ValueError('Unknown SF art profile')
    tiles = [bytes(64)]
    tile_ids = {tiles[0]: (0,0)}
    records, attributes, catalog = [], [], {}
    palettes = {}

    def words(pixels, bank):
        result = []
        for y, x in ((0, 0), (0, 8), (8, 0), (8, 8)):
            tile = crop(pixels, 16, x, y, 8, 8)
            if tile not in tile_ids:
                index=len(tiles);tiles.append(tile)
                for flags in (0,0x400,0x800,0xc00):
                    flipped=bytes(tile[(7-dy if flags&0x800 else dy)*8+
                                       (7-dx if flags&0x400 else dx)]
                                  for dy in range(8) for dx in range(8))
                    tile_ids.setdefault(flipped,(index,flags))
            index,flags=tile_ids[tile]
            result.append(0x10000000 | index << 16 | flags | bank << 12)
        return result

    def card(name, pixels, width, height, bank, ground, ground_bank, blocked=True, behavior=0, floor=False, ground_width=16, deduplicate=False):
        if len(pixels) != width*height or width % 16 or height % 16 or max(pixels) > 15:
            raise ValueError('Native SF card dimensions/palette are invalid')
        ids = []
        for y in range(0, height, 16):
            row = []
            for x in range(0, width, 16):
                piece=crop(pixels,width,x,y,16,16)
                base=crop(ground,ground_width,x,y,16,16) if ground_width>16 else ground
                # Reference General's native grass metatile directly. Its
                # graphics/palette stay in the player-supplied Emerald base;
                # no extracted bitmap or palette is distributed in this repo.
                native_grass=[0x2002,0x2003,0x2003,0x2002]
                lower=native_grass if ground_bank==10 and profile!='residential' else words(base,ground_bank)
                record=words(piece,bank)+words(empty,bank) if floor else lower+words(piece,bank)
                attribute=LAYER_COVERED | behavior
                prior=next((i for i,(r,a) in enumerate(zip(records,attributes)) if r==record and a==attribute),None) if deduplicate else None
                if prior is None:
                    prior=len(records);records.append(record);attributes.append(attribute)
                row.append(FIRST_METATILE+prior)
            ids.append(row)
        catalog[name] = {'tiles': ids, 'blocked': blocked}
        if deduplicate:catalog[name]['explicit_cells']=True

    paving_dir = root / 'assets/tiles/south-park-paving-v1'
    paving_info = json.loads((paving_dir / 'conversion.json').read_text())
    paving = checked(paving_dir, 'paving.indices', paving_info)
    palettes[7] = checked(paving_dir, 'paving.gbapal', paving_info)
    if profile != 'residential':
        from world_surfaces import concrete, stone_palette
        paving = concrete()
        palettes[7] = stone_palette(palettes[7])
    empty = bytes(256)
    card('paving', empty, 16, 16, 7, paving, 7, False)
    # Use existing original asphalt, not a yellow or teal ground replacement.
    street_dir = root / 'assets/tiles/sunset-streets'
    street_info = json.loads((street_dir / 'conversion.json').read_text())
    source = checked(street_dir, 'tiles.indices', street_info)
    palettes[8] = checked(street_dir, 'street.gbapal', street_info)
    asphalt = bytes(source[(y % 4)*64+x] for y in range(16) for x in range(16))
    crossing = crop(source, 64, 16, 16, 16, 16)
    if profile!='residential':
        from world_surfaces import crossing_paint
        crossing=crossing_paint(asphalt)
        # Slot3 duplicated slot2 and is absent from asphalt. Preserve the
        # existing curb/seawall shades while adding neutral off-white paint.
        colors=list(struct.unpack('<16H',palettes[8]))
        colors[3]=28 | 28<<5 | 27<<10
        palettes[8]=struct.pack('<16H',*colors)
    card('asphalt', empty, 16, 16, 8, asphalt, 8, False)
    card('crossing', empty, 16, 16, 8, crossing, 8, False)
    house_dir = root / 'assets/tiles/connected-frontage-v3'
    info = json.loads((house_dir / 'conversion.json').read_text())
    houses = checked(house_dir, 'block.indices', info)
    palettes[6] = checked(house_dir, 'block.gbapal', info)
    from world_architecture import district_palette
    palettes[6] = district_palette(palettes[6],profile)
    # Shared attached fronts keep roofs, walls and stoops together at native scale.
    for name, x, width in [('coral', 0, 48), ('cafe', 48, 32),
                            ('cream', 80, 48), ('lilac', 128, 48)]:
        if name in styles[profile] and not (profile in ('industrial','civic') and name in ('coral','cafe','cream')):
            card(name, crop(houses, 176, x, 0, width, 64), width, 64, 6, paving, 7)
    pair_dir = root / 'assets/tiles/compact-townhouses-v1'
    pair_info = json.loads((pair_dir / 'conversion.json').read_text())
    if 'pair' in styles[profile]:
        card('pair', checked(pair_dir, 'pair.indices', pair_info), 64, 64, 6, paving, 7)
    furniture_dir = root / 'assets/tiles/city-furniture-v1'
    furniture_info = json.loads((furniture_dir / 'conversion.json').read_text())
    furniture = {}
    for item in furniture_info['cards']:
        name = item['name']; raw = (furniture_dir / (name + '.indices')).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['indices_sha256']:
            raise ValueError('Original furniture changed: ' + name)
        w, h = item['size']
        furniture[name]=(raw,w,h)
        card(name, raw, w, h, 6, paving, 7)
    if profile == 'residential':
        # Decode the existing original apartment's indexed native cards. This is
        # palette-preserving tile compilation, not a resampled room backdrop.
        room_dir = root / 'assets/tiles/courier-apartment'
        room_info = json.loads((room_dir / 'conversion.json').read_text())
        raw = checked(room_dir, 'tiles.4bpp', room_info)
        original_palettes = checked(room_dir, 'palettes.gbapal', room_info)
        palettes[9] = original_palettes[192:224]
        room = bytearray(176*160)
        for y in range(160):
            for x in range(176):
                index = ((y//16)*11+x//16)*4+(y%16//8)*2+x%16//8
                value = raw[index*32+(y%8)*4+x%8//2]
                room[y*176+x] = value >> ((x%2)*4) & 15
        floor = crop(room,176,80,32,16,16)
        card('wood_floor', empty,16,16,9,floor,9,False)
        for name,x,y,w,h,solid in [
                ('rug',72,80,48,32,False),
                ('wall_top',64,0,16,16,True),('wall_low',64,16,16,16,True),
                ('bed',32,48,32,32,True),('shelf',32,80,32,32,True),
                ('desk',128,64,32,16,True),('indoor_plant',128,96,16,32,True),
                ('wall_side',0,48,16,16,True),('threshold',80,144,16,16,False)]:
            card(name,crop(room,176,x,y,w,h),w,h,9,floor,9,solid,0x80 if name=='desk' else 0)
        colors = struct.unpack('<16H',palettes[9])
        darkest = min(range(1,16),key=lambda i:sum((colors[i]>>c*5)&31 for c in range(3)))
        card('void',bytes([darkest])*256,16,16,9,floor,9)
        card('door_frame',crop(room,176,80,144,16,16),16,16,9,floor,9)
        card('wall_bottom',crop(room,176,16,144,16,16),16,16,9,floor,9)
        card('wall_span',crop(room,176,0,0,176,32),176,32,9,floor,9)
        from world_room_furniture import cards as room_furniture
        for name,w,h,pixels in room_furniture():
            card(name,pixels,w,h,9,floor,9,True,0x80 if name=='service_counter' else 0)
    if profile in ('industrial','civic'):
        directory=root/'assets/tiles/south-park-services-v3'
        receipt=json.loads((directory/'conversion.json').read_text())
        source=checked(directory,'buildings.indices',receipt)
        service_palettes=checked(directory,'building-palettes.gbapal',receipt)
        palettes[12]=service_palettes[:32] if profile=='industrial' else service_palettes[32:64]
        name='warehouse' if profile=='industrial' else 'clinic'
        offset=0 if profile=='industrial' else 8960
        card(name,source[offset:offset+8960],112,80,12,paving,7)
    if profile != 'residential':
        directory=root/'assets/tiles/sunset-terrain'
        receipt=json.loads((directory/'conversion.json').read_text())
        grass_spec=(directory/'grass-native.json').read_bytes()
        if hashlib.sha256(grass_spec).hexdigest()!=receipt['native_grass_sha256']:
            raise ValueError('Authored sage grass changed without its receipt')
        grass=bytes(int(c,16) for row in json.loads(grass_spec)['cells']['0'] for c in row)
        palettes[10]=checked(directory,'terrain.gbapal',receipt)
        card('grass',empty,16,16,10,grass,10,False)
        if profile in ('nature','ridge_town','park_edge'):
            directory=root/'assets/tiles/sf-foliage-v1'
            receipt=json.loads((directory/'conversion.json').read_text())
            palettes[11]=checked(directory,'foliage.gbapal',receipt)
            shrub=checked(directory,'shrub.indices',receipt)
            card('grove',crop(shrub,32,8,8,16,16),16,16,11,grass,10)
            for name in ('cypress','pine','shrub','rocks'):
                spec=next(item for item in receipt['cards'] if item['name']==name)
                w,h=spec['size'];card(name,checked(directory,name+'.indices',receipt),w,h,11,grass,10)
        for name in ('tree','bench','lamp','bin'):
            raw,w,h=furniture[name]
            card(name+'_grass',raw,w,h,6,grass,10)
    landmarks={'industrial':('crane',),'civic':('highrise',),
               'nature':('sutro_tower','windmill','conservatory','bath_ruins'),
               'park_edge':('windmill','conservatory'),
               'culture':('theater',),'stadium':('stadium_gate',)}
    if profile in landmarks:
        directory=root/'assets/tiles/sf-landmarks-v1'
        receipt=json.loads((directory/'conversion.json').read_text())
        palettes[9]=checked(directory,'landmarks.gbapal',receipt)
        for name in landmarks[profile]:
            data=next(item for item in receipt['cards'] if item['name']==name)
            raw=checked(directory,name+'.indices',receipt);w,h=data['size']
            background,bank=(grass,10) if profile in ('nature','park_edge') else (paving,7)
            card(name,raw,w,h,9,background,bank)
    if profile in ('neighborhood','mixed_use'):
        directory=root/'assets/tiles/neighborhood-landmarks-v1'
        receipt=json.loads((directory/'conversion.json').read_text())
        palettes[11]=checked(directory,'neighborhood.gbapal',receipt)
        for name in ('mural','mansion','surfboards','bar_sign','book_box'):
            if profile=='mixed_use' and name=='mansion':continue
            if profile=='neighborhood' and name in ('mural','book_box'):continue
            spec=next(c for c in receipt['cards'] if c['name']==name);w,h=spec['size']
            card(name,checked(directory,name+'.indices',receipt),w,h,11,paving,7)
        if profile=='mixed_use':
            raw=checked(directory,'lookout.indices',receipt)
            card('lookout_left',crop(raw,48,0,0,16,32),16,32,11,paving,7)
            # A real traversable stair surface uses only the lower native ground
            # layer; it cannot cover the walking sprite like an overhead facade.
            source_colors=struct.unpack('<16H',palettes[7]);target=struct.unpack('<16H',palettes[11])
            remap=[min(range(1,16),key=lambda j:sum((((color>>c*5)&31)-((target[j]>>c*5)&31))**2 for c in range(3))) for color in source_colors]
            steps=crop(raw,48,16,0,16,32)
            opaque=bytes(value or remap[paving[(y%16)*16+x]] for y in range(32) for x in range(16)
                         for value in (steps[y*16+x],))
            card('lookout_steps',opaque,16,32,11,paving,7,False,floor=True)
            card('lookout_right',crop(raw,48,32,0,16,32),16,32,11,paving,7)
    # Scenic water is separated by an explicit solid seawall. Traversable bay
    # crossings still use the independently modelled native Surf/Waterfall cells.
    directory=root/'assets/tiles/sunset-terrain'
    receipt=json.loads((directory/'conversion.json').read_text())
    coast=checked(directory,'tiles.indices',receipt)
    palettes[10]=checked(directory,'terrain.gbapal',receipt)
    card('scenic_sea',coast[2*256:3*256],16,16,10,paving,7)
    street_colors=struct.unpack('<16H',palettes[8])
    def gray(value):
        return min((i for i in range(1,16) if i!=3),
                   key=lambda i:sum((((street_colors[i]>>c*5)&31)-value)**2 for c in range(3)))
    dark,shade,light,stone=map(gray,(9,15,27,22))
    # Original native stone curb: a shaded seaward face, clear cap and sparse
    # joints. The barrier must look solid rather than like walkable grass.
    wall=bytes(dark if x==0 or y==15 or (y==7 and x<4) else shade if x<4
               else light if x==4 or y==0 else shade if (x==10 and y<7) or (x==7 and y>7) else stone
               for y in range(16) for x in range(16))
    card('seawall',wall,16,16,8,paving,7)
    directory=root/'assets/tiles/sf-foliage-v1'
    receipt=json.loads((directory/'conversion.json').read_text())
    shrub=checked(directory,'shrub.indices',receipt)
    source_colors=struct.unpack('<16H',checked(directory,'foliage.gbapal',receipt))
    target_colors=struct.unpack('<16H',palettes[10])
    remap=[0]+[min(range(1,16),key=lambda j:sum((((color>>c*5)&31)-((target_colors[j]>>c*5)&31))**2 for c in range(3)))
               for color in source_colors[1:]]
    hedge=bytes(remap[shrub[(y*2)*32+x*2]] for y in range(16) for x in range(16))
    card('edge_hedge',hedge,16,16,10,paving,7)
    if profile not in ('residential', 'nature'):
        from world_surfaces import surfaces
        for name, w, h, pixels in surfaces():
            card(name,pixels,w,h,7,paving,7,False,floor=True)
        pit=next(pixels for name,_,_,pixels in surfaces() if name=='tree_well')
        raw,w,h=furniture['tree']
        card('street_tree',raw,w,h,6,pit,7,ground_width=32)
        from world_botany import cards, palette
        palettes[7]=palette(palettes[7])
        for name,w,h,pixels in cards():
            card(name,pixels,w,h,7,paving,7)
    # A crop from the middle of the connected frontage atlas is a shared-wall
    # facade. Exposed ends must use complete outer art or a finished variant.
    edges={'coral':['left'],'cafe':[],'cream':[],'lilac':['right'],
           'pair':['left','right'],'warehouse':['left','right'],
           'clinic':['left','right'],'brick':['left','right'],
           'highrise':['left','right'],'theater':['left','right'],
           'mansion':['left','right'],'stadium_gate':['left','right']}
    families={'coral':'bay_house','cream':'bay_house','lilac':'bay_house',
              'pair':'paired_townhouse','cafe':'corner_shop',
              'warehouse':'warehouse','clinic':'clinic','highrise':'office_tower',
              'theater':'theater','mansion':'mansion','stadium_gate':'stadium_gate'}
    for name,closed in edges.items():
        if name in catalog:
            catalog[name]['closed_edges']=closed
            if name in families:catalog[name]['architecture_type']=families[name]
    if profile in ('neighborhood','mixed_use'):
        base,width,offset=('cream',48,80) if profile in ('neighborhood','mixed_use') else ('cafe',32,48)
        raw=crop(houses,176,offset,0,width,64)
        variants=(('lr',['left','right']),) if profile in ('neighborhood','mixed_use') else (('l',['left']),('r',['right']),('lr',['left','right']))
        for suffix,closed in variants:
            pixels=bytearray(raw)
            for side in closed:
                outer,inner=(0,1) if side=='left' else (width-1,width-2)
                for y in range(64):
                    band=range(0,8) if side=='left' else range(width-8,width)
                    if any(raw[y*width+x] for x in band):
                        pixels[y*width+outer]=1
                        pixels[y*width+inner]=5 if y<12 else 6 if y<60 else 13
            name=base+'_'+suffix
            card(name,bytes(pixels),width,64,6,paving,7)
            catalog[name]['closed_edges']=closed
            catalog[name]['architecture_type']=families[base]
    from world_architecture import paint_palette, FORMS
    from world_rich_facades import fronts,facade
    for name,w,h,raw in fronts(profile):
        card(name,raw,w,h,6,paving,7,deduplicate=True)
        catalog[name]['closed_edges']=['left','right']
        catalog[name]['architecture_type']=name
    for name in FORMS:
        if name not in catalog:continue
        for suffix,closed in [('l',['left']),('m',[]),('r',['right'])]:
            w,h,raw=facade(name,closed)
            variant=name+'_'+suffix
            card(variant,raw,w,h,6,paving,7,deduplicate=True)
            catalog[variant]['closed_edges']=closed
            catalog[variant]['architecture_type']=name
    # Alternate paint uses free native palette banks and shares every 8x8 tile.
    # It does not spend the sprite budget on recolored copies of the same art.
    banks={'neighborhood':(9,12),'mixed_use':(9,12),'ridge_town':(9,12),'park_edge':(12,),
           'culture':(11,12),'stadium':(11,12),
           'industrial':(11,),'civic':(11,)}.get(profile,())
    # Service and reserved-gym fronts only draw their base paint. Avoid
    # allocating unused recolor records at the expense of connection margins.
    base_fronts=[(n,c) for n,c in catalog.items() if (n in (*FORMS,'coral') or n.rsplit('_',1)[0] in FORMS) and 'closed_edges' in c and
                 any((w>>12)&15==6 for row in c['tiles'] for t in row for w in records[t-FIRST_METATILE][4:])]
    for scheme,bank in zip(('sage','slate'),banks):
        if bank in palettes:raise ValueError('Building paint would overwrite a loaded palette')
        palettes[bank]=paint_palette(palettes[6],scheme)
        for name,base in base_fronts:
            ids=[]
            for row in base['tiles']:
                out=[]
                for tile in row:
                    source=records[tile-FIRST_METATILE]
                    changed=[(w&~0xf000)|(bank<<12) if (w>>12)&15==6 and any(
                        palettes[6][v*2:v*2+2]!=palettes[bank][v*2:v*2+2]
                        for v in set(tiles[(w>>16)&0xfff])) else w for w in source]
                    attribute=attributes[tile-FIRST_METATILE]
                    prior=next((i for i,(r,a) in enumerate(zip(records,attributes)) if r==changed and a==attribute),None)
                    if prior is None:prior=len(records);records.append(changed);attributes.append(attribute)
                    out.append(FIRST_METATILE+prior)
                ids.append(out)
            catalog[name+'__'+scheme]=dict(base,tiles=ids,explicit_cells=True)
    if profile == 'culture':
        # Append the finished bay-house end without moving existing card IDs.
        pixels=bytearray(crop(houses,176,80,0,48,64))
        for y in range(64):
            pixels[y*48+47]=2 if y<4 else 1 if y<62 else 13
            pixels[y*48+46]=5 if y<12 else 6 if y<60 else 13
        card('cream_r',bytes(pixels),48,64,6,paving,7)
        catalog['cream_r']['closed_edges']=['right']
        catalog['cream_r']['architecture_type']='bay_house'
        # A quiet 16px sidewalk joint, smaller than a player's silhouette.
        # Keep the authored forecourt from reading as oversized concrete slabs.
        quiet = bytes(3 if x == 15 or y == 15 else 1
                      for y in range(16) for x in range(16))
        card('court_walk',quiet,16,16,7,paving,7,False,floor=True)
    if profile=='civic':
        # Reuse complete roof/foundation rows and repeat the existing window
        # storey. Height changes consume no extra graphics or metatile IDs.
        base=catalog['highrise']
        for name,repeats in [('highrise_medium',2),('highrise_tall',4)]:
            catalog[name]=dict(base,tiles=[list(r) for r in
                (base['tiles'][:3]+base['tiles'][3:4]*repeats+base['tiles'][4:])],
                explicit_cells=True)
        # Broader commercial blocks keep finished outer edges but omit the
        # tower's narrow antenna. Only the middle window column repeats.
        for name,repeats in [('office_wide',3),('lab_wide',1)]:
            rows=base['tiles'][1:3]+base['tiles'][3:4]*repeats+base['tiles'][4:]
            catalog[name]=dict(base,tiles=[[row[0],row[1],row[1],row[1],row[2]]
                                          for row in rows],explicit_cells=True)
    if profile=='industrial':
        # Complete adjoining workshop bays form one broad garage hall. Share
        # normal records/graphics, retaining actual outer caps and foundations.
        left,right=(catalog[n]['tiles'] for n in ('workshop_l','workshop_r'))
        if (len(left)!=4 or len(right)!=4 or any(len(r)!=3 for r in left+right)
                or catalog['workshop_l']['closed_edges']!=['left']
                or catalog['workshop_r']['closed_edges']!=['right']):
            raise ValueError('Garage hall requires two complete3x4 workshop bays')
        catalog['garage_hall']=dict(tiles=[list(a+b) for a,b in zip(left,right)],
            blocked=True,closed_edges=['left','right'],architecture_type='garage_hall',
            explicit_cells=True)
    if profile=='mixed_use':
        # A broad campus hall reuses finished outer wings and a continuous
        # central gable. Its scale changes without allocating another atlas.
        wings=[catalog[n]['tiles'] for n in ('flats_l','gable_m','flats_r')]
        catalog['campus_hall']=dict(tiles=[list(a+b+c) for a,b,c in zip(*wings)],
            blocked=True,closed_edges=['left','right'],architecture_type='campus_hall',
            explicit_cells=True)
    if profile=='industrial':
        # A distinct scenery card leaves the original Repair Counter front
        # and its fixed central doorway intact. Existing loaded sage paint
        # provides a second factory finish without another graphics palette.
        from world_industrial_factory import factory
        w,h,raw=factory()
        if (w,h)!=(112,80):raise ValueError('Factory must keep its declared7x5 footprint')
        for name,bank in (('factory',12),('factory_sage',11)):
            card(name,raw,w,h,bank,paving,7,deduplicate=name.endswith('_sage'))
            catalog[name]['closed_edges']=['left','right']
            catalog[name]['architecture_type']='industrial_factory'
    if profile=='industrial':
        from world_industrial_factory import factory_block,dock_surfaces
        w,h,raw=factory_block()
        for name,bank in (('factory_block',12),('factory_block_sage',11)):
            card(name,raw,w,h,bank,paving,7,deduplicate=True)
            catalog[name]['closed_edges']=['left','right']
            catalog[name]['architecture_type']='industrial_factory_block'
        deck,rail=dock_surfaces()
        card('dock_deck',deck,16,16,12,paving,7,False,floor=True)
        card('dock_rail',rail,16,16,12,paving,7,True)
    if len(records) > 512:
        raise ValueError('SF world kit exceeds native secondary allocation')
    if any(not 6<=bank<=12 or len(raw)!=32 for bank,raw in palettes.items()):
        raise ValueError('A secondary palette falls outside the seven native loaded banks')
    from world_shared_primary import pack_graphics
    tiles, primary_tiles, records = pack_graphics(tiles,records)
    return {'tiles': tiles, 'primary_tiles':primary_tiles, 'records': records, 'attributes': attributes,
            'palettes': palettes, 'catalog': catalog, 'profile':profile,
            'uses_native_grass':profile!='residential'}


def apply_kit(engine, original, kit):
    """Normal compile inputs, never unverified post-link cartridge replacements."""
    from PIL import Image
    profile = kit.get('profile','residential')
    directory = ('data/tilesets/secondary/petalburg/' if profile=='residential'
                 else 'data/tilesets/secondary/sf_world_'+profile+'/')
    (engine / directory).mkdir(parents=True,exist_ok=True)
    files = []
    pixels = bytearray(128*256)
    for index, tile in enumerate(kit['tiles']):
        left, top = index % 16 * 8, index // 16 * 8
        for y in range(8):
            pixels[(top+y)*128+left:(top+y)*128+left+8] = tile[y*8:y*8+8]
    image = Image.new('P', (128, 256)); image.putdata(pixels)
    image.putpalette([v for i in range(256) for v in (i, i, i)])
    image.save(engine / directory / 'tiles.png', bits=4)
    files.append(directory + 'tiles.png')
    for name, data in [('metatiles.bin', b''.join(struct.pack('<8H', *r) for r in kit['records'])),
                       ('metatile_attributes.bin', struct.pack('<'+'H'*len(kit['attributes']), *kit['attributes']))]:
        (engine / directory / name).write_bytes(data); files.append(directory + name)
    primary=kit.get('primary_tiles',{})
    for name,data in [('primary-slots.bin',struct.pack('<'+'H'*len(primary),*primary)),
                      ('primary-art.4bpp',bytes(v for tile in primary.values() for y in range(8)
                                               for x in range(0,8,2) for v in [tile[y*8+x]|tile[y*8+x+1]<<4]))]:
        (engine/directory/name).write_bytes(data);files.append(directory+name)
    if profile != 'residential':
        relative=directory+'palettes.gbapal'
        (engine/relative).write_bytes(b''.join(kit['palettes'].get(bank,bytes(32)) for bank in range(16)))
        files.append(relative)
        suffix=PROFILES[profile].removeprefix('gTileset_')
        # agbcc rejects an INCBIN of a zero-length file. The count remains zero
        # for profiles without overflow art; harmless C sentinels keep their
        # symbols valid without transferring an invented tile or slot.
        slots=(f'INCBIN_U16("{directory}primary-slots.bin")' if primary else '{0}')
        graphics=(f'INCBIN_U8("{directory}primary-art.4bpp")' if primary else '{0}')
        for path,text in [
            ('src/data/tilesets/graphics.h',
             f'\nconst u32 gTilesetTiles_{suffix}[] = INCGFX_U32("{directory}tiles.png", ".4bpp.lz", "-num_tiles 512 -Wnum_tiles");\n'
             f'const u16 gSFPrimaryCount_{suffix} = {len(primary)};\n'
             f'const u16 gSFPrimarySlots_{suffix}[] = {slots};\n'
             f'const u8 ALIGNED(4) gSFPrimaryGraphics_{suffix}[] = {graphics};\n'
             f'const u16 gTilesetPalettes_{suffix}[] = INCBIN_U16("{directory}palettes.gbapal");\n'),
            ('src/data/tilesets/metatiles.h',
             f'\nconst u16 gMetatiles_{suffix}[] = INCBIN_U16("{directory}metatiles.bin");\n'
             f'const u16 gMetatileAttributes_{suffix}[] = INCBIN_U16("{directory}metatile_attributes.bin");\n'),
            ('src/data/tilesets/headers.h',
             f'\nconst struct Tileset {PROFILES[profile]} = {{ .isCompressed=TRUE, .isSecondary=TRUE,\n'
             f' .tiles=gTilesetTiles_{suffix}, .palettes=(const u16 (*)[16])gTilesetPalettes_{suffix},\n'
             f' .metatiles=gMetatiles_{suffix}, .metatileAttributes=gMetatileAttributes_{suffix}, .callback=NULL }};\n')]:
            existing=(engine/path).read_text()
            if ('const struct Tileset '+PROFILES[profile]+' =') in existing:
                raise ValueError('Restore native headers before applying an art profile')
            (engine/path).write_text(existing+text);files.append(path)
        return files
    for bank, raw in kit['palettes'].items():
        colors = [tuple(((w >> c*5) & 31)*255//31 for c in range(3)) for w in struct.unpack('<16H', raw)]
        relative = directory + f'palettes/{bank:02d}.pal'
        (engine / relative).write_text('JASC-PAL\n0100\n16\n' + '\n'.join(' '.join(map(str, rgb)) for rgb in colors) + '\n')
        files.append(relative)
    path = 'src/data/tilesets/graphics.h'
    source = original(path)
    old = '"-num_tiles 159 -Wnum_tiles"'
    line = next(line for line in source.splitlines() if line.startswith('const u32 gTilesetTiles_Petalburg[]'))
    if old not in line:
        raise ValueError('Pinned secondary tileset allocation changed')
    (engine / path).write_text(source.replace(line, line.replace(old, '"-num_tiles 512 -Wnum_tiles"'), 1))
    files.append(path)
    path = 'src/data/tilesets/headers.h'
    source = original(path)
    (engine / path).write_text(source.replace('.callback = InitTilesetAnim_Petalburg,', '.callback = NULL,', 1))
    files.append(path)
    return files


def describe(kit):
    return {'secondary':PROFILES[kit['profile']], 'cards':{
        name:{'first':card['tiles'][0][0],'width':len(card['tiles'][0]),
              'height':len(card['tiles']),'blocked':card['blocked'],
              'behavior':kit['attributes'][card['tiles'][0][0]-512]&255,'layer':1,
              **({'cells':card['tiles']} if card.get('explicit_cells') else {}),
              **({'closed_edges':card['closed_edges']} if 'closed_edges' in card else {}),
              **({'architecture_type':card['architecture_type']} if 'architecture_type' in card else {})}
        for name,card in kit['catalog'].items()}}


def legend_for(kit):
    legend={'.':[1,False,3],'#':[11,True,3],'W':[368,False,1],'V':[179,False,1]}
    for card in kit['catalog'].values():
        for row in card['tiles']:
            for tile in row:legend[chr(0x100+tile-512)]=[tile,card['blocked'],3]
    return legend
