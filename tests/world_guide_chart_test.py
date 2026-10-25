"""Native chart packing and geometry contracts; no aesthetic approval claims."""
import json
from pathlib import Path
import sys
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from world_guide_art import tiled_bytes
from world_guide_layout import chart_positions, route_path, path_midpoint
from generate_world import records


class NativeChartTest(unittest.TestCase):
    def test_native_4bpp_tile_rows_do_not_transpose_or_mix_nibbles(self):
        image = Image.new('P', (24, 16))
        for y in range(16):
            for x in range(24):
                image.putpixel((x, y), (x // 3 + y * 7) % 16)
        encoded = tiled_bytes(image)
        self.assertEqual(len(encoded), 192)
        for y in range(16):
            for x in range(24):
                offset = ((y // 8) * 3 + x // 8) * 32 + (y % 8) * 4 + (x % 8) // 2
                decoded = (encoded[offset] >> (4 if x % 2 else 0)) & 15
                self.assertEqual(decoded, image.getpixel((x, y)))

    def test_route_location_uses_distance_along_corridor_not_diagonal_average(self):
        self.assertEqual(path_midpoint([(10, 30), (30, 30), (30, 60)]), (30, 35))
        self.assertEqual(path_midpoint([(30, 60), (30, 30), (10, 30)]), (30, 35))
        self.assertEqual(path_midpoint([(12, 20), (12, 40)]), (12, 30))

    def test_all_actual_routes_and_marker_extents_fit_the_native_chart(self):
        manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
        places, routes = records(manifest, physical=False)
        positions = chart_positions(manifest)
        self.assertEqual(set(positions), {a['id'] for a in places})
        self.assertEqual(len(set(positions.values())), 19)
        self.assertEqual(len(routes), 21)
        for x, y in positions.values():
            # Selected corners, the current-player cap and bottom name panel.
            self.assertGreaterEqual(x - 8, 0)
            self.assertLessEqual(x + 8, 223)
            self.assertGreaterEqual(y - 11, 16)
            self.assertLessEqual(y + 6, 127)
        for route in routes:
            points = route_path(route, positions)
            self.assertEqual(points[0], positions[route['from']])
            self.assertEqual(points[-1], positions[route['to']])
            point = path_midpoint(points)
            self.assertTrue(any(min(x, u) <= point[0] <= max(x, u) and
                                min(y, v) <= point[1] <= max(y, v)
                                for (x, y), (u, v) in zip(points, points[1:])))


if __name__ == '__main__':
    unittest.main()
