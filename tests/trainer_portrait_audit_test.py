"""Independent ROM/ELF fault vectors for original trainer portrait presentation."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts/romhack'), str(ROOT/'scripts/quality')]
from check_creature_resources import Cartridge
from trainer_portrait_audit import audit_portraits
from trainer_portraits import portrait_registry, verified_portrait, apply_portrait, PORTRAITS


class MemoryFile:
    def __init__(self, data): self.data = bytes(data)
    def read_bytes(self): return self.data


def literal_lz(raw):
    return b'\x10' + len(raw).to_bytes(3, 'little') + b''.join(
        b'\0' + raw[i:i+8] for i in range(0, len(raw), 8))


def addresses(resources):
    result, length = {}, 0
    for name, data in resources.items():
        length += (-length) % 4
        result[name] = 0x08000000 + length
        length += len(data)
    return result


def linked_pair(resources):
    # A bounded independently serialized ARM ELF32, not a mocked resource reader.
    rom, strings, definitions = bytearray(), bytearray(b'\0'), []
    for name, data in resources.items():
        rom.extend(bytes((-len(rom)) % 4))
        definitions.append((len(strings), 0x08000000+len(rom), len(data), 0x11, 0, 1))
        strings.extend(name.encode()+b'\0'); rom.extend(data)
    text_start = 212
    strings_start = text_start + len(rom)
    symbols_start = (strings_start + len(strings) + 3) & ~3
    elf = bytearray(symbols_start + (len(definitions)+1)*16)
    elf[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<H', elf, 18, 40)
    struct.pack_into('<I', elf, 32, 52)
    struct.pack_into('<HH', elf, 46, 40, 4)
    struct.pack_into('<10I', elf, 92, 0, 1, 2, 0x08000000, text_start, len(rom), 0, 0, 4, 0)
    struct.pack_into('<10I', elf, 132, 0, 3, 0, 0, strings_start, len(strings), 0, 0, 1, 0)
    struct.pack_into('<10I', elf, 172, 0, 2, 0, 0, symbols_start,
                     (len(definitions)+1)*16, 2, 1, 4, 16)
    elf[text_start:strings_start] = rom
    elf[strings_start:strings_start+len(strings)] = strings
    for i, definition in enumerate(definitions, 1):
        struct.pack_into('<IIIBBH', elf, symbols_start+i*16, *definition)
    return MemoryFile(rom), MemoryFile(elf)


def fixture():
    parent = ROOT/'.tools/trainer-portrait-audit-tests'
    parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix='case-', dir=parent))
    # Deliberately specified here, rather than imported from either registry.
    people = [('ScottWu', 'scott-wu', 93, 265), ('WaldenYan', 'walden-yan', 94, 320),
              ('StevenHao', 'steven-hao', 95, 321)]
    resources = {}
    for number, (symbol, slug, pic, trainer) in enumerate(people):
        directory = root/'assets/characters/cognition-cast'/slug/'battle-portrait-v1'
        directory.mkdir(parents=True)
        native_colors = [(0,0,0), (31,17+number,6), (5,6,9)] + [(0,0,0)]*13
        colors = [tuple(v*255//31 for v in color) for color in native_colors]
        image = Image.new('P', (64,64), 0)
        image.putpalette([v for c in colors for v in c]+[0]*720)
        for y in range(54,63):
            for x in range(26,36): image.putpixel((x,y), 1+(x+y+number)%2)
        image.save(directory/'portrait.png', transparency=0, bits=4)
        pixels = image.tobytes()
        raw = bytearray()
        for ty in range(8):
            for tx in range(8):
                for y in range(8):
                    for x in range(0,8,2):
                        offset = (ty*8+y)*64+tx*8+x
                        raw.append(pixels[offset] | pixels[offset+1]<<4)
        palette = b''.join(struct.pack('<H', sum(c[k] << (5*k) for k in range(3))) for c in native_colors)
        (directory/'portrait.4bpp').write_bytes(raw)
        (directory/'portrait.gbapal').write_bytes(palette)
        (directory/'source.png').write_bytes((directory/'portrait.png').read_bytes())
        metadata = {'native_size':[64,64], 'baseline':62, 'palette_colors':16,
                    'source_sha256':hashlib.sha256((directory/'source.png').read_bytes()).hexdigest(),
                    'files':{name:hashlib.sha256((directory/name).read_bytes()).hexdigest()
                             for name in ('portrait.png','portrait.4bpp','portrait.gbapal')}}
        (directory/'conversion.json').write_text(json.dumps(metadata))
        resources['gTrainerFrontPic_'+symbol] = literal_lz(raw)
        resources['gTrainerPalette_'+symbol] = literal_lz(palette)
        resources['sAnims_'+symbol] = bytes(4)
    resources.update({'sAnim_GeneralFrame0':bytes.fromhex('00000000ffff0000'),
        # Native agbcc rounds each unpacked record to32 bits, not host sizeof(two u8).
        'gTrainerFrontPicCoords':bytes.fromhex('08010000')*96, 'gTrainerFrontPicTable':bytes(96*8),
        'gTrainerFrontPicPaletteTable':bytes(96*8), 'gTrainerFrontAnimsPtrTable':bytes(96*4),
        'gTrainers':bytes(322*40), 'gTrainerUnrelated':b'ignored'})
    locations = addresses(resources)
    for symbol, slug, pic, trainer in people:
        resources['sAnims_'+symbol] = struct.pack('<I', locations['sAnim_GeneralFrame0'])
    sheets, palettes, animations = bytearray(), bytearray(), bytearray()
    for pic in range(96):
        symbol = {94:'WaldenYan',95:'StevenHao'}.get(pic,'ScottWu')
        sheets.extend(struct.pack('<IHH', locations['gTrainerFrontPic_'+symbol],2048,pic))
        palettes.extend(struct.pack('<IHxx', locations['gTrainerPalette_'+symbol],pic))
        animations.extend(struct.pack('<I', locations['sAnims_'+symbol]))
    resources['gTrainerFrontPicTable'] = bytes(sheets)
    resources['gTrainerFrontPicPaletteTable'] = bytes(palettes)
    resources['gTrainerFrontAnimsPtrTable'] = bytes(animations)
    trainers = bytearray(resources['gTrainers'])
    for symbol, slug, pic, trainer in people: trainers[trainer*40+3] = pic
    resources['gTrainers'] = bytes(trainers)
    return root, resources


class TrainerPortraitAuditTest(unittest.TestCase):
    def setUp(self): self.root, self.resources = fixture()

    def audit(self, resources=None):
        return audit_portraits(*linked_pair(self.resources if resources is None else resources), self.root)

    def reject(self, resources, target):
        result = self.audit(resources)
        self.assertFalse(result['passed'])
        self.assertTrue(any(c['name']==target and not c['passed'] for c in result['checks']),
                        [(c['name'],c['passed'],c.get('error')) for c in result['checks']])

    def fault(self, symbol, offset, mask=1):
        result = self.resources.copy(); data = bytearray(result[symbol]); data[offset] ^= mask
        result[symbol] = bytes(data)
        return result

    def test_exact_resource_identity_and_native_bindings_pass(self):
        result = self.audit()
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['counts'], {'total':26, 'matched':26})
        self.assertEqual(result['errors'], [])
        self.assertTrue(result['inputs'])
        self.assertNotIn('gTrainerUnrelated', Cartridge(*linked_pair(self.resources)).symbols)

    def test_each_actual_trainer_selector_is_independent_of_the_producer_registry(self):
        for symbol, trainer in [('ScottWu',265),('WaldenYan',320),('StevenHao',321)]:
            self.reject(self.fault('gTrainers',trainer*40+3),symbol+':trainer_selector')
        mistaken = tuple((asset,symbol,picture,slot+1) for asset,symbol,picture,slot in PORTRAITS)
        with patch('trainer_portraits.PORTRAITS', mistaken):
            with self.assertRaises(ValueError): portrait_registry()
            self.assertTrue(self.audit()['passed'])

    def test_sheet_and_palette_pointer_tag_size_faults_are_rejected(self):
        for table, offset, target in [('gTrainerFrontPicTable',0,'sheet_binding'),
                                     ('gTrainerFrontPicTable',4,'sheet_binding'),
                                     ('gTrainerFrontPicTable',6,'sheet_binding'),
                                     ('gTrainerFrontPicPaletteTable',0,'palette_binding'),
                                     ('gTrainerFrontPicPaletteTable',4,'palette_binding')]:
            with self.subTest(table=table, offset=offset):
                self.reject(self.fault(table,94*8+offset),'WaldenYan:'+target)

    def test_all_four_complete_tables_reject_truncation_and_unrelated_bad_entries(self):
        for table, stride in [('gTrainerFrontPicCoords',4),('gTrainerFrontPicTable',8),
                              ('gTrainerFrontPicPaletteTable',8),('gTrainerFrontAnimsPtrTable',4)]:
            resources = self.resources.copy(); resources[table] = resources[table][:-stride]
            self.reject(resources,table+':complete_table')
            # Corrupt an old row, not one of the three new portrait bindings.
            self.reject(self.fault(table,0,0xFF),table+':complete_table')

    def test_pixels_palette_coords_and_both_animation_links_are_checked(self):
        self.reject(self.fault('gTrainerFrontPic_WaldenYan',5),'WaldenYan:pixels')
        self.reject(self.fault('gTrainerPalette_WaldenYan',5),'WaldenYan:palette')
        self.reject(self.fault('gTrainerFrontPicCoords',94*4+1),'WaldenYan:coords')
        self.reject(self.fault('gTrainerFrontAnimsPtrTable',94*4),'WaldenYan:animation_binding')
        self.reject(self.fault('sAnims_WaldenYan',0),'WaldenYan:animation_binding')
        self.reject(self.fault('sAnim_GeneralFrame0',4),'single_frame_animation')

    def test_native_coords_reject_packed_rows_padding_and_wrong_stride_semantics(self):
        resources = self.resources.copy()
        resources['gTrainerFrontPicCoords'] = bytes.fromhex('0801')*96
        self.reject(resources,'gTrainerFrontPicCoords:complete_table')
        for offset in (93*4+2,94*4+3):
            self.reject(self.fault('gTrainerFrontPicCoords',offset),
                        'gTrainerFrontPicCoords:complete_table')
        # Distinguish odd/even slots; a two-byte reader used to see padding for
        # Scott93/Steven95 and an unrelated old row for Walden94.
        for symbol, pic in [('ScottWu',93),('WaldenYan',94),('StevenHao',95)]:
            resources = self.resources.copy()
            coords = bytearray(resources['gTrainerFrontPicCoords'])
            coords[pic*4+1] = 2  # Structurally valid offset, wrong authored binding.
            resources['gTrainerFrontPicCoords'] = bytes(coords)
            self.reject(resources,symbol+':coords')

    def test_missing_resources_malformed_lz_and_stale_rom_elf_fail_closed(self):
        for name in self.resources:
            if name=='gTrainerUnrelated': continue
            resources = self.resources.copy(); del resources[name]
            with self.subTest(missing=name): self.assertFalse(self.audit(resources)['passed'])
        resources = self.resources.copy(); resources['gTrainerFrontPic_StevenHao'] = b'bad'
        self.reject(resources,'StevenHao:pixels')
        rom,elf = linked_pair(self.resources)
        changed = bytearray(rom.data);changed[5] ^= 1
        result = audit_portraits(MemoryFile(changed),elf,self.root)
        self.assertFalse(result['passed'])
        self.assertTrue(any('ROM/ELF resource bytes differ' in e for e in result['errors']))
        self.assertFalse(audit_portraits(MemoryFile(b''),MemoryFile(b'bad'),self.root)['passed'])

    def test_art_receipt_and_serialization_faults_are_rejected(self):
        directory=self.root/'assets/characters/cognition-cast/walden-yan/battle-portrait-v1'
        (directory/'source.png').write_bytes(b'changed source')
        self.reject(self.resources,'WaldenYan:source')
        with self.assertRaises(ValueError): verified_portrait(self.root,str(directory.relative_to(self.root)))

    def test_rehashed_binary_cannot_override_independent_png_pixels_or_palette(self):
        directory=self.root/'assets/characters/cognition-cast/steven-hao/battle-portrait-v1'
        for filename in ('portrait.4bpp','portrait.gbapal'):
            with self.subTest(filename=filename):
                original=(directory/filename).read_bytes()
                changed=bytearray(original);changed[0] ^= 1
                (directory/filename).write_bytes(changed)
                metadata=json.loads((directory/'conversion.json').read_text())
                metadata['files'][filename]=hashlib.sha256(changed).hexdigest()
                (directory/'conversion.json').write_text(json.dumps(metadata))
                self.reject(self.resources,'StevenHao:source')
                (directory/filename).write_bytes(original)
                metadata['files'][filename]=hashlib.sha256(original).hexdigest()
                (directory/'conversion.json').write_text(json.dumps(metadata))

    def test_registry_rejects_duplicate_assets_slots_unsafe_paths_and_byte_overflow(self):
        for entry in [(PORTRAITS[0][0],*PORTRAITS[1][1:]),
                      (*PORTRAITS[1][:3],93), ('../escape','WaldenYan','WALDEN_YAN',94),
                      (*PORTRAITS[1][:3],256)]:
            with patch('trainer_portraits.PORTRAITS',(PORTRAITS[0],entry,PORTRAITS[2])):
                with self.assertRaises(ValueError): portrait_registry()

    def test_apply_preserves_existing_headers_and_registers_all_three_once(self):
        engine=self.root/'engine'
        originals = {'include/constants/trainers.h':'#define TRAINER_PIC_RS_MAY                92\n',
            'include/graphics.h':'extern const u32 gExistingFieldArt[];\n',
            'src/data/graphics/trainers.h':'/* original trainer resources */\n',
            'src/data/trainer_graphics/front_pic_tables.h':
                'const struct MonCoords gTrainerFrontPicCoords[] =\n{\n};\n'
                'const struct CompressedSpriteSheet gTrainerFrontPicTable[] =\n{\n};\n'
                'const struct CompressedSpritePalette gTrainerFrontPicPaletteTable[] =\n{\n};\n',
            'src/data/trainer_graphics/front_pic_anims.h':
                'const union AnimCmd *const *const gTrainerFrontAnimsPtrTable[] =\n{\n};\n'}
        for name,data in originals.items():
            path=engine/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data)
        paths=apply_portrait(self.root,engine,originals.__getitem__)
        self.assertEqual(set(paths),set(originals))
        self.assertIn('gExistingFieldArt',(engine/'include/graphics.h').read_text())
        constants=(engine/'include/constants/trainers.h').read_text()
        for symbol,constant,slot in [('ScottWu','SCOTT_WU',93),('WaldenYan','WALDEN_YAN',94),
                                    ('StevenHao','STEVEN_HAO',95)]:
            self.assertEqual(constants.count('#define TRAINER_PIC_'+constant+' '+str(slot)),1)
            target=engine/'graphics/trainers/front_pics'/('sf_'+constant.lower())/'portrait.png'
            self.assertTrue(target.is_file())
            for table in ['src/data/trainer_graphics/front_pic_tables.h',
                          'src/data/trainer_graphics/front_pic_anims.h']:
                self.assertIn('TRAINER_PIC_'+constant if 'anims' in table else constant,
                              (engine/table).read_text())


if __name__=='__main__': unittest.main()
