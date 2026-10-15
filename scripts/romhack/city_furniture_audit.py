"""Independent compiled city-furniture extension of frozen v77 resources.

No art, recovery, animation, save, campaign, browser, performance or human
approval is established. Native source conversion and producers are not imported.
"""
import hashlib
import json
from pathlib import Path
import struct
from connected_frontage_audit import cell_pixels

ASSET='assets/tiles/city-furniture-v1'
SOURCE={
    'bench.indices':(512,'a025d84bc36af2a5db2127b8f42861c81d8247c03557721cca81ff5be71598c4'),
    'bench.png':(270,'4779bd4ebc38b8c21c6d14493f87401ba93402275e831c3b855d91413d7977c2'),
    'bin.indices':(256,'a9b58d23f38cb202481efecec82361983be4d5d7dc7d1d25f6010e6ff16e22a7'),
    'bin.png':(220,'800e300aaa71110a6fb426fcb68acdb4e28e71aef3309ff07c3c5440daa44d3c'),
    'conversion.json':(3359,'70882aa2caf7c32b8140ffe50ffa40252b34a1a294e5eaf183c7958187bfa723'),
    'furniture.gbapal':(32,'2c4864885ac0b05ef38c629d7e700df61c3a81e88633edf19604b534e7cc65bf'),
    'hydrant.indices':(256,'c1a0dd4a44054d9a290417feea0477e380db43d74324d2e9c6d45c46b97702dd'),
    'hydrant.png':(234,'b1f5abf7d10b22e0b495664255e4354bfd25c4425976202ac1191f744766ea54'),
    'lamp.indices':(512,'4ba0cd683515cd62acce7929312edb139be5ec98350e054b386adeff85e04580'),
    'lamp.png':(236,'ce906ae98fb395f834cb46ed020ebb6692eaa9f4d4ceccebfd31d651fe9b95e9'),
    'meter.indices':(256,'1d6d352d943816f4754f234a594b60ac953e88caa20196e10abbf543578a68dd'),
    'meter.png':(216,'ff34c0539114e5bb830afd385a7982c67a2ea6314efd00d0cecd9643c2cd30ec'),
    'prompt.md':(2016,'7ae91082403a47b2682607337b98927ae3446f2512fda355e0705bc6e7f655b8'),
    'rack.indices':(512,'d75f4b3d9d152ab6769869d189eb142b90ec8de0e162412c2ac55aeef5d926eb'),
    'rack.png':(282,'d89ed0ffbe558c040f3eba89248b8bb51674f6519b56987c58c0a6c994e6f21f'),
    'recycling.indices':(512,'3a570f453a54e4c2996b65a6d13657c0f499bfa85da5a1a147560e1ac74b430d'),
    'recycling.png':(287,'7b34a210428742005656f6f5e50de5dbe189281401db57cd95a79d52b872b29a'),
    'source.png':(1167322,'e7c7a9289c8f904c8fd30245077cd9b352d590f4abe634c86c3197edfe91cc00'),
    'tree.indices':(1024,'dc75caed4cbad393fef6c45fd202db10900e4b5185c5fb8b3bc31b86a5648025'),
    'tree.png':(383,'93cd17e55a6ff83a823d0b9f3765cb50afd61c8d80da9954265dee1110c066dd'),
}
BASELINE={
    'attributes.bin':(240,'d45e0ca57b5f5e26297676e07bb86974a9673712f52c3c7bea72a32d66d0b45a'),
    'metatiles.bin':(1920,'08c7fa770909b88f17100bfaae71c15177ee89bf2453a8912fc0b5838a788221'),
    'palettes.gbapal':(512,'a8f49d272a8e9acc542a81c8d34c4e50a17727bac85fc27a322c51183c560f4e'),
    'primary.4bpp':(12640,'326d27bc217cdd3ba11f4de4d4d5880bb7d5c8b74f5f631443648b6a0826aa39'),
    'receipt.json':(967,'cfc2b2c79c4fd99ca63a0d0c58b98b12fb962bdd3bd3dd37ec478474ed592d4e'),
    'south-park-map.bin':(2560,'f8e7c473e0cf93447cb5c6be9bfdc8a465ff7a8d21cfc7cb1b57e78785fe3f80'),
}
# name, source bounds, native width/height, first appended metatile.
CARDS=(('lamp',(118,106,292,579),16,32,120),('meter',(533,390,619,578),16,16,122),
       ('hydrant',(897,414,1027,580),16,16,123),('bin',(1264,404,1394,578),16,16,124),
       ('rack',(43,804,353,966),32,16,125),('tree',(426,583,720,972),32,32,127),
       ('bench',(811,802,1110,974),32,16,131),('recycling',(1204,797,1477,974),32,16,133))
# Independent final layout: x,y, record, solid base. Never read producer placement constants.
CITY_CELLS=((17,6,120,False),(17,7,121,True),(36,6,120,False),(36,7,121,True),
            (19,7,122,True),(26,7,122,True),(11,7,123,True),(15,7,124,True),
            (23,7,125,True),(24,7,126,True),(37,6,127,False),(38,6,128,False),
            (37,7,129,True),(38,7,130,True),(18,11,131,True),(19,11,132,True),
            (34,11,133,True),(35,11,134,True))


def sha(blob):return hashlib.sha256(blob).hexdigest()


def audit_furniture(rom,elf,root):
    from check_creature_resources import Cartridge,decode_lz
    from PIL import Image
    checks,hashes,errors=[],{},[]
    result={'passed':False,'checks':checks,'hashes':hashes,'errors':errors,
            'quality_approval':'pending','scope':__doc__}
    def source(path):
        blob=path.read_bytes();hashes[str(path)]=sha(blob);return blob
    def pinned(directory,specification):
        blobs={}
        for name,(size,digest) in specification.items():
            blob=source(directory/name)
            if len(blob)!=size or sha(blob)!=digest:raise ValueError('Pinned original resource differs: '+str(directory/name))
            blobs[name]=blob
        return blobs
    def compare(name,expected,observe):
        row={'name':name,'passed':False,'expected_bytes':len(expected),'expected_sha256':sha(expected)}
        try:
            actual=observe();row.update(passed=actual==expected,actual_bytes=len(actual),actual_sha256=sha(actual))
        except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
            row['error']=str(error);errors.append(name+': '+str(error))
        checks.append(row)
    try:
        root=Path(root);source(Path(__file__));source(Path(__file__).with_name('connected_frontage_audit.py'))
        source(Path(__file__).parents[1]/'quality/check_creature_resources.py')
        assets=pinned(root/ASSET,SOURCE);baseline=pinned(root/ASSET/'baseline-v77',BASELINE)
        reference=source(root/'assets/tiles/connected-frontage-v3/native.png')
        if sha(reference)!='bad3ee2d2370fef7279cdc6defc42f85e2cf2199093e41a1db4932bbbeb9a791':
            raise ValueError('Original style reference differs.')
        info=json.loads(assets['conversion.json'])
        palette=assets['furniture.gbapal'];words=struct.unpack('<16H',palette)
        colors=[tuple((word>>(5*c))&31 for c in range(3)) for word in words]
        flat=[c*255//31 for rgb in colors for c in rgb]
        if info['source_sha256']!=sha(assets['source.png']) or info['prompt_sha256']!=sha(assets['prompt.md']) or \
                info['palette_sha256']!=sha(palette) or info['reference_sha256']!=sha(reference) or len(info['cards'])!=8:
            raise ValueError('Furniture provenance or card receipt differs.')
        pixels={}
        with Image.open(root/ASSET/'source.png') as original:
            if original.size!=(1536,1024):raise ValueError('Original furniture source geometry differs.')
            original=original.convert('RGBA')
            for number,(name,bounds,width,height,first) in enumerate(CARDS):
                receipt=info['cards'][number]
                if receipt!={'name':name,'bounds':list(bounds),'size':[width,height],
                    'indices_sha256':sha(assets[name+'.indices']),'png_sha256':sha(assets[name+'.png'])}:
                    raise ValueError('Furniture card geometry or serialized receipt differs: '+name)
                crop=original.crop(bounds)
                factor=min(width/crop.width,height/crop.height)
                scaled=(max(1,round(crop.width*factor)),max(1,round(crop.height*factor)))
                sample=crop.resize(scaled,Image.Resampling.NEAREST)
                derived=bytearray(width*height)
                # Preserve exact source alpha and bottom-center placement.
                for y in range(scaled[1]):
                    for x in range(scaled[0]):
                        rgba=sample.getpixel((x,y))
                        if rgba[3]>=128:
                            rgb=tuple(round(c*31/255) for c in rgba[:3])
                            derived[(height-scaled[1]+y)*width+(width-scaled[0])//2+x]=min(range(1,16),
                                key=lambda i:sum((rgb[c]-colors[i][c])**2 for c in range(3)))
                pixels[name]=assets[name+'.indices']
                compare(name+':source_pixels',pixels[name],lambda derived=derived:bytes(derived))
                with Image.open(root/ASSET/(name+'.png')) as preview:
                    if (preview.mode,preview.size,preview.info.get('transparency'),preview.getpalette()[:48],preview.tobytes()) != (
                            'P',(width,height),0,flat,pixels[name]):
                        raise ValueError('Furniture preview/index/palette differs: '+name)

        cart=Cartridge(rom,elf);hashes.update(rom=sha(cart.rom),elf=sha(cart.elf))
        for suffix,secondary in (('SFParkFrontage',0),('SFSouthPark',1)):
            expected=struct.pack('<BB2x5I',1,secondary,*(cart.symbols[p+suffix][0] for p in (
                'gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_')),0)
            compare(suffix+':header',expected,lambda suffix=suffix:cart.data('gTileset_'+suffix))
        def layout():
            value=cart.data('OldaleTown_Layout',24)
            width,height,border,blocks,primary,secondary=struct.unpack('<ii4I',value)
            if (width,height,blocks,primary,secondary)!=(40,32,cart.symbols['OldaleTown_Layout_Blockdata'][0],
                    cart.symbols['gTileset_SFParkFrontage'][0],cart.symbols['gTileset_SFSouthPark'][0]) or border%2 or \
                    not 0x08000000<=border<=0x08000000+len(cart.rom)-8:
                raise ValueError('City layout geometry or native pointers differ.')
            return b'exact40x32-layout'
        compare('layout_binding',b'exact40x32-layout',layout)
        raw=decode_lz(cart.data('gTilesetTiles_SFParkFrontage'))
        records=cart.data('gMetatiles_SFParkFrontage');attrs=cart.data('gMetatileAttributes_SFParkFrontage')
        palettes=cart.data('gTilesetPalettes_SFParkFrontage')
        compare('primary_allocations',struct.pack('<4I',449*32,135*16,135*2,512),
                lambda:struct.pack('<4I',len(raw),len(records),len(attrs),len(palettes)))
        compare('original395_tile_prefix',baseline['primary.4bpp'],lambda:raw[:395*32])
        compare('original120_record_prefix',baseline['metatiles.bin'],lambda:records[:120*16])
        compare('original120_attribute_prefix',baseline['attributes.bin'],lambda:attrs[:120*2])
        compare('complete_primary_palette',baseline['palettes.gbapal'],lambda:palettes)
        if palettes[160:192]!=palette:raise ValueError('Furniture does not use the unchanged curated bank5.')
        compare('blank_primary_tile0',bytes(32),lambda:raw[:32])
        secondary=decode_lz(cart.data('gTilesetTiles_SFSouthPark'));secondary_records=cart.data('gMetatiles_SFSouthPark')
        if not 0<len(secondary)<=504*32 or len(secondary)%32 or len(secondary_records)!=150*16:
            raise ValueError('Secondary residency/table leaves its reviewed bound.')
        if any((word&1023)>=1016 for word in struct.unpack('<1200H',secondary_records)):
            raise ValueError('Secondary words reference reserved door cache.')
        frozen_palette=source(root/'assets/tiles/connected-frontage-v3/baseline-v76/secondary-palettes.gbapal')
        if len(frozen_palette)!=512 or sha(frozen_palette)!='73e3ba1b6d1f0a9385e97e92eba6a4a2d1268384e4cdf6f45f452a49fda512db':
            raise ValueError('Frozen secondary palette differs.')
        expected_secondary_palette=bytearray(frozen_palette);expected_secondary_palette[256:320]=palette*2
        compare('complete_secondary_palette',bytes(expected_secondary_palette),lambda:cart.data('gTilesetPalettes_SFSouthPark'))
        paving=source(root/'assets/tiles/south-park-paving-v1/paving.indices')
        if len(paving)!=256 or sha(paving)!='36d87ab45a3526bad751c51b330e8b66baf9f13f53d20fd32c191be678be9b96':
            raise ValueError('Original paving pixels differ.')
        compare('secondary19_paving',paving,lambda:cell_pixels(secondary,
            struct.unpack_from('<4H',secondary_records,19*16+8),secondary=True,bank=4))
        for index in range(135):
            compare('underlay_%03d'%index,paving,lambda index=index:cell_pixels(secondary,
                struct.unpack_from('<4H',records,index*16),secondary=True,bank=4))
        expected_attrs=bytearray(baseline['attributes.bin'])
        for name,bounds,width,height,first in CARDS:
            for row in range(height//16):
                expected_attrs.extend(struct.pack('<H',0x1000 if row==height//16-1 else 0)*(width//16))
            def decoded(name=name,width=width,height=height,first=first):
                result=bytearray(width*height)
                for index in range(width*height//256):
                    cell=cell_pixels(raw,struct.unpack_from('<4H',records,(first+index)*16+8),bank=5)
                    for y in range(16):
                        at=(index//(width//16)*16+y)*width+(index%(width//16))*16
                        result[at:at+16]=cell[y*16:y*16+16]
                return bytes(result)
            compare(name+':native_pixels',pixels[name],decoded)
        compare('all135_layer_attributes',bytes(expected_attrs),lambda:attrs)
        blocks=cart.data('OldaleTown_Layout_Blockdata',2560);expected=bytearray(baseline['south-park-map.bin'])
        for x,y,record,solid in CITY_CELLS:
            at=(y*40+x)*2
            if struct.unpack_from('<H',expected,at)[0]!=0x3213:
                raise ValueError('Furniture baseline cell is not an existing elevation3 sidewalk.')
            struct.pack_into('<H',expected,at,0x3000|record|(0xC00 if solid else 0))
        compare('all1280_map_words',bytes(expected),lambda:blocks)
        compare('all1280_collision_elevation',bytes(v&0xFC for v in expected[1::2]),
                lambda:bytes(v&0xFC for v in blocks[1::2]))
        expected_points={i for i,(word,) in enumerate(struct.iter_unpack('<H',expected)) if (word&1023)<512}
        def footprint():
            actual={i for i,(word,) in enumerate(struct.iter_unpack('<H',blocks)) if (word&1023)<512}
            if actual!=expected_points or len(actual)!=118:raise ValueError('Furniture requires exactly118 declared primary map cells.')
            return b'exact118-primary-cells'
        compare('primary_map_footprint',b'exact118-primary-cells',footprint)
        result['counts']={'new_records':15,'new_map_cells':18,'solid_bases':14,'walkable_upper_cells':4,
                          'primary_map_cells':118,'primary_tiles':len(raw)//32}
    except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
        errors.append(str(error));checks.append({'name':'audit_inputs','passed':False,'error':str(error)})
    result.setdefault('counts',{});result['counts'].update(total=len(checks),matched=sum(row['passed'] for row in checks))
    result['passed']=bool(checks) and all(row['passed'] for row in checks) and not errors
    return result
