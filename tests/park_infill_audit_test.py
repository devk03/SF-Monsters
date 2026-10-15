"""Independent native ROM/ELF fault vectors for South Park primary frontage."""
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/romhack'),str(ROOT/'scripts/quality'),str(ROOT/'tests')]
from park_infill_audit import audit_infill
from trainer_portrait_audit_test import MemoryFile,addresses,literal_lz,linked_pair

# Deliberately independent of both the producer and auditor placement constants.
APRON_ROWS=((2,6,(60,61,62)),(2,17,(57,58,59)),(2,25,(54,55,56)),
    (21,6,(63,64)),(18,6,(60,61,62)),(23,6,(60,61,62)),(26,6,(60,61,62)),
    (11,17,(60,61,62,60,61,62)),(11,24,(60,61,62,60,61,62)),
    (11,6,(54,54,55,56,56,56)),(30,6,(54,54,55,56,56,56)))
CARDS=(('brick',2,1,3,5,1,0),('sage',2,12,3,5,16,1),
       ('sandstone',2,20,3,5,31,2),('coffee',21,2,2,4,46,3))


def fixture():
    # This remains a historical v76 audit. Freeze its original secondary bytes
    # while the current producer installs the user-requested architectural art.
    frozen=ROOT/'assets/tiles/connected-frontage-v3/baseline-v76'
    secondary,old_records,old_attrs,old_palette=((frozen/name).read_bytes() for name in
        ('secondary.4bpp','secondary-metatiles.bin','secondary-attributes.bin','secondary-palettes.gbapal'))
    sidewalk=old_records[19*16+8:20*16]
    baseline=ROOT/'assets/tiles/sidewalk-thresholds-v1/baseline-v75'
    tiles=bytearray((baseline/'primary.4bpp').read_bytes())
    records=bytearray((baseline/'metatiles.bin').read_bytes())
    attrs=list(struct.unpack('<54H',(baseline/'attributes.bin').read_bytes()))
    palette=bytearray((baseline/'palettes.gbapal').read_bytes())
    blocks=list(struct.unpack('<1280H',(baseline/'south-park-map.bin').read_bytes()))
    directory=ROOT/'assets/tiles/sidewalk-thresholds-v1'
    palette[160:192]=(directory/'thresholds.gbapal').read_bytes()
    pool={bytes(32):0}
    for name,width,first in [('brick',48,54),('sage',48,57),('bay',48,60),('coffee',32,63)]:
        pixels=(directory/(name+'.indices')).read_bytes()
        if name=='coffee':
            pixels=b''.join(pixels[start:start+width][::-1] for start in range(0,len(pixels),width))
        for cell in range(width//16):
            words=[]
            for q in range(4):
                # New apron fixture exercises flipped native tiles independently.
                flip=q<<10;encoded=bytearray()
                for y in range(8):
                    for x in range(0,8,2):
                        pair=[]
                        for dx in range(2):
                            sx=7-x-dx if flip&0x400 else x+dx
                            sy=7-y if flip&0x800 else y
                            pair.append(pixels[(q//2*8+sy)*width+cell*16+q%2*8+sx])
                        encoded.append(pair[0]|pair[1]<<4)
                blob=bytes(encoded)
                if blob not in pool:
                    pool[blob]=len(tiles)//32;tiles.extend(blob)
                words.append(pool[blob]|flip|5<<12)
            records.extend(sidewalk+struct.pack('<4H',*words));attrs.append(0x1000)
    if len(tiles)!=235*32:raise ValueError('Independent apron fixture must fit235 tiles.')
    for left,top,ids in APRON_ROWS:
        for x,tile in enumerate(ids):blocks[top*40+left+x]=0x3000|tile
    resources={
        'gTilesetTiles_SFSouthPark':literal_lz(secondary),
        'gMetatiles_SFSouthPark':old_records,
        'gMetatileAttributes_SFSouthPark':old_attrs,
        'gTilesetPalettes_SFSouthPark':old_palette,
        'gTilesetTiles_SFParkFrontage':literal_lz(tiles),
        'gMetatiles_SFParkFrontage':bytes(records),
        'gMetatileAttributes_SFParkFrontage':struct.pack('<65H',*attrs),
        'gTilesetPalettes_SFParkFrontage':bytes(palette),
        'gTileset_SFParkFrontage':bytes(24),'gTileset_SFSouthPark':bytes(24),
        'OldaleTown_Layout':bytes(24),
        'OldaleTown_Layout_Blockdata':struct.pack('<1280H',*blocks)}
    locations=addresses(resources)
    for suffix,secondary_flag in [('SFParkFrontage',0),('SFSouthPark',1)]:
        resources['gTileset_'+suffix]=struct.pack('<BB2x5I',1,secondary_flag,
            *(locations[p+suffix] for p in ['gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_']),0)
    resources['OldaleTown_Layout']=struct.pack('<ii4I',40,32,locations['OldaleTown_Layout_Blockdata'],
        locations['OldaleTown_Layout_Blockdata'],locations['gTileset_SFParkFrontage'],locations['gTileset_SFSouthPark'])
    return resources


class ParkInfillAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.resources=fixture()

    def audit(self,resources=None,root=ROOT):
        return audit_infill(*linked_pair(self.resources if resources is None else resources),root)

    def fault(self,symbol,offset,mask=1):
        resources=self.resources.copy();data=bytearray(resources[symbol]);data[offset]^=mask
        resources[symbol]=bytes(data);return resources

    def reject(self,resources,target):
        result=self.audit(resources)
        self.assertFalse(result['passed'])
        self.assertTrue(any(c['name']==target and not c['passed'] for c in result['checks']),result)

    def test_original_pixels_all_flip_states_and_bindings_pass_without_artifact_writes(self):
        result=self.audit()
        self.assertTrue(result['passed'],result)
        self.assertEqual(result['counts']['total'],result['counts']['matched'])
        self.assertGreaterEqual(result['counts']['total'],40)
        self.assertTrue(result['paving']['passed'])
        self.assertEqual(result['paving']['counts']['logical_quadrants_checked'],1200)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['quality_approval'],'pending')

    def test_both_native_headers_reject_flags_every_pointer_and_callbacks(self):
        for name in ('gTileset_SFParkFrontage','gTileset_SFSouthPark'):
            for offset in (0,1,2,4,8,12,16,20):
                with self.subTest(name=name,offset=offset):
                    self.reject(self.fault(name,offset),name+':binding')

    def test_layout_rejects_dimensions_pointers_and_invalid_border(self):
        for offset in (0,4,8,12,16,20):
            with self.subTest(offset=offset):
                self.reject(self.fault('OldaleTown_Layout',offset),'layout_binding')

    def test_every_map_cell_rejects_id_collision_and_elevation_changes(self):
        for name,left,top,width,height,first,bank in CARDS:
            for y in range(height):
                for x in range(width):
                    offset=((top+y)*40+left+x)*2
                    for byte,mask in ((0,1),(1,4),(1,16)):
                        with self.subTest(card=name,x=x,y=y,mask=mask):
                            self.reject(self.fault('OldaleTown_Layout_Blockdata',offset+byte,mask),name+':solid_map_cells')
        self.reject(self.fault('OldaleTown_Layout_Blockdata',1,2),'primary_map_footprint')

    def test_all_cards_reject_wrong_bank_foreground_pixel_and_flip(self):
        for name,left,top,width,height,first,bank in CARDS:
            at=first*16+8
            self.reject(self.fault('gMetatiles_SFParkFrontage',at+1,16),name+':all_native_pixels')
            # Check the complete image; find a non-symmetric quadrant for each flip.
            for flip in (4,8):
                candidates=[self.fault('gMetatiles_SFParkFrontage',(first+i)*16+9+q*2,flip)
                    for i in range(width*height) for q in range(4)]
                self.assertTrue(any(not self.audit(r)['passed'] for r in candidates))
            resources=self.resources.copy();raw=bytearray(32*235)
            resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw)
            self.reject(resources,name+':all_native_pixels')

    def test_all_underlays_and_layer_attributes_are_checked(self):
        for record in range(65):
            self.reject(self.fault('gMetatiles_SFParkFrontage',record*16),'all65_secondary_underlays')
            self.reject(self.fault('gMetatileAttributes_SFParkFrontage',record*2),'all65_layer_attributes')
        self.reject(self.fault('gMetatiles_SFParkFrontage',8),'primary_empty_metatile0')

    def test_full_palette_including_unused_tail_is_checked(self):
        for offset in (0,32,64,96,128,160,511):
            self.reject(self.fault('gTilesetPalettes_SFParkFrontage',offset),'all_primary_palette_bytes')

    def test_secondary_paving_delta_is_bounded_and_door_vram_is_reserved(self):
        for name in ('gTilesetTiles_SFSouthPark','gMetatiles_SFSouthPark',
                     'gMetatileAttributes_SFSouthPark','gTilesetPalettes_SFSouthPark'):
            target = 'secondary_paving_delta' if name in ('gTilesetTiles_SFSouthPark',
                'gMetatiles_SFSouthPark') else name+':preserved'
            self.reject(self.fault(name,5),target)
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFSouthPark'])
        struct.pack_into('<H',records,0,1016)
        resources['gMetatiles_SFSouthPark']=bytes(records)
        self.reject(resources,'resident_door_reservation')

    def test_every_apron_cell_rejects_id_collision_elevation_and_location_changes(self):
        for left,top,ids in APRON_ROWS:
            for x,tile in enumerate(ids):
                offset=(top*40+left+x)*2
                for byte,mask in ((0,1),(1,4),(1,16)):
                    with self.subTest(x=left+x,y=top,mask=mask):
                        self.reject(self.fault('OldaleTown_Layout_Blockdata',offset+byte,mask),
                                    'apron_map_%d_%d'%(left,top))
        resources=self.resources.copy();blocks=bytearray(resources['OldaleTown_Layout_Blockdata'])
        # Move a threshold onto an undeclared adjacent P cell, restoring its old cell.
        struct.pack_into('<H',blocks,(6*40+2)*2,0x3213)
        struct.pack_into('<H',blocks,(6*40+1)*2,0x3036)
        resources['OldaleTown_Layout_Blockdata']=bytes(blocks)
        self.reject(resources,'primary_map_footprint')

    def test_all_nonapron_map_words_protect_roads_doors_signs_and_other_collisions(self):
        for x,y in ((0,0),(7,8),(13,5),(32,5),(16,16),(10,6),(29,6),(21,8),(38,30)):
            with self.subTest(x=x,y=y):
                self.reject(self.fault('OldaleTown_Layout_Blockdata',(y*40+x)*2),
                            'all_nonapron_map_words')

    def test_each_apron_rejects_native_pixel_palette_and_foreground_bank_changes(self):
        from check_creature_resources import decode_lz
        for name,first in [('brick',54),('sage',57),('bay',60),('coffee',63)]:
            self.reject(self.fault('gMetatiles_SFParkFrontage',first*16+9,16),
                        name+':apron_native_pixels')
            resources=self.resources.copy()
            raw=bytearray(decode_lz(resources['gTilesetTiles_SFParkFrontage']))
            tile=struct.unpack_from('<H',resources['gMetatiles_SFParkFrontage'],first*16+8)[0]&1023
            raw[tile*32]^=1
            resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw)
            self.reject(resources,name+':apron_native_pixels')
        self.reject(self.fault('gTilesetPalettes_SFParkFrontage',160),'all_primary_palette_bytes')
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFParkFrontage'])
        struct.pack_into('<H',records,54*16+8,5<<12|1016)
        resources['gMetatiles_SFParkFrontage']=bytes(records)
        self.reject(resources,'resident_door_reservation')

    def test_frozen_old_prefixes_reject_equivalent_resource_rebindings(self):
        # No old resource may be repacked merely because its decoded art matches.
        self.reject(self.fault('gMetatiles_SFParkFrontage',16+8),'original54_record_prefix')
        self.reject(self.fault('gMetatileAttributes_SFParkFrontage',0),'original54_attribute_prefix')
        from check_creature_resources import decode_lz
        resources=self.resources.copy();raw=bytearray(decode_lz(resources['gTilesetTiles_SFParkFrontage']))
        raw[32]^=1;resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw)
        self.reject(resources,'original213_tile_prefix')

    def test_apron_source_and_self_rehashed_baseline_faults_fail_closed(self):
        import hashlib,json
        parent=ROOT/'.tools/park-infill-audit-tests';parent.mkdir(parents=True,exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='apron-',dir=parent))
        for name in ('south-park-frontage-v1','south-park-paving-v1','sidewalk-thresholds-v1'):
            shutil.copytree(ROOT/'assets/tiles'/name,root/'assets/tiles'/name)
        directory=root/'assets/tiles/sidewalk-thresholds-v1'
        for filename in ('source.png','prompt.md','thresholds.gbapal','brick.png','brick.indices','conversion.json'):
            path=directory/filename;original=path.read_bytes();path.write_bytes(original+b'bad')
            with self.subTest(file=filename):self.assertFalse(self.audit(root=root)['passed'])
            path.write_bytes(original)
        baseline=directory/'baseline-v75'
        for filename in ('primary.4bpp','metatiles.bin','attributes.bin','palettes.gbapal','south-park-map.bin','receipt.json'):
            path=baseline/filename;original=path.read_bytes();changed=bytes([original[0]^1])+original[1:]
            path.write_bytes(changed)
            with self.subTest(baseline=filename):self.assertFalse(self.audit(root=root)['passed'])
            path.write_bytes(original)
        # Updating a baseline's own manifest never authorizes changing its bytes.
        path=baseline/'south-park-map.bin';changed=bytearray(path.read_bytes());changed[0]^=1;path.write_bytes(changed)
        receipt=json.loads((baseline/'receipt.json').read_text())
        receipt['files']['south-park-map.bin']['sha256']=hashlib.sha256(changed).hexdigest()
        (baseline/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        self.assertFalse(self.audit(root=root)['passed'])

    def test_missing_symbols_and_truncated_native_resources_fail_closed(self):
        for name in self.resources:
            resources=self.resources.copy();del resources[name]
            with self.subTest(missing=name):self.assertFalse(self.audit(resources)['passed'])
        for name in self.resources:
            resources=self.resources.copy();resources[name]=resources[name][:-1]
            with self.subTest(truncated=name):self.assertFalse(self.audit(resources)['passed'])

    def test_primary_tile0_count_and_lz_bounds_are_checked(self):
        from check_creature_resources import decode_lz
        raw=decode_lz(self.resources['gTilesetTiles_SFParkFrontage'])
        resources=self.resources.copy();changed=bytearray(raw);changed[0]=1
        resources['gTilesetTiles_SFParkFrontage']=literal_lz(changed)
        self.reject(resources,'transparent_primary_tile0')
        resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw+bytes(32))
        self.reject(resources,'primary_allocations')
        for payload in (b'bad',b'\x10\xff\xff\xff'):
            resources['gTilesetTiles_SFParkFrontage']=payload
            self.assertFalse(self.audit(resources)['passed'])

    def test_stale_rom_elf_and_non_file_backed_section_are_rejected(self):
        rom,elf=linked_pair(self.resources)
        changed=bytearray(rom.data);changed[5]^=1
        result=audit_infill(MemoryFile(changed),elf,ROOT)
        self.assertFalse(result['passed'])
        self.assertTrue(any('ROM/ELF resource bytes differ' in e for e in result['errors']))
        changed=bytearray(elf.data);struct.pack_into('<I',changed,96,8) # SHT_NOBITS
        self.assertFalse(audit_infill(rom,MemoryFile(changed),ROOT)['passed'])
        self.assertFalse(audit_infill(MemoryFile(b''),MemoryFile(b'bad'),ROOT)['passed'])

    def test_source_receipt_faults_fail_without_writing_to_source_assets(self):
        parent=ROOT/'.tools/park-infill-audit-tests';parent.mkdir(parents=True,exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='case-',dir=parent))
        target=root/'assets/tiles/south-park-frontage-v1'
        shutil.copytree(ROOT/'assets/tiles/south-park-frontage-v1',target)
        shutil.copytree(ROOT/'assets/tiles/south-park-paving-v1',
                        root/'assets/tiles/south-park-paving-v1')
        shutil.copytree(ROOT/'assets/tiles/sidewalk-thresholds-v1',
                        root/'assets/tiles/sidewalk-thresholds-v1')
        self.assertTrue(self.audit(root=root)['passed'])
        (target/'brick.indices').write_bytes(b'bad')
        result=self.audit(root=root)
        self.assertFalse(result['passed'])
        self.assertIn('Original card file differs: brick.indices',result['errors'])


if __name__=='__main__':unittest.main()
