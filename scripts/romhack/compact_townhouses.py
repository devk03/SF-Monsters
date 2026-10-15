"""Original narrow pair matching the accepted connected SF house palette."""
import json
from pathlib import Path
import struct
from connected_frontage import COLORS,sha

ASSET='assets/tiles/compact-townhouses-v1'
BOUNDS=(137,166,1117,1058)


def encode(root):
    from PIL import Image
    directory=root/ASSET;source=Image.open(directory/'source.png').convert('RGBA')
    if source.size!=(1254,1254):raise ValueError('Review compact townhouse source coordinates.')
    native=source.crop(BOUNDS).resize((64,64),Image.Resampling.NEAREST)
    pixels=bytes(0 if rgba[3]<128 else min(range(1,16),key=lambda index:
        sum((round(rgba[c]*31/255)-COLORS[index][c])**2 for c in range(3)))
        for rgba in native.get_flattened_data())
    palette=b''.join(struct.pack('<H',sum(rgb[c]<<(5*c) for c in range(3))) for rgb in COLORS)
    image=Image.new('P',(64,64));image.putpalette([c*255//31 for rgb in COLORS for c in rgb]+[0]*720)
    image.putdata(pixels);image.save(directory/'native.png',bits=4,transparency=0)
    (directory/'pair.indices').write_bytes(pixels);(directory/'pair.gbapal').write_bytes(palette)
    info={'generator':'Built-in imagegen, original compact SF architecture',
          'source_sha256':sha((directory/'source.png').read_bytes()),
          'prompt_sha256':sha((directory/'prompt.md').read_bytes()),
          'reference_sha256':sha((root/'assets/tiles/connected-frontage-v3/native.png').read_bytes()),
          'source_size':[1254,1254],'source_bounds':list(BOUNDS),'native_size':[64,64],
          'method':'Whole paired block crop; nearest64x64; alpha128; unchanged shared RGB55515',
          'files':{n:sha((directory/n).read_bytes()) for n in ('native.png','pair.indices','pair.gbapal')},
          'approval':'Candidate only; native map integration and human review pending'}
    (directory/'conversion.json').write_text(json.dumps(info,indent=2)+'\n');return info


def load(root):
    from PIL import Image
    directory=root/ASSET;info=json.loads((directory/'conversion.json').read_text())
    for file,key in (('source.png','source_sha256'),('prompt.md','prompt_sha256')):
        if sha((directory/file).read_bytes())!=info[key]:raise ValueError('Compact townhouse provenance changed: '+file)
    reference=root/'assets/tiles/connected-frontage-v3/native.png'
    if sha(reference.read_bytes())!=info['reference_sha256'] or (
            info['source_size'],info['source_bounds'],info['native_size'])!=([1254,1254],list(BOUNDS),[64,64]):
        raise ValueError('Compact townhouse geometry or original style reference changed.')
    if set(info['files'])!={'native.png','pair.indices','pair.gbapal'}:
        raise ValueError('Compact townhouse consumed file set changed.')
    for file,digest in info['files'].items():
        if sha((directory/file).read_bytes())!=digest:raise ValueError('Compact townhouse native resource changed: '+file)
    pixels=(directory/'pair.indices').read_bytes();palette=(directory/'pair.gbapal').read_bytes()
    expected=b''.join(struct.pack('<H',sum(rgb[c]<<(5*c) for c in range(3))) for rgb in COLORS)
    if len(pixels)!=4096 or max(pixels)>15 or palette!=expected:
        raise ValueError('Compact townhouse allocation or shared palette changed.')
    with Image.open(directory/'native.png') as image:
        if (image.mode,image.size,image.tobytes(),image.getpalette()[:48],image.info.get('transparency'))!=(
                'P',(64,64),pixels,[c*255//31 for rgb in COLORS for c in rgb],0):
            raise ValueError('Compact townhouse preview differs from native indices.')
    return pixels,palette


if __name__=='__main__':
    print(json.dumps(encode(Path(__file__).resolve().parents[2]),indent=2))
