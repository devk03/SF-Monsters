"""Independent compiled primary-frontage artwork, bindings and map-word audit."""
import hashlib
import json
from pathlib import Path
import struct

# Acceptance positions and banks are independent of the production placement table.
CARDS=(('brick',2,1,3,5,1,0),('sage',2,12,3,5,16,1),
       ('sandstone',2,20,3,5,31,2),('coffee',21,2,2,4,46,3))
SECONDARY={
    'gTilesetTiles_SFSouthPark':(16096,'1028cc530238a128ba379d2de5f8153cdbf2eb6c1054f67501f5e4900ce2b6c8'),
    'gMetatiles_SFSouthPark':(2400,'c5a357ba4d453bb0e856b09a594334303b50ead542ef7081b92a243a7269a0c8'),
    'gMetatileAttributes_SFSouthPark':(300,'5d75b62c2517473238cfe7967401f492d506a41ffbbd5de58ea9c99ad39eab2f'),
    'gTilesetPalettes_SFSouthPark':(512,'73e3ba1b6d1f0a9385e97e92eba6a4a2d1268384e4cdf6f45f452a49fda512db'),
}


def audit_infill(rom,elf,root):
    from check_creature_resources import Cartridge,decode_lz
    from PIL import Image

    checks,hashes,errors=[],{},[]
    result={'passed':False,'checks':checks,'hashes':hashes,'errors':errors,'quality_approval':'pending',
        'scope':'Compiled original primary frontage pixels/palettes/layers,53 solid map cells, '
                'layout/header bindings and byte-preserved v71 secondary resources. '
                'No art, animation, old-save recovery, campaign or performance approval.'}

    def source(path):
        data=path.read_bytes();hashes[str(path)]=hashlib.sha256(data).hexdigest();return data

    def compare(name,expected,read):
        row={'name':name,'passed':False,'expected_bytes':len(expected),
             'expected_sha256':hashlib.sha256(expected).hexdigest()}
        try:
            actual=read()
            row.update(passed=actual==expected,actual_bytes=len(actual),actual_sha256=hashlib.sha256(actual).hexdigest())
        except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
            row['error']=str(error);errors.append(name+': '+str(error))
        checks.append(row)

    try:
        hashes['rom']=hashlib.sha256(rom.read_bytes()).hexdigest()
        hashes['elf']=hashlib.sha256(elf.read_bytes()).hexdigest()
        source(Path(__file__));source(Path(__file__).parents[1]/'quality/check_creature_resources.py')
        cart=Cartridge(rom,elf)
        def data(name,length=None):return cart.data(name,length)
        def header(primary):
            suffix='SFParkFrontage' if primary else 'SFSouthPark'
            names=['gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_']
            return struct.pack('<BB2x5I',1,0 if primary else 1,
                *(cart.symbols[prefix+suffix][0] for prefix in names),0)
        for primary,name in [(True,'gTileset_SFParkFrontage'),(False,'gTileset_SFSouthPark')]:
            # Compute expected pointers within the check so missing symbols fail closed.
            def binding(primary=primary,name=name):
                expected=header(primary);actual=data(name)
                if actual!=expected:raise ValueError('Tileset compression, role, resource pointers or NULL callback differs.')
                return b'exact-native24-byte-tileset'
            compare(name+':binding',b'exact-native24-byte-tileset',binding)

        def layout():
            if cart.symbols['OldaleTown_Layout'][1] not in (None,24):
                raise ValueError('MapLayout must keep its native24-byte ABI.')
            value=data('OldaleTown_Layout',24)
            width,height,border,blocks,primary,secondary=struct.unpack('<ii4I',value)
            if (width,height,blocks,primary,secondary)!=(40,32,
                cart.symbols['OldaleTown_Layout_Blockdata'][0],
                cart.symbols['gTileset_SFParkFrontage'][0],cart.symbols['gTileset_SFSouthPark'][0]) or \
                border%2 or not 0x08000000<=border<=0x08000000+len(cart.rom)-8:
                raise ValueError('South Park dimensions, blockdata or primary/secondary layout binding differs.')
            return b'40x32:original-primary:preserved-secondary'
        compare('layout_binding',b'40x32:original-primary:preserved-secondary',layout)

        for name,(length,digest) in SECONDARY.items():
            def preserved(name=name,length=length):
                raw=data(name);return decode_lz(raw) if name=='gTilesetTiles_SFSouthPark' else raw
            row={'name':name+':preserved','passed':False,'expected_bytes':length,'expected_sha256':digest}
            try:
                actual=preserved();row.update(passed=len(actual)==length and hashlib.sha256(actual).hexdigest()==digest,
                    actual_bytes=len(actual),actual_sha256=hashlib.sha256(actual).hexdigest())
            except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
                row['error']=str(error);errors.append(name+': '+str(error))
            checks.append(row)

        raw=decode_lz(data('gTilesetTiles_SFParkFrontage'))
        records=data('gMetatiles_SFParkFrontage');attrs=data('gMetatileAttributes_SFParkFrontage')
        palettes=data('gTilesetPalettes_SFParkFrontage')
        compare('primary_allocations',struct.pack('<4I',213*32,54*16,54*2,512),
                lambda:struct.pack('<4I',len(raw),len(records),len(attrs),len(palettes)))
        compare('transparent_primary_tile0',bytes(32),lambda:raw[:32])
        secondary_records=data('gMetatiles_SFSouthPark')
        sidewalk=secondary_records[19*16+8:20*16]
        if len(sidewalk)!=8 or any(w>>12!=6 or not 512<=(w&1023)<1016 for w in struct.unpack('<4H',sidewalk)):
            raise ValueError('Facade underlay must use resident secondary sidewalk, never door VRAM.')
        compare('all54_secondary_underlays',sidewalk*54,
                lambda:b''.join(records[i*16:i*16+8] for i in range(54)))
        compare('primary_empty_metatile0',sidewalk+bytes(8),lambda:records[:16])
        expected_attrs=[0x1000]+[0]*53
        for name,left,top,width,height,first,bank in CARDS:
            for index in range(width*height):
                expected_attrs[first+index]=0x1000 if index//width==height-1 else 0
        compare('all54_layer_attributes',struct.pack('<54H',*expected_attrs),lambda:attrs)

        directory=root/'assets/tiles/south-park-frontage-v1'
        info=json.loads(source(directory/'conversion.json'))
        if hashlib.sha256(source(directory/'source.png')).hexdigest()!=info['source_sha256'] or \
           hashlib.sha256(source(directory/'prompt.md')).hexdigest()!=info['prompt_sha256'] or \
           info.get('alpha_threshold')!=128 or len(info['cards'])!=4:
            raise ValueError('Original frontage source/prompt contract changed.')
        expected_palettes=bytearray(512)
        for number,(name,left,top,width,height,first,bank) in enumerate(CARDS):
            card=info['cards'][number]
            if (card['name'],card['size'],card['bank'])!=(name,[width*16,height*16],bank) or \
               set(card['files'])!={name+s for s in ('.png','.indices','.gbapal')}:
                raise ValueError('Original card identity, dimensions, bank or source receipt differs.')
            for filename,expected in card['files'].items():
                if hashlib.sha256(source(directory/filename)).hexdigest()!=expected:
                    raise ValueError('Original card file differs: '+filename)
            with Image.open(directory/(name+'.png')) as image:
                if image.mode!='P' or image.size!=(width*16,height*16) or image.info.get('transparency')!=0:
                    raise ValueError('Original card must retain native indexed dimensions and transparent0.')
                expected_pixels=image.tobytes();flat=image.getpalette()[:48]
            palette=(directory/(name+'.gbapal')).read_bytes()
            if len(palette)!=32 or max(expected_pixels)>15 or \
               expected_pixels!=(directory/(name+'.indices')).read_bytes():
                raise ValueError('PNG and serialized card pixels/palette dimensions disagree.')
            words=struct.unpack('<16H',palette)
            if words[0] or any(w>0x7fff for w in words) or flat!=[
                ((w>>(5*c))&31)*255//31 for w in words for c in range(3)]:
                raise ValueError('Card palette must match its PNG and native RGB555 bank.')
            expected_palettes[bank*32:(bank+1)*32]=palette

            def decoded(first=first,width=width,height=height,bank=bank):
                pixels=bytearray(width*height*256)
                for cell in range(width*height):
                    at=(first+cell)*16
                    if len(records[at:at+16])!=16:raise ValueError('Truncated original primary metatile.')
                    for q,word in enumerate(struct.unpack_from('<4H',records,at+8)):
                        tile=word&1023
                        if word>>12!=bank or tile>=213 or (tile+1)*32>len(raw):
                            raise ValueError('Primary foreground uses the wrong bank or leaves213 resident tiles.')
                        for y in range(8):
                            for x in range(8):
                                xx=7-x if word&0x400 else x;yy=7-y if word&0x800 else y
                                value=raw[tile*32+yy*4+xx//2]>>(4*(xx%2))&15
                                px=cell%width*16+q%2*8+x;py=cell//width*16+q//2*8+y
                                pixels[py*width*16+px]=value
                return bytes(pixels)
            compare(name+':all_native_pixels',expected_pixels,decoded)
            expected_map=struct.pack('<'+'H'*(width*height),*(0xC00+first+i for i in range(width*height)))
            def map_cells(left=left,top=top,width=width,height=height):
                blocks=data('OldaleTown_Layout_Blockdata',40*32*2)
                return b''.join(blocks[((top+y)*40+left+x)*2:((top+y)*40+left+x)*2+2]
                                for y in range(height) for x in range(width))
            compare(name+':solid_map_cells',expected_map,map_cells)
        compare('all_primary_palette_bytes',bytes(expected_palettes),lambda:palettes)

        def primary_footprint():
            blocks=data('OldaleTown_Layout_Blockdata',40*32*2)
            points={(left+x,top+y) for name,left,top,width,height,first,bank in CARDS
                    for y in range(height) for x in range(width)}
            actual={(i%40,i//40) for i,(word,) in enumerate(struct.iter_unpack('<H',blocks)) if (word&1023)<512}
            if actual!=points or len(points)!=53:
                raise ValueError('Only the53 declared map cells may reference primary metatiles.')
            return b'exact53-cell-primary-footprint'
        compare('primary_map_footprint',b'exact53-cell-primary-footprint',primary_footprint)
        def reservation():
            secondary=decode_lz(data('gTilesetTiles_SFSouthPark'))
            if len(secondary)!=503*32 or any((word&1023)>=1016 for word in struct.unpack('<1200H',secondary_records)):
                raise ValueError('Secondary art overlaps the eight native door-animation tiles.')
            return b'primary213:secondary503:door1016..1023-reserved'
        compare('resident_door_reservation',b'primary213:secondary503:door1016..1023-reserved',reservation)
    except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
        errors.append(str(error));checks.append({'name':'audit_inputs','passed':False,'error':str(error)})
    result['counts']={'total':len(checks),'matched':sum(c['passed'] for c in checks)}
    result['passed']=bool(checks) and all(c['passed'] for c in checks) and not errors
    return result
