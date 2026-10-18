"""Compile the original generated atlas into small palette-bounded GBA cards."""
import hashlib
import json
import struct
from collections import deque
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
DIRECTORY=ROOT/'assets/tiles/sf-landmarks-v1'
# Measured alpha-component bounds, not assumed equal atlas cells. Transparent
# neighbors never bleed into a card; source and all native outputs stay saved.
CARDS=[('sutro_tower',(68,20,298,466),(48,80)),
       ('windmill',(416,107,704,460),(48,64)),
       ('conservatory',(762,170,1217,467),(64,48)),
       ('bath_ruins',(1266,290,1740,476),(64,32)),
       ('highrise',(50,510,286,858),(48,80)),
       ('crane',(381,521,792,849),(64,64)),
       ('stadium_gate',(788,563,1250,840),(96,64)),
       ('theater',(1346,572,1758,849),(80,64))]
# One original fifteen-color RGB555 set plus transparency. No dithering or
# intermediate subpixel colors enter the cartridge.
COLORS=[(0,0,0),(5,7,10),(14,15,16),(21,21,20),(30,30,28),
        (27,9,7),(17,5,5),(13,18,21),(20,25,27),(9,16,8),
        (5,10,5),(28,22,13),(18,12,8),(31,27,19),(24,17,8),(19,18,16)]


def silhouette(image):
    """Select the main alpha component; adjacent atlas silhouettes may overlap bounds."""
    w,h=image.size;pending={y*w+x for y in range(h) for x in range(w)
                            if image.getpixel((x,y))[3]>=128};largest=set()
    while pending:
        first=pending.pop();component={first};queue=deque([first])
        while queue:
            value=queue.popleft();y,x=divmod(value,w)
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    xx,yy=x+dx,y+dy;n=yy*w+xx
                    if 0<=xx<w and 0<=yy<h and n in pending:
                        pending.remove(n);component.add(n);queue.append(n)
        if len(component)>len(largest):largest=component
    result=image.copy()
    result.putalpha(Image.frombytes('L',(w,h),bytes(255 if i in largest else 0 for i in range(w*h))))
    return result


def main():
    source=Image.open(DIRECTORY/'source.png').convert('RGBA')
    rgb=[tuple(c*255//31 for c in color) for color in COLORS]
    palette=Image.new('P',(1,1));palette.putpalette([c for color in rgb for c in color]+[0]*720)
    # Fit each silhouette within its native card without stretching the object.
    # Alpha is thresholded only after BOX area reduction, preserving clear edges.
    preview=Image.new('RGBA',(320,176),(202,207,205,255));records=[]
    files={}
    for index,(name,bounds,size) in enumerate(CARDS):
        cut=silhouette(source.crop(bounds));scale=min((size[0]-4)/cut.width,(size[1]-2)/cut.height)
        cut=cut.resize((round(cut.width*scale),round(cut.height*scale)),Image.Resampling.BOX)
        quantized=cut.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE)
        pixels=bytearray(size[0]*size[1]);ox=(size[0]-cut.width)//2;oy=size[1]-cut.height
        for y in range(cut.height):
            for x in range(cut.width):
                if cut.getpixel((x,y))[3]>=128:
                    value=quantized.getpixel((x,y))
                    # Palette entry zero is reserved for transparent pixels.
                    if value==0:
                        color=cut.getpixel((x,y))[:3]
                        value=min(range(1,16),key=lambda i:sum((color[c]-rgb[i][c])**2 for c in range(3)))
                    pixels[(oy+y)*size[0]+ox+x]=value
        path=DIRECTORY/(name+'.indices');path.write_bytes(pixels)
        image=Image.new('P',size);image.putdata(pixels);image.putpalette(palette.getpalette())
        image.info['transparency']=0
        image.save(DIRECTORY/(name+'.png'),transparency=0)
        preview.alpha_composite(image.convert('RGBA'),((index%4)*80,(index//4)*88))
        records.append({'name':name,'source_bounds':bounds,'size':size,'indices_sha256':hashlib.sha256(pixels).hexdigest()})
        for suffix in ('.indices','.png'):
            p=DIRECTORY/(name+suffix);files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    pal=struct.pack('<16H',*(r|(g<<5)|(b<<10) for r,g,b in COLORS))
    (DIRECTORY/'landmarks.gbapal').write_bytes(pal)
    preview.resize((1280,704),Image.Resampling.NEAREST).save(DIRECTORY/'native-preview.png')
    for name in ('source.png','prompt.md','landmarks.gbapal','native-preview.png'):
        files[name]=hashlib.sha256((DIRECTORY/name).read_bytes()).hexdigest()
    receipt={'schema_version':1,'tool':'built-in imagegen','source_size':source.size,
             'conversion':'measured alpha bounds; aspect-preserving BOX reduction; fixed RGB555 palette; no dithering',
             'cards':records,'files':files}
    (DIRECTORY/'conversion.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'cards':len(records),'palette_colors':16,'preview':str(DIRECTORY/'native-preview.png')}))


if __name__=='__main__':main()
