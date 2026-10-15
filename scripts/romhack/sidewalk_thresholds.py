"""Original shallow facade aprons, top-aligned over existing gray paving."""
import hashlib
import json
from pathlib import Path
import struct

ASSET='assets/tiles/sidewalk-thresholds-v1'
# source quadrant, name, native width. Remaining native rows stay transparent.
STYLES=((0,'bay',48),(1,'brick',48),(2,'sage',48),(3,'coffee',32))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(root):
    from PIL import Image
    directory=root/ASSET
    source=Image.open(directory/'source.png').convert('RGBA')
    cards=[];visible=[]
    for quadrant,name,width in STYLES:
        col,row=quadrant%2,quadrant//2
        box=(col*source.width//2,row*source.height//2,
             (col+1)*source.width//2,(row+1)*source.height//2)
        cell=source.crop(box)
        bounds=cell.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
        if bounds is None:raise ValueError('Each threshold quadrant needs visible architecture.')
        cell=cell.crop(bounds)
        height=round(cell.height*width/cell.width)
        if not 1<=height<=8:raise ValueError('Keep threshold art shallow; at least half the apron stays open.')
        cell=cell.resize((width,height),Image.Resampling.NEAREST)
        visible.extend(rgba[:3] for rgba in cell.get_flattened_data() if rgba[3]>=128)
        cards.append((name,width,height,box,bounds,cell))
    samples=Image.new('RGB',(len(visible),1));samples.putdata(visible)
    palette=samples.quantize(colors=15,method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    colors=[(0,0,0)]+[tuple(round(c*31/255) for c in palette[i:i+3]) for i in range(0,45,3)]
    packed=b''.join(struct.pack('<H',sum(rgb[c]<<(5*c) for c in range(3))) for rgb in colors)
    (directory/'thresholds.gbapal').write_bytes(packed)
    metadata=[]
    for name,width,height,box,bounds,cell in cards:
        native=Image.new('P',(width,16),0)
        native.putpalette([value*255//31 for color in colors for value in color]+[0]*720)
        pixels=bytearray(width*16)
        for i,rgba in enumerate(cell.get_flattened_data()):
            if rgba[3]>=128:
                rgb=tuple(round(c*31/255) for c in rgba[:3])
                pixels[i]=min(range(1,16),key=lambda index:sum((rgb[c]-colors[index][c])**2 for c in range(3)))
        native.putdata(pixels);native.save(directory/(name+'.png'),bits=4,transparency=0)
        (directory/(name+'.indices')).write_bytes(pixels)
        files={name+suffix:sha((directory/(name+suffix)).read_bytes()) for suffix in ('.png','.indices')}
        metadata.append({'name':name,'size':[width,16],'art_height':height,
                         'source_quadrant':box,'source_bounds':list(bounds),'files':files})
    info={'source_sha256':sha((directory/'source.png').read_bytes()),
          'prompt_sha256':sha((directory/'prompt.md').read_bytes()),'source_size':list(source.size),
          'palette_sha256':sha(packed),'alpha_threshold':128,'bank':5,'cards':metadata,
          'method':'Quadrant alpha crop; aspect-preserving nearest resize; top-aligned; shared RGB55515; transparent0',
          'generator':'Built-in imagegen, original architectural ground details',
          'quality_approval':'pending'}
    (directory/'conversion.json').write_text(json.dumps(info,indent=2)+'\n')
    return info


def load(root):
    from PIL import Image
    directory=root/ASSET
    info=json.loads((directory/'conversion.json').read_text())
    if info['source_sha256']!=sha((directory/'source.png').read_bytes()) or \
       info['prompt_sha256']!=sha((directory/'prompt.md').read_bytes()):
        raise ValueError('Threshold source/prompt differs from consumed native resources.')
    palette=(directory/'thresholds.gbapal').read_bytes()
    if len(palette)!=32 or sha(palette)!=info['palette_sha256'] or info['bank']!=5 or \
       info['alpha_threshold']!=128 or len(info['cards'])!=4:
        raise ValueError('Threshold palette, bank or conversion contract changed.')
    words=struct.unpack('<16H',palette)
    if words[0]!=0 or any(word>0x7fff for word in words):
        raise ValueError('Threshold palette requires transparent0 and RGB555 colors.')
    result={}
    for descriptor,(_,name,width) in zip(info['cards'],STYLES):
        if descriptor['name']!=name or descriptor['size']!=[width,16] or \
           not 1<=descriptor['art_height']<=8 or set(descriptor['files'])!={name+'.png',name+'.indices'}:
            raise ValueError('Threshold card geometry/order changed.')
        for filename,expected in descriptor['files'].items():
            if sha((directory/filename).read_bytes())!=expected:
                raise ValueError('Threshold resource changed: '+filename)
        pixels=(directory/(name+'.indices')).read_bytes()
        with Image.open(directory/(name+'.png')) as preview:
            image=preview.copy()
        if len(pixels)!=width*16 or not any(pixels) or max(pixels)>15 or any(pixels[width*8:]):
            raise ValueError('Threshold art must leave its lower eight rows transparent.')
        if image.mode!='P' or image.size!=(width,16) or image.tobytes()!=pixels or \
           image.info.get('transparency')!=0:
            raise ValueError('Threshold preview differs from its native pixels/transparency.')
        expected=[((word>>(5*c))&31)*255//31 for word in words for c in range(3)]
        if image.getpalette()[:48]!=expected:
            raise ValueError('Threshold preview palette differs from native colors.')
        result[name]={'width':width,'height':16,'pixels':pixels,'palette':palette,'bank':5}
    return result


if __name__=='__main__':
    print(json.dumps(encode(Path(__file__).resolve().parents[2]),indent=2))
