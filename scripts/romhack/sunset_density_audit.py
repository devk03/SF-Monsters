"""Independent compiled Sunset extension of frozen v79; no producer imports.

Checks resources, exact geometry and native animation bindings. Art acceptance,
event tables, old-save recovery, campaigns and runtime performance remain pending.
Opaque unused inherited resources are identified by hashes, never copied here.
"""
import hashlib
import json
from pathlib import Path
import struct

BASE='assets/tiles/sunset-density-v1/baseline-v79'
PINNED={
    'secondary.4bpp':(16384,'b3d61aaa7594b0dc84398b19222660c73b7179ae0f9a48c9ed9d8ede8525af98'),
    'owned-records.json':(9996,'3e301b1e59cd8971af50f35e945d2716189bec040ce59847a877cd2a9fb29a6c'),
    'source-plan.json':(3542,'7bfa566bdb8d4f8c3ba7495d51c4f9674867ac52af083b33bf40713f130f22e5'),
    'sunset-map.bin':(2048,'a3959bfceda3bd9d679ee1a539d8f9b66b1eab5de9d27e2bb1c131c20756279a'),
    'receipt.json':(1500,'dd06b3cb1630383106b2e7f3cedc998c0e3e0182d8eb15bfdd6f408874ecb1f0'),
}
SOURCES={
    'assets/tiles/connected-frontage-v3/block.indices':(14080,'a5803bee61035648f7e63fb4fd97cba0d594817e61bc0689be4b634fa8d5c82a'),
    'assets/tiles/connected-frontage-v3/block.gbapal':(32,'2c4864885ac0b05ef38c629d7e700df61c3a81e88633edf19604b534e7cc65bf'),
    'assets/tiles/connected-frontage-v3/native.png':(2409,'bad3ee2d2370fef7279cdc6defc42f85e2cf2199093e41a1db4932bbbeb9a791'),
    'assets/tiles/south-park-paving-v1/master8.indices':(64,'abc57fa59cab578112d578c18b4a2c524770ed2b58fce83123afb17f6b3722bf'),
    'assets/tiles/south-park-paving-v1/paving.gbapal':(32,'9e4b3bb698c497d3086a05137d0d71af1a8b7b5c47fff9e2056e17aee38e0c86'),
}
GENERAL={
    'gTilesetTiles_General':(16384,'24d47a59efccb7febfcd78bbfe472659694b2501bb9e34704138b5dd302dcc8b'),
    'gTilesetPalettes_General':(512,'747bc680f93d7097dba41c904fcf2ac25780e66540413ac33e88bdbf9f1368a9'),
    'gMetatiles_General':(8192,'17974b0ba1bb9d105d5ba255c69a3b80d8484a26ea0b8ff22c6c6567c6c22910'),
    'gMetatileAttributes_General':(1024,'06c9548a6c70d133b6d47638090f5d36f3fec92aace3d90deca758a4404cfa9b'),
}


def sha(blob):return hashlib.sha256(blob).hexdigest()


def density_cells():
    cells={}
    for top,first in ((4,194),(10,206),(25,218)):
        for row in range(4):
            for col in range(3):cells[28+col,top+row]=(512+first+row*3+col,True)
        for col in range(3):cells[28+col,top+4]=(742,False)
    return cells


def audit_sunset_density(rom,elf,root):
    from check_creature_resources import Cartridge,decode_lz
    from connected_frontage_audit import cell_pixels
    from PIL import Image
    checks,hashes,errors=[],{},[]
    result={'passed':False,'checks':checks,'hashes':hashes,'errors':errors,
            'quality_approval':'pending','scope':__doc__}
    def compare(name,expected,observe):
        row={'name':name,'passed':False,'expected_bytes':len(expected),'expected_sha256':sha(expected)}
        try:
            actual=observe();row.update(passed=actual==expected,actual_bytes=len(actual),actual_sha256=sha(actual))
        except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
            row['error']=str(error);errors.append(name+': '+str(error))
        checks.append(row)
    def require(condition,message):
        if not condition:raise ValueError(message)
    def pinned(path,spec):
        data=path.read_bytes();hashes[str(path)]=sha(data)
        require((len(data),sha(data))==spec,'Pinned source differs: '+str(path));return data
    try:
        root=Path(root)
        frozen={name:pinned(root/BASE/name,spec) for name,spec in PINNED.items()}
        assets={name:pinned(root/name,spec) for name,spec in SOURCES.items()}
        receipt=json.loads(frozen['receipt.json']);owned=json.loads(frozen['owned-records.json'])
        require(receipt['source_target_sha256']=='185cab500852af16e5229e9005cc601b7a16ac6cf764ce30778a7a15bbe820db',
                'Wrong v79 baseline identity.')
        require(receipt['files']=={n:{'bytes':s,'sha256':h} for n,(s,h) in PINNED.items() if n!='receipt.json'},
                'Baseline receipt payload list differs.')
        cart=Cartridge(rom,elf);hashes.update(rom=sha(cart.rom),elf=sha(cart.elf))
        data=cart.data;address=lambda name:cart.symbols[name][0]
        raw=decode_lz(data('gTilesetTiles_Petalburg'));records=data('gMetatiles_Petalburg')
        attrs=data('gMetatileAttributes_Petalburg');palettes=data('gTilesetPalettes_Petalburg')
        compare('allocations',struct.pack('<4I',16384,231*16,231*2,512),
                lambda:struct.pack('<4I',len(raw),len(records),len(attrs),len(palettes)))
        require((len(raw),len(records),len(attrs),len(palettes))==(16384,3696,462,512),'Wrong bounded Sunset allocation.')
        compare('old401_graphics',frozen['secondary.4bpp'][:401*32],lambda:raw[:401*32])
        for name,blob,key in (('old194_records',records[:194*16],'full_metatiles_sha256'),
                              ('old194_attributes',attrs[:194*2],'full_attributes_sha256'),
                              ('old_other_palettes',palettes[:256]+bytes(64)+palettes[320:],'palettes_excluding8_and9_sha256')):
            compare(name,bytes.fromhex(receipt[key]),lambda blob=blob:bytes.fromhex(sha(blob)))
        general={}
        for name,(size,digest) in GENERAL.items():
            general[name]=decode_lz(data(name)) if 'Tiles_' in name else data(name)
            compare(name+':preserved',struct.pack('<I',size)+bytes.fromhex(digest),
                    lambda name=name:struct.pack('<I',len(general[name]))+bytes.fromhex(sha(general[name])))
        # These are genuine SF-owned old groups; opaque unused groups stay hash-only.
        for index,entry in owned.items():
            i=int(index)
            compare('owned_record_'+index,bytes.fromhex(entry['metatile']+entry['attribute']),
                    lambda i=i:records[i*16:(i+1)*16]+attrs[i*2:(i+1)*2])
        for suffix,secondary in (('General',0),('Petalburg',1)):
            header=data('gTileset_'+suffix,24)
            compare(suffix+':header',struct.pack('<BB2x5I',1,secondary,
                    *(address(p+suffix) for p in ('gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_')),
                    address('InitTilesetAnim_'+suffix)|1),lambda header=header:header)
        # The pinned MapLayout is24 bytes. The next bytes belong to the next
        # map's border; Emerald does not store border dimensions in this struct.
        layout=data('LittlerootTown_Layout',24)
        compare('layout_binding',struct.pack('<ii4I',32,32,address('LittlerootTown_Layout_Border'),
                address('LittlerootTown_Layout_Blockdata'),address('gTileset_General'),address('gTileset_Petalburg')),lambda:layout)
        border=data('LittlerootTown_Layout_Border',8)
        compare('native_border',bytes.fromhex('d401d501dc01dd01'),lambda:border)
        oldwords=struct.unpack('<1024H',frozen['sunset-map.bin'])
        active={w&1023 for w in oldwords}|set(struct.unpack('<4H',border))|{572,573,574,575}
        banks=set()
        for i in active:
            oldrecord=(general['gMetatiles_General'][i*16:(i+1)*16] if i<512 else records[(i-512)*16:(i-511)*16])
            if i>=512:require(str(i-512) in owned,'Active old group is not an owned baseline group.')
            banks|={w>>12 for w in struct.unpack('<8H',oldrecord)}
        compare('old_active_banks_avoid8_9',b'\0',lambda:bytes([bool(banks&{8,9})]))
        source=assets['assets/tiles/connected-frontage-v3/block.indices']
        palette=assets['assets/tiles/connected-frontage-v3/block.gbapal']
        with Image.open(root/'assets/tiles/connected-frontage-v3/native.png') as image:
            require((image.mode,image.size,image.info.get('transparency'),image.tobytes())==('P',(176,80),0,source),
                    'Accepted native source PNG and indices differ.')
        gray=assets['assets/tiles/south-park-paving-v1/paving.gbapal']
        compare('homes_palette8',palette,lambda:palettes[256:288]);compare('gray_palette9',gray,lambda:palettes[288:320])
        master=assets['assets/tiles/south-park-paving-v1/master8.indices']
        paving=bytes(master[(y%8)*8+x%8] for y in range(16) for x in range(16))
        patterns={bytes(32),bytes(master[i]|master[i+1]<<4 for i in range(0,64,2))}
        def expected_cell(col,row):
            return b''.join(source[(row*16+y)*176+col*16:(row*16+y)*176+col*16+16] for y in range(16))
        for first,start in ((194,0),(206,5)):
            for row in range(4):
                for col in range(3):
                    i=first+row*3+col;expected=expected_cell(start+col,row)
                    compare('home_pixels_'+str(i),expected,lambda i=i:cell_pixels(raw,
                            struct.unpack_from('<4H',records,i*16+8),secondary=True,bank=8))
                    for q in range(4):
                        p=bytes(expected[(q//2*8+y)*16+q%2*8+x] for y in range(8) for x in range(8))
                        patterns.add(bytes(p[k]|p[k+1]<<4 for k in range(0,64,2)))
        for row in range(4):
            for col in range(3):
                i=218+row*3+col;original=struct.unpack_from('<4H',records,(194+row*3+2-col)*16+8)
                compare('mirrored_quadrants_'+str(i),struct.pack('<4H',*(original[q]^0x400 for q in (1,0,3,2))),
                        lambda i=i:records[i*16+8:(i+1)*16])
                expected=expected_cell(2-col,row)
                expected=b''.join(expected[y*16:(y+1)*16][::-1] for y in range(16))
                compare('home_pixels_'+str(i),expected,lambda i=i:cell_pixels(raw,
                        struct.unpack_from('<4H',records,i*16+8),secondary=True,bank=8))
        ground=records[230*16:230*16+8]
        for i in range(194,230):compare('gray_underlay_'+str(i),ground,lambda i=i:records[i*16:i*16+8])
        compare('new37_layer_roles',struct.pack('<37H',*(([0]*9+[0x1000]*3)*3+[0x1000])),lambda:attrs[194*2:])
        compare('paving_pixels',paving,lambda:cell_pixels(raw,struct.unpack_from('<4H',records,230*16),secondary=True,bank=9))
        compare('paving_transparent_overlay',bytes(256),lambda:cell_pixels(raw,
                struct.unpack_from('<4H',records,230*16+8),secondary=True,bank=8))
        patterns-={frozen['secondary.4bpp'][i*32:(i+1)*32] for i in range(401) if i not in range(240,248)}
        require(len(patterns)==90,'Independent two-home plus blank and gray tile count changed.')
        actual=[raw[i*32:(i+1)*32] for i in range(401,491)]
        compare('exact90_new_patterns',b''.join(sorted(patterns)),lambda:b''.join(sorted(actual)))
        compare('unused_tail_and_door_cache_zero',bytes(21*32),lambda:raw[491*32:])
        newrefs=struct.unpack('<296H',records[194*16:])
        require(all((w&1023)<512 or 512<=w&1023<1016 and not 752<=w&1023<760 for w in newrefs),
                'New static reference reaches animated waves or door cache.')
        expected=bytearray(frozen['sunset-map.bin']);cells=density_cells()
        for (x,y),(record,solid) in cells.items():struct.pack_into('<H',expected,(y*32+x)*2,record|(0xC00 if solid else 0x3000))
        blocks=data('LittlerootTown_Layout_Blockdata',2048)
        compare('all1024_map_words',bytes(expected),lambda:blocks)
        observed=struct.unpack('<1024H',blocks)
        counts=(sum(a!=b for a,b in zip(oldwords,observed)),sum(not(a&0xC00) and bool(b&0xC00) for a,b in zip(oldwords,observed)),
                sum(bool(a&0xC00) and not(b&0xC00) for a,b in zip(oldwords,observed)))
        compare('exact_map_delta',struct.pack('<3I',45,36,0),lambda:struct.pack('<3I',*counts))
        for name,size,digest in (('sSFCoastalWaves',768,'c3f8350cb8074a8706f08c358da6974808ad1cf1fad6cd3e0c9d498b637dbaac'),
                                 ('sSFDoorTiles',768,'a3767e2ace6ae9f85f47e56103a04522855b842b33d0b71f7382d5b81d77c680')):
            compare(name+':preserved',bytes.fromhex(digest),lambda name=name,size=size:bytes.fromhex(sha(data(name,size))))
        compare('door_palette10',bytes([10])*8,lambda:data('sSFDoorPalettes',8))
        table=data('sDoorAnimGraphicsTable');entries=[table[i:i+12] for i in range(0,len(table)-11,12)
                                                   if struct.unpack_from('<H',table,i)[0]==635]
        compare('native_apartment_door_binding',struct.pack('<HBBII',635,0,1,address('sSFDoorTiles'),address('sSFDoorPalettes')),
                lambda:b''.join(entries))
        initializer=data('InitTilesetAnim_Petalburg')
        compare('coast_initializer_shape',bytes.fromhex('04490020088004493020088003490448086070473a0f00033c0f0003440f0003'),
                lambda:initializer[:32])
        compare('coast_callback_binding',struct.pack('<I',address('TilesetAnim_SFCoast')|1),lambda:initializer[32:36])
        coast=data('TilesetAnim_SFCoast')
        compare('coast_function_allocations',struct.pack('<2I',36,44),lambda:struct.pack('<2I',len(initializer),len(coast)))
        compare('coast_cadence_and_copy_shape',bytes.fromhex('00b50104f02000030840002808d1080d00020449401804498022520001bc0047'),
                lambda:coast[:28]+coast[32:36])
        compare('coast_wave_and_vram_literals',struct.pack('<II',address('sSFCoastalWaves'),0x06005E00),lambda:coast[36:44])
        hi,lo=struct.unpack_from('<HH',coast,28);displacement=((hi&0x7FF)<<12)|((lo&0x7FF)<<1)
        compare('coast_copy_call_encoding',struct.pack('<2H',0xF000,0xF800),lambda:struct.pack('<2H',hi&0xF800,lo&0xF800))
        if displacement&0x400000:displacement-=0x800000
        compare('coast_copy_call',struct.pack('<I',address('AppendTilesetAnimToBuffer')&~1),
                lambda:struct.pack('<I',(address('TilesetAnim_SFCoast')&~1)+32+displacement))
        result['counts']={'changed_map_words':counts[0],'new_solid_cells':counts[1],'freed_cells':counts[2],
                          'ground_cells':9,'secondary_tiles':512,'metatiles':231,'new_unique_tiles':90}
    except (OSError,ValueError,KeyError,TypeError,IndexError,struct.error) as error:errors.append(str(error))
    result.setdefault('counts',{}).update(matched=sum(row['passed'] for row in checks),total=len(checks))
    result['passed']=bool(checks) and all(row['passed'] for row in checks) and not errors
    return result
