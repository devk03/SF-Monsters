"""Original-only linked ARM fixtures for bounded South Park density changes."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/romhack'),str(ROOT/'scripts/quality'),str(ROOT/'tests')]
from park_density_audit import audit_density
from trainer_portrait_audit_test import addresses,literal_lz,linked_pair,MemoryFile
BASE=ROOT/'assets/tiles/park-density-v1/baseline-v78'
ASSET=ROOT/'assets/tiles/compact-townhouses-v1'
BLOCKS=((1,1,(135,136,137,138),4,True),(1,12,(135,136,137,138),4,True),
        (1,20,(135,136,137,138),4,True),(10,13,(135,136,137,138),4,False),
        (10,20,(135,136,137,138),4,False),(25,11,(65,66,67,70,71,72,73,74,75),11,False))


def flip(blob,bits):
    pixels=[byte>>shift&15 for byte in blob for shift in (0,4)]
    output=[pixels[(7-y if bits&0x800 else y)*8+(7-x if bits&0x400 else x)] for y in range(8) for x in range(8)]
    return bytes(output[i]|output[i+1]<<4 for i in range(0,64,2))


def rebind(resources):
    resources=resources.copy();locations=addresses(resources)
    for suffix,secondary in (('SFParkFrontage',0),('SFSouthPark',1)):
        resources['gTileset_'+suffix]=struct.pack('<BB2x5I',1,secondary,
            *(locations[p+suffix] for p in ('gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_')),0)
    resources['OldaleTown_Layout']=struct.pack('<ii4I',40,32,locations['OldaleTown_Layout_Blockdata'],
        locations['OldaleTown_Layout_Blockdata'],locations['gTileset_SFParkFrontage'],locations['gTileset_SFSouthPark'])
    return resources


def fixture():
    raw=bytearray((BASE/'primary.4bpp').read_bytes());records=bytearray((BASE/'primary-metatiles.bin').read_bytes())
    attrs=bytearray((BASE/'primary-attributes.bin').read_bytes());pool={}
    for tile in range(449):
        blob=bytes(raw[tile*32:tile*32+32])
        for bits in (0,0x400,0x800,0xC00):pool.setdefault(flip(blob,bits),(tile,bits))
    pixels=(ASSET/'pair.indices').read_bytes();sidewalk=records[:8]
    for row in range(4):
        for col in range(4):
            words=[]
            for q in range(4):
                values=[pixels[(row*16+q//2*8+y)*64+col*16+q%2*8+x] for y in range(8) for x in range(8)]
                blob=bytes(values[i]|values[i+1]<<4 for i in range(0,64,2))
                if blob not in pool:
                    tile=len(raw)//32;stored=flip(blob,q<<10);raw.extend(stored)
                    for bits in (0,0x400,0x800,0xC00):pool.setdefault(flip(stored,bits),(tile,bits))
                tile,bits=pool[blob];words.append(0x5000|bits|tile)
            records.extend(sidewalk+struct.pack('<4H',*words));attrs.extend(struct.pack('<H',0 if row<3 else 0x1000))
    if len(raw)!=511*32:raise ValueError('Independent compact pair must append62 tiles.')
    blocks=bytearray((BASE/'south-park-map.bin').read_bytes())
    for left,top,columns,stride,clear in BLOCKS:
        for y in range(4):
            for x,record in enumerate(columns):struct.pack_into('<H',blocks,((top+y)*40+left+x)*2,0xC00|record+y*stride)
        if clear:
            for x in range(len(columns)):struct.pack_into('<H',blocks,((top+4)*40+left+x)*2,0x3213)
    resources={'gTilesetTiles_SFParkFrontage':literal_lz(raw),'gMetatiles_SFParkFrontage':bytes(records),
        'gMetatileAttributes_SFParkFrontage':bytes(attrs),'gTilesetPalettes_SFParkFrontage':(BASE/'primary-palettes.bin').read_bytes(),
        'gTilesetTiles_SFSouthPark':literal_lz((BASE/'secondary.4bpp').read_bytes()),
        'gMetatiles_SFSouthPark':(BASE/'secondary-metatiles.bin').read_bytes(),
        'gMetatileAttributes_SFSouthPark':(BASE/'secondary-attributes.bin').read_bytes(),
        'gTilesetPalettes_SFSouthPark':(BASE/'secondary-palettes.bin').read_bytes(),
        'gTileset_SFParkFrontage':bytes(24),'gTileset_SFSouthPark':bytes(24),'OldaleTown_Layout':bytes(24),
        'OldaleTown_Layout_Blockdata':bytes(blocks)}
    return rebind(resources)


class ParkDensityAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.resources=fixture()
    def audit(self,resources=None,root=ROOT):return audit_density(*linked_pair(self.resources if resources is None else resources),root)
    def fault(self,name,at,mask=1):
        resources=self.resources.copy();blob=bytearray(resources[name]);blob[at]^=mask;resources[name]=bytes(blob);return resources
    def reject(self,resources,target):
        result=self.audit(resources);self.assertFalse(result['passed'])
        self.assertTrue(any(row['name']==target and not row['passed'] for row in result['checks']),
            {'errors':result['errors'],'failed':[row['name'] for row in result['checks'] if not row['passed']]})
    def test_independent_compact_density_preserves_resources_and_exact_map_delta(self):
        result=self.audit()
        self.assertTrue(result['passed'],{'errors':result['errors'],'failed':[row for row in result['checks'] if not row['passed']]})
        self.assertEqual(result['counts']['primary_tiles'],511)
        self.assertEqual(result['counts']['changed_map_words'],125)
        self.assertEqual(result['counts']['collision_changes'],65)
        self.assertEqual(result['counts']['new_solid_cells'],56)
        self.assertEqual(result['counts']['freed_cells'],9)
        self.assertEqual(result['counts']['primary_map_cells'],189)
        self.assertEqual(result['counts']['matched'],result['counts']['total'])
        self.assertEqual(result['quality_approval'],'pending')

    def test_legacy_projections_require_validated_density_and_reject_all_bad_extensions(self):
        from city_furniture_audit import audit_furniture
        from connected_frontage_audit import audit_connected
        rom,elf=linked_pair(self.resources)
        self.assertFalse(audit_furniture(rom,elf,ROOT)['passed'])
        self.assertFalse(audit_connected(rom,elf,ROOT,furniture=True)['passed'])
        city=audit_furniture(rom,elf,ROOT,density=True)
        connected=audit_connected(rom,elf,ROOT,furniture=True,density=True)
        self.assertTrue(city['passed'],city['errors'])
        self.assertTrue(connected['passed'],connected['errors'])
        self.assertEqual(city['counts']['primary_tiles'],449)
        self.assertEqual(city['density']['counts']['primary_tiles'],511)
        self.assertEqual(city['normalization']['restored_map_cells'],128)
        self.assertEqual(connected['counts']['matched'],135)
        for bad in (self.fault('gMetatileAttributes_SFParkFrontage',150*2),
                    self.fault('OldaleTown_Layout_Blockdata',(13*40+9)*2),
                    self.fault('gMetatiles_SFParkFrontage',135*16+9,16)):
            rom,elf=linked_pair(bad)
            city=audit_furniture(rom,elf,ROOT,density=True)
            connected=audit_connected(rom,elf,ROOT,furniture=True,density=True)
            self.assertFalse(city['passed']);self.assertNotIn('normalization',city)
            self.assertFalse(connected['passed']);self.assertNotIn('normalization',connected)
        rom,elf=linked_pair(self.resources)
        self.assertFalse(audit_connected(rom,elf,ROOT,density=True)['passed'])
        self.assertFalse(audit_furniture(rom,elf,ROOT,density=1)['passed'])

    def test_all_v78_resource_prefixes_and_complete_palettes_secondary_remain_exact(self):
        from check_creature_resources import decode_lz
        names=(('gTilesetTiles_SFParkFrontage','primary.4bpp:v78_prefix',True),
               ('gMetatiles_SFParkFrontage','primary-metatiles.bin:v78_prefix',False),
               ('gMetatileAttributes_SFParkFrontage','primary-attributes.bin:v78_prefix',False),
               ('gTilesetPalettes_SFParkFrontage','primary-palettes.bin:byte_exact',False),
               ('gTilesetTiles_SFSouthPark','secondary.4bpp:byte_exact',True),
               ('gMetatiles_SFSouthPark','secondary-metatiles.bin:byte_exact',False),
               ('gMetatileAttributes_SFSouthPark','secondary-attributes.bin:byte_exact',False),
               ('gTilesetPalettes_SFSouthPark','secondary-palettes.bin:byte_exact',False))
        for name,target,compressed in names:
            resources=self.resources.copy();blob=resources[name]
            if compressed:
                raw=bytearray(decode_lz(blob));raw[32]^=1;resources[name]=literal_lz(raw)
            else:resources[name]=bytes([blob[0]^1])+blob[1:]
            with self.subTest(name=name):self.reject(resources,target)
        # Changing even an unused palette slot is outside the density scope.
        for name,target in (('gTilesetPalettes_SFParkFrontage','primary-palettes.bin:byte_exact'),
                            ('gTilesetPalettes_SFSouthPark','secondary-palettes.bin:byte_exact')):
            for at in (128,160,256,288,511):self.reject(self.fault(name,at),target)

    def test_compact_pixels_banks_flips_and_all_sixteen_layer_roles_are_checked(self):
        from check_creature_resources import decode_lz
        raw=decode_lz(self.resources['gTilesetTiles_SFParkFrontage'])
        for index in (135,138,139,146,147,150):
            self.reject(self.fault('gMetatiles_SFParkFrontage',index*16+9,16),'compact_native_pixels')
        for flag in (4,8):
            for index in range(135,151):
                word=struct.unpack_from('<H',self.resources['gMetatiles_SFParkFrontage'],index*16+8)[0]
                tile=raw[(word&1023)*32:((word&1023)+1)*32]
                if flip(tile,flag<<8)!=tile:
                    self.reject(self.fault('gMetatiles_SFParkFrontage',index*16+9,flag),'compact_native_pixels');break
            else:self.fail('Need asymmetric compact pair pixels.')
        resources=self.resources.copy();changed=bytearray(raw);changed[449*32]^=1
        resources['gTilesetTiles_SFParkFrontage']=literal_lz(changed)
        self.reject(resources,'compact_native_pixels')
        for index in range(135,151):
            self.reject(self.fault('gMetatileAttributes_SFParkFrontage',index*2+1,16),'all151_primary_attributes')

    def test_new_ground_underlays_are_gray_resident_secondary_never_primary_or_door_cache(self):
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFParkFrontage'])
        for index in range(135,151):records[index*16+1]^=16
        resources['gMetatiles_SFParkFrontage']=bytes(records);result=self.audit(resources)
        failed={row['name'] for row in result['checks'] if not row['passed']}
        self.assertTrue({'compact_underlay_%d'%i for i in range(135,151)}<=failed)
        for tile in (0,511,988,1016,1023):
            resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFParkFrontage'])
            struct.pack_into('<H',records,135*16,0x4000|tile);resources['gMetatiles_SFParkFrontage']=bytes(records)
            self.reject(resources,'compact_underlay_135')
        self.reject(self.fault('gMetatiles_SFParkFrontage',135*16+1,8),'compact_underlay_135')

    def test_six_literal_parcel_mappings_ground_rows_collision_and_elevation_are_exact(self):
        for left,top,columns,stride,clear in BLOCKS:
            for x,y in ((left,top),(left+len(columns)-1,top+3)):
                at=(y*40+x)*2
                self.reject(self.fault('OldaleTown_Layout_Blockdata',at),'all1280_map_words')
                for mask in (4,16):self.reject(self.fault('OldaleTown_Layout_Blockdata',at+1,mask),'all1280_collision_elevation')
            if clear:
                for x in (left,left+len(columns)-1):
                    at=((top+4)*40+x)*2
                    self.reject(self.fault('OldaleTown_Layout_Blockdata',at),'all1280_map_words')
                    self.reject(self.fault('OldaleTown_Layout_Blockdata',at+1,4),'all1280_collision_elevation')
        # A wrong accepted source column still passes collision/count checks,
        # so the complete literal map comparison is necessary.
        self.reject(self.fault('OldaleTown_Layout_Blockdata',(13*40+10)*2),'all1280_map_words')

    def test_x5_sidewalk_seed_house_homes_furniture_park_roads_and_events_are_unchanged(self):
        points={(5,y) for y in (1,4,5,12,15,16,20,23,24)}
        points|={(9,y) for y in (12,13,14,15,16,17,19,20,21,22,23,24)}
        points|={(x,y) for y in range(13,17) for x in range(14,17)}
        points|={(18,2),(28,2),(18,6),(28,6),(21,7),(21,8),(13,5),(13,6),(32,5),(32,6),
                 (10,6),(29,6),(7,25),(7,26),(26,18),(34,23),(33,20),(18,21),
                 (17,6),(17,7),(36,7),(38,7),(18,11),(35,11),(25,15),(27,19),(7,9)}
        for x,y in points:self.reject(self.fault('OldaleTown_Layout_Blockdata',(y*40+x)*2),'all1280_map_words')
        resources=self.resources.copy();blocks=bytearray(resources['OldaleTown_Layout_Blockdata'])
        struct.pack_into('<H',blocks,(4*40+5)*2,0xC87);resources['OldaleTown_Layout_Blockdata']=bytes(blocks)
        self.reject(resources,'primary_map_footprint')
        self.reject(resources,'exact_density_delta')

    def test_headers_layout_exact_counts_malformed_lz_and_stale_elf_fail_closed(self):
        from check_creature_resources import decode_lz
        for suffix in ('SFParkFrontage','SFSouthPark'):
            for at in (0,1,2,4,8,12,16,20):self.reject(self.fault('gTileset_'+suffix,at),suffix+':header')
        for at in (0,4,8,12,16,20):self.reject(self.fault('OldaleTown_Layout',at),'layout_binding')
        resources=self.resources.copy();raw=decode_lz(resources['gTilesetTiles_SFParkFrontage'])
        resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw+bytes(32))
        self.reject(rebind(resources),'primary_allocations')
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFParkFrontage'])
        struct.pack_into('<H',records,135*16+8,0x5000|511);resources['gMetatiles_SFParkFrontage']=bytes(records)
        self.reject(resources,'compact_native_pixels')
        for name in self.resources:
            resources=self.resources.copy();del resources[name]
            with self.subTest(missing=name):self.assertFalse(self.audit(resources)['passed'])
        for name in self.resources:
            resources=self.resources.copy();resources[name]=resources[name][:-1]
            with self.subTest(truncated=name):self.assertFalse(self.audit(resources)['passed'])
        resources=self.resources.copy();resources['gTilesetTiles_SFParkFrontage']=b'bad'
        self.assertFalse(self.audit(resources)['passed'])
        rom,elf=linked_pair(self.resources);changed=bytearray(rom.data);changed[5]^=1
        self.assertFalse(audit_density(MemoryFile(changed),elf,ROOT)['passed'])
        changed=bytearray(elf.data);struct.pack_into('<I',changed,96,8)
        self.assertFalse(audit_density(rom,MemoryFile(changed),ROOT)['passed'])

    def test_pinned_original_assets_and_self_rehashed_v78_baseline_fail_closed(self):
        parent=ROOT/'.tools/park-density-audit-tests';parent.mkdir(parents=True,exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='case-',dir=parent))
        shutil.copytree(BASE,root/BASE.relative_to(ROOT));shutil.copytree(ASSET,root/ASSET.relative_to(ROOT))
        reference=Path('assets/tiles/connected-frontage-v3/native.png')
        (root/reference).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/reference,root/reference)
        self.assertTrue(self.audit(root=root)['passed'])
        for directory in (root/BASE.relative_to(ROOT),root/ASSET.relative_to(ROOT)):
            for path in sorted(directory.iterdir()):
                if not path.is_file() or path.name=='README.md':continue
                old=path.read_bytes();path.write_bytes(bytes([old[0]^1])+old[1:])
                with self.subTest(file=path.name):self.assertFalse(self.audit(root=root)['passed'])
                path.write_bytes(old)
        path=root/BASE.relative_to(ROOT)/'south-park-map.bin';changed=bytearray(path.read_bytes());changed[0]^=1;path.write_bytes(changed)
        receipt=root/BASE.relative_to(ROOT)/'receipt.json';info=json.loads(receipt.read_text())
        info['files'][path.name]['sha256']=hashlib.sha256(changed).hexdigest();receipt.write_text(json.dumps(info))
        self.assertFalse(self.audit(root=root)['passed'])


if __name__=='__main__':unittest.main()
