"""Catch visually wrong linked tiles/palettes even when collision still passes."""
import importlib.util,json,struct,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from world_resource_audit import audit_resources


class WorldResourceTests(unittest.TestCase):
    def setUp(self):
        self.folder=Path(tempfile.mkdtemp(prefix='world-resources-',dir=ROOT/'.tools'))
        self.directory=self.folder/'data/tilesets/secondary/sf_world_nature';self.directory.mkdir(parents=True)
        image=Image.new('P',(128,256),3);image.putpalette([v for i in range(256) for v in (i,i,i)])
        image.save(self.directory/'tiles.png',bits=4)
        graphics=bytes([0x33])*16384
        packed=bytearray(b'\x10\x00\x40\x00')
        for start in range(0,len(graphics),8):packed+=bytes([0])+graphics[start:start+8]
        self.rom=bytearray(0x6400);self.rom[0x200:0x200+len(packed)]=packed
        struct.pack_into('<4I',self.rom,0x104,0x08000200,0x08006000,0x08006200,0x08006300)
        for name,offset,data in [('metatiles',0x6200,struct.pack('<8H',*([0x6200]*8))),
                                 ('metatile_attributes',0x6300,struct.pack('<H',0x1000)),
                                 ('palettes',0x6000,bytes(512))]:
            (self.directory/(name+'.gbapal' if name=='palettes' else name+'.bin')).write_bytes(data)
            self.rom[offset:offset+len(data)]=data

    def audit(self):
        def read(address,fmt):return struct.unpack_from('<'+fmt,self.rom,address-0x08000000)
        return audit_resources(bytes(self.rom),read,0x08000100,'nature',self.folder)

    def test_matching_normal_inputs(self):
        result=self.audit();self.assertEqual(len(result['resources']),4)
        self.assertFalse(result['post_link_writes'])

    def test_wrong_linked_resource_is_detected_without_collision_changes(self):
        for offset in (0x205,0x6000,0x6200,0x6300):
            with self.subTest(offset=offset):
                self.rom[offset]^=1
                with self.assertRaisesRegex(ValueError,'compiled'):self.audit()
                self.rom[offset]^=1

    def test_source_and_rom_cannot_agree_on_an_unloaded_palette_bank(self):
        raw=struct.pack('<8H',*([0xD200]*8))
        (self.directory/'metatiles.bin').write_bytes(raw);self.rom[0x6200:0x6210]=raw
        with self.assertRaisesRegex(ValueError,'unloaded'):self.audit()


if __name__=='__main__':unittest.main()
