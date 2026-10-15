"""Read final ROM/ELF bytes to verify the centered seed door and its bindings."""
import hashlib
import json
import struct

from seed_door_art import load


def audit_seed_door(rom, elf, root):
    from check_creature_resources import Cartridge, decode_lz

    checks = []
    receipt = {'passed': False, 'checks': checks, 'quality_approval': 'pending',
               'scope': 'Compiled seed-door resources and bindings; not animation, save, art or performance acceptance'}

    def compare(name, expected, read):
        record = {'name': name, 'passed': False,
                  'expected_sha256': hashlib.sha256(expected).hexdigest(),
                  'expected_bytes': len(expected)}
        try:
            actual = read()
            record.update(passed=actual == expected, actual_bytes=len(actual),
                          actual_sha256=hashlib.sha256(actual).hexdigest())
        except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
            record['error'] = str(error)
        checks.append(record)

    try:
        cart = Cartridge(rom, elf)
        receipt['rom_sha256'] = hashlib.sha256(cart.rom).hexdigest()
        art = load(root)
        payload = (root / 'assets/tiles/seed-room-door/frames.4bpp').read_bytes()
        if len(payload) != 768 or len(art['palette']) != 32:
            raise ValueError('Require three 256-byte stages and a sixteen-color palette.')
        compare('animation_payload', payload, lambda: cart.data('sSFSeedDoor_Tiles'))
        compare('animation_palette_selectors', bytes([11]) * 8,
                lambda: cart.data('sSFSeedDoor_Palettes'))

        def registration():
            table = cart.data('sDoorAnimGraphicsTable')
            if not table or len(table) % 12:
                raise ValueError('Door table must contain complete twelve-byte records.')
            entries = list(struct.iter_unpack('<HBBII', table))
            rows = [row for row in entries if row[0] == 660]
            if len(rows) != 1:
                raise ValueError('Require exactly one registered seed door (660).')
            first_null = next((i for i, row in enumerate(entries) if row[3] == 0), len(entries))
            if entries.index(rows[0]) >= first_null:
                raise ValueError('Seed door registration is unreachable after the table terminator.')
            _, sound, size, tiles, palettes = rows[0]
            expected = (0, 1, cart.symbols['sSFSeedDoor_Tiles'][0],
                        cart.symbols['sSFSeedDoor_Palettes'][0])
            if (sound, size, tiles, palettes) != expected:
                raise ValueError('Seed door sound, size or resource pointers differ.')
            return b'660:normal:size1:exact-pointers'

        compare('unique_registration', b'660:normal:size1:exact-pointers', registration)
        compare('resident_palette11', art['palette'],
                lambda: cart.data('gTilesetPalettes_SFSouthPark')[11 * 32:12 * 32])

        def tile_budget():
            raw = decode_lz(cart.data('gTilesetTiles_SFSouthPark'))
            if not raw or len(raw) % 32 or len(raw) // 32 > 504:
                raise ValueError('Park tiles overlap the eight reserved native door tiles.')
            receipt['resident_tiles'] = len(raw) // 32
            return b'within-size1-reservation'

        compare('resident_tile_budget', b'within-size1-reservation', tile_budget)

        def foreground(index):
            raw = decode_lz(cart.data('gTilesetTiles_SFSouthPark'))
            records = cart.data('gMetatiles_SFSouthPark')
            if len(records) % 16 or len(records) < (index + 1) * 16:
                raise ValueError('Missing complete seed-door metatile record.')
            words = struct.unpack_from('<8H', records, index * 16)
            pixels = bytearray()
            for y in range(16):
                for x in range(16):
                    word = words[4 + (y // 8) * 2 + x // 8]
                    tile = (word & 1023) - 512
                    if word >> 12 != 11 or not 0 <= tile < len(raw) // 32 or tile >= 504:
                        raise ValueError('Door foreground must reference resident palette11 tiles.')
                    tx = 7 - x % 8 if word & 0x400 else x % 8
                    ty = 7 - y % 8 if word & 0x800 else y % 8
                    value = raw[tile * 32 + ty * 4 + tx // 2]
                    pixels.append((value >> (4 * (tx % 2))) & 15)
            return bytes(pixels)

        compare('closed_upper661', art['frames'][0][:256], lambda: foreground(149))
        compare('closed_lower660', art['frames'][0][256:], lambda: foreground(148))
        for index, expected in ((149, 0), (148, 0x1069)):
            compare('attribute' + str(index + 512), struct.pack('<H', expected),
                    lambda index=index: cart.data('gMetatileAttributes_SFSouthPark')[index * 2:index * 2 + 2])
        plan = json.loads((root / 'romhack/content/south-park.json').read_text())
        width, height = len(plan['rows'][0]), len(plan['rows'])
        if width <= 16 or height <= 16 or any(len(row) != width for row in plan['rows']):
            raise ValueError('Park layout cannot contain the authored seed-door coordinates.')
        for x, y, word in ((16, 15, 661 | 0xC00), (16, 16, 660 | 0x3000)):
            offset = (y * width + x) * 2
            compare('map_word_' + str(x) + '_' + str(y), struct.pack('<H', word),
                    lambda offset=offset: cart.data('OldaleTown_Layout_Blockdata', width * height * 2)[offset:offset + 2])
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        checks.append({'name': 'audit_inputs', 'passed': False, 'error': str(error)})
    receipt['counts'] = {'total': len(checks), 'matched': sum(c['passed'] for c in checks)}
    receipt['passed'] = bool(checks) and all(c['passed'] for c in checks)
    return receipt
