"""Independent linked ARM fault vectors; opaque legacy bytes stay memory-only.

Provenance cases always run. Compiled vectors explicitly skip without the pinned
private v79 cartridge; they neither publish inherited payloads nor bypass hashes.
"""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/romhack'),str(ROOT/'scripts/quality'),str(ROOT/'tests')]
from sunset_density_audit import audit_sunset_density,PINNED,SOURCES,BASE
from trainer_portrait_audit_test import addresses,literal_lz,linked_pair,MemoryFile
from check_creature_resources import decode_lz
PRIVATE=ROOT/'.tools/romhack-drafts/0.0.79-park-density-preview/185cab500852af16e5229e9005cc601b7a16ac6cf764ce30778a7a15bbe820db'


def compiled_pair(resources):
    rom,elf=linked_pair(resources);raw=bytearray(elf.data)
    start,size=struct.unpack_from('<II',raw,172+16)
    # Genuine ARM Thumb STT_FUNC values carry a low address bit; resource reads
    # must normalize it without changing the pointer stored in native headers.
    for index,name in enumerate(resources,1):
        if name.startswith(('InitTilesetAnim_','TilesetAnim_','AppendTilesetAnim')):
            at=start+index*16;address=struct.unpack_from('<I',raw,at+4)[0]
            struct.pack_into('<I',raw,at+4,address|1);raw[at+12]=0x12
    return rom,MemoryFile(raw)


def rebind(resources):
    out=resources.copy();a=addresses(out)
    for suffix,secondary in (('General',0),('Petalburg',1)):
        out['gTileset_'+suffix]=struct.pack('<BB2x5I',1,secondary,
            *(a[p+suffix] for p in ('gTilesetTiles_','gTilesetPalettes_','gMetatiles_','gMetatileAttributes_')),
            a['InitTilesetAnim_'+suffix]|1)
    out['LittlerootTown_Layout']=struct.pack('<ii4I',32,32,a['LittlerootTown_Layout_Border'],
        a['LittlerootTown_Layout_Blockdata'],a['gTileset_General'],a['gTileset_Petalburg'])
    out['sDoorAnimGraphicsTable']=struct.pack('<HBBII',635,0,1,a['sSFDoorTiles'],a['sSFDoorPalettes'])
    init=bytearray(out['InitTilesetAnim_Petalburg']);struct.pack_into('<I',init,32,a['TilesetAnim_SFCoast']|1)
    out['InitTilesetAnim_Petalburg']=bytes(init)
    code=bytearray(out['TilesetAnim_SFCoast']);offset=a['AppendTilesetAnimToBuffer']-(a['TilesetAnim_SFCoast']+32)
    struct.pack_into('<HH',code,28,0xF000|((offset>>12)&0x7FF),0xF800|((offset>>1)&0x7FF))
    struct.pack_into('<II',code,36,a['sSFCoastalWaves'],0x06005E00);out['TilesetAnim_SFCoast']=bytes(code)
    return out


def fixture():
    rom=(PRIVATE/'target.gba').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=PRIVATE.name:raise ValueError('Private v79 cartridge identity changed.')
    syms={}
    for line in subprocess.check_output(['arm-none-eabi-nm','-S','--defined-only',str(PRIVATE/'target.elf')],text=True).splitlines():
        s=line.split()
        if len(s) in (3,4):syms[s[-1]]=(int(s[0],16),int(s[1],16) if len(s)==4 else 0)
    def old(name,size=None):
        a,n=syms[name]
        if name.startswith(('InitTilesetAnim_','TilesetAnim_','AppendTilesetAnim')):a&=~1
        return rom[a-0x08000000:a-0x08000000+(size or n)]
    resources={n:old(n) for n in ('gTilesetTiles_General','gTilesetPalettes_General','gMetatiles_General',
        'gMetatileAttributes_General','InitTilesetAnim_General','InitTilesetAnim_Petalburg','TilesetAnim_SFCoast',
        'sSFCoastalWaves','sSFDoorTiles','sSFDoorPalettes')}
    graphics=bytearray((ROOT/BASE/'secondary.4bpp').read_bytes())
    records=bytearray(old('gMetatiles_Petalburg')+bytes(37*16));attrs=bytearray(old('gMetatileAttributes_Petalburg')+bytes(74))
    pal=bytearray(old('gTilesetPalettes_Petalburg'));pal[256:288]=(ROOT/'assets/tiles/connected-frontage-v3/block.gbapal').read_bytes()
    pal[288:320]=(ROOT/'assets/tiles/south-park-paving-v1/paving.gbapal').read_bytes()
    pixels=(ROOT/'assets/tiles/connected-frontage-v3/block.indices').read_bytes()
    master=(ROOT/'assets/tiles/south-park-paving-v1/master8.indices').read_bytes()
    # Deliberately allocate blank before paving, unlike the producer's order.
    pool={bytes(graphics[i*32:(i+1)*32]):i for i in reversed(range(401)) if i not in range(240,248)};next_tile=401
    def allocate(p):
        nonlocal next_tile
        packed=bytes(p[i]|p[i+1]<<4 for i in range(0,64,2))
        if packed not in pool:pool[packed]=next_tile;graphics[next_tile*32:(next_tile+1)*32]=packed;next_tile+=1
        return pool[packed]
    blank=0x8200|allocate(bytes(64));paving=0x9200|allocate(master)
    struct.pack_into('<8H',records,230*16,*([paving]*4),*([blank]*4));struct.pack_into('<H',attrs,460,0x1000)
    for first,start in ((194,0),(206,5)):
        for row in range(4):
            for col in range(3):
                words=[]
                for q in range(4):
                    p=bytes(pixels[(row*16+q//2*8+y)*176+(start+col)*16+q%2*8+x] for y in range(8) for x in range(8))
                    words.append(0x8200|allocate(p))
                index=first+row*3+col
                struct.pack_into('<8H',records,index*16,*([paving]*4),*words)
                struct.pack_into('<H',attrs,index*2,0x1000 if row==3 else 0)
    for row in range(4):
        for col in range(3):
            words=struct.unpack_from('<4H',records,(194+row*3+2-col)*16+8)
            struct.pack_into('<8H',records,(218+row*3+col)*16,*([paving]*4),*(words[q]^0x400 for q in (1,0,3,2)))
            struct.pack_into('<H',attrs,(218+row*3+col)*2,0x1000 if row==3 else 0)
    if next_tile!=491:raise ValueError('Independent original art budget changed: '+str(next_tile))
    blocks=bytearray((ROOT/BASE/'sunset-map.bin').read_bytes())
    for top,first in ((4,194),(10,206),(25,218)):
        for y in range(4):
            for x in range(3):struct.pack_into('<H',blocks,((top+y)*32+28+x)*2,0xC00|512|first+y*3+x)
        for x in range(3):struct.pack_into('<H',blocks,((top+4)*32+28+x)*2,0x3000|742)
    resources.update({'gTilesetTiles_Petalburg':literal_lz(graphics),'gMetatiles_Petalburg':bytes(records),
        'gMetatileAttributes_Petalburg':bytes(attrs),'gTilesetPalettes_Petalburg':bytes(pal),
        'LittlerootTown_Layout_Blockdata':bytes(blocks),'LittlerootTown_Layout_Border':old('LittlerootTown_Layout_Border',8),
        'gTileset_General':bytes(24),'gTileset_Petalburg':bytes(24),'LittlerootTown_Layout':bytes(24),
        'sDoorAnimGraphicsTable':bytes(12),'AppendTilesetAnimToBuffer':bytes.fromhex('7047')})
    return rebind(resources)


class SunsetProvenanceTest(unittest.TestCase):
    def test_published_original_payloads_and_receipt_are_independently_pinned(self):
        for relative,spec in {**{BASE+'/'+n:v for n,v in PINNED.items()},**SOURCES}.items():
            blob=(ROOT/relative).read_bytes()
            with self.subTest(path=relative):self.assertEqual((len(blob),hashlib.sha256(blob).hexdigest()),spec)
        receipt=json.loads((ROOT/BASE/'receipt.json').read_bytes())
        self.assertEqual(receipt['files'],{n:{'bytes':s,'sha256':h} for n,(s,h) in PINNED.items() if n!='receipt.json'})
    def test_self_rehashed_or_changed_public_baseline_fails_before_reading_cartridge(self):
        parent=ROOT/'.tools/sunset-density-audit-tests';parent.mkdir(parents=True,exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='provenance-',dir=parent));shutil.copytree(ROOT/BASE,root/BASE)
        p=root/BASE/'secondary.4bpp';old=p.read_bytes();p.write_bytes(bytes([old[0]^1])+old[1:])
        receipt=root/BASE/'receipt.json';info=json.loads(receipt.read_bytes())
        info['files'][p.name]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();receipt.write_text(json.dumps(info))
        result=audit_sunset_density(MemoryFile(b''),MemoryFile(b''),root)
        self.assertFalse(result['passed']);self.assertTrue(any('Pinned source differs' in e for e in result['errors']))
    def test_each_public_payload_mutation_fails_closed_without_a_private_cartridge(self):
        parent=ROOT/'.tools/sunset-density-audit-tests';parent.mkdir(parents=True,exist_ok=True)
        root=Path(tempfile.mkdtemp(prefix='payloads-',dir=parent));shutil.copytree(ROOT/BASE,root/BASE)
        for name in SOURCES:
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,path)
        for path in [*(root/BASE/n for n in PINNED),*(root/n for n in SOURCES)]:
            old=path.read_bytes();path.write_bytes(bytes([old[0]^1])+old[1:])
            result=audit_sunset_density(MemoryFile(b''),MemoryFile(b''),root)
            with self.subTest(path=str(path.relative_to(root))):
                self.assertFalse(result['passed']);self.assertTrue(any('Pinned source differs' in e for e in result['errors']))
            path.write_bytes(old)


@unittest.skipUnless((PRIVATE/'target.gba').is_file() and (PRIVATE/'target.elf').is_file(),'Pinned private v79 cartridge unavailable; no inherited fixture is published.')
class SunsetCompiledAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.resources=fixture()
    def audit(self,resources=None):return audit_sunset_density(*compiled_pair(self.resources if resources is None else resources),ROOT)
    def fault(self,name,at,mask=1):
        r=self.resources.copy();b=bytearray(r[name]);b[at]^=mask;r[name]=bytes(b);return r
    def reject(self,resources,check=None):
        result=self.audit(resources);self.assertFalse(result['passed'])
        if check:self.assertTrue(any(r['name']==check and not r['passed'] for r in result['checks']),
            {'errors':result['errors'],'failed':[r['name'] for r in result['checks'] if not r['passed']]})
    def test_independent_linked_fixture_passes_exact_geometry_and_resource_contract(self):
        result=self.audit();self.assertTrue(result['passed'],{'errors':result['errors'],'failed':[r for r in result['checks'] if not r['passed']]})
        for key,value in {'changed_map_words':45,'new_solid_cells':36,'freed_cells':0,'ground_cells':9,'metatiles':231,'new_unique_tiles':90}.items():self.assertEqual(result['counts'][key],value)
        self.assertEqual(result['quality_approval'],'pending')
    def test_legacy_graphics_records_attributes_and_both_palette_domains_are_protected(self):
        for name,at,check in (('gMetatiles_Petalburg',0,'old194_records'),('gMetatileAttributes_Petalburg',0,'old194_attributes'),
            ('gTilesetPalettes_Petalburg',320,'old_other_palettes'),('gTilesetPalettes_Petalburg',256,'homes_palette8'),
            ('gTilesetPalettes_Petalburg',288,'gray_palette9'),('gMetatiles_General',0,'gMetatiles_General:preserved')):
            with self.subTest(name=name,at=at):self.reject(self.fault(name,at),check)
        r=self.resources.copy();raw=bytearray(decode_lz(r['gTilesetTiles_Petalburg']));raw[240*32]^=1
        r['gTilesetTiles_Petalburg']=literal_lz(raw);self.reject(r,'old401_graphics')
    def test_native_pixels_banks_mirrors_and_actor_layers_catch_facade_regressions(self):
        for index in (194,205,206,217,218,229):
            self.reject(self.fault('gMetatiles_Petalburg',index*16+9,16),'home_pixels_'+str(index))
            self.reject(self.fault('gMetatileAttributes_Petalburg',index*2+1,16),'new37_layer_roles')
        self.reject(self.fault('gMetatiles_Petalburg',218*16+9,4),'mirrored_quadrants_218')
        self.reject(self.fault('gMetatiles_Petalburg',194*16),'gray_underlay_194')
        self.reject(self.fault('gMetatiles_Petalburg',230*16+1,16),'paving_pixels')
        for tile in (752,759,1016,1023):
            r=self.resources.copy();b=bytearray(r['gMetatiles_Petalburg']);struct.pack_into('<H',b,194*16+8,0x8000|tile)
            r['gMetatiles_Petalburg']=bytes(b);self.reject(r)
    def test_all_parcels_ground_roads_event_approaches_and_collision_are_exact(self):
        for x,y in ((28,4),(30,7),(28,10),(30,13),(28,25),(30,28),(28,8),(30,14),(30,29),
                    (27,4),(25,20),(16,8),(29,22),(10,17),(6,18)):
            self.reject(self.fault('LittlerootTown_Layout_Blockdata',(y*32+x)*2),'all1024_map_words')
        for x,y in ((28,4),(28,8)):
            for mask in (4,16):self.reject(self.fault('LittlerootTown_Layout_Blockdata',(y*32+x)*2+1,mask),'all1024_map_words')
    def test_reserved_waves_cache_tail_and_animation_bindings_are_preserved(self):
        for slot in (401,490,491,503,504,511):
            r=self.resources.copy();raw=bytearray(decode_lz(r['gTilesetTiles_Petalburg']));raw[slot*32]^=1
            r['gTilesetTiles_Petalburg']=literal_lz(raw);self.reject(r,'exact90_new_patterns' if slot<491 else 'unused_tail_and_door_cache_zero')
        for name,at,check in (('sSFCoastalWaves',256,'sSFCoastalWaves:preserved'),('sSFDoorTiles',512,'sSFDoorTiles:preserved'),
            ('sSFDoorPalettes',0,'door_palette10'),('sDoorAnimGraphicsTable',4,'native_apartment_door_binding'),
            ('InitTilesetAnim_Petalburg',8,'coast_initializer_shape'),('InitTilesetAnim_Petalburg',32,'coast_callback_binding'),
            ('TilesetAnim_SFCoast',24,'coast_cadence_and_copy_shape'),('TilesetAnim_SFCoast',40,'coast_wave_and_vram_literals'),
            ('TilesetAnim_SFCoast',30,'coast_copy_call')):self.reject(self.fault(name,at),check)
        self.reject(self.fault('TilesetAnim_SFCoast',29,16),'coast_copy_call_encoding')
        self.reject(self.fault('InitTilesetAnim_Petalburg',20),'coast_initializer_shape')
    def test_headers_allocations_missing_symbols_lz_and_stale_elf_fail_closed(self):
        for name in ('gTileset_General','gTileset_Petalburg'):
            for at in (0,1,4,8,12,16,20):self.reject(self.fault(name,at),name.split('_',1)[1]+':header')
        for at in (0,4,8,12,16,20):self.reject(self.fault('LittlerootTown_Layout',at),'layout_binding')
        for name in self.resources:
            r=self.resources.copy();del r[name]
            with self.subTest(missing=name):self.reject(r)
        for name in ('gTilesetTiles_Petalburg','gMetatiles_Petalburg','gMetatileAttributes_Petalburg'):
            r=self.resources.copy();r[name]=r[name][:-1];self.reject(rebind(r))
        rom,elf=linked_pair(self.resources);changed=bytearray(rom.data);changed[0]^=1
        self.assertFalse(audit_sunset_density(MemoryFile(changed),elf,ROOT)['passed'])


if __name__=='__main__':unittest.main()
