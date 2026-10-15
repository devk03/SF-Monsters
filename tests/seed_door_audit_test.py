"""Fault injection at the compiled ROM/ELF boundary, including native BG flips."""
from pathlib import Path
import json
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts/romhack'), str(ROOT / 'scripts/quality')]
from check_creature_resources import Cartridge
from seed_door_art import load
from seed_door_audit import audit_seed_door


class MemoryFile:
    def __init__(self, data):
        self.data = bytes(data)

    def read_bytes(self):
        return self.data


def linked_pair(resources):
    """Independent minimal ELF32 with one file-backed ROM section."""
    rom, names, definitions = bytearray(), bytearray(b'\0'), []
    for name, data in resources.items():
        rom.extend(bytes((-len(rom)) % 4))
        definitions.append((len(names), 0x08000000 + len(rom), len(data), 0x11, 0, 1))
        names.extend(name.encode() + b'\0')
        rom.extend(data)
    payload_start = 212
    strings_start = payload_start + len(rom)
    symbols_start = (strings_start + len(names) + 3) & ~3
    elf = bytearray(symbols_start + (len(definitions) + 1) * 16)
    elf[:7] = b'\x7fELF\x01\x01\x01'
    struct.pack_into('<H', elf, 18, 40)
    struct.pack_into('<I', elf, 32, 52)
    struct.pack_into('<HH', elf, 46, 40, 4)
    struct.pack_into('<10I', elf, 92, 0, 1, 2, 0x08000000, payload_start, len(rom), 0, 0, 4, 0)
    struct.pack_into('<10I', elf, 132, 0, 3, 0, 0, strings_start, len(names), 0, 0, 1, 0)
    struct.pack_into('<10I', elf, 172, 0, 2, 0, 0, symbols_start,
                     (len(definitions) + 1) * 16, 2, 1, 4, 16)
    elf[payload_start:strings_start] = rom
    elf[strings_start:strings_start + len(names)] = names
    for i, definition in enumerate(definitions, 1):
        struct.pack_into('<IIIBBH', elf, symbols_start + i * 16, *definition)
    return MemoryFile(rom), MemoryFile(elf)


def literal_lz(raw):
    return b'\x10' + len(raw).to_bytes(3, 'little') + b''.join(
        b'\0' + raw[i:i + 8] for i in range(0, len(raw), 8))


def fixture(art):
    frame = art['frames'][0]
    raw = bytearray(503 * 32)
    records = bytearray(150 * 16)
    # All four flip states are independently encoded into physical tile storage.
    for half, index in ((0, 149), (1, 148)):
        words = [0] * 4
        for q in range(4):
            tile = half * 4 + q
            flip_x, flip_y = bool(q & 1), bool(q & 2)
            for y in range(8):
                for x in range(0, 8, 2):
                    pixels = []
                    for dx in (0, 1):
                        sx = 7 - x - dx if flip_x else x + dx
                        sy = 7 - y if flip_y else y
                        pixels.append(frame[(half * 16 + q // 2 * 8 + sy) * 16 + q % 2 * 8 + sx])
                    raw[tile * 32 + y * 4 + x // 2] = pixels[0] | pixels[1] << 4
            words.append(0xB000 | (512 + tile) | (0x400 if flip_x else 0) | (0x800 if flip_y else 0))
        struct.pack_into('<8H', records, index * 16, *words)
    attributes = bytearray(300)
    struct.pack_into('<H', attributes, 148 * 2, 0x1069)
    plan = json.loads((ROOT / 'romhack/content/south-park.json').read_text())
    width, height = len(plan['rows'][0]), len(plan['rows'])
    blocks = bytearray(width * height * 2)
    for y, word in ((15, 661 | 0xC00), (16, 660 | 0x3000)):
        struct.pack_into('<H', blocks, (y * width + 16) * 2, word)
    resources = {
        'sSFSeedDoor_Tiles': (ROOT / 'assets/tiles/seed-room-door/frames.4bpp').read_bytes(),
        'sSFSeedDoor_Palettes': bytes([11]) * 8,
        'sDoorAnimGraphicsTable': bytes(24),
        'gTilesetTiles_SFSouthPark': literal_lz(raw),
        'gTilesetPalettes_SFSouthPark': bytes(352) + art['palette'] + bytes(128),
        'gMetatiles_SFSouthPark': bytes(records),
        'gMetatileAttributes_SFSouthPark': bytes(attributes),
        'OldaleTown_Layout_Blockdata': bytes(blocks),
        'gUnrelatedDoorTest': b'ignored'
    }
    # Compute independent linked addresses; table size remains fixed.
    rom, elf = linked_pair(resources)
    symbols = Cartridge(rom, elf).symbols
    resources['sDoorAnimGraphicsTable'] = struct.pack('<HBBII', 660, 0, 1,
        symbols['sSFSeedDoor_Tiles'][0], symbols['sSFSeedDoor_Palettes'][0]) + bytes(12)
    return resources


class SeedDoorAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resources = fixture(load(ROOT))

    def audit(self, resources=None):
        return audit_seed_door(*linked_pair(self.resources if resources is None else resources), ROOT)

    def reject(self, resources, target):
        receipt = self.audit(resources)
        self.assertFalse(receipt['passed'])
        self.assertTrue(any(c['name'] == target and not c['passed'] for c in receipt['checks']), receipt)

    def test_exact_linked_fixture_with_all_flips_and_near_capacity_passes(self):
        result = self.audit()
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['resident_tiles'], 503)
        self.assertEqual(result['counts'], {'total': 11, 'matched': 11})
        self.assertNotIn('gUnrelatedDoorTest', Cartridge(*linked_pair(self.resources)).symbols)

    def test_payload_and_palette_faults_fail_their_compiled_checks(self):
        for symbol, offset, target in (
                ('sSFSeedDoor_Tiles', 127, 'animation_payload'),
                ('sSFSeedDoor_Palettes', 3, 'animation_palette_selectors'),
                ('gTilesetPalettes_SFSouthPark', 353, 'resident_palette11')):
            with self.subTest(symbol=symbol):
                resources = self.resources.copy()
                data = bytearray(resources[symbol]); data[offset] ^= 1
                resources[symbol] = bytes(data)
                self.reject(resources, target)

    def test_registration_rejects_wrong_sound_size_pointers_duplicate_and_unreachable_rows(self):
        table = self.resources['sDoorAnimGraphicsTable']
        for offset in (2, 3, 4, 8):
            with self.subTest(offset=offset):
                resources = self.resources.copy()
                data = bytearray(table); data[offset] ^= 1
                resources['sDoorAnimGraphicsTable'] = bytes(data)
                self.reject(resources, 'unique_registration')
        for data in (table[:12] * 2, bytes(12) + table[:12], table[:-1]):
            resources = self.resources.copy(); resources['sDoorAnimGraphicsTable'] = data
            self.reject(resources, 'unique_registration')

    def test_foreground_rejects_wrong_palette_primary_and_out_of_bounds_tiles(self):
        for word in (0xA200, 0xB1FF, 0xB3F8):
            resources = self.resources.copy()
            records = bytearray(resources['gMetatiles_SFSouthPark'])
            struct.pack_into('<H', records, 149 * 16 + 8, word)
            resources['gMetatiles_SFSouthPark'] = bytes(records)
            self.reject(resources, 'closed_upper661')
        resources = self.resources.copy()
        records = bytearray(resources['gMetatiles_SFSouthPark'])
        # Dropping the horizontal flip changes the reconstructed native pixels.
        records[149 * 16 + 11] ^= 4
        resources['gMetatiles_SFSouthPark'] = bytes(records)
        self.reject(resources, 'closed_upper661')

    def test_tile_budget_and_lz_corruption_fail_closed(self):
        for raw in (bytes(505 * 32), bytes(503 * 32 + 1)):
            resources = self.resources.copy(); resources['gTilesetTiles_SFSouthPark'] = literal_lz(raw)
            self.reject(resources, 'resident_tile_budget')
        resources = self.resources.copy(); resources['gTilesetTiles_SFSouthPark'] = b'bad'
        self.reject(resources, 'resident_tile_budget')

    def test_resident_pixel_faults_detect_each_closed_half_independently(self):
        for tile, target in ((0, 'closed_upper661'), (4, 'closed_lower660')):
            resources = self.resources.copy()
            data = bytearray(resources['gTilesetTiles_SFSouthPark'])
            raw_offset = tile * 32
            data[5 + raw_offset + raw_offset // 8] ^= 1
            resources['gTilesetTiles_SFSouthPark'] = bytes(data)
            self.reject(resources, target)

    def test_attributes_and_map_collision_or_elevation_faults_fail(self):
        for index, target in ((149, 'attribute661'), (148, 'attribute660')):
            resources = self.resources.copy()
            data = bytearray(resources['gMetatileAttributes_SFSouthPark']); data[index * 2] ^= 1
            resources['gMetatileAttributes_SFSouthPark'] = bytes(data)
            self.reject(resources, target)
        width = len(json.loads((ROOT / 'romhack/content/south-park.json').read_text())['rows'][0])
        for y, mask in ((15, 0xC00), (16, 0x1000)):
            resources = self.resources.copy()
            data = bytearray(resources['OldaleTown_Layout_Blockdata'])
            offset = (y * width + 16) * 2
            struct.pack_into('<H', data, offset, struct.unpack_from('<H', data, offset)[0] ^ mask)
            resources['OldaleTown_Layout_Blockdata'] = bytes(data)
            self.reject(resources, 'map_word_16_' + str(y))

    def test_missing_resources_and_invalid_or_stale_pairs_return_failed_receipts(self):
        for symbol in self.resources:
            if symbol == 'gUnrelatedDoorTest':
                continue
            with self.subTest(symbol=symbol):
                resources = self.resources.copy(); del resources[symbol]
                self.assertFalse(self.audit(resources)['passed'])
        bad = audit_seed_door(MemoryFile(b''), MemoryFile(b'bad'), ROOT)
        self.assertFalse(bad['passed'])
        self.assertEqual(bad['checks'][0]['name'], 'audit_inputs')
        rom, elf = linked_pair(self.resources)
        changed = bytearray(rom.data); changed[0] ^= 1
        receipt = audit_seed_door(MemoryFile(changed), elf, ROOT)
        self.assertFalse(receipt['passed'])
        self.assertTrue(any('ROM/ELF resource bytes differ' in c.get('error', '') for c in receipt['checks']))


if __name__ == '__main__':
    unittest.main()
