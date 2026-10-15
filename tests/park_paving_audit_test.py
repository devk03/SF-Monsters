"""Independent native paving pixels and bounded ROM/ELF fault vectors."""
from pathlib import Path
import json
import shutil
import struct
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/romhack'),str(ROOT/'scripts/quality'),str(ROOT/'tests')]
from park_paving_audit import audit_paving,compare_paving,decode_quadrant,candidate_quadrants
from trainer_portrait_audit_test import MemoryFile,literal_lz,linked_pair

FILES=('tiles.4bpp','metatiles.bin','attributes.bin','palettes.gbapal')
SYMBOLS=('gTilesetTiles_SFSouthPark','gMetatiles_SFSouthPark','gMetatileAttributes_SFSouthPark','gTilesetPalettes_SFSouthPark')
BASE=ROOT/'assets/tiles/south-park-paving-v1/baseline-v74'


def packed(pixels):
    return bytes(pixels[i]|pixels[i+1]<<4 for i in range(0,64,2))


def independent_fixture():
    old=tuple((BASE/name).read_bytes() for name in FILES)
    # 180-degree symmetry but neither individual reflection is a symmetry.
    # This permits all four native flip combinations with two reclaimed tiles.
    master=bytes(2 if (x,y) in {(1,2),(2,2),(6,5),(5,5)} else 1 for y in range(8) for x in range(8))
    pixels=bytes(master[(y%8)*8+x%8] for y in range(16) for x in range(16))
    mirrored=bytes(master[y*8+7-x] for y in range(8) for x in range(8))
    raw=bytearray(old[0]);raw[40*32:41*32]=packed(master);raw[41*32:42*32]=packed(mirrored)
    records=bytearray(old[1])
    # Specify the accepted exception table here, independently of the auditor.
    for record in range(150):
        for q in range(8):
            if (record in (16,19) and q in (4,5,6,7)) or (record>=40 and q in (0,1,2,3)):
                local=q%4;tile=552 if local in (0,3) else 553
                struct.pack_into('<H',records,record*16+q*2,6<<12|local<<10|tile)
    return old,(bytes(raw),bytes(records),old[2],old[3]),pixels


class PavingPixels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.old,cls.actual,cls.pixels=independent_fixture()

    def test_all1200_quadrants_and_four_flips_pass_independent_serialization(self):
        result=compare_paving(self.old,self.actual,self.pixels)
        self.assertTrue(result['passed'],result)
        self.assertEqual(result['counts'],{'total':152,'matched':152,'logical_quadrants_checked':1200,
            'paving_quadrants':448,'exact_nonresident_words':160,'resident_tiles':503})
        for q in range(4):
            word=struct.unpack_from('<H',self.actual[1],16*16+(q+4)*2)[0]
            self.assertEqual(decode_quadrant(self.actual[0],word),candidate_quadrants(self.pixels)[q])
        self.assertFalse(compare_paving(self.old,self.old,self.pixels)['passed'])

    def test_horizontal_vertical_and_combined_flips_have_distinct_native_axes(self):
        rows=[bytes((3*y+x)%16 for x in range(8)) for y in range(8)]
        raw=packed(b''.join(rows))
        for flags,expected in [(0,rows),(0x400,[r[::-1] for r in rows]),
                               (0x800,rows[::-1]),(0xc00,[r[::-1] for r in rows[::-1]])]:
            with self.subTest(flags=flags):self.assertEqual(decode_quadrant(raw,512|flags),b''.join(expected))

    def test_every_declared_paving_quadrant_requires_the_new_bank6_pixels(self):
        for record in (16,19,*range(40,150)):
            quadrants=range(4,8) if record<40 else range(4)
            for q in quadrants:
                actual=list(self.actual);records=bytearray(actual[1]);offset=record*16+q*2
                struct.pack_into('<H',records,offset,0x6200);actual[1]=bytes(records)
                with self.subTest(record=record,q=q):self.assertFalse(compare_paving(self.old,actual,self.pixels)['passed'])

    def test_unaffected_pixels_banks_and_each_single_flip_are_checked(self):
        actual=list(self.actual);raw=bytearray(actual[0]);raw[0]^=1;actual[0]=bytes(raw)
        self.assertFalse(compare_paving(self.old,actual,self.pixels)['passed'])
        for record,q in ((0,4),(40,4),(149,7),(16,4)):
            for mask in (0x1000,0x400,0x800):
                actual=list(self.actual);records=bytearray(actual[1]);offset=record*16+q*2
                word=struct.unpack_from('<H',records,offset)[0]^mask;struct.pack_into('<H',records,offset,word);actual[1]=bytes(records)
                # Use known asymmetric paving for flip faults, any bank change elsewhere.
                if mask==0x1000 or record==16:
                    with self.subTest(record=record,q=q,mask=mask):self.assertFalse(compare_paving(self.old,actual,self.pixels)['passed'])

    def test_complete_attributes_and_palette_all_bytes_remain_exact(self):
        for index in (2,3):
            for offset in (0,len(self.actual[index])//2,len(self.actual[index])-1):
                actual=list(self.actual);value=bytearray(actual[index]);value[offset]^=1;actual[index]=bytes(value)
                self.assertFalse(compare_paving(self.old,actual,self.pixels)['passed'])

    def test_reserved_nonresident_door_and_primary_blank_words_remain_literal(self):
        baseline=list(self.old);actual=list(self.actual)
        for resources in (baseline,actual):
            records=bytearray(resources[1]);struct.pack_into('<H',records,0,0x6000|0x400|1016);resources[1]=bytes(records)
        self.assertTrue(compare_paving(baseline,actual,self.pixels)['passed'])
        for offset,mask in ((0,1),(1,4),(1,16),(2,1)):
            changed=list(actual);records=bytearray(changed[1]);records[offset]^=mask;changed[1]=bytes(records)
            self.assertFalse(compare_paving(baseline,changed,self.pixels)['passed'])

    def test_resident504_limit_truncation_and_door_intrusion_fail_closed(self):
        actual=list(self.actual);actual[0]+=bytes(32)
        self.assertTrue(compare_paving(self.old,actual,self.pixels)['passed'])
        actual[0]+=bytes(32)
        with self.assertRaises(ValueError):compare_paving(self.old,actual,self.pixels)
        for index in range(4):
            actual=list(self.actual);actual[index]=actual[index][:-1]
            with self.subTest(index=index),self.assertRaises(ValueError):compare_paving(self.old,actual,self.pixels)
        for tile in (511,1015,1016,1023):
            actual=list(self.actual);records=bytearray(actual[1]);struct.pack_into('<H',records,16*16+8,0x6000|tile);actual[1]=bytes(records)
            self.assertFalse(compare_paving(self.old,actual,self.pixels)['passed'])
        actual=list(self.actual);actual[0]=actual[0][:32]
        self.assertFalse(compare_paving(self.old,actual,self.pixels)['passed'])

    def test_paving_shape_indices_transparency_and_repeat_contract(self):
        for pixels in (bytes(256),bytes([3])*256,bytes([1])*255):
            with self.assertRaises(ValueError):candidate_quadrants(pixels)
        pixels=bytearray(self.pixels);pixels[0]=3-pixels[0]
        with self.assertRaisesRegex(ValueError,'repeat'):candidate_quadrants(pixels)


class CompiledPaving(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old,cls.actual,cls.pixels=independent_fixture()
        parent=ROOT/'.tools/park-paving-audit-tests';parent.mkdir(parents=True,exist_ok=True)
        cls.root=Path(tempfile.mkdtemp(prefix='case-',dir=parent))
        cls.directory=cls.root/'assets/tiles/south-park-paving-v1'
        shutil.copytree(BASE,cls.directory/'baseline-v74')
        (cls.directory/'paving.indices').write_bytes(cls.pixels)

    def resources(self):return {name:literal_lz(value) if index==0 else value for index,(name,value) in enumerate(zip(SYMBOLS,self.actual))}

    def audit(self,resources=None):return audit_paving(*linked_pair(self.resources() if resources is None else resources),self.root)

    def test_compiled_resources_pass_and_report_hashes_without_art_approval(self):
        result=self.audit();self.assertTrue(result['passed'],result)
        self.assertEqual(result['counts']['logical_quadrants_checked'],1200)
        self.assertEqual(result['quality_approval'],'pending');self.assertTrue(result['hashes'])

    def test_missing_symbols_stale_rom_elf_malformed_lz_and_sections_fail(self):
        for name in SYMBOLS:
            resources=self.resources();del resources[name]
            self.assertFalse(self.audit(resources)['passed'])
        resources=self.resources();resources[SYMBOLS[0]]=b'bad'
        self.assertFalse(self.audit(resources)['passed'])
        rom,elf=linked_pair(self.resources());data=bytearray(rom.data);data[5]^=1
        self.assertFalse(audit_paving(MemoryFile(data),elf,self.root)['passed'])
        data=bytearray(elf.data);struct.pack_into('<I',data,96,8)
        self.assertFalse(audit_paving(rom,MemoryFile(data),self.root)['passed'])

    def test_rehashed_baseline_mutation_cannot_replace_the_pinned_original(self):
        parent=ROOT/'.tools/park-paving-audit-tests'
        root=Path(tempfile.mkdtemp(prefix='baseline-fault-',dir=parent))
        target=root/'assets/tiles/south-park-paving-v1'
        shutil.copytree(self.directory,target)
        path=target/'baseline-v74/attributes.bin';data=bytearray(path.read_bytes());data[0]^=1;path.write_bytes(data)
        import hashlib
        receipt=target/'baseline-v74/receipt.json';info=json.loads(receipt.read_text())
        info['files']['attributes.bin']['sha256']=hashlib.sha256(data).hexdigest();receipt.write_text(json.dumps(info))
        result=audit_paving(*linked_pair(self.resources()),root)
        self.assertFalse(result['passed']);self.assertTrue(any('Frozen original baseline differs' in e for e in result['errors']))


if __name__=='__main__':unittest.main()
