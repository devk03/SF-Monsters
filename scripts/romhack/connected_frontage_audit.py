"""Independent compiled connected frontage resources and exact map-delta audit.

This does not approve artwork, service/door resources, animations, events, saves,
campaign behavior or performance. It never imports the production converter.
"""
import hashlib
import json
from pathlib import Path
import struct


ASSET = 'assets/tiles/connected-frontage-v3'
SIZE = (176, 80)
COLORS = ((0,0,0), (5,7,10), (12,13,16), (17,17,19), (8,11,15),
          (29,26,20), (22,18,14), (25,14,11), (18,9,8), (18,10,7),
          (28,22,14), (20,17,22), (20,20,20), (14,14,14), (9,14,4), (11,8,9))
# These are acceptance fingerprints, independent of self-rehashed metadata.
SOURCE = {
    'source.png': (1219459, '54e68307c8340ad51f759b440161b1c1907e9313ad1bfdff90ade3860404f3f7'),
    'prompt.md': (1243, 'ec1bfdc1723e7e5f20d41428135810aad5e1a2eedd5f4fdcbfe4e4200641c1a2'),
    'conversion.json': (880, '65050d363157c7f7ddd087bfc43a93edaf3c9478ae4c38e1888df57374989645'),
    'native.png': (2409, 'bad3ee2d2370fef7279cdc6defc42f85e2cf2199093e41a1db4932bbbeb9a791'),
    'block.indices': (14080, 'a5803bee61035648f7e63fb4fd97cba0d594817e61bc0689be4b634fa8d5c82a'),
    'block.gbapal': (32, '2c4864885ac0b05ef38c629d7e700df61c3a81e88633edf19604b534e7cc65bf'),
}
BASELINE = {
    'primary.4bpp': (7520, 'ead15c695c8155da75caf0fb3376ccbac676d21e8acfc3c0e4d30dcda8c93a67'),
    'metatiles.bin': (1040, '22cfd59f547bf780a80111606b4bc063b8133bcdf7d1401dadf9f7004b298ab3'),
    'attributes.bin': (130, 'ad210381edd1ddfe7f5a4a43de890c88ecddaa50ecc25fb2dec5699c92c11446'),
    'palettes.gbapal': (512, '7535c33e74b38bf508dbc2de826ebf095895f1a87fde61f08b914892b2400c62'),
    'south-park-map.bin': (2560, '99fd32736d89e67e501c17d6e8fece0d228a42f08cec35f1ece2fecc8a38b26f'),
    'secondary.4bpp': (16064, '025b15ff1b4e9606d010b85031c71476a3071183015300e2466e6c60f98c4d42'),
    'secondary-metatiles.bin': (2400, 'c1d17b5e9bc2c04371c6a2aaea46321f2326c70822d9a8c87974fa9ed596a9aa'),
    'secondary-attributes.bin': (300, '5d75b62c2517473238cfe7967401f492d506a41ffbbd5de58ea9c99ad39eab2f'),
    'secondary-palettes.gbapal': (512, '73e3ba1b6d1f0a9385e97e92eba6a4a2d1268384e4cdf6f45f452a49fda512db'),
    'receipt.json': (1523, '0c0bef56b717668dc0f5ca949250e9ee318a4ee3e46d45fa8eb4628c3f839fc8'),
}
OLD_APRONS = ((2,6,(60,61,62)), (2,17,(57,58,59)), (2,25,(54,55,56)),
              (21,6,(63,64)), (18,6,(60,61,62)), (23,6,(60,61,62)),
              (26,6,(60,61,62)), (11,17,(60,61,62,60,61,62)),
              (11,24,(60,61,62,60,61,62)), (11,6,(54,54,55,56,56,56)),
              (30,6,(54,54,55,56,56,56)))
PAVING_SHA = '36d87ab45a3526bad751c51b330e8b66baf9f13f53d20fd32c191be678be9b96'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def quadrant(raw, word, *, secondary=False, bank=None):
    """Decode one bounded resident 8x8 word, including both native flips."""
    tile = (word & 1023) - (512 if secondary else 0)
    if bank is not None and word >> 12 != bank:
        raise ValueError('Unexpected native palette bank.')
    if tile < 0 or (tile + 1) * 32 > len(raw) or (secondary and (word & 1023) >= 1016):
        raise ValueError('Tile leaves its resident allocation or enters door cache.')
    return bytes((raw[tile*32 + (7-y if word & 0x800 else y)*4
                      + (7-x if word & 0x400 else x)//2]
                  >> (4*((7-x if word & 0x400 else x) % 2))) & 15
                 for y in range(8) for x in range(8))


def cell_pixels(raw, words, *, secondary=False, bank=None):
    if len(words) != 4:
        raise ValueError('Four quadrants are required for a complete native cell.')
    parts = [quadrant(raw, word, secondary=secondary, bank=bank) for word in words]
    return b''.join(parts[2*(y//8)][(y%8)*8:(y%8+1)*8]
                    + parts[2*(y//8)+1][(y%8)*8:(y%8+1)*8] for y in range(16))


def audit_connected(rom, elf, root):
    from check_creature_resources import Cartridge, decode_lz
    from PIL import Image

    checks, hashes, errors = [], {}, []
    result = {'passed': False, 'checks': checks, 'hashes': hashes, 'errors': errors,
              'quality_approval': 'pending',
              'scope': __doc__}

    def source(path):
        blob = path.read_bytes(); hashes[str(path)] = sha(blob); return blob

    def pinned(directory, specification):
        blobs = {}
        for name, (length, digest) in specification.items():
            blob = source(directory/name)
            if len(blob) != length or sha(blob) != digest:
                raise ValueError('Pinned original resource differs: ' + str(directory/name))
            blobs[name] = blob
        return blobs

    def compare(name, expected, observe):
        row = {'name': name, 'passed': False, 'expected_bytes': len(expected),
               'expected_sha256': sha(expected)}
        try:
            actual = observe()
            row.update(passed=actual == expected, actual_bytes=len(actual), actual_sha256=sha(actual))
        except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
            row['error'] = str(error); errors.append(name + ': ' + str(error))
        checks.append(row)

    try:
        root = Path(root)
        source(Path(__file__))
        source(Path(__file__).parents[1]/'quality/check_creature_resources.py')
        hashes.update(rom=sha(rom.read_bytes()), elf=sha(elf.read_bytes()))
        assets = pinned(root/ASSET, SOURCE)
        baseline = pinned(root/ASSET/'baseline-v76', BASELINE)
        info = json.loads(assets['conversion.json'])
        if (info['size'], info['source_bounds'], info['source_ground_y'],
                info['blocked_rows'], info['walkable_rows']) != (
                [176,80], [2,2,1858,637], 637, [0,64], [64,80]) or \
                info['source_sha256'] != sha(assets['source.png']) or \
                info['prompt_sha256'] != sha(assets['prompt.md']) or \
                info['files'] != {name:sha(assets[name]) for name in ('native.png','block.indices','block.gbapal')}:
            raise ValueError('Connected scene provenance or geometry differs.')
        palette = b''.join(struct.pack('<H', sum(rgb[c] << (5*c) for c in range(3))) for rgb in COLORS)
        if assets['block.gbapal'] != palette:
            raise ValueError('Scene colors differ from the independent RGB555 palette.')
        flat_palette = [value*255//31 for rgb in COLORS for value in rgb]
        with Image.open(root/ASSET/'native.png') as image:
            if (image.mode, image.size, image.info.get('transparency')) != ('P', SIZE, 0) or \
                    image.tobytes() != assets['block.indices'] or image.getpalette()[:48] != flat_palette:
                raise ValueError('Scene PNG, serialized indices, palette or transparency differ.')
        # Read the pinned original directly. Pillow NEAREST retains the specified
        # boundary sampling; an integer-center approximation differs at ties.
        # No production converter, quantizer or scene compiler is called.
        with Image.open(root/ASSET/'source.png') as image:
            if image.size != (1859,846):
                raise ValueError('Original source dimensions differ.')
            rgba = image.convert('RGBA').crop((2,2,1858,637)).resize((176,64),Image.Resampling.NEAREST)
            derived = bytearray(176*80)
            for y in range(64):
                for x in range(176):
                    pixel = rgba.getpixel((x,y))
                    if pixel[3] >= 128:
                        rgb = tuple(round(value*31/255) for value in pixel[:3])
                        derived[y*176+x] = min(range(1,16), key=lambda i:
                            sum((rgb[c]-COLORS[i][c])**2 for c in range(3)))
        compare('source_crop_native_pixels', assets['block.indices'], lambda:bytes(derived))
        if any(assets['block.indices'][176*64:]):
            raise ValueError('The entire sixteen-pixel approach must remain transparent.')

        cart = Cartridge(rom, elf)
        def data(name, length=None): return cart.data(name, length)
        for suffix, secondary in (('SFParkFrontage',0), ('SFSouthPark',1)):
            def header(suffix=suffix, secondary=secondary):
                names = ('gTilesetTiles_', 'gTilesetPalettes_', 'gMetatiles_', 'gMetatileAttributes_')
                return struct.pack('<BB2x5I',1,secondary,
                    *(cart.symbols[name+suffix][0] for name in names),0)
            # Missing symbols and invalid resource pointers fail closed.
            expected = header()
            compare(suffix+':header', expected, lambda suffix=suffix:data('gTileset_'+suffix))
        def layout():
            value = data('OldaleTown_Layout',24)
            width,height,border,blocks,primary,secondary = struct.unpack('<ii4I',value)
            if cart.symbols['OldaleTown_Layout'][1] not in (None,24) or \
                    (width,height,blocks,primary,secondary) != (40,32,
                     cart.symbols['OldaleTown_Layout_Blockdata'][0],
                     cart.symbols['gTileset_SFParkFrontage'][0],
                     cart.symbols['gTileset_SFSouthPark'][0]) or border % 2 or \
                    not 0x08000000 <= border <= 0x08000000+len(cart.rom)-8:
                raise ValueError('Native layout dimensions, pointers or border bounds differ.')
            return b'exact40x32-layout'
        compare('layout_binding', b'exact40x32-layout', layout)

        raw = decode_lz(data('gTilesetTiles_SFParkFrontage'))
        records = data('gMetatiles_SFParkFrontage')
        attrs = data('gMetatileAttributes_SFParkFrontage')
        palettes = data('gTilesetPalettes_SFParkFrontage')
        compare('primary_allocations', struct.pack('<4I',395*32,120*16,120*2,512),
                lambda:struct.pack('<4I',len(raw),len(records),len(attrs),len(palettes)))
        compare('original235_tile_prefix', baseline['primary.4bpp'], lambda:raw[:235*32])
        compare('blank_primary_tile0', bytes(32), lambda:raw[:32])
        compare('original65_foreground_words',
                b''.join(baseline['metatiles.bin'][i*16+8:(i+1)*16] for i in range(65)),
                lambda:b''.join(records[i*16+8:(i+1)*16] for i in range(65)))
        expected_attrs = baseline['attributes.bin'] + struct.pack('<55H',
            *(0 if row < 3 else 0x1000 for row in range(5) for col in range(11)))
        compare('all120_layer_attributes', expected_attrs, lambda:attrs)
        expected_palettes = bytearray(baseline['palettes.gbapal']); expected_palettes[160:192] = palette
        compare('complete_primary_palette', bytes(expected_palettes), lambda:palettes)

        secondary_raw = decode_lz(data('gTilesetTiles_SFSouthPark'))
        secondary_records = data('gMetatiles_SFSouthPark')
        if not 0 < len(secondary_raw) <= 504*32 or len(secondary_raw) % 32 or \
                not 20*16 <= len(secondary_records) <= 512*16 or len(secondary_records) % 16:
            raise ValueError('Secondary resident allocation or metatile table exceeds its bound.')
        if any((word & 1023) >= 1016 for word in struct.unpack('<'+'H'*(len(secondary_records)//2),secondary_records)):
            raise ValueError('Static secondary words reference reserved door-cache tiles.')
        paving = source(root/'assets/tiles/south-park-paving-v1/paving.indices')
        if len(paving) != 256 or sha(paving) != PAVING_SHA or set(paving) != {1,2}:
            raise ValueError('Original gray paving pixels differ.')
        sidewalk = cell_pixels(secondary_raw,
            struct.unpack_from('<4H',secondary_records,19*16+8),secondary=True,bank=4)
        compare('secondary19_gray_paving', paving, lambda:sidewalk)
        for index in range(120):
            compare('underlay_%03d'%index, paving,
                lambda index=index:cell_pixels(secondary_raw,
                    struct.unpack_from('<4H',records,index*16),secondary=True,bank=4))
        def scene():
            image = bytearray(176*80)
            for index in range(55):
                cell = cell_pixels(raw,struct.unpack_from('<4H',records,(65+index)*16+8),bank=5)
                for y in range(16):
                    at = (index//11*16+y)*176+index%11*16
                    image[at:at+16] = cell[y*16:(y+1)*16]
            return bytes(image)
        compare('complete_scene_native_pixels', assets['block.indices'], scene)

        original_map = baseline['south-park-map.bin']
        expected_map = bytearray(original_map)
        apron_points = set()
        for left,top,ids in OLD_APRONS:
            for col,tile in enumerate(ids):
                at = (top*40+left+col)*2
                if struct.unpack_from('<H',original_map,at)[0] != (0x3000|tile):
                    raise ValueError('Frozen map does not have the declared old apron bindings.')
                apron_points.add((left+col,top))
                struct.pack_into('<H',expected_map,at,0x3000|531)
        for row in range(5):
            for col in range(11):
                at = ((2+row)*40+18+col)*2
                upper = struct.unpack_from('<H',expected_map,at)[0] & 0xFC00
                struct.pack_into('<H',expected_map,at,upper | (65+row*11+col))
        blocks = data('OldaleTown_Layout_Blockdata',40*32*2)
        compare('all1280_map_words', bytes(expected_map), lambda:blocks)
        compare('all1280_collision_elevation_words',
            bytes(v & 0xFC for v in original_map[1::2]),
            lambda:bytes(v & 0xFC for v in blocks[1::2]))
        expected_points = {(i%40,i//40) for i,(word,) in enumerate(struct.iter_unpack('<H',expected_map)) if (word & 1023) < 512}
        if len(apron_points) != 44 or len(expected_points) != 100:
            raise ValueError('Independent map change set must retain100 primary cells after44 apron reversions.')
        def footprint():
            actual = {(i%40,i//40) for i,(word,) in enumerate(struct.iter_unpack('<H',blocks)) if (word & 1023) < 512}
            if actual != expected_points:
                raise ValueError('Primary footprint differs from the exact100 cells.')
            return b'exact100-primary-cells'
        compare('primary_map_footprint', b'exact100-primary-cells', footprint)
        result['counts'] = {'primary_cells':100, 'connected_cells':55, 'old_aprons_removed':44,
                            'map_words':1280, 'primary_tiles':len(raw)//32,
                            'secondary_tiles':len(secondary_raw)//32}
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        errors.append(str(error)); checks.append({'name':'audit_inputs','passed':False,'error':str(error)})
    result.setdefault('counts', {})
    result['counts'].update(total=len(checks), matched=sum(row['passed'] for row in checks))
    result['passed'] = bool(checks) and all(row['passed'] for row in checks) and not errors
    return result
