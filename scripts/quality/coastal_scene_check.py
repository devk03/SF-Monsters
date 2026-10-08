"""Reject the known beach capture where opaque ground hid the courier sprite.

This checks the fixed standing-at-(4,8) scene, not arbitrary maps or art quality.
Run against capture.final.rgba after the documented native coast boot route.
"""
from pathlib import Path
import argparse
import json


def check_coastal_courier(rgba):
    if len(rgba) != 240 * 160 * 4:
        raise ValueError('Expected one complete native 240x160 RGBA frame.')
    def pixel(x, y):
        return rgba[(y * 240 + x) * 4:(y * 240 + x) * 4 + 3]
    # Establish the warm beach scene so a dark title/menu cannot pass this check.
    warm_sand = sum(r > g + 10 and g > b + 10
                    for y in range(16, 32) for x in range(144, 160)
                    for r, g, b in [pixel(x, y)])
    rows = [sum(max(pixel(x, y)) < 140 for x in range(112, 128))
            for y in range(56, 88)]
    result = {'warm_sand_pixels': warm_sand, 'courier_dark_pixels': sum(rows),
              'courier_visible_rows': sum(count > 0 for count in rows)}
    if warm_sand < 128:
        raise ValueError('Capture is not the documented beach scene.')
    if sum(rows) < 96 or sum(count > 0 for count in rows) < 18:
        raise ValueError('Courier silhouette is obscured in the documented beach scene.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    print(json.dumps(check_coastal_courier(args.frame.read_bytes())))
