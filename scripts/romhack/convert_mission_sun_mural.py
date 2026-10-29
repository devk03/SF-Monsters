"""Convert original generated mural into the existing GBA neighborhood palette."""
import hashlib
import json
from pathlib import Path
from PIL import Image
from convert_neighborhood_landmarks import COLORS

ROOT=Path(__file__).resolve().parents[2]
DIRECTORY=ROOT/'assets/tiles/mission-mural-sun-v1'


def main():
    source=Image.open(DIRECTORY/'source.png').convert('RGBA')
    mask=source.getchannel('A').point(lambda value:255 if value>=128 else 0)
    bounds=mask.getbbox()
    if not bounds:raise ValueError('Mural source has no visible pixels')
    cut=source.crop(bounds);size=(64,32)
    scale=min((size[0]-2)/cut.width,(size[1]-2)/cut.height)
    cut=cut.resize((round(cut.width*scale),round(cut.height*scale)),Image.Resampling.BOX)
    palette=[tuple(c*255//31 for c in rgb) for rgb in COLORS]
    raw=bytearray(size[0]*size[1]);left=(size[0]-cut.width)//2;top=size[1]-cut.height
    for y in range(cut.height):
        for x in range(cut.width):
            pixel=cut.getpixel((x,y))
            if pixel[3]>=128:
                raw[(top+y)*size[0]+left+x]=min(range(1,16),key=lambda i:sum((pixel[c]-palette[i][c])**2 for c in range(3)))
    (DIRECTORY/'mural.indices').write_bytes(raw)
    image=Image.new('P',size);image.putpalette([c for rgb in palette for c in rgb]+[0]*720)
    image.putdata(raw);image.info['transparency']=0;image.save(DIRECTORY/'mural.png')
    files={n:hashlib.sha256((DIRECTORY/n).read_bytes()).hexdigest()
           for n in ('source.png','mural.indices','mural.png','prompt.md')}
    receipt={'schema_version':1,'tool':'built-in imagegen','source_size':list(source.size),
             'source_bounds':list(bounds),'size':list(size),'palette':'neighborhood-landmarks-v1 bank11',
             'conversion':'alpha crop, aspect-preserving BOX reduction, fixed RGB555 palette, no dithering',
             'files':files}
    (DIRECTORY/'conversion.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'bounds':bounds,'output':str(DIRECTORY/'mural.png')}))


if __name__=='__main__':main()
