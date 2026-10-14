"""Native habitat behavior and the two incompatible GBA tilemap encodings."""
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))
from city_map_art import make_map

parent = ROOT / '.tools/city-map-tests'
parent.mkdir(parents=True, exist_ok=True)
work = Path(tempfile.mkdtemp(prefix='case-', dir=parent))
(work / 'sf_habitat_maps.h').write_text('static const u8 sSFHabitatMapIds[][2]={{0,9},{0,10}};\n')
(work / 'sf_city_map_parents.h').write_text(
    'static const u8 sSFRegionMapParents[][3]={{0,9,0},{1,0,0},{0,10,1},{1,4,1},{11,3,1},{2,0,1}};\n')
subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                '-I' + str(work), str(ROOT / 'tests/city_map_native_test.c'), '-o', str(work / 'test')], check=True)
subprocess.run([str(work / 'test')], check=True)
image, atlas, regular, affine, palette, hubs, count = make_map(ROOT)
assert len(regular) == 2048 and len(affine) == 4096 and len(palette) == 96
assert count <= 232 and [(h['x'], h['y']) for h in hubs] == [(7, 8), (18, 5)]
assert set(image.tobytes()) <= set(range(112, 160))
# Independently reconstruct both hardware formats to catch swapped sizes/stride.
words = struct.unpack('<1024H', regular)
for y in range(32):
    for x in range(32):
        tile = words[y * 32 + x]
        assert tile == affine[y * 64 + x] and tile < count
        actual = atlas.crop((tile % 16 * 8, tile // 16 * 8, tile % 16 * 8 + 8, tile // 16 * 8 + 8)).tobytes()
        assert actual == image.crop((x * 8, y * 8, x * 8 + 8, y * 8 + 8)).tobytes()
print('SF map: native text/affine strides, geographic anchors, palette isolation and tile budget passed.')
