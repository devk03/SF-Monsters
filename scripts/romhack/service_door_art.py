"""Compile original service-door stages with stationary jambs and opaque portals."""
import json
from pathlib import Path
import struct
from connected_frontage import COLORS, sha
from door_art import native_frames

ASSET='assets/tiles/service-door-v2'
NAMES=('warehouse','clinic')
BOXES=(((43,73,316,596),(407,73,679,596),(771,73,1044,596)),
       ((43,763,316,1286),(407,762,679,1286),(771,763,1044,1286)))
MOVING=(3,5,13,26)


def validate(frames):
    if len(frames)!=3 or any(len(f)!=512 or max(f)>15 for f in frames):
        raise ValueError('Service door requires three16x32 four-bit stages.')
    moving={y*16+x for y in range(MOVING[1],MOVING[3])
            for x in range(MOVING[0],MOVING[2])}
    for frame in frames:
        if any(frame[i]!=frames[0][i] for i in range(512) if i not in moving):
            raise ValueError('Service-door jambs and steps must stay stationary.')
        if any(not frame[i] for i in moving):
            raise ValueError('Service doorway must remain opaque during opening.')
    if frames[0]==frames[1] or frames[1]==frames[2] or frames[0]==frames[2]:
        raise ValueError('Service door needs distinct closed, partial and open stages.')
    return native_frames(frames)


def encode(root):
    from PIL import Image
    directory=root/ASSET;source=Image.open(directory/'source.png').convert('RGBA')
    if source.size!=(1086,1448):
        raise ValueError('Review original service-door source coordinates.')
    files=[]
    for name,boxes in zip(NAMES,BOXES):
        candidates=[]
        for box in boxes:
            image=source.crop(box).resize((16,32),Image.Resampling.NEAREST)
            candidates.append(bytes(0 if rgba[3]<128 else min(range(1,16),key=lambda i:
                sum((round(rgba[c]*31/255)-COLORS[i][c])**2 for c in range(3)))
                for rgba in image.get_flattened_data()))
        frames=[candidates[0]]
        for candidate in candidates[1:]:
            frame=bytearray(frames[0])
            for y in range(MOVING[1],MOVING[3]):
                for x in range(MOVING[0],MOVING[2]):frame[y*16+x]=candidate[y*16+x]
            frames.append(bytes(frame))
        packed=validate(frames)
        sheet=Image.new('P',(48,32))
        sheet.putpalette([c*255//31 for rgb in COLORS for c in rgb]+[0]*720)
        sheet.putdata(b''.join(f[y*16:(y+1)*16] for y in range(32) for f in frames))
        sheet.save(directory/(name+'.png'),bits=4,transparency=0)
        (directory/(name+'.indices')).write_bytes(b''.join(frames))
        (directory/(name+'.4bpp')).write_bytes(packed)
        files.extend(name+suffix for suffix in ('.png','.indices','.4bpp'))
    references={name+'-closed-reference.png':sha((directory/(name+'-closed-reference.png')).read_bytes())
                for name in NAMES}
    metadata={'source_sha256':sha((directory/'source.png').read_bytes()),
        'prompt_sha256':sha((directory/'prompt.md').read_bytes()),
        'source_bounds':BOXES,'moving_rectangle':MOVING,'size':[16,32],'stages':3,
        'palette_banks':[8,9],'references':references,
        'palette_sha256':sha(b''.join(struct.pack('<H',sum(rgb[c]<<(5*c) for c in range(3))) for rgb in COLORS)),
        'method':'Original source crops; nearest16x32; RGB55515; alpha128; fixed closed-frame jambs/steps',
        'static_door_cells':[[64,71],[99,106]],'quality_approval':'pending',
        'generator':'Built-in imagegen; original project references only',
        'files':{name:sha((directory/name).read_bytes()) for name in files}}
    (directory/'conversion.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata


def load(root):
    from PIL import Image
    directory=root/ASSET;info=json.loads((directory/'conversion.json').read_text())
    for file,key in [('source.png','source_sha256'),('prompt.md','prompt_sha256')]:
        if sha((directory/file).read_bytes())!=info[key]:
            raise ValueError('Service-door source provenance changed.')
    if info['source_bounds']!=[[list(b) for b in row] for row in BOXES] or (
            info['moving_rectangle'],info['size'],info['stages'],info['palette_banks'])!=(list(MOVING),[16,32],3,[8,9]):
        raise ValueError('Service-door native geometry changed.')
    packed_palette=b''.join(struct.pack('<H',sum(rgb[c]<<(5*c) for c in range(3))) for rgb in COLORS)
    if info['palette_sha256']!=sha(packed_palette) or info['static_door_cells']!=[[64,71],[99,106]]:
        raise ValueError('Service-door palette or static bindings changed.')
    for name,digest in {**info['files'],**info['references']}.items():
        if sha((directory/name).read_bytes())!=digest:
            raise ValueError('Service-door serialized resource changed: '+name)
    result={};palette=[c*255//31 for rgb in COLORS for c in rgb]
    for name in NAMES:
        data=(directory/(name+'.indices')).read_bytes()
        if len(data)!=1536:raise ValueError('Service-door indexed length changed.')
        frames=[data[i*512:(i+1)*512] for i in range(3)]
        if validate(frames)!=(directory/(name+'.4bpp')).read_bytes():
            raise ValueError('Service-door native tile order differs from indexed stages.')
        image=Image.open(directory/(name+'.png'))
        expected=b''.join(f[y*16:(y+1)*16] for y in range(32) for f in frames)
        if (image.mode,image.size,image.tobytes(),image.getpalette()[:48])!=('P',(48,32),expected,palette):
            raise ValueError('Service-door preview differs from consumed frames.')
        result[name]=frames
    return result


if __name__=='__main__':
    print(json.dumps(encode(Path(__file__).resolve().parents[2]),indent=2))
