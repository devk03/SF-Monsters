"""Compile the original generated SF relief into the native window palette."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / 'assets/ui/sf-region-relief-v2'
PALETTE = [(0,0,0),(31,31,29),(4,10,14),(22,22,18),(5,13,23),(11,20,28),
           (14,20,8),(20,24,12),(4,12,6),(26,24,17),(15,12,8),(29,22,10),
           (4,10,20),(16,25,28),(26,9,4),(31,29,22)]


def convert(directory=DIRECTORY):
    source = directory / 'source.png'
    image = Image.open(source).convert('RGB').resize((224,112), Image.Resampling.BOX)
    colors = [tuple(v * 255 // 31 for v in color) for color in PALETTE]
    indices = bytes(min(range(1,16), key=lambda n: sum((pixel[c]-colors[n][c])**2 for c in range(3)))
                    for pixel in image.get_flattened_data())
    output = Image.frombytes('P', (224,112), indices)
    output.putpalette([v for color in colors for v in color]+[0]*(768-48))
    output.save(directory / 'native.png')
    (directory / 'native.indices').write_bytes(indices)
    (directory / 'palette.json').write_text(json.dumps(PALETTE,indent=2)+'\n')
    proof = dict(tool='built-in imagegen',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                 native_sha256=hashlib.sha256(indices).hexdigest(),size=[224,112],
                 conversion='BOX native reduction; curated RGB555 palette; nearest color without dithering',
                 human_quality_approval='pending')
    (directory / 'conversion.json').write_text(json.dumps(proof,indent=2)+'\n')


if __name__ == '__main__':
    convert()
