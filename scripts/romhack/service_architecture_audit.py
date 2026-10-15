"""Independent compiled service buildings, static doors and registrations.

Resource integrity only. No art/animation quality, timing, save, browser,
performance, campaign or human approval is established by this audit.
"""
import hashlib
import json
from pathlib import Path
import struct

from connected_frontage_audit import cell_pixels


COLORS = ((0,0,0),(5,7,10),(12,13,16),(17,17,19),(8,11,15),
          (29,26,20),(22,18,14),(25,14,11),(18,9,8),(18,10,7),
          (28,22,14),(20,17,22),(20,20,20),(14,14,14),(9,14,4),(11,8,9))
SERVICE = 'assets/tiles/south-park-services-v3'
DOORS = 'assets/tiles/service-door-v2'
BASE = 'assets/tiles/connected-frontage-v3/baseline-v76'
SERVICE_CARDS = (('warehouse',(87,23,974,704),40,8,64,71,583),
                 ('clinic',(1124,23,2012,704),75,9,99,106,618))
DOOR_BOXES = (((43,73,316,596),(407,73,679,596),(771,73,1044,596)),
              ((43,763,316,1286),(407,762,679,1286),(771,763,1044,1286)))
MOVING = {y*16+x for y in range(5,26) for x in range(3,13)}
# Original acceptance fingerprints, never supplied by producer metadata.
ASSETS = {
    'assets/tiles/south-park-services-v3/building-palettes.gbapal':(64,'a27f25bf4bdb0eea3ce7214f4d8e0c4f05d05f482165dee5f3af5435f8e45361'),
    'assets/tiles/south-park-services-v3/buildings.indices':(17920,'f31039636d261d556bd579896134d1a3a2a45097ea82099823f989c033891b86'),
    'assets/tiles/south-park-services-v3/clinic.png':(1699,'1871608b7590406e296a935ffebd61430ffc92cb33bc518730367e516a46e0c6'),
    'assets/tiles/south-park-services-v3/conversion.json':(1243,'c6d7f4616b377b0e482274dc978cf09b667453fadb44a167bfe110c216a9c4c3'),
    'assets/tiles/south-park-services-v3/prompt.md':(1737,'80d3a0eb7a56c653e8c0a32da3343b8b0f059267399c86d97e11c41796c8c10f'),
    'assets/tiles/south-park-services-v3/source.png':(1241734,'f09ddf5412ee3d5425a36f322c0ffad471a8264b5de8a7e69be49d2b1f3b7e86'),
    'assets/tiles/south-park-services-v3/warehouse.png':(1614,'996f7d664d0df45ee0434311fb3842051b9bbbb77d7e95c8b98a16725ceb28c2'),
    'assets/tiles/service-door-v2/clinic-closed-reference.png':(268,'fef799ba1aea5179530870d1034ea63e4fe5c55ce1fdec9b37197649d055097d'),
    'assets/tiles/service-door-v2/clinic.4bpp':(768,'e0e4783886ed42dfa1f027a9a0a6a5c66570220b9a664ba37ca352f4e08f6e2f'),
    'assets/tiles/service-door-v2/clinic.indices':(1536,'9fe7c77f9098e0f515bae027b3c5c17de10e09c21c9e632d182638833e89f818'),
    'assets/tiles/service-door-v2/clinic.png':(371,'eb6f895b049821d94ce643726d83f0df9b2ce5efafb50214ae814b0e37cf44da'),
    'assets/tiles/service-door-v2/conversion.json':(1949,'aa22748615185bf9dee3ac44f5de85b1393d06f0ed71a2cdf7803ab3b301896d'),
    'assets/tiles/service-door-v2/prompt.md':(1829,'e9ed34ed33d0c7f2a0c8475e11ded6757fc43e1417297f0cfd8c919ff93ab3b9'),
    'assets/tiles/service-door-v2/source.png':(813880,'5502852a784e0e49765ed2e464f15f64a8b2ef09043a4022828ffa776197b1b3'),
    'assets/tiles/service-door-v2/warehouse-closed-reference.png':(296,'c0d372c1cbb4df72133edba071503e236d725ae8e55617683f57c6d10199fc08'),
    'assets/tiles/service-door-v2/warehouse.4bpp':(768,'096ae5e6379a0cd24b575b2eb5d74a499e04eb2300a38e705b9d2afb239a51a6'),
    'assets/tiles/service-door-v2/warehouse.indices':(1536,'0e701c66663d3be6b6e94fad5008372bfd3c0ec8b5790720f38b8095b6639e0f'),
    'assets/tiles/service-door-v2/warehouse.png':(423,'ab5e4d69a5fbcb66c37d1ae653f78382d01f2602c0a6dc5669a2d778da3e76d5'),
    'assets/tiles/south-park-services-v2/source.png':(1290826,'9269ae6e8e93aa9d17df2d88cda7f8c4566115c141c136b66fb878e649805c40'),
}
BASELINE = {
    'secondary.4bpp':(16064,'025b15ff1b4e9606d010b85031c71476a3071183015300e2466e6c60f98c4d42'),
    'secondary-metatiles.bin':(2400,'c1d17b5e9bc2c04371c6a2aaea46321f2326c70822d9a8c87974fa9ed596a9aa'),
    'secondary-attributes.bin':(300,'5d75b62c2517473238cfe7967401f492d506a41ffbbd5de58ea9c99ad39eab2f'),
    'secondary-palettes.gbapal':(512,'73e3ba1b6d1f0a9385e97e92eba6a4a2d1268384e4cdf6f45f452a49fda512db'),
    'receipt.json':(1523,'0c0bef56b717668dc0f5ca949250e9ee318a4ee3e46d45fa8eb4628c3f839fc8'),
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def native_door_pixels(payload):
    """Decode native three-stage 2x4 tile order without a production packer."""
    if len(payload) != 768:
        raise ValueError('Require exactly three eight-tile door stages.')
    return [bytes((payload[stage*256+(y//8*2+x//8)*32+(y%8)*4+(x%8)//2]
                   >> (4*(x%2))) & 15 for y in range(32) for x in range(16))
            for stage in range(3)]


def validate_door_frames(frames):
    if len(frames)!=3 or any(len(frame)!=512 or max(frame)>15 for frame in frames):
        raise ValueError('Door indices require three complete four-bit16x32 frames.')
    if len(set(frames))!=3:
        raise ValueError('Closed, partial and open stages must be distinct.')
    for frame in frames:
        if any(frame[i]!=frames[0][i] for i in range(512) if i not in MOVING):
            raise ValueError('Door jambs and steps move outside the reviewed rectangle.')
        if any(not frame[i] for i in MOVING):
            raise ValueError('The moving portal must remain opaque in every stage.')


def audit_services(rom, elf, root):
    from check_creature_resources import Cartridge, decode_lz
    from PIL import Image

    checks, hashes, errors = [], {}, []
    result = {'passed':False,'checks':checks,'hashes':hashes,'errors':errors,
              'quality_approval':'pending','scope':__doc__}

    def source(path):
        blob=path.read_bytes();hashes[str(path)]=sha(blob);return blob

    def pinned(directory, specification):
        blobs={}
        for name,(length,digest) in specification.items():
            blob=source(directory/name)
            if len(blob)!=length or sha(blob)!=digest:
                raise ValueError('Pinned original resource differs: '+str(directory/name))
            blobs[name]=blob
        return blobs

    def compare(name, expected, observe):
        row={'name':name,'passed':False,'expected_bytes':len(expected),'expected_sha256':sha(expected)}
        try:
            actual=observe()
            row.update(passed=actual==expected,actual_bytes=len(actual),actual_sha256=sha(actual))
        except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
            row['error']=str(error);errors.append(name+': '+str(error))
        checks.append(row)

    try:
        root=Path(root)
        source(Path(__file__))
        source(Path(__file__).with_name('connected_frontage_audit.py'))
        source(Path(__file__).parents[1]/'quality/check_creature_resources.py')
        assets=pinned(root,ASSETS)
        baseline=pinned(root/BASE,BASELINE)
        palette=b''.join(struct.pack('<H',sum(rgb[c]<<(5*c) for c in range(3))) for rgb in COLORS)
        flat=[c*255//31 for rgb in COLORS for c in rgb]
        service=json.loads(assets[SERVICE+'/conversion.json'])
        doors=json.loads(assets[DOORS+'/conversion.json'])
        if service['native_size']!=[112,80] or service['cards'] != [
                {'name':name,'source_bounds':list(box)} for name,box,*rest in SERVICE_CARDS] or \
                service['source_sha256']!=sha(assets[SERVICE+'/source.png']) or \
                service['prompt_sha256']!=sha(assets[SERVICE+'/prompt.md']) or \
                service['references']!={'assets/tiles/south-park-services-v2/source.png':
                    sha(assets['assets/tiles/south-park-services-v2/source.png'])} or \
                service['files']!={name:sha(assets[SERVICE+'/'+name]) for name in (
                    'warehouse.png','clinic.png','buildings.indices','building-palettes.gbapal')}:
            raise ValueError('Service provenance, geometry or resource receipt differs.')
        if (doors['source_bounds'],doors['moving_rectangle'],doors['size'],doors['stages'],
                doors['palette_banks'],doors['static_door_cells']) != (
                [[list(box) for box in row] for row in DOOR_BOXES],[3,5,13,26],[16,32],3,[8,9],[[64,71],[99,106]]) or \
                doors['source_sha256']!=sha(assets[DOORS+'/source.png']) or \
                doors['prompt_sha256']!=sha(assets[DOORS+'/prompt.md']) or doors['palette_sha256']!=sha(palette) or \
                doors['references']!={name+'-closed-reference.png':sha(assets[DOORS+'/'+name+'-closed-reference.png'])
                    for name in ('warehouse','clinic')} or doors['files']!={name+suffix:sha(assets[DOORS+'/'+name+suffix])
                    for name in ('warehouse','clinic') for suffix in ('.png','.indices','.4bpp')}:
            raise ValueError('Door provenance, geometry, static bindings or resource receipt differs.')
        if assets[SERVICE+'/building-palettes.gbapal']!=palette*2:
            raise ValueError('Both service palettes must match the reviewed literal RGB555 colors.')

        def quantized(image):
            return bytes(0 if rgba[3]<128 else min(range(1,16),key=lambda i:
                sum((round(rgba[c]*31/255)-COLORS[i][c])**2 for c in range(3)))
                for rgba in image.get_flattened_data())

        with Image.open(root/SERVICE/'source.png') as image:
            if image.size!=(2100,749):raise ValueError('Service source dimensions differ.')
            rgba=image.convert('RGBA')
            body=[quantized(rgba.crop(box).resize((112,80),Image.Resampling.NEAREST))
                  for name,box,*rest in SERVICE_CARDS]
        compare('source_service_pixels',assets[SERVICE+'/buildings.indices'],lambda:b''.join(body))
        if len(assets[SERVICE+'/buildings.indices'])!=17920:
            raise ValueError('Service indexed allocation differs.')
        for number,(name,*rest) in enumerate(SERVICE_CARDS):
            with Image.open(root/SERVICE/(name+'.png')) as image:
                if (image.mode,image.size,image.info.get('transparency'),image.getpalette()[:48],image.tobytes()) != (
                        'P',(112,80),0,flat,body[number]):
                    raise ValueError('Service preview, source crop and indexed pixels differ: '+name)

        door_frames={}
        with Image.open(root/DOORS/'source.png') as image:
            if image.size!=(1086,1448):raise ValueError('Door source dimensions differ.')
            rgba=image.convert('RGBA')
            for (name,*rest),boxes in zip(SERVICE_CARDS,DOOR_BOXES):
                candidates=[quantized(rgba.crop(box).resize((16,32),Image.Resampling.NEAREST)) for box in boxes]
                frames=[candidates[0]]
                for candidate in candidates[1:]:
                    frame=bytearray(frames[0])
                    for i in MOVING:frame[i]=candidate[i]
                    frames.append(bytes(frame))
                validate_door_frames(frames)
                compare(name+':source_door_pixels',assets[DOORS+'/'+name+'.indices'],lambda frames=frames:b''.join(frames))
                if native_door_pixels(assets[DOORS+'/'+name+'.4bpp'])!=frames:
                    raise ValueError('Source door tile order differs: '+name)
                with Image.open(root/DOORS/(name+'.png')) as preview:
                    expected=b''.join(frame[y*16:(y+1)*16] for y in range(32) for frame in frames)
                    if (preview.mode,preview.size,preview.info.get('transparency'),preview.getpalette()[:48],preview.tobytes()) != (
                            'P',(48,32),0,flat,expected):
                        raise ValueError('Door preview does not match the indexed stage sheet: '+name)
                door_frames[name]=frames

        cart=Cartridge(rom,elf)
        hashes.update(rom=sha(cart.rom),elf=sha(cart.elf))
        raw=decode_lz(cart.data('gTilesetTiles_SFSouthPark'))
        records=cart.data('gMetatiles_SFSouthPark')
        attrs=cart.data('gMetatileAttributes_SFSouthPark')
        palettes=cart.data('gTilesetPalettes_SFSouthPark')
        compare('secondary_allocations',struct.pack('<4I',476*32,150*16,150*2,512),
                lambda:struct.pack('<4I',len(raw),len(records),len(attrs),len(palettes)))
        if not 0<len(raw)<=504*32 or len(raw)%32 or len(records)!=2400:
            raise ValueError('Secondary art exceeds its resident/cache/table bound.')
        compare('all150_attributes',baseline['secondary-attributes.bin'],lambda:attrs)
        expected_palette=bytearray(baseline['secondary-palettes.gbapal'])
        expected_palette[8*32:10*32]=palette*2
        compare('complete_secondary_palette',bytes(expected_palette),lambda:palettes)
        old_raw=baseline['secondary.4bpp'];old_records=baseline['secondary-metatiles.bin']
        expected_cells=[cell_pixels(old_raw,struct.unpack_from('<4H',old_records,i*16+8),secondary=True)
                        for i in range(150)]
        expected_banks=[bytes(word>>12 for word in struct.unpack_from('<4H',old_records,i*16+8)) for i in range(150)]
        for number,(name,box,first,bank,upper,lower,metatile) in enumerate(SERVICE_CARDS):
            for cell in range(35):
                expected_cells[first+cell]=b''.join(body[number][(cell//7*16+y)*112+cell%7*16:
                    (cell//7*16+y)*112+cell%7*16+16] for y in range(16))
                expected_banks[first+cell]=bytes([bank])*4
            expected_cells[upper]=door_frames[name][0][:256]
            expected_cells[lower]=door_frames[name][0][256:]
        for index in range(150):
            def foreground(index=index):
                words=struct.unpack_from('<4H',records,index*16+8)
                return bytes(word>>12 for word in words)+cell_pixels(raw,words,secondary=True)
            compare('foreground_%03d'%index,expected_banks[index]+expected_cells[index],foreground)
        compare('first40_literal_zero_underlays',bytes(40*8),
                lambda:b''.join(records[i*16:i*16+8] for i in range(40)))
        paving=cell_pixels(old_raw,struct.unpack_from('<4H',old_records,19*16+8),secondary=True,bank=4)
        if set(paving)!={1,2}:raise ValueError('Frozen paving no longer describes opaque original gray pixels.')
        for index in range(40,150):
            compare('underlay_%03d'%index,paving,
                lambda index=index:cell_pixels(raw,struct.unpack_from('<4H',records,index*16),secondary=True,bank=4))

        registrations={}
        for name,box,first,bank,upper,lower,metatile in SERVICE_CARDS:
            title=name.title()
            tile_symbol='sSFPark'+title+'Door';selector_symbol='sSFPark'+title+'Palette'
            payload=cart.data(tile_symbol)
            compare(name+':animation_bytes',assets[DOORS+'/'+name+'.4bpp'],lambda payload=payload:payload)
            compare(name+':animation_decoded_stages',b''.join(door_frames[name]),
                    lambda payload=payload:b''.join(native_door_pixels(payload)))
            def frame_geometry(payload=payload):
                validate_door_frames(native_door_pixels(payload));return b'distinct-opaque-portal-fixed-jambs'
            compare(name+':animation_rectangle',b'distinct-opaque-portal-fixed-jambs',frame_geometry)
            compare(name+':palette_selectors',bytes([bank])*8,lambda selector_symbol=selector_symbol:cart.data(selector_symbol))
            def static(upper=upper,lower=lower):
                return b''.join(cell_pixels(raw,struct.unpack_from('<4H',records,index*16+8),secondary=True)
                                for index in (upper,lower))
            compare(name+':static_closed_frame',door_frames[name][0],static)
            registrations[metatile]=(metatile,0,1,cart.symbols[tile_symbol][0],cart.symbols[selector_symbol][0])
        def table():
            payload=cart.data('sDoorAnimGraphicsTable')
            if not 12<=len(payload)<=256*12 or len(payload)%12:
                raise ValueError('Door table must contain bounded twelve-byte native records.')
            entries=list(struct.iter_unpack('<HBBII',payload))
            terminators=[i for i,row in enumerate(entries) if row[0]==0]
            if terminators!=[len(entries)-1] or entries[-1]!=(0,0,0,0,0):
                raise ValueError('Door table requires one final complete null terminator.')
            for metatile,expected in registrations.items():
                if [row for row in entries[:-1] if row[0]==metatile]!=[expected]:
                    raise ValueError('Service door missing, duplicated or registered with wrong sound/size/pointers: '+str(metatile))
            return b'exact-two-native-service-registrations'
        compare('door_registration',b'exact-two-native-service-registrations',table)
        result['counts']={'foreground_cells':150,'service_cells':70,'preserved_cells':80,
                          'static_door_cells':4,'door_stages':6,'door_cache_tiles_reserved':8,
                          'secondary_tiles':len(raw)//32}
    except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
        errors.append(str(error));checks.append({'name':'audit_inputs','passed':False,'error':str(error)})
    result.setdefault('counts',{})
    result['counts'].update(total=len(checks),matched=sum(row['passed'] for row in checks))
    result['passed']=bool(checks) and all(row['passed'] for row in checks) and not errors
    return result
