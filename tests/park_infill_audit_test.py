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
CARDS=(('brick',2,1,3,5,1,0),('sage',2,12,3,5,16,1),
       ('sandstone',2,20,3,5,31,2),('coffee',21,2,2,4,46,3))


def fixture():
    # Only the secondary resources use their existing source compiler.
    # Primary pixels, words, pointers and map cells below are serialized here.
    # The independent auditor checks the exact decoded paving delta.
    from park_map import park_resources
    secondary,old_records,old_attrs,old_palette=park_resources(ROOT)
    sidewalk=old_records[19*16+8:20*16]
    tiles=bytearray(32);records=bytearray(sidewalk+bytes(8));attrs=[0x1000]
    palette=bytearray(512);blocks=[0xE00]*(40*32)
    palette[128:160]=(ROOT/'assets/tiles/south-park-paving-v1/paving.gbapal').read_bytes()
    for name,left,top,width,height,first,bank in CARDS:
        with Image.open(ROOT/'assets/tiles/south-park-frontage-v1'/(name+'.png')) as image:
            pixels=image.tobytes()
        palette[bank*32:(bank+1)*32]=(ROOT/'assets/tiles/south-park-frontage-v1'/(name+'.gbapal')).read_bytes()
        for cell in range(width*height):
            words=[]
            for q in range(4):
                # Exercise every flip combination while retaining original pixels.
                flip=q<<10;tile=len(tiles)//32
                for y in range(8):
                    for x in range(0,8,2):
                        values=[]
                        for dx in range(2):
                            sx=7-(x+dx) if flip&0x400 else x+dx
                            sy=7-y if flip&0x800 else y
                            px=cell%width*16+q%2*8+sx
                            py=cell//width*16+q//2*8+sy
                            values.append(pixels[py*width*16+px])
                        tiles.append(values[0]|values[1]<<4)
                words.append(tile|flip|bank<<12)
            records.extend(sidewalk+struct.pack('<4H',*words))
            attrs.append(0x1000 if cell//width==height-1 else 0)
            blocks[(top+cell//width)*40+left+cell%width]=0xC00+first+cell
    resources={
        'gTilesetTiles_SFSouthPark':literal_lz(secondary),
        'gMetatiles_SFSouthPark':old_records,
        'gMetatileAttributes_SFSouthPark':old_attrs,
        'gTilesetPalettes_SFSouthPark':old_palette,
        'gTilesetTiles_SFParkFrontage':literal_lz(tiles),
        'gMetatiles_SFParkFrontage':bytes(records),
        'gMetatileAttributes_SFParkFrontage':struct.pack('<54H',*attrs),
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
        self.assertEqual(result['counts'],{'total':22,'matched':22})
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
            resources=self.resources.copy();raw=bytearray(32*213)
            resources['gTilesetTiles_SFParkFrontage']=literal_lz(raw)
            self.reject(resources,name+':all_native_pixels')

    def test_all_underlays_and_layer_attributes_are_checked(self):
        for record in range(54):
            self.reject(self.fault('gMetatiles_SFParkFrontage',record*16),'all54_secondary_underlays')
            self.reject(self.fault('gMetatileAttributes_SFParkFrontage',record*2),'all54_layer_attributes')
        self.reject(self.fault('gMetatiles_SFParkFrontage',8),'primary_empty_metatile0')

    def test_full_palette_including_unused_tail_is_checked(self):
        for offset in (0,32,64,96,128,511):
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
        self.assertTrue(self.audit(root=root)['passed'])
        (target/'brick.indices').write_bytes(b'bad')
        result=self.audit(root=root)
        self.assertFalse(result['passed'])
        self.assertIn('Original card file differs: brick.indices',result['errors'])


if __name__=='__main__':unittest.main()
