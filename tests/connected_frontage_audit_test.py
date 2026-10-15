"""Linked ARM ROM/ELF fault vectors for the connected northern frontage.

The fixture starts with original-only frozen v76 bytes and independently writes
the new scene, a relocated paving tile and exact map delta. No producer imports.
"""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts/romhack'),str(ROOT/'scripts/quality'),str(ROOT/'tests')]
from connected_frontage_audit import audit_connected
from trainer_portrait_audit_test import MemoryFile, addresses, literal_lz, linked_pair

ASSET = ROOT/'assets/tiles/connected-frontage-v3'
BASE = ASSET/'baseline-v76'
APRONS = ((2,6,(60,61,62)),(2,17,(57,58,59)),(2,25,(54,55,56)),
          (21,6,(63,64)),(18,6,(60,61,62)),(23,6,(60,61,62)),(26,6,(60,61,62)),
          (11,17,(60,61,62,60,61,62)),(11,24,(60,61,62,60,61,62)),
          (11,6,(54,54,55,56,56,56)),(30,6,(54,54,55,56,56,56)))


def packed(pixels):
    return bytes(pixels[i] | pixels[i+1] << 4 for i in range(0,64,2))


def flip_tile(blob, bits):
    pixels = [value >> shift & 15 for value in blob for shift in (0,4)]
    return packed(bytes(pixels[(7-y if bits & 0x800 else y)*8
                               + (7-x if bits & 0x400 else x)] for y in range(8) for x in range(8)))


def fixture():
    secondary = bytearray((BASE/'secondary.4bpp').read_bytes())
    secondary_records = bytearray((BASE/'secondary-metatiles.bin').read_bytes())
    paving = (ROOT/'assets/tiles/south-park-paving-v1/paving.indices').read_bytes()
    master = bytes(paving[y*16+x] for y in range(8) for x in range(8))
    # A different resident paving binding demonstrates that secondary repacking
    # may change underlay words without weakening the decoded pixel comparison.
    paving_word = 0x4000 | (512+len(secondary)//32)
    secondary.extend(packed(master))
    sidewalk = struct.pack('<4H',*([paving_word]*4))
    secondary_records[19*16+8:20*16] = sidewalk
    raw = bytearray((BASE/'primary.4bpp').read_bytes())
    records = bytearray((BASE/'metatiles.bin').read_bytes())
    for index in range(65): records[index*16:index*16+8] = sidewalk
    attrs = bytearray((BASE/'attributes.bin').read_bytes())
    palette = bytearray((BASE/'palettes.gbapal').read_bytes())
    palette[160:192] = (ASSET/'block.gbapal').read_bytes()
    source = (ASSET/'block.indices').read_bytes()
    pool = {}
    for tile in range(len(raw)//32):
        blob = bytes(raw[tile*32:(tile+1)*32])
        for bits in (0,0x400,0x800,0xC00): pool.setdefault(flip_tile(blob,bits),(tile,bits))
    for row in range(5):
        for col in range(11):
            words = []
            for q in range(4):
                blob = packed(bytes(source[(row*16+q//2*8+y)*176+col*16+q%2*8+x]
                                    for y in range(8) for x in range(8)))
                if blob not in pool:
                    tile = len(raw)//32
                    # Serialize alternating orientations to exercise native
                    # H/V decoding without depending on a producer's packing.
                    orientation = (q % 4) << 10
                    stored = flip_tile(blob,orientation)
                    raw.extend(stored)
                    for bits in (0,0x400,0x800,0xC00):
                        pool.setdefault(flip_tile(stored,bits),(tile,bits))
                tile,bits = pool[blob]; words.append(5<<12 | bits | tile)
            records.extend(sidewalk+struct.pack('<4H',*words))
            attrs.extend(struct.pack('<H',0 if row<3 else 0x1000))
    if len(raw)>395*32: raise ValueError('Independent fixture exceeds the reviewed primary allocation.')
    raw.extend(bytes(395*32-len(raw)))
    blocks = bytearray((BASE/'south-park-map.bin').read_bytes())
    for left,y,ids in APRONS:
        for col in range(len(ids)): struct.pack_into('<H',blocks,(y*40+left+col)*2,0x3213)
    for row in range(5):
        for col in range(11):
            at = ((row+2)*40+col+18)*2
            old = struct.unpack_from('<H',blocks,at)[0]
            struct.pack_into('<H',blocks,at,old & 0xFC00 | 65+row*11+col)
    resources = {
        'gTilesetTiles_SFSouthPark':literal_lz(secondary),
        'gMetatiles_SFSouthPark':bytes(secondary_records),
        'gMetatileAttributes_SFSouthPark':(BASE/'secondary-attributes.bin').read_bytes(),
        'gTilesetPalettes_SFSouthPark':(BASE/'secondary-palettes.gbapal').read_bytes(),
        'gTilesetTiles_SFParkFrontage':literal_lz(raw),
        'gMetatiles_SFParkFrontage':bytes(records),
        'gMetatileAttributes_SFParkFrontage':bytes(attrs),
        'gTilesetPalettes_SFParkFrontage':bytes(palette),
        'gTileset_SFParkFrontage':bytes(24), 'gTileset_SFSouthPark':bytes(24),
        'OldaleTown_Layout':bytes(24), 'OldaleTown_Layout_Blockdata':bytes(blocks),
    }
    return rebind(resources)


def rebind(resources):
    resources=resources.copy()
    locations = addresses(resources)
    for suffix,secondary_flag in (('SFParkFrontage',0),('SFSouthPark',1)):
        resources['gTileset_'+suffix] = struct.pack('<BB2x5I',1,secondary_flag,
            *(locations[p+suffix] for p in ('gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_')),0)
    resources['OldaleTown_Layout'] = struct.pack('<ii4I',40,32,
        locations['OldaleTown_Layout_Blockdata'],locations['OldaleTown_Layout_Blockdata'],
        locations['gTileset_SFParkFrontage'],locations['gTileset_SFSouthPark'])
    return resources


class ConnectedFrontageAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.resources = fixture()

    def audit(self, resources=None, root=ROOT):
        return audit_connected(*linked_pair(self.resources if resources is None else resources),root)

    def fault(self, symbol, offset, mask=1):
        resources = self.resources.copy(); blob = bytearray(resources[symbol]); blob[offset] ^= mask
        resources[symbol] = bytes(blob); return resources

    def reject(self, resources, name):
        result = self.audit(resources)
        self.assertFalse(result['passed'])
        self.assertTrue(any(row['name']==name and not row['passed'] for row in result['checks']),result)

    def copy_sources(self):
        parent=ROOT/'.tools/connected-frontage-audit-tests'; parent.mkdir(parents=True,exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='case-',dir=parent))
        shutil.copytree(ASSET,root/'assets/tiles/connected-frontage-v3')
        directory=root/'assets/tiles/south-park-paving-v1';directory.mkdir(parents=True)
        shutil.copy2(ROOT/'assets/tiles/south-park-paving-v1/paving.indices',directory/'paving.indices')
        return root

    def test_independent_linked_scene_with_repacked_underlays_passes(self):
        result=self.audit();self.assertTrue(result['passed'],{'errors':result['errors'],'failed':[r for r in result['checks'] if not r['passed']]})
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['quality_approval'],'pending')
        self.assertEqual({key:result['counts'][key] for key in ('primary_cells','connected_cells','old_aprons_removed','map_words','primary_tiles','secondary_tiles')},
            dict(primary_cells=100,connected_cells=55,old_aprons_removed=44,map_words=1280,primary_tiles=395,secondary_tiles=503))
        self.assertEqual(result['counts']['matched'],result['counts']['total'])

    def test_native_headers_reject_flags_reserved_bytes_all_pointers_and_callback(self):
        for suffix in ('SFParkFrontage','SFSouthPark'):
            for offset in (0,1,2,4,8,12,16,20):
                with self.subTest(suffix=suffix,offset=offset):
                    self.reject(self.fault('gTileset_'+suffix,offset),suffix+':header')
        for offset in (0,4,8,12,16,20):
            self.reject(self.fault('OldaleTown_Layout',offset),'layout_binding')

    def test_scene_pixels_bank_and_flips_reject_corruption(self):
        from check_creature_resources import decode_lz
        raw=decode_lz(self.resources['gTilesetTiles_SFParkFrontage'])
        # Both roof/wall rows and the transparent walkable row are observed.
        for record in (65,76,87,98,109,119):
            with self.subTest(record=record):
                self.reject(self.fault('gMetatiles_SFParkFrontage',record*16+9,16),'complete_scene_native_pixels')
        word=struct.unpack_from('<H',self.resources['gMetatiles_SFParkFrontage'],65*16+8)[0]
        changed=bytearray(raw);changed[(word&1023)*32]^=1
        resources=self.resources.copy();resources['gTilesetTiles_SFParkFrontage']=literal_lz(changed)
        self.reject(resources,'complete_scene_native_pixels')
        # Find an asymmetric scene tile, then prove either flip changes pixels.
        for bit in (4,8):
            for record in range(65,109):
                at=record*16+8;word=struct.unpack_from('<H',self.resources['gMetatiles_SFParkFrontage'],at)[0]
                tile=raw[(word&1023)*32:((word&1023)+1)*32]
                if flip_tile(tile,bit<<8)!=tile:
                    self.reject(self.fault('gMetatiles_SFParkFrontage',at+1,bit),'complete_scene_native_pixels');break
            else:self.fail('Fixture needs an asymmetric scene tile.')

    def test_walkable_approach_cannot_gain_opaque_scene_pixels(self):
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFParkFrontage'])
        records[109*16+8:110*16]=records[65*16+8:66*16]
        resources['gMetatiles_SFParkFrontage']=bytes(records)
        self.reject(resources,'complete_scene_native_pixels')

    def test_every_underlay_rejects_bank_flip_primary_and_reserved_cache_references(self):
        # Every record's underlay participates, including preserved old cards.
        for record in range(120):
            with self.subTest(record=record):
                self.reject(self.fault('gMetatiles_SFParkFrontage',record*16+1,16),'underlay_%03d'%record)
        for word in (0x4000,0x4000|511,0x4000|1016,0x4000|1023):
            resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFParkFrontage'])
            struct.pack_into('<H',records,65*16,word);resources['gMetatiles_SFParkFrontage']=bytes(records)
            self.reject(resources,'underlay_065')
        # The original gray master is vertically asymmetric.
        self.reject(self.fault('gMetatiles_SFParkFrontage',65*16+1,8),'underlay_065')

    def test_all_layer_attributes_and_complete_primary_palette_are_exact(self):
        for record in (0,54,64,65,86,97,98,108,109,119):
            self.reject(self.fault('gMetatileAttributes_SFParkFrontage',record*2+1,16),'all120_layer_attributes')
        for offset in (0,32,96,128,130,132,134,160,191,192,511):
            self.reject(self.fault('gTilesetPalettes_SFParkFrontage',offset),'complete_primary_palette')

    def test_old_primary_prefix_and_all65_foreground_words_remain_exact(self):
        from check_creature_resources import decode_lz
        raw=bytearray(decode_lz(self.resources['gTilesetTiles_SFParkFrontage']));raw[234*32]^=1
        resources=self.resources.copy();resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw)
        self.reject(resources,'original235_tile_prefix')
        for record in (0,1,53,54,64):
            self.reject(self.fault('gMetatiles_SFParkFrontage',record*16+8),'original65_foreground_words')

    def test_map_rejects_scene_ids_collisions_elevation_and_any_other_word_change(self):
        for x,y in ((18,2),(28,2),(18,4),(28,5),(18,6),(28,6)):
            at=(y*40+x)*2
            self.reject(self.fault('OldaleTown_Layout_Blockdata',at),'all1280_map_words')
            for mask in (4,16):
                with self.subTest(x=x,y=y,mask=mask):
                    self.reject(self.fault('OldaleTown_Layout_Blockdata',at+1,mask),'all1280_collision_elevation_words')
        for x,y in ((2,6),(3,17),(4,25),(11,6),(35,6),(13,5),(32,5),(16,16),(10,6),(29,6),(21,8),(0,0)):
            self.reject(self.fault('OldaleTown_Layout_Blockdata',(y*40+x)*2),'all1280_map_words')
        resources=self.resources.copy();blocks=bytearray(resources['OldaleTown_Layout_Blockdata'])
        # An undeclared additional primary map cell fails even with unchanged collision.
        struct.pack_into('<H',blocks,(7*40+18)*2,0x3041)
        resources['OldaleTown_Layout_Blockdata']=bytes(blocks)
        self.reject(resources,'primary_map_footprint')

    def test_secondary_cache_bounds_and_underlay_pixels_fail_without_freezing_services(self):
        from check_creature_resources import decode_lz
        resources=self.resources.copy();raw=decode_lz(resources['gTilesetTiles_SFSouthPark'])
        resources['gTilesetTiles_SFSouthPark']=literal_lz(raw+bytes(32))
        self.assertTrue(self.audit(rebind(resources))['passed'])
        resources['gTilesetTiles_SFSouthPark']=literal_lz(raw+bytes(64))
        result=self.audit(rebind(resources))
        self.assertFalse(result['passed'])
        self.assertTrue(any('Secondary resident allocation' in error for error in result['errors']))
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFSouthPark'])
        struct.pack_into('<H',records,0,1016);resources['gMetatiles_SFSouthPark']=bytes(records)
        self.assertFalse(self.audit(resources)['passed'])
        resources=self.resources.copy();raw=bytearray(raw);raw[502*32]^=1
        resources['gTilesetTiles_SFSouthPark']=literal_lz(raw)
        self.reject(resources,'secondary19_gray_paving')
        # This audit deliberately leaves service art/secondary palettes to the
        # separate owning audit, rather than claiming whole-secondary parity.
        resources=self.fault('gTilesetPalettes_SFSouthPark',8*32)
        self.assertTrue(self.audit(resources)['passed'])

    def test_missing_symbols_truncated_resources_malformed_lz_and_stale_elf_fail(self):
        for name in self.resources:
            resources=self.resources.copy();del resources[name]
            with self.subTest(missing=name):self.assertFalse(self.audit(resources)['passed'])
        for name in ('gTilesetTiles_SFParkFrontage','gMetatiles_SFParkFrontage','gMetatileAttributes_SFParkFrontage','gTilesetPalettes_SFParkFrontage','OldaleTown_Layout_Blockdata'):
            resources=self.resources.copy();resources[name]=resources[name][:-1]
            with self.subTest(truncated=name):self.assertFalse(self.audit(resources)['passed'])
        from check_creature_resources import decode_lz
        resources=self.resources.copy();raw=decode_lz(resources['gTilesetTiles_SFParkFrontage'])
        resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw+bytes(32))
        self.reject(resources,'primary_allocations')
        resources=self.resources.copy();resources['gTilesetTiles_SFParkFrontage']=b'\x10\xff\xff\xff'
        self.assertFalse(self.audit(resources)['passed'])
        rom,elf=linked_pair(self.resources);changed=bytearray(rom.data);changed[5]^=1
        self.assertFalse(audit_connected(MemoryFile(changed),elf,ROOT)['passed'])
        changed=bytearray(elf.data);struct.pack_into('<I',changed,96,8)
        self.assertFalse(audit_connected(rom,MemoryFile(changed),ROOT)['passed'])

    def test_original_asset_and_self_rehashed_baseline_receipts_cannot_change_expectation(self):
        root=self.copy_sources();directory=root/'assets/tiles/connected-frontage-v3'
        for name in ('source.png','prompt.md','conversion.json','native.png','block.indices','block.gbapal'):
            path=directory/name;original=path.read_bytes();path.write_bytes(original+b'changed')
            with self.subTest(source=name):self.assertFalse(self.audit(root=root)['passed'])
            path.write_bytes(original)
        for path in sorted((directory/'baseline-v76').iterdir()):
            original=path.read_bytes();path.write_bytes(bytes([original[0]^1])+original[1:])
            with self.subTest(baseline=path.name):self.assertFalse(self.audit(root=root)['passed'])
            path.write_bytes(original)
        path=directory/'baseline-v76/south-park-map.bin';changed=bytearray(path.read_bytes());changed[0]^=1;path.write_bytes(changed)
        receipt=directory/'baseline-v76/receipt.json';info=json.loads(receipt.read_text())
        info['files'][path.name]['sha256']=hashlib.sha256(changed).hexdigest();receipt.write_text(json.dumps(info))
        self.assertFalse(self.audit(root=root)['passed'])


if __name__=='__main__': unittest.main()
