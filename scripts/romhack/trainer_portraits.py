"""Original SF trainer portraits compiled into new native presentation slots."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
from title_art import tiles8
from title_creature import pack4

ASSET='assets/characters/cognition-cast/scott-wu/battle-portrait-v1'


def replace_once(source,anchor,replacement):
    if source.count(anchor)!=1:raise ValueError('Pinned trainer portrait source anchor changed.')
    return source.replace(anchor,replacement,1)


def encode_portrait(root):
    from PIL import Image
    directory=root/ASSET
    image=Image.open(directory/'source.png').convert('RGBA')
    mask=image.getchannel('A').point(lambda a:255 if a>=128 else 0)
    bounds=mask.getbbox()
    if not bounds:raise ValueError('Trainer portrait needs a visible figure.')
    cell=image.crop(bounds);mask=mask.crop(bounds)
    scale=min(44/cell.width,58/cell.height)
    size=(max(1,round(cell.width*scale)),max(1,round(cell.height*scale)))
    cell=cell.resize(size,Image.Resampling.NEAREST)
    mask=mask.resize(size,Image.Resampling.NEAREST)
    colors=[rgb[:3] for rgb,a in zip(cell.get_flattened_data(),mask.get_flattened_data()) if a]
    samples=Image.new('RGB',(len(colors),1));samples.putdata(colors)
    reduced=samples.quantize(colors=15,method=Image.Quantize.MEDIANCUT).getpalette()[:45]
    palette=[(0,0,0)]+[tuple(round(c*31/255)*255//31 for c in reduced[i:i+3])
                         for i in range(0,45,3)]
    pixels=bytearray(4096);left=(64-size[0])//2;top=63-size[1]
    for y in range(size[1]):
        for x in range(size[0]):
            if mask.getpixel((x,y)):
                rgb=cell.getpixel((x,y))
                pixels[(top+y)*64+left+x]=min(range(1,16),key=lambda i:
                    sum((rgb[c]-palette[i][c])**2 for c in range(3)))
    preview=Image.new('P',(64,64),0)
    preview.putpalette([c for rgb in palette for c in rgb]+[0]*720)
    preview.putdata(pixels);preview.save(directory/'portrait.png',transparency=0,bits=4)
    data=pack4(tiles8(pixels,64,64,8,8))
    pal=b''.join(struct.pack('<H',sum(round(rgb[c]*31/255)<<(5*c) for c in range(3))) for rgb in palette)
    files={'portrait.4bpp':data,'portrait.gbapal':pal}
    for name,value in files.items():(directory/name).write_bytes(value)
    (directory/'conversion.json').write_text(json.dumps({
        'source_sha256':hashlib.sha256((directory/'source.png').read_bytes()).hexdigest(),
        'native_size':[64,64],'source_alpha_bounds':list(bounds),'figure_size':list(size),
        'baseline':62,'palette_colors':16,'quality_approval':'pending','pixel_cleanup':'pending',
        'files':{name:hashlib.sha256(value).hexdigest() for name,value in files.items()}},indent=2)+'\n')


def apply_portrait(root,engine,original):
    directory=root/ASSET
    metadata=json.loads((directory/'conversion.json').read_text())
    for name,digest in dict(metadata['files'],**{'source.png':metadata['source_sha256']}).items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Regenerate original trainer portrait after changing '+name)
    if (directory/'portrait.4bpp').stat().st_size!=2048 or (directory/'portrait.gbapal').stat().st_size!=32:
        raise ValueError('Trainer portrait must fit one64x64 four-bit frame and sixteen colors.')
    destination=engine/'graphics/trainers/front_pics/sf_scott_wu'
    destination.mkdir(parents=True,exist_ok=True)
    shutil.copy2(directory/'portrait.png',destination/'portrait.png')
    paths=['include/constants/trainers.h','include/graphics.h','src/data/graphics/trainers.h',
           'src/data/trainer_graphics/front_pic_tables.h','src/data/trainer_graphics/front_pic_anims.h']
    constants=original(paths[0])
    if '#define TRAINER_PIC_RS_MAY                92' not in constants:
        raise ValueError('Pinned trainer picture allocation changed.')
    constants=constants.replace('#define TRAINER_PIC_RS_MAY                92',
                               '#define TRAINER_PIC_RS_MAY                92\n#define TRAINER_PIC_SCOTT_WU                  93',1)
    (engine/paths[0]).write_text(constants)
    (engine/paths[1]).write_text((engine/paths[1]).read_text()+
        '\nextern const u32 gTrainerFrontPic_ScottWu[];\nextern const u32 gTrainerPalette_ScottWu[];\n')
    (engine/paths[2]).write_text(original(paths[2])+'''
const u32 gTrainerFrontPic_ScottWu[] = INCGFX_U32("graphics/trainers/front_pics/sf_scott_wu/portrait.png", ".4bpp.lz");
const u32 gTrainerPalette_ScottWu[] = INCGFX_U32("graphics/trainers/front_pics/sf_scott_wu/portrait.png", ".gbapal.lz");
''')
    tables=original(paths[3])
    for anchor,entry in (
        ('const struct MonCoords gTrainerFrontPicCoords[] =\n{',
         '[TRAINER_PIC_SCOTT_WU] = {.size = 8, .y_offset = 1},'),
        ('const struct CompressedSpriteSheet gTrainerFrontPicTable[] =\n{',
         'TRAINER_SPRITE(SCOTT_WU, gTrainerFrontPic_ScottWu, TRAINER_PIC_SIZE),'),
        ('const struct CompressedSpritePalette gTrainerFrontPicPaletteTable[] =\n{',
         'TRAINER_PAL(SCOTT_WU, gTrainerPalette_ScottWu),')):
        tables=replace_once(tables,anchor,anchor+'\n    '+entry)
    (engine/paths[3]).write_text(tables)
    anchor='const union AnimCmd *const *const gTrainerFrontAnimsPtrTable[] =\n{'
    (engine/paths[4]).write_text(replace_once(original(paths[4]),anchor,
        'static const union AnimCmd *const sAnims_ScottWu[] = {sAnim_GeneralFrame0};\n\n'+
        anchor+'\n    [TRAINER_PIC_SCOTT_WU] = sAnims_ScottWu,'))
    return paths


if __name__=='__main__':encode_portrait(Path(__file__).resolve().parents[2])
