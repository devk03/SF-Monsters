"""Independent compiled South Park density extension of frozen v78.

The v78 resource prefixes, secondary resources and all palettes remain byte-exact. This gate does not establish art,
event-table, old-save, animation, campaign, browser, performance or human approval.
"""
import hashlib
import json
from pathlib import Path
import struct

BASE='assets/tiles/park-density-v1/baseline-v78'
PINNED={
    'primary-attributes.bin':(270,'d9ebf396a54b25e8c5d166bbc2eaf7f7c956358d68f3cbb8b03ce476ad0c8f8f'),
    'primary-metatiles.bin':(2160,'8dee2baaa7a90b48377a25e5e6601b8495ca9b2959c347e272fde2d7c998697a'),
    'primary-palettes.bin':(512,'a8f49d272a8e9acc542a81c8d34c4e50a17727bac85fc27a322c51183c560f4e'),
    'primary.4bpp':(14368,'f5613d0ba1d03a19cadefe8e8ced3f17f9bfa2a4a17a14331a016267f75e3467'),
    'receipt.json':(1685,'81a2b0958f398343653e1fdcffe1c1a422a964aa3e089fa61997d25dbfad80e9'),
    'secondary-attributes.bin':(300,'5d75b62c2517473238cfe7967401f492d506a41ffbbd5de58ea9c99ad39eab2f'),
    'secondary-metatiles.bin':(2400,'2edd2a730271e51d6590e6d6d8bd11a2f04d7fbd0f9759a5db833bc1cf7942e4'),
    'secondary-palettes.bin':(512,'53d2f51e1a11b857492336f599d186c147e32a89ddcfa6c6c8eab5cfbc4d60ad'),
    'secondary.4bpp':(15232,'1a50e9f7ef57a68cd10e39f18dd8e9956f0dea7b1cad04aac504f2cd76f7d95a'),
    'source-plan.json':(5584,'896aeaf6e7135dbf3212c3a16d883e463b493eae4eb55f32486d3682c4573119'),
    'south-park-map.bin':(2560,'5dedf3f48b650fe1eb007f3f70efd210c64105fb631bb8055517f8a39a0c5782'),
}
# Each tuple names x,y, literal ordered source columns from the accepted11-wide
# connected kit, and whether to clear the old fifth wall row to paving.
PARCELS=((1,1,(135,136,137,138),4,True),(1,12,(135,136,137,138),4,True),
         (1,20,(135,136,137,138),4,True),(10,13,(135,136,137,138),4,False),
         (10,20,(135,136,137,138),4,False),(25,11,(65,66,67,70,71,72,73,74,75),11,False))
ASSET='assets/tiles/compact-townhouses-v1'
SOURCE={
    'conversion.json':(931,'e06204a4ac86881018231054447dde2bf49d73f225a39930f84e66df74355e01'),
    'native.png':(1029,'ace5aca5c0bcd96de348546da3b67ab0bcbfe31765afca91a344bfc79fff3ec5'),
    'pair.gbapal':(32,'2c4864885ac0b05ef38c629d7e700df61c3a81e88633edf19604b534e7cc65bf'),
    'pair.indices':(4096,'51edd02604c50fa9b7b2dde4a295ec61ea131eb9e7157a6e8c682d0259180876'),
    'prompt.md':(1857,'327467aeb1666dd7d9079e7eeb7c26efcff5afd109434633ebbba2a01da9eeab'),
    'source.png':(869209,'36454f2dabbbfad1c40876c2532830f950e6e1be28b288bbbab3e5d46cb26568'),
}
RESOURCES={
    'primary.4bpp':('gTilesetTiles_SFParkFrontage',True),
    'primary-metatiles.bin':('gMetatiles_SFParkFrontage',False),
    'primary-attributes.bin':('gMetatileAttributes_SFParkFrontage',False),
    'primary-palettes.bin':('gTilesetPalettes_SFParkFrontage',False),
    'secondary.4bpp':('gTilesetTiles_SFSouthPark',True),
    'secondary-metatiles.bin':('gMetatiles_SFSouthPark',False),
    'secondary-attributes.bin':('gMetatileAttributes_SFSouthPark',False),
    'secondary-palettes.bin':('gTilesetPalettes_SFSouthPark',False),
}


def sha(blob):return hashlib.sha256(blob).hexdigest()


def parcel_cells():
    """Independent declared projection for subsequent gated compatibility checks."""
    cells={}
    for left,top,columns,stride,clear_front in PARCELS:
        for row in range(4):
            for col,source in enumerate(columns):
                point=(left+col,top+row)
                if point in cells:raise ValueError('Density parcels overlap.')
                cells[point]=(source+row*stride,True)
        if clear_front:
            for col in range(len(columns)):
                point=(left+col,top+4)
                if point in cells:raise ValueError('Density ground overlaps another parcel.')
                cells[point]=(531,False)
    return cells


def audit_density(rom,elf,root):
    from check_creature_resources import Cartridge,decode_lz
    from connected_frontage_audit import cell_pixels
    from PIL import Image
    checks,hashes,errors=[],{},[]
    result={'passed':False,'checks':checks,'hashes':hashes,'errors':errors,
            'quality_approval':'pending','scope':__doc__}
    def source(path):
        blob=path.read_bytes();hashes[str(path)]=sha(blob);return blob
    def compare(name,expected,observe):
        row={'name':name,'passed':False,'expected_bytes':len(expected),'expected_sha256':sha(expected)}
        try:
            actual=observe();row.update(passed=actual==expected,actual_bytes=len(actual),actual_sha256=sha(actual))
        except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
            row['error']=str(error);errors.append(name+': '+str(error))
        checks.append(row)
    try:
        root=Path(root);source(Path(__file__))
        source(Path(__file__).parents[1]/'quality/check_creature_resources.py')
        frozen={}
        for name,(size,digest) in PINNED.items():
            blob=source(root/BASE/name)
            if len(blob)!=size or sha(blob)!=digest:raise ValueError('Frozen original v78 resource differs: '+name)
            frozen[name]=blob
        assets={}
        for name,(size,digest) in SOURCE.items():
            blob=source(root/ASSET/name)
            if len(blob)!=size or sha(blob)!=digest:raise ValueError('Pinned compact source differs: '+name)
            assets[name]=blob
        info=json.loads(assets['conversion.json'])
        reference=source(root/'assets/tiles/connected-frontage-v3/native.png')
        if sha(reference)!='bad3ee2d2370fef7279cdc6defc42f85e2cf2199093e41a1db4932bbbeb9a791' or \
                (info['source_size'],info['source_bounds'],info['native_size'])!=([1254,1254],[137,166,1117,1058],[64,64]) or \
                info['source_sha256']!=sha(assets['source.png']) or info['prompt_sha256']!=sha(assets['prompt.md']) or \
                info['reference_sha256']!=sha(reference) or \
                info['files']!={name:sha(assets[name]) for name in ('native.png','pair.indices','pair.gbapal')}:
            raise ValueError('Compact source provenance or geometry differs.')
        palette=assets['pair.gbapal']
        if palette!=frozen['primary-palettes.bin'][160:192]:raise ValueError('Compact pair must retain curated bank5.')
        colors=[tuple((word>>(5*c))&31 for c in range(3)) for word in struct.unpack('<16H',palette)]
        with Image.open(root/ASSET/'source.png') as image:
            if image.size!=(1254,1254):raise ValueError('Compact source dimensions differ.')
            sample=image.convert('RGBA').crop((137,166,1117,1058)).resize((64,64),Image.Resampling.NEAREST)
            derived=bytes(0 if rgba[3]<128 else min(range(1,16),key=lambda i:
                sum((round(rgba[c]*31/255)-colors[i][c])**2 for c in range(3))) for rgba in sample.get_flattened_data())
        compare('compact_source_pixels',assets['pair.indices'],lambda:derived)
        with Image.open(root/ASSET/'native.png') as image:
            if (image.mode,image.size,image.info.get('transparency'),image.tobytes(),image.getpalette()[:48])!=(
                    'P',(64,64),0,assets['pair.indices'],[c*255//31 for rgb in colors for c in rgb]):
                raise ValueError('Compact native PNG/index/palette differ.')
        receipt=json.loads(frozen['receipt.json'])
        if receipt['target_sha256']!='46d971f88b9345fd36cfba76cb9d1bc528b27bb03d5b7dbb8d529a7d1a45e943' or \
                receipt['files']!={name:{'bytes':size,'sha256':digest} for name,(size,digest) in PINNED.items() if name!='receipt.json'}:
            raise ValueError('Frozen v78 receipt identities differ.')
        cart=Cartridge(rom,elf);hashes.update(rom=sha(cart.rom),elf=sha(cart.elf))
        for name,(symbol,compressed) in RESOURCES.items():
            def observed(symbol=symbol,compressed=compressed):
                blob=cart.data(symbol);return decode_lz(blob) if compressed else blob
            if name in ('primary.4bpp','primary-metatiles.bin','primary-attributes.bin'):
                compare(name+':v78_prefix',frozen[name],lambda observed=observed,name=name:observed()[:len(frozen[name])])
            else:compare(name+':byte_exact',frozen[name],observed)
        primary=decode_lz(cart.data('gTilesetTiles_SFParkFrontage'))
        records=cart.data('gMetatiles_SFParkFrontage');attributes=cart.data('gMetatileAttributes_SFParkFrontage')
        compare('primary_allocations',struct.pack('<3I',511*32,151*16,151*2),
                lambda:struct.pack('<3I',len(primary),len(records),len(attributes)))
        compare('blank_primary_tile0',bytes(32),lambda:primary[:32])
        secondary=decode_lz(cart.data('gTilesetTiles_SFSouthPark'))
        secondary_records=cart.data('gMetatiles_SFSouthPark')
        if not 0<len(primary)<=512*32 or len(primary)%32 or not 0<len(secondary)<=504*32 or len(secondary)%32:
            raise ValueError('Native tile allocations enter reserved door cache.')
        if any((word&1023)>=1016 for word in struct.unpack('<1200H',secondary_records)):
            raise ValueError('Secondary words enter reserved door cache.')
        paving=cell_pixels(frozen['secondary.4bpp'],struct.unpack_from('<4H',frozen['secondary-metatiles.bin'],19*16+8),secondary=True,bank=4)
        for index in range(135,151):
            compare('compact_underlay_%d'%index,paving,lambda index=index:cell_pixels(secondary,
                struct.unpack_from('<4H',records,index*16),secondary=True,bank=4))
        expected_attrs=frozen['primary-attributes.bin']+struct.pack('<16H',*([0]*12+[0x1000]*4))
        compare('all151_primary_attributes',expected_attrs,lambda:attributes)
        def compact_pixels():
            pixels=bytearray(4096)
            for i in range(16):
                cell=cell_pixels(primary,struct.unpack_from('<4H',records,(135+i)*16+8),bank=5)
                for y in range(16):
                    at=(i//4*16+y)*64+(i%4)*16;pixels[at:at+16]=cell[y*16:y*16+16]
            return bytes(pixels)
        compare('compact_native_pixels',assets['pair.indices'],compact_pixels)
        for suffix,secondary in (('SFParkFrontage',0),('SFSouthPark',1)):
            expected=struct.pack('<BB2x5I',1,secondary,*(cart.symbols[p+suffix][0] for p in (
                'gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_')),0)
            compare(suffix+':header',expected,lambda suffix=suffix:cart.data('gTileset_'+suffix))
        def layout():
            raw=cart.data('OldaleTown_Layout',24)
            width,height,border,blocks,primary,secondary=struct.unpack('<ii4I',raw)
            if cart.symbols['OldaleTown_Layout'][1] not in (None,24) or \
                    (width,height,blocks,primary,secondary)!=(40,32,cart.symbols['OldaleTown_Layout_Blockdata'][0],
                     cart.symbols['gTileset_SFParkFrontage'][0],cart.symbols['gTileset_SFSouthPark'][0]) or border%2 or \
                    not 0x08000000<=border<=0x08000000+len(cart.rom)-8:
                raise ValueError('Density layout dimensions or native resource bindings differ.')
            return b'exact40x32-layout'
        compare('layout_binding',b'exact40x32-layout',layout)
        original=frozen['south-park-map.bin'];expected=bytearray(original);cells=parcel_cells()
        plan=json.loads(frozen['source-plan.json'])
        protected={(e['x'],e['y']) for key in ('npcs','warp_events','bg_events') for e in plan[key]}
        protected|={(x,y) for x in range(18,29) for y in range(2,7)}
        protected|={(x,y) for x in range(14,17) for y in range(13,17)}
        protected|={(13,6),(13,7),(32,6),(32,7),(21,6),(21,7),(16,17),(7,26)}
        protected|={(x,y) for y,row in enumerate(plan['rows']) for x,token in enumerate(row)
                    if token in 'R.GBT#uUQq'}
        if len(cells)!=128 or protected & cells.keys():
            raise ValueError('Density parcels overlap a protected home, park, road, furnishing, entry or event.')
        attrs=cart.data('gMetatileAttributes_SFParkFrontage')
        for (x,y),(record,solid) in cells.items():
            at=(y*40+x)*2
            struct.pack_into('<H',expected,at,(0xC00|record) if solid else (0x3000|record))
        def source_layers():
            for left,top,columns,stride,clear in PARCELS:
                for row in range(4):
                    for column in columns:
                        if struct.unpack_from('<H',attrs,(column+row*stride)*2)[0]!=(0 if row<3 else 0x1000):
                            raise ValueError('Reused architecture has the wrong native layer/behavior.')
            return b'normal-upper-three:covered-base'
        compare('reused_source_layer_roles',b'normal-upper-three:covered-base',source_layers)
        blocks=cart.data('OldaleTown_Layout_Blockdata',2560)
        compare('all1280_map_words',bytes(expected),lambda:blocks)
        compare('all1280_collision_elevation',bytes(b&0xFC for b in expected[1::2]),
                lambda:bytes(b&0xFC for b in blocks[1::2]))
        before=list(struct.unpack('<1280H',original));after=list(struct.unpack('<1280H',blocks))
        def summary():
            changed=sum(a!=b for a,b in zip(before,after))
            upper=sum((a&0xFC00)!=(b&0xFC00) for a,b in zip(before,after))
            solid=sum(not(a&0xC00) and bool(b&0xC00) for a,b in zip(before,after))
            freed=sum(bool(a&0xC00) and not(b&0xC00) for a,b in zip(before,after))
            primary=sum((word&1023)<512 for word in after)
            return struct.pack('<5I',changed,upper,solid,freed,primary)
        compare('exact_density_delta',struct.pack('<5I',125,65,56,9,189),summary)
        expected_primary={i for i,(word,) in enumerate(struct.iter_unpack('<H',expected)) if (word&1023)<512}
        def footprint():
            if {i for i,word in enumerate(after) if (word&1023)<512}!=expected_primary:
                raise ValueError('Density primary footprint differs from the189 declared cells.')
            return b'exact189-primary-cells'
        compare('primary_map_footprint',b'exact189-primary-cells',footprint)
        result['counts']={'declared_cells':128,'wall_cells':116,'ground_cells':12,'changed_map_words':125,
                          'collision_changes':65,'new_solid_cells':56,'freed_cells':9,'primary_map_cells':189,
                          'primary_tiles':511,'secondary_tiles':476}
    except (OSError,ValueError,KeyError,TypeError,struct.error) as error:
        errors.append(str(error));checks.append({'name':'audit_inputs','passed':False,'error':str(error)})
    result.setdefault('counts',{});result['counts'].update(total=len(checks),matched=sum(row['passed'] for row in checks))
    result['passed']=bool(checks) and all(row['passed'] for row in checks) and not errors
    return result
