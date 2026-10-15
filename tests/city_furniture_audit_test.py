"""Original-only linked ARM fixtures for city props and opt-in normalization."""
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
from city_furniture_audit import audit_furniture
from connected_frontage_audit import audit_connected
from service_architecture_audit_test import fixture as service_fixture,packed,flipped
from trainer_portrait_audit_test import addresses,literal_lz,linked_pair

ASSET=ROOT/'assets/tiles/city-furniture-v1'
BASE=ASSET/'baseline-v77'
# Independent acceptance geometry, not producer/auditor placement constants.
CELLS=((17,6,120,False),(17,7,121,True),(36,6,120,False),(36,7,121,True),
       (19,7,122,True),(26,7,122,True),(11,7,123,True),(15,7,124,True),
       (23,7,125,True),(24,7,126,True),(37,6,127,False),(38,6,128,False),
       (37,7,129,True),(38,7,130,True),(18,11,131,True),(19,11,132,True),
       (34,11,133,True),(35,11,134,True))


def rebind(resources):
    resources=resources.copy();locations=addresses(resources)
    for suffix,secondary in (('SFParkFrontage',0),('SFSouthPark',1)):
        resources['gTileset_'+suffix]=struct.pack('<BB2x5I',1,secondary,
            *(locations[p+suffix] for p in ('gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_')),0)
    resources['OldaleTown_Layout']=struct.pack('<ii4I',40,32,locations['OldaleTown_Layout_Blockdata'],
        locations['OldaleTown_Layout_Blockdata'],locations['gTileset_SFParkFrontage'],locations['gTileset_SFSouthPark'])
    return resources


def fixture(extension=True):
    # Shared independent service fixture serializes only original SF resources;
    # it does not invoke a producer, converter, compiler or native emulator.
    resources=service_fixture()
    raw=bytearray((BASE/'primary.4bpp').read_bytes())
    records=bytearray((BASE/'metatiles.bin').read_bytes());attrs=bytearray((BASE/'attributes.bin').read_bytes())
    blocks=bytearray((BASE/'south-park-map.bin').read_bytes());pool={}
    for tile in range(395):
        blob=bytes(raw[tile*32:tile*32+32])
        for bits in (0,0x400,0x800,0xC00):pool.setdefault(flipped(blob,bits),(tile,bits))
    if extension:
        for name,w,h in (('lamp',16,32),('meter',16,16),('hydrant',16,16),('bin',16,16),
                         ('rack',32,16),('tree',32,32),('bench',32,16),('recycling',32,16)):
            pixels=(ASSET/(name+'.indices')).read_bytes()
            for row in range(h//16):
                for col in range(w//16):
                    words=[]
                    for q in range(4):
                        blob=packed(bytes(pixels[(row*16+q//2*8+y)*w+col*16+q%2*8+x]
                            for y in range(8) for x in range(8)))
                        if blob not in pool:
                            tile=len(raw)//32;stored=flipped(blob,q<<10);raw.extend(stored)
                            for bits in (0,0x400,0x800,0xC00):pool.setdefault(flipped(stored,bits),(tile,bits))
                        tile,bits=pool[blob];words.append(0x5000|bits|tile)
                    records.extend(records[:8]+struct.pack('<4H',*words))
                    attrs.extend(struct.pack('<H',0x1000 if row==h//16-1 else 0))
        if len(raw)!=449*32:raise ValueError('Independent furniture fixture must append54 resident tiles.')
        for x,y,record,solid in CELLS:struct.pack_into('<H',blocks,(y*40+x)*2,0x3000|record|(0xC00 if solid else 0))
    resources.update({'gTilesetTiles_SFParkFrontage':literal_lz(raw),
        'gMetatiles_SFParkFrontage':bytes(records),'gMetatileAttributes_SFParkFrontage':bytes(attrs),
        'gTilesetPalettes_SFParkFrontage':(BASE/'palettes.gbapal').read_bytes(),
        'gTileset_SFParkFrontage':bytes(24),'gTileset_SFSouthPark':bytes(24),
        'OldaleTown_Layout':bytes(24),'OldaleTown_Layout_Blockdata':bytes(blocks)})
    return rebind(resources)


class CityFurnitureAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.resources=fixture();cls.old=fixture(False)
    def audit(self,resources=None,root=ROOT):
        return audit_furniture(*linked_pair(self.resources if resources is None else resources),root)
    def fault(self,symbol,at,mask=1):
        resources=self.resources.copy();blob=bytearray(resources[symbol]);blob[at]^=mask
        resources[symbol]=bytes(blob);return resources
    def reject(self,resources,target):
        result=self.audit(resources);self.assertFalse(result['passed'])
        self.assertTrue(any(row['name']==target and not row['passed'] for row in result['checks']),
            {'errors':result['errors'],'failed':[r['name'] for r in result['checks'] if not r['passed']]})

    def test_independent_full_extension_passes_and_strict_default_stays_v77_only(self):
        result=self.audit()
        self.assertTrue(result['passed'],{'errors':result['errors'],'failed':[r for r in result['checks'] if not r['passed']]})
        self.assertEqual(result['counts']['primary_tiles'],449)
        self.assertEqual(result['counts']['primary_map_cells'],118)
        self.assertEqual(result['counts']['solid_bases'],14)
        self.assertEqual(result['counts']['walkable_upper_cells'],4)
        self.assertEqual(result['counts']['matched'],result['counts']['total'])
        self.assertEqual(result['quality_approval'],'pending')
        self.assertTrue(audit_connected(*linked_pair(self.old),ROOT)['passed'])
        self.assertFalse(audit_connected(*linked_pair(self.resources),ROOT)['passed'])
        optional=audit_connected(*linked_pair(self.resources),ROOT,furniture=True)
        self.assertTrue(optional['passed'],{'errors':optional['errors'],'failed':[r for r in optional['checks'] if not r['passed']]})
        self.assertEqual(optional['counts']['total'],135)
        self.assertTrue(optional['furniture']['passed'])
        self.assertEqual(optional['normalization']['restored_map_cells'],18)
        self.assertFalse(audit_connected(*linked_pair(self.old),ROOT,furniture=True)['passed'])
        self.assertFalse(audit_connected(*linked_pair(self.old),ROOT,furniture=1)['passed'])

    def test_optional_mode_never_normalizes_a_corrupted_extension_or_old_data(self):
        for resources in (self.fault('gMetatiles_SFParkFrontage',120*16+9,16),
                          self.fault('OldaleTown_Layout_Blockdata',(7*40+19)*2+1,4),
                          self.fault('OldaleTown_Layout_Blockdata',(7*40+21)*2),
                          self.fault('gTilesetPalettes_SFParkFrontage',160),
                          self.fault('gMetatiles_SFParkFrontage',65*16+8)):
            result=audit_connected(*linked_pair(resources),ROOT,furniture=True)
            self.assertFalse(result['passed']);self.assertFalse(result['furniture']['passed'])
            self.assertNotIn('normalization',result)

    def test_every_prop_pixels_banks_flips_and_boundaries_are_observed(self):
        from check_creature_resources import decode_lz
        raw=decode_lz(self.resources['gTilesetTiles_SFParkFrontage'])
        for name,first in (('lamp',120),('meter',122),('hydrant',123),('bin',124),('rack',125),('tree',127),('bench',131),('recycling',133)):
            self.reject(self.fault('gMetatiles_SFParkFrontage',first*16+9,16),name+':native_pixels')
            resources=self.resources.copy();changed=bytearray(raw)
            tile=struct.unpack_from('<H',resources['gMetatiles_SFParkFrontage'],first*16+8)[0]&1023
            changed[tile*32]^=1;resources['gTilesetTiles_SFParkFrontage']=literal_lz(changed)
            self.reject(resources,name+':native_pixels')
        for flag in (4,8):
            for record in range(120,135):
                word=struct.unpack_from('<H',self.resources['gMetatiles_SFParkFrontage'],record*16+8)[0]
                tile=raw[(word&1023)*32:((word&1023)+1)*32]
                if flipped(tile,flag<<8)!=tile:
                    self.assertFalse(self.audit(self.fault('gMetatiles_SFParkFrontage',record*16+9,flag))['passed']);break
            else:self.fail('Furniture fixture needs asymmetric pixels.')

    def test_old_prefixes_and_both_complete_palettes_remain_exact(self):
        from check_creature_resources import decode_lz
        resources=self.resources.copy();raw=bytearray(decode_lz(resources['gTilesetTiles_SFParkFrontage']))
        raw[394*32]^=1;resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw)
        self.reject(resources,'original395_tile_prefix')
        self.reject(self.fault('gMetatiles_SFParkFrontage',119*16+8),'original120_record_prefix')
        self.reject(self.fault('gMetatileAttributes_SFParkFrontage',119*2),'original120_attribute_prefix')
        for bank in range(16):
            self.reject(self.fault('gTilesetPalettes_SFParkFrontage',bank*32),'complete_primary_palette')
            self.reject(self.fault('gTilesetPalettes_SFSouthPark',bank*32),'complete_secondary_palette')

    def test_all135_underlays_require_gray_bank4_and_cannot_reference_door_cache(self):
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFParkFrontage'])
        for index in range(135):records[index*16+1]^=16
        resources['gMetatiles_SFParkFrontage']=bytes(records);result=self.audit(resources)
        failed={row['name'] for row in result['checks'] if not row['passed']}
        self.assertTrue({'underlay_%03d'%i for i in range(135)}<=failed)
        for tile in (0,511,1016,1023):
            resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFParkFrontage'])
            struct.pack_into('<H',records,120*16,0x4000|tile);resources['gMetatiles_SFParkFrontage']=bytes(records)
            self.reject(resources,'underlay_120')
        self.reject(self.fault('gMetatiles_SFParkFrontage',120*16+1,8),'underlay_120')

    def test_upper_base_layer_roles_all18_map_cells_and_only14_collisions_are_exact(self):
        for record in range(120,135):
            self.reject(self.fault('gMetatileAttributes_SFParkFrontage',record*2+1,16),'all135_layer_attributes')
        for x,y,record,solid in CELLS:
            at=(y*40+x)*2
            self.reject(self.fault('OldaleTown_Layout_Blockdata',at),'all1280_map_words')
            for mask in (4,16):self.reject(self.fault('OldaleTown_Layout_Blockdata',at+1,mask),'all1280_collision_elevation')
        for x,y in ((21,7),(13,6),(32,6),(16,17),(20,5),(26,6),(7,26),(10,6),(29,6),(21,8),(26,18)):
            self.reject(self.fault('OldaleTown_Layout_Blockdata',(y*40+x)*2),'all1280_map_words')
        resources=self.resources.copy();blocks=bytearray(resources['OldaleTown_Layout_Blockdata'])
        struct.pack_into('<H',blocks,(7*40+18)*2,0x3C79);resources['OldaleTown_Layout_Blockdata']=bytes(blocks)
        self.reject(resources,'primary_map_footprint')

    def test_headers_layout_counts_residency_and_malformed_resources_fail_closed(self):
        from check_creature_resources import decode_lz
        for suffix in ('SFParkFrontage','SFSouthPark'):
            for at in (0,1,2,4,8,12,16,20):self.reject(self.fault('gTileset_'+suffix,at),suffix+':header')
        for at in (0,4,8,12,16,20):self.reject(self.fault('OldaleTown_Layout',at),'layout_binding')
        raw=decode_lz(self.resources['gTilesetTiles_SFParkFrontage'])
        resources=self.resources.copy();resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw+bytes(32))
        self.reject(rebind(resources),'primary_allocations')
        for symbol in self.resources:
            resources=self.resources.copy();del resources[symbol]
            if symbol.startswith('sSFPark') or symbol=='sDoorAnimGraphicsTable':continue
            self.assertFalse(self.audit(resources)['passed'])
        resources=self.resources.copy();resources['gTilesetTiles_SFParkFrontage']=b'\x10\xff\xff\xff'
        self.assertFalse(self.audit(resources)['passed'])
        resources=self.resources.copy();raw=decode_lz(resources['gTilesetTiles_SFSouthPark'])
        resources['gTilesetTiles_SFSouthPark']=literal_lz(raw+bytes((505-476)*32))
        self.assertFalse(self.audit(rebind(resources))['passed'])

    def test_source_and_self_rehashed_baseline_changes_cannot_override_acceptance(self):
        parent=ROOT/'.tools/city-furniture-audit-tests';parent.mkdir(parents=True,exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='case-',dir=parent))
        shutil.copytree(ASSET,root/ASSET.relative_to(ROOT))
        for path in (Path('assets/tiles/connected-frontage-v3/native.png'),
                     Path('assets/tiles/connected-frontage-v3/baseline-v76/secondary-palettes.gbapal'),
                     Path('assets/tiles/south-park-paving-v1/paving.indices')):
            (root/path).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/path,root/path)
        self.assertTrue(self.audit(root=root)['passed'])
        directory=root/ASSET.relative_to(ROOT)
        for name in ('source.png','prompt.md','conversion.json','furniture.gbapal','lamp.png','tree.indices',
                     'baseline-v77/primary.4bpp','baseline-v77/metatiles.bin','baseline-v77/attributes.bin',
                     'baseline-v77/palettes.gbapal','baseline-v77/south-park-map.bin','baseline-v77/receipt.json'):
            path=directory/name;old=path.read_bytes();path.write_bytes(old+b'bad')
            self.assertFalse(self.audit(root=root)['passed']);path.write_bytes(old)
        path=directory/'baseline-v77/south-park-map.bin';changed=bytearray(path.read_bytes());changed[0]^=1;path.write_bytes(changed)
        receipt=directory/'baseline-v77/receipt.json';info=json.loads(receipt.read_text())
        info['files'][path.name]['sha256']=hashlib.sha256(changed).hexdigest();receipt.write_text(json.dumps(info))
        self.assertFalse(self.audit(root=root)['passed'])


if __name__=='__main__':unittest.main()
