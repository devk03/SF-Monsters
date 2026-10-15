"""Independent linked ARM fixtures for compiled service art and native doors."""
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
from service_architecture_audit import audit_services
from connected_frontage_audit import cell_pixels
from trainer_portrait_audit_test import MemoryFile,addresses,literal_lz,linked_pair

BASE=ROOT/'assets/tiles/connected-frontage-v3/baseline-v76'
SERVICE=ROOT/'assets/tiles/south-park-services-v3'
DOORS=ROOT/'assets/tiles/service-door-v2'


def packed(pixels):
    return bytes(pixels[i]|pixels[i+1]<<4 for i in range(0,64,2))


def flipped(blob,bits):
    pixels=[value>>shift&15 for value in blob for shift in (0,4)]
    return packed(bytes(pixels[(7-y if bits&0x800 else y)*8+(7-x if bits&0x400 else x)]
                        for y in range(8) for x in range(8)))


def door_bytes(frames):
    # Independent eight-tile row order for each16x32 stage.
    return b''.join(packed(bytes(frame[(ty*8+y)*16+tx*8+x] for y in range(8) for x in range(8)))
                    for frame in frames for ty in range(4) for tx in range(2))


def fixture():
    old_raw=(BASE/'secondary.4bpp').read_bytes()
    old_records=(BASE/'secondary-metatiles.bin').read_bytes()
    cells=[cell_pixels(old_raw,struct.unpack_from('<4H',old_records,i*16+8),secondary=True) for i in range(150)]
    banks=[tuple(word>>12 for word in struct.unpack_from('<4H',old_records,i*16+8)) for i in range(150)]
    body=(SERVICE/'buildings.indices').read_bytes()
    stages={name:[(DOORS/(name+'.indices')).read_bytes()[i*512:(i+1)*512] for i in range(3)]
            for name in ('warehouse','clinic')}
    for number,(name,first,bank,upper,lower) in enumerate((('warehouse',40,8,64,71),('clinic',75,9,99,106))):
        frame=body[number*8960:(number+1)*8960]
        for cell in range(35):
            cells[first+cell]=b''.join(frame[(cell//7*16+y)*112+cell%7*16:
                (cell//7*16+y)*112+cell%7*16+16] for y in range(16))
            banks[first+cell]=(bank,)*4
        cells[upper],cells[lower]=stages[name][0][:256],stages[name][0][256:]
    raw=bytearray();records=bytearray();pool={}
    for i,(pixels,cell_banks) in enumerate(zip(cells,banks)):
        words=[]
        for q in range(4):
            blob=packed(bytes(pixels[(q//2*8+y)*16+q%2*8+x] for y in range(8) for x in range(8)))
            if blob not in pool:
                tile=len(raw)//32
                orientation=q<<10
                stored=flipped(blob,orientation);raw.extend(stored)
                for bits in (0,0x400,0x800,0xC00):pool.setdefault(flipped(stored,bits),(tile,bits))
            tile,bits=pool[blob];words.append(cell_banks[q]<<12|bits|512+tile)
        records.extend(bytes(8)+struct.pack('<4H',*words))
    if len(raw)>476*32:raise ValueError('Independent service fixture exceeds476 resident tiles.')
    raw.extend(bytes(476*32-len(raw)))
    sidewalk=records[19*16+8:20*16]
    for i in range(40,150):records[i*16:i*16+8]=sidewalk
    palette=bytearray((BASE/'secondary-palettes.gbapal').read_bytes())
    palette[8*32:10*32]=(SERVICE/'building-palettes.gbapal').read_bytes()
    resources={
        'gTilesetTiles_SFSouthPark':literal_lz(raw),
        'gMetatiles_SFSouthPark':bytes(records),
        'gMetatileAttributes_SFSouthPark':(BASE/'secondary-attributes.bin').read_bytes(),
        'gTilesetPalettes_SFSouthPark':bytes(palette),
        'sSFParkWarehouseDoor':door_bytes(stages['warehouse']),
        'sSFParkClinicDoor':door_bytes(stages['clinic']),
        'sSFParkWarehousePalette':bytes([8])*8,
        'sSFParkClinicPalette':bytes([9])*8,
        'sDoorAnimGraphicsTable':bytes(48),
    }
    location=addresses(resources)
    rows=[(583,0,1,location['sSFParkWarehouseDoor'],location['sSFParkWarehousePalette']),
          (618,0,1,location['sSFParkClinicDoor'],location['sSFParkClinicPalette']),
          (700,1,2,0x08000000,0x08000000), # Unrelated synthetic registration, not commercial data.
          (0,0,0,0,0)]
    resources['sDoorAnimGraphicsTable']=b''.join(struct.pack('<HBBII',*row) for row in rows)
    return resources


class ServiceArchitectureAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.resources=fixture()

    def audit(self,resources=None,root=ROOT):
        return audit_services(*linked_pair(self.resources if resources is None else resources),root)

    def fault(self,symbol,offset,mask=1):
        resources=self.resources.copy();blob=bytearray(resources[symbol]);blob[offset]^=mask
        resources[symbol]=bytes(blob);return resources

    def reject(self,resources,target):
        result=self.audit(resources)
        self.assertFalse(result['passed'])
        self.assertTrue(any(row['name']==target and not row['passed'] for row in result['checks']),
            {'target':target,'errors':result['errors'],'failed':[row['name'] for row in result['checks'] if not row['passed']]})

    def copy_sources(self):
        parent=ROOT/'.tools/service-architecture-audit-tests';parent.mkdir(parents=True,exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='case-',dir=parent))
        for directory in (SERVICE,DOORS,BASE):shutil.copytree(directory,root/directory.relative_to(ROOT))
        reference=Path('assets/tiles/south-park-services-v2/source.png')
        (root/reference).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/reference,root/reference)
        return root

    def test_linked_original_only_body_and_door_resources_pass(self):
        result=self.audit()
        self.assertTrue(result['passed'],{'errors':result['errors'],'failed':[row for row in result['checks'] if not row['passed']]})
        self.assertEqual(result['quality_approval'],'pending')
        self.assertEqual(result['counts']['foreground_cells'],150)
        self.assertEqual(result['counts']['preserved_cells'],80)
        self.assertEqual(result['counts']['service_cells'],70)
        self.assertEqual(result['counts']['static_door_cells'],4)
        self.assertEqual(result['counts']['door_stages'],6)
        self.assertEqual(result['counts']['secondary_tiles'],476)
        self.assertEqual(result['counts']['matched'],result['counts']['total'])

    def test_each_foreground_cell_rejects_bank_change_including_all_preserved_cells(self):
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFSouthPark'])
        for index in range(150):records[index*16+9]^=16
        resources['gMetatiles_SFSouthPark']=bytes(records)
        result=self.audit(resources)
        failed={row['name'] for row in result['checks'] if not row['passed']}
        self.assertFalse(result['passed'])
        self.assertTrue({'foreground_%03d'%i for i in range(150)}<=failed)

    def test_body_unchanged_pixels_and_native_flips_are_checked(self):
        from check_creature_resources import decode_lz
        original=decode_lz(self.resources['gTilesetTiles_SFSouthPark'])
        for index in (0,19,39,40,74,75,109,110,149):
            resources=self.resources.copy();raw=bytearray(original)
            tile=struct.unpack_from('<H',resources['gMetatiles_SFSouthPark'],index*16+8)[0]&1023
            raw[(tile-512)*32]^=1;resources['gTilesetTiles_SFSouthPark']=literal_lz(raw)
            with self.subTest(index=index):self.reject(resources,'foreground_%03d'%index)
        for flag in (4,8):
            for index in range(40,110):
                word=struct.unpack_from('<H',self.resources['gMetatiles_SFSouthPark'],index*16+8)[0]
                tile=original[((word&1023)-512)*32:((word&1023)-511)*32]
                if flipped(tile,flag<<8)!=tile:
                    self.reject(self.fault('gMetatiles_SFSouthPark',index*16+9,flag),'foreground_%03d'%index);break
            else:self.fail('Need an asymmetric service foreground tile.')

    def test_all_literal_zero_and_gray_underlays_reject_mutations_and_cache_leaks(self):
        for index in (0,1,19,39):
            self.reject(self.fault('gMetatiles_SFSouthPark',index*16),'first40_literal_zero_underlays')
        resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFSouthPark'])
        for index in range(40,150):records[index*16+1]^=16
        resources['gMetatiles_SFSouthPark']=bytes(records)
        result=self.audit(resources)
        failed={row['name'] for row in result['checks'] if not row['passed']}
        self.assertFalse(result['passed'])
        self.assertTrue({'underlay_%03d'%i for i in range(40,150)}<=failed)
        for tile in (0,511,988,1015,1016,1023):
            resources=self.resources.copy();records=bytearray(resources['gMetatiles_SFSouthPark'])
            struct.pack_into('<H',records,40*16,0x4000|tile);resources['gMetatiles_SFSouthPark']=bytes(records)
            self.reject(resources,'underlay_040')
        self.reject(self.fault('gMetatiles_SFSouthPark',40*16+1,8),'underlay_040')

    def test_all_attributes_and_palette_bytes_are_preserved_except_reviewed_service_banks(self):
        for index in (0,24,40,64,71,99,106,119,148,149):
            self.reject(self.fault('gMetatileAttributes_SFSouthPark',index*2+1,16),'all150_attributes')
        for offset in (0,4*32,6*32,7*32,8*32,9*32,10*32,12*32,511):
            self.reject(self.fault('gTilesetPalettes_SFSouthPark',offset),'complete_secondary_palette')

    def test_closed_static_cells_equal_the_registered_frame0(self):
        for title,indices in (('warehouse',(64,71)),('clinic',(99,106))):
            for index in indices:
                self.reject(self.fault('gMetatiles_SFSouthPark',index*16+8),title+':static_closed_frame')

    def test_native_animation_bytes_stage_order_and_eight_selectors_are_exact(self):
        for title in ('Warehouse','Clinic'):
            symbol='sSFPark'+title+'Door';target=title.lower()
            for stage in range(3):self.reject(self.fault(symbol,stage*256+100),target+':animation_bytes')
            resources=self.resources.copy();payload=resources[symbol]
            resources[symbol]=payload[256:512]+payload[:256]+payload[512:]
            self.reject(resources,target+':animation_decoded_stages')
            for index in range(8):
                self.reject(self.fault('sSFPark'+title+'Palette',index),target+':palette_selectors')

    def test_moving_rectangle_stationary_edges_opaque_portal_and_distinct_stages(self):
        for title in ('Warehouse','Clinic'):
            symbol='sSFPark'+title+'Door';target=title.lower()
            # Pixel(0,0), stage1 lies outside the moving rectangle.
            self.reject(self.fault(symbol,256),target+':animation_rectangle')
            resources=self.resources.copy();payload=bytearray(resources[symbol])
            # Pixel(3,5), stage1 must remain opaque; clear its high nibble.
            at=256+5*4+1;payload[at]&=15;resources[symbol]=bytes(payload)
            self.reject(resources,target+':animation_rectangle')
            resources=self.resources.copy();payload=resources[symbol]
            resources[symbol]=payload[:256]*2+payload[512:]
            self.reject(resources,target+':animation_rectangle')

    def test_service_door_table_requires_unique_native_registration_before_null(self):
        for row in (0,1):
            for offset in (0,2,3,4,8):
                with self.subTest(row=row,offset=offset):
                    self.reject(self.fault('sDoorAnimGraphicsTable',row*12+offset),'door_registration')
        resources=self.resources.copy();table=bytearray(resources['sDoorAnimGraphicsTable'])
        table[12:24]=table[:12];resources['sDoorAnimGraphicsTable']=bytes(table)
        self.reject(resources,'door_registration')
        for row in (0,1,2):
            resources=self.resources.copy();table=bytearray(resources['sDoorAnimGraphicsTable'])
            table[row*12:(row+1)*12]=bytes(12);resources['sDoorAnimGraphicsTable']=bytes(table)
            self.reject(resources,'door_registration')
        self.reject(self.fault('sDoorAnimGraphicsTable',36),'door_registration')
        self.reject(self.fault('sDoorAnimGraphicsTable',40),'door_registration')
        # The gate does not freeze ordering or unrelated entries/timing.
        resources=self.resources.copy();table=resources['sDoorAnimGraphicsTable']
        resources['sDoorAnimGraphicsTable']=table[12:24]+table[:12]+table[24:]
        self.assertTrue(self.audit(resources)['passed'])
        self.assertTrue(self.audit(self.fault('sDoorAnimGraphicsTable',26))['passed'])

    def test_exact_allocations_malformed_lz_missing_symbols_and_stale_elf_fail(self):
        from check_creature_resources import decode_lz
        for name in self.resources:
            resources=self.resources.copy();del resources[name]
            with self.subTest(missing=name):self.assertFalse(self.audit(resources)['passed'])
        for name in self.resources:
            resources=self.resources.copy();resources[name]=resources[name][:-1]
            with self.subTest(truncated=name):self.assertFalse(self.audit(resources)['passed'])
        raw=decode_lz(self.resources['gTilesetTiles_SFSouthPark'])
        for count in (475,477,505):
            resources=self.resources.copy();resized=raw[:count*32]+bytes(max(0,count*32-len(raw)))
            resources['gTilesetTiles_SFSouthPark']=literal_lz(resized)
            self.reject(resources,'secondary_allocations')
        resources=self.resources.copy();resources['gTilesetTiles_SFSouthPark']=b'\x10\xff\xff\xff'
        self.assertFalse(self.audit(resources)['passed'])
        rom,elf=linked_pair(self.resources);changed=bytearray(rom.data);changed[5]^=1
        self.assertFalse(audit_services(MemoryFile(changed),elf,ROOT)['passed'])
        changed=bytearray(elf.data);struct.pack_into('<I',changed,96,8)
        self.assertFalse(audit_services(rom,MemoryFile(changed),ROOT)['passed'])

    def test_pinned_provenance_pixels_and_self_rehashed_receipts_fail_closed(self):
        root=self.copy_sources()
        paths=(SERVICE/'source.png',SERVICE/'prompt.md',SERVICE/'conversion.json',SERVICE/'warehouse.png',
               SERVICE/'buildings.indices',SERVICE/'building-palettes.gbapal',DOORS/'source.png',
               DOORS/'prompt.md',DOORS/'conversion.json',DOORS/'clinic.png',DOORS/'clinic.indices',
               DOORS/'clinic.4bpp',DOORS/'clinic-closed-reference.png',BASE/'secondary.4bpp',
               BASE/'secondary-metatiles.bin',BASE/'secondary-attributes.bin',BASE/'secondary-palettes.gbapal',BASE/'receipt.json')
        for original_path in paths:
            path=root/original_path.relative_to(ROOT);original=path.read_bytes()
            path.write_bytes(bytes([original[0]^1])+original[1:])
            with self.subTest(path=str(original_path)):self.assertFalse(self.audit(root=root)['passed'])
            path.write_bytes(original)
        path=root/DOORS.relative_to(ROOT)/'clinic.indices';changed=bytearray(path.read_bytes());changed[100]^=1;path.write_bytes(changed)
        receipt=root/DOORS.relative_to(ROOT)/'conversion.json';info=json.loads(receipt.read_text())
        info['files']['clinic.indices']=hashlib.sha256(changed).hexdigest();receipt.write_text(json.dumps(info))
        self.assertFalse(self.audit(root=root)['passed'])


if __name__=='__main__':unittest.main()
