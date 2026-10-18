"""Read compiled scenery bytes independently of the SF art/tile composer."""
import hashlib,struct,sys
from pathlib import Path
from PIL import Image


def audit_resources(rom,read,secondary,profile,engine):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'quality'))
    from check_creature_resources import decode_lz
    directory=engine/'data/tilesets/secondary'/('petalburg' if profile=='residential' else 'sf_world_'+profile)
    image=Image.open(directory/'tiles.png')
    if image.mode!='P' or image.size!=(128,256):raise ValueError('Scenery needs 512 indexed native tiles')
    raw=bytearray()
    for index in range(512):
        left,top=index%16*8,index//16*8
        for y in range(8):
            for x in range(0,8,2):
                a,b=image.getpixel((left+x,top+y)),image.getpixel((left+x+1,top+y))
                if not 0<=a<16 or not 0<=b<16:raise ValueError('Scenery PNG exceeds 4bpp')
                raw.append(a|b<<4)
    graphics,palettes,metatiles,attributes=read(secondary+4,'4I')
    compressed=rom[graphics-0x08000000:graphics-0x08000000+32768]
    resources=[('graphics',bytes(raw),decode_lz(compressed))]
    for name,pointer in (('metatiles',metatiles),('metatile_attributes',attributes)):
        source=(directory/(name+'.bin')).read_bytes()
        actual=bytes(read(pointer,str(len(source))+'B'))
        resources.append((name,source,actual))
    source=resources[1][1]
    if len(source)%16:raise ValueError('Native metatile records are incomplete')
    for word in struct.unpack('<'+'H'*(len(source)//2),source):
        if not 512<=word&1023<1024 or not 6<=word>>12<=12:
            raise ValueError('SF record addresses an unloaded native tile/palette bank')
    if profile=='residential':
        colors=[]
        for bank in range(16):
            rows=(directory/f'palettes/{bank:02d}.pal').read_text().splitlines()
            if rows[:3]!=['JASC-PAL','0100','16'] or len(rows)!=19:raise ValueError('Invalid native palette input')
            for row in rows[3:]:
                rgb=tuple(map(int,row.split()))
                if len(rgb)!=3 or any(not 0<=c<=255 for c in rgb):raise ValueError('Palette channel out of bounds')
                colors.append(sum((rgb[c]//8)<<(5*c) for c in range(3)))
        source=struct.pack('<256H',*colors)
    else:source=(directory/'palettes.gbapal').read_bytes()
    if len(source)!=512:raise ValueError('Native scenery palettes need sixteen stored banks')
    resources.append(('palettes',source,bytes(read(palettes,'512B'))))
    result=[]
    for name,expected,actual in resources:
        if actual!=expected:raise ValueError(profile+': compiled '+name+' differs from normal compiler input')
        result.append({'resource':name,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest()})
    return {'profile':profile,'resources':result,'post_link_writes':False}
