"""Compile original curbside props to small, palette-compatible native cards."""
import hashlib
import json
from pathlib import Path
from connected_frontage import COLORS
import struct

ASSET = 'assets/tiles/city-furniture-v1'
# name, original source bounds, native footprint. Crops retain original alpha.
CARDS = (
    ('lamp', (118,106,292,579), (16,32)),
    ('meter', (533,390,619,578), (16,16)),
    ('hydrant', (897,414,1027,580), (16,16)),
    ('bin', (1264,404,1394,578), (16,16)),
    ('rack', (43,804,353,966), (32,16)),
    ('tree', (426,583,720,972), (32,32)),
    ('bench', (811,802,1110,974), (32,16)),
    ('recycling', (1204,797,1477,974), (32,16)),
)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def encode(root):
    from PIL import Image
    directory = root/ASSET
    source = Image.open(directory/'source.png').convert('RGBA')
    if source.size != (1536,1024):
        raise ValueError('Review original furniture source coordinates.')
    frames = []
    palette = b''.join(struct.pack('<H',sum(rgb[c]<<(5*c) for c in range(3))) for rgb in COLORS)
    preview_palette = [c*255//31 for rgb in COLORS for c in rgb]+[0]*720
    for name,bounds,(width,height) in CARDS:
        crop = source.crop(bounds)
        # Preserve proportions; all feet share the bottom of their native card.
        factor = min(width/crop.width,height/crop.height)
        size = (max(1,round(crop.width*factor)),max(1,round(crop.height*factor)))
        native = crop.resize(size,Image.Resampling.NEAREST)
        canvas = Image.new('RGBA',(width,height));canvas.paste(native,((width-size[0])//2,height-size[1]))
        pixels = bytes(0 if rgba[3]<128 else min(range(1,16),key=lambda index:
            sum((round(rgba[c]*31/255)-COLORS[index][c])**2 for c in range(3)))
            for rgba in canvas.get_flattened_data())
        image = Image.new('P',(width,height));image.putpalette(preview_palette)
        image.putdata(pixels);image.save(directory/(name+'.png'),bits=4,transparency=0)
        frames.append({'name':name,'bounds':list(bounds),'size':[width,height],
                       'indices_sha256':sha(pixels),'png_sha256':sha((directory/(name+'.png')).read_bytes())})
        (directory/(name+'.indices')).write_bytes(pixels)
    (directory/'furniture.gbapal').write_bytes(palette)
    result = {'generator':'Built-in imagegen; original city furniture',
              'source_sha256':sha((directory/'source.png').read_bytes()),
              'prompt_sha256':sha((directory/'prompt.md').read_bytes()),
              'reference_sha256':sha((root/'assets/tiles/connected-frontage-v3/native.png').read_bytes()),
              'method':'Fixed original crops; proportional nearest; bottom-center alignment; alpha128; shared RGB55515',
              'palette_sha256':sha(palette),'cards':frames,
              'approval':'Candidate; native placement and human quality acceptance pending'}
    (directory/'conversion.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def load(root):
    from PIL import Image
    directory = root/ASSET
    info = json.loads((directory/'conversion.json').read_text())
    for file,key in (('source.png','source_sha256'),('prompt.md','prompt_sha256'),
                     ('furniture.gbapal','palette_sha256')):
        if sha((directory/file).read_bytes()) != info[key]:
            raise ValueError('City furniture provenance changed: '+file)
    palette = b''.join(struct.pack('<H',sum(rgb[c]<<(5*c) for c in range(3))) for rgb in COLORS)
    if (directory/'furniture.gbapal').read_bytes() != palette:
        raise ValueError('City furniture must retain the connected block palette.')
    if len(info['cards']) != len(CARDS):
        raise ValueError('City furniture card allocation changed.')
    result = []
    for expected,receipt in zip(CARDS,info['cards']):
        name,bounds,size = expected
        if (receipt['name'],receipt['bounds'],receipt['size']) != (name,list(bounds),list(size)):
            raise ValueError('City furniture geometry changed.')
        pixels = (directory/(name+'.indices')).read_bytes()
        if len(pixels) != size[0]*size[1] or max(pixels)>15 or sha(pixels)!=receipt['indices_sha256']:
            raise ValueError('City furniture indices changed: '+name)
        file = directory/(name+'.png')
        if sha(file.read_bytes())!=receipt['png_sha256']:
            raise ValueError('City furniture preview changed: '+name)
        with Image.open(file) as image:
            if (image.mode,image.size,image.tobytes(),image.getpalette()[:48],image.info.get('transparency')) != (
                    'P',size,pixels,[c*255//31 for rgb in COLORS for c in rgb],0):
                raise ValueError('City furniture preview differs from native data: '+name)
        result.append({'name':name,'width':size[0],'height':size[1],'pixels':pixels,'bank':5})
    return result


if __name__ == '__main__':
    print(json.dumps(encode(Path(__file__).resolve().parents[2]),indent=2))
