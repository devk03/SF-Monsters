"""Compile six original neighborhood silhouettes to restrained native SF cards."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from convert_world_landmarks import silhouette

DIRECTORY=Path(__file__).resolve().parents[2]/'assets/tiles/neighborhood-landmarks-v1'
CARDS=[('mural',(20,255,500,555),(64,32)),('lookout',(520,260,1055,560),(48,32)),
       ('mansion',(1060,20,1536,580),(64,64)),('surfboards',(85,650,505,955),(32,32)),
       ('bar_sign',(690,665,855,985),(16,32)),('book_box',(1160,670,1385,990),(16,32))]
COLORS=[(0,0,0),(5,7,10),(14,15,16),(23,24,22),(31,30,25),(29,15,9),
        (30,20,6),(25,7,5),(21,17,26),(5,12,18),(12,21,26),(8,15,7),
        (17,21,10),(19,14,9),(31,26,10),(27,12,20)]


def main():
    source=Image.open(DIRECTORY/'source.png').convert('RGBA');rgb=[tuple(c*255//31 for c in color) for color in COLORS]
    files={};cards=[];preview=Image.new('RGBA',(240,144),(204,207,205,255))
    for index,(name,bounds,size) in enumerate(CARDS):
        cut=silhouette(source.crop(bounds));cut=cut.crop(cut.getbbox());scale=min((size[0]-2)/cut.width,(size[1]-2)/cut.height)
        cut=cut.resize((round(cut.width*scale),round(cut.height*scale)),Image.Resampling.BOX)
        raw=bytearray(size[0]*size[1]);left=(size[0]-cut.width)//2;top=size[1]-cut.height
        for y in range(cut.height):
            for x in range(cut.width):
                color=cut.getpixel((x,y))
                if color[3]>=128:raw[(top+y)*size[0]+left+x]=min(range(1,16),key=lambda i:sum((color[c]-rgb[i][c])**2 for c in range(3)))
        (DIRECTORY/(name+'.indices')).write_bytes(raw)
        image=Image.new('P',size);image.putpalette([c for color in rgb for c in color]+[0]*720);image.putdata(raw)
        image.info['transparency']=0;image.save(DIRECTORY/(name+'.png'))
        preview.alpha_composite(image.convert('RGBA'),((index%3)*80,(index//3)*72+64-size[1]))
        cards.append({'name':name,'source_bounds':bounds,'size':size})
        for suffix in ('.indices','.png'):
            p=DIRECTORY/(name+suffix);files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    (DIRECTORY/'neighborhood.gbapal').write_bytes(struct.pack('<16H',*(r|g<<5|b<<10 for r,g,b in COLORS)))
    preview.resize((1200,720),Image.Resampling.NEAREST).save(DIRECTORY/'native-preview.png')
    for name in ('source.png','prompt.md','neighborhood.gbapal','native-preview.png'):
        files[name]=hashlib.sha256((DIRECTORY/name).read_bytes()).hexdigest()
    (DIRECTORY/'conversion.json').write_text(json.dumps({'schema_version':1,'tool':'built-in imagegen',
        'method':'connected opaque silhouette; proportional native reduction; fixed15-color RGB555; alpha128; no dithering',
        'cards':cards,'files':files},indent=2)+'\n');print(json.dumps({'cards':len(cards),'colors':16}))


if __name__=='__main__':main()
