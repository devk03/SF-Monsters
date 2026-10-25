"""Prototype contract: exact indexed pixels, safe slots and real attachment roles."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from world_rich_facades import FORMS, facade, fronts
from world_shared_primary import REQUIRED_METATILES, FIXED_RESERVED, plan_shared_primary


class RichFacadeTests(unittest.TestCase):
    def test_every_attachment_keeps_footprint_and_changes_only_edge_pixels(self):
        for name in FORMS:
            w, h, isolated = facade(name)
            self.assertEqual((w,h), (32 if name in ('shophouse','flats') else 48,64))
            self.assertEqual(len(isolated), w*h)
            for closed in ((), ('left',), ('right',)):
                vw, vh, pixels = facade(name, closed)
                self.assertEqual((vw,vh,len(pixels)), (w,h,w*h))
                self.assertLessEqual(max(pixels), 15)
                self.assertNotEqual(pixels, isolated)
                for y in range(h):
                    self.assertEqual(pixels[y*w+2:y*w+w-2], isolated[y*w+2:y*w+w-2])
        self.assertEqual(len(fronts('mixed_use', variants=True)), 32)
        self.assertEqual(fronts('nature', variants=True), [])
        self.assertEqual(len({facade(n)[2] for n in FORMS}), 8)

    def records(self):
        # Hand fixture reserves tile100 for every protected terrain record,
        # plus tile101 for a future caller-declared native terrain record.
        return {**{n:[100]*8 for n in REQUIRED_METATILES}, 400:[101]*8}

    def test_primary_plan_preserves_pixels_flips_and_seam_ownership(self):
        tile = bytes((x+3*y)%16 for y in range(8) for x in range(8))
        horizontal = b''.join(tile[y*8:(y+1)*8][::-1] for y in range(8))
        vertical = b''.join(tile[y*8:(y+1)*8] for y in range(7,-1,-1))
        result = plan_shared_primary(self.records(), [tile,horizontal,vertical], seam_slots={200,201}, seam_headroom=30)
        self.assertEqual(len(result['used_slots']), 1)
        self.assertFalse(set(result['used_slots']) & (set(FIXED_RESERVED)|{100,101,200,201}))
        self.assertTrue({100,101} <= set(result['reserved_slots']))
        for original, word in zip((tile,horizontal,vertical), result['references']):
            raw = result['graphics'][result['used_slots'].index(word & 1023)]
            rows = [list(raw[y*8:(y+1)*8]) for y in range(8)]
            if word & 0x400: rows = [row[::-1] for row in rows]
            if word & 0x800: rows = rows[::-1]
            self.assertEqual(bytes(v for row in rows for v in row), original)

    def test_missing_terrain_conflicting_seams_and_exhaustion_fail_closed(self):
        r = self.records();r.pop(0xaf)
        with self.assertRaisesRegex(ValueError, 'Missing protected'):
            plan_shared_primary(r, [], seam_slots=[])
        with self.assertRaisesRegex(ValueError, 'collide'):
            plan_shared_primary(self.records(), [], seam_slots=[100])
        with self.assertRaisesRegex(ValueError, 'only0available'):
            plan_shared_primary(self.records(), [bytes(64)], seam_slots=set(range(16,432))-{20,100,101})
        with self.assertRaisesRegex(ValueError, 'seam reserve'):
            plan_shared_primary(self.records(), [], seam_slots=[], seam_headroom=1000)
        with self.assertRaisesRegex(ValueError, 'indexed4bpp'):
            plan_shared_primary(self.records(), [bytes([16]*64)], seam_slots=[])

    def test_primary_assignment_is_stable_when_input_order_changes(self):
        a = bytes(range(16))*4
        b = bytes((n*n+3)%16 for n in range(64))
        first = plan_shared_primary(self.records(), [a,b], seam_slots=[200])
        second = plan_shared_primary(self.records(), [b,a], seam_slots=[200])
        self.assertEqual(first['graphics'],second['graphics'])
        self.assertEqual(first['used_slots'],second['used_slots'])
        self.assertEqual(first['references'],second['references'][::-1])


if __name__ == '__main__':
    unittest.main()
