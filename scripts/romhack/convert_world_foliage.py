"""Bound the original foliage atlas to native cards and an original RGB555 palette."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from convert_world_landmarks import silhouette

DIRECTORY=Path(__file__).resolve().parents[2]/'assets/tiles/sf-foliage-v1'
COLORS=[(0,0,0),(3,7,6),(5,11,7),(9,14,7),(12,17,9),(16,20,11),
        (20,23,14),(11,8,5),(17,11,6),(22,16,9),(6,9,13),
        (10,14,18),(16,20,23),(22,25,26),(28,29,27),(13,16,13)]
CARDS=[('cypress',(0,0,595,724),(32,32)),('pine',(600,0,1080,724),(32,48)),
       ('shrub',(1090,0,1640,724),(32,32)),('rocks',(1650,0,2172,724),(32,32))]


def main():
    source=Image.open(DIRECTORY/'source.png').convert('RGBA')
    rgb=[tuple(c*255//31 for c in color) for color in COLORS]
    files={};cards=[];preview=Image.new('RGBA',(160,64),(149,164,113,255))
    for index,(name,bounds,size) in enumerate(CARDS):
        cut=silhouette(source.crop(bounds));cut=cut.crop(cut.getbbox())
        scale=min((size[0]-2)/cut.width,(size[1]-2)/cut.height)
        cut=cut.resize((round(cut.width*scale),round(cut.height*scale)),Image.Resampling.BOX)
        raw=bytearray(size[0]*size[1]);left=(size[0]-cut.width)//2;top=size[1]-cut.height
        for y in range(cut.height):
            for x in range(cut.width):
                color=cut.getpixel((x,y))
                if color[3]>=128:
                    raw[(top+y)*size[0]+left+x]=min(range(1,16),key=lambda i:sum((color[c]-rgb[i][c])**2 for c in range(3)))
        (DIRECTORY/(name+'.indices')).write_bytes(raw)
        image=Image.new('P',size);image.putpalette([c for color in rgb for c in color]+[0]*720)
        image.putdata(raw);image.info['transparency']=0;image.save(DIRECTORY/(name+'.png'))
        preview.alpha_composite(image.convert('RGBA'),(index*40,64-size[1]))
        cards.append({'name':name,'source_bounds':bounds,'size':size})
        for suffix in ('.indices','.png'):
            p=DIRECTORY/(name+suffix);files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    (DIRECTORY/'foliage.gbapal').write_bytes(struct.pack('<16H',*(r|g<<5|b<<10 for r,g,b in COLORS)))
    preview.resize((960,384),Image.Resampling.NEAREST).save(DIRECTORY/'native-preview.png')
    for name in ('source.png','prompt.md','foliage.gbapal','native-preview.png'):
        files[name]=hashlib.sha256((DIRECTORY/name).read_bytes()).hexdigest()
    (DIRECTORY/'conversion.json').write_text(json.dumps({'schema_version':1,'tool':'built-in imagegen',
        'conversion':'connected silhouette; proportional BOX reduction; nearest RGB555 color; alpha128; no dithering',
        'cards':cards,'files':files},indent=2)+'\n')
    print(json.dumps({'cards':len(cards),'palette_colors':16}))


if __name__=='__main__':main()
