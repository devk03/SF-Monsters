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
        return audit_resources(bytes(self.rom),read,0x08000100,getattr(self,'profile','nature'),self.folder,getattr(self,'symbols',None))

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

    def own_primary(self,profile='mixed_use',suffix='SFMixedUse'):
        self.profile=profile
        self.directory=self.directory.rename(self.directory.with_name('sf_world_'+profile))
        self.symbols={'gSFPrimaryCount_'+suffix:0x08000120,
                      'gSFPrimarySlots_'+suffix:0x08000122,
                      'gSFPrimaryGraphics_'+suffix:0x08000140}
        struct.pack_into('<HH',self.rom,0x120,1,18)
        raw=bytes([0x21])*32
        self.rom[0x140:0x160]=raw
        (self.directory/'primary-slots.bin').write_bytes(struct.pack('<H',18))
        (self.directory/'primary-art.4bpp').write_bytes(raw)
        record=struct.pack('<8H',*([0x6012]*8))
        (self.directory/'metatiles.bin').write_bytes(record)
        self.rom[0x6200:0x6210]=record

    def test_linked_primary_art_is_compared_with_normal_inputs(self):
        self.own_primary()
        self.assertEqual(len(self.audit()['resources']),6)
        for offset in (0x120,0x122,0x140):
            with self.subTest(offset=offset):
                self.rom[offset]^=1
                with self.assertRaisesRegex(ValueError,'[Cc]ompiled'):self.audit()
                self.rom[offset]^=1

    def test_agreeing_source_and_rom_cannot_reference_unloaded_primary_art(self):
        self.own_primary()
        record=struct.pack('<8H',*([0x6013]*8))
        (self.directory/'metatiles.bin').write_bytes(record)
        self.rom[0x6200:0x6210]=record
        with self.assertRaisesRegex(ValueError,'unloaded own-primary'):self.audit()

    def test_hybrid_ridge_profile_checks_its_own_linked_primary_symbols(self):
        self.own_primary('ridge_town','SFRidgeTown')
        self.assertEqual(self.audit()['profile'],'ridge_town')
        self.rom[0x140]^=1
        with self.assertRaisesRegex(ValueError,'compiled primary-art differs'):self.audit()


class LiveSourceArtTests(unittest.TestCase):
    def test_independent_render_audit_decodes_primary_art_with_palette_and_flips(self):
        from types import SimpleNamespace
        sys.path.insert(0,str(ROOT/'scripts/quality'))
        from verify_world_seams import RenderAudit
        rom=bytearray(0x1000)
        struct.pack_into('<I',rom,0x104,0x08000800)
        struct.pack_into('<HH',rom,0x120,1,18)
        pixels=bytes(i%16 for i in range(64))
        rom[0x140:0x160]=bytes(pixels[i]|pixels[i+1]<<4 for i in range(0,64,2))
        colors=[0]+[0x100+i for i in range(1,16)]
        struct.pack_into('<16H',rom,0x400+6*32,*colors)
        audit=RenderAudit.__new__(RenderAudit)
        audit.c=SimpleNamespace(symbols={'gTileset_SFMixedUse':0x08000100,
            'gSFPrimaryCount_SFMixedUse':0x08000120,'gSFPrimarySlots_SFMixedUse':0x08000122,
            'gSFPrimaryGraphics_SFMixedUse':0x08000140})
        audit.rom=bytes(rom);audit.graphics={};audit.own_graphics={}
        for flags in (0,0x400,0x800,0xc00):
            expected=[]
            for y in range(8):
                for x in range(8):
                    index=((7-y if flags&0x800 else y)*8+(7-x if flags&0x400 else x))%16
                    expected.append(0x100+index if index else None)
            self.assertEqual(audit.source_pixels(0x6012|flags,0x08000800,0x08000400),expected)
        with self.assertRaisesRegex(ValueError,'unloaded own-primary'):
            audit.source_pixels(0x6013,0x08000800,0x08000400)


if __name__=='__main__':unittest.main()
