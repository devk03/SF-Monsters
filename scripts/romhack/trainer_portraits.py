"""Original SF trainer portraits compiled into new native presentation slots."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from title_art import tiles8
from title_creature import pack4
from cast_palette import cast_palette

ASSET='assets/characters/cognition-cast/scott-wu/battle-portrait-v1'
PORTRAITS = (
    (ASSET, 'ScottWu', 'SCOTT_WU', 93),
    ('assets/characters/cognition-cast/walden-yan/battle-portrait-v1', 'WaldenYan', 'WALDEN_YAN', 94),
    ('assets/characters/cognition-cast/steven-hao/battle-portrait-v1', 'StevenHao', 'STEVEN_HAO', 95),
)


def portrait_registry():
    for column in range(4):
        if len({entry[column] for entry in PORTRAITS}) != len(PORTRAITS):
            raise ValueError('Trainer portrait registry duplicates an asset, symbol, constant or slot.')
    for asset, symbol, picture, slot in PORTRAITS:
        path = Path(asset)
        if path.is_absolute() or '..' in path.parts or path.parts[:2] != ('assets', 'characters') or \
           not re.fullmatch('[A-Za-z][A-Za-z0-9]*', symbol) or \
           not re.fullmatch('[A-Z][A-Z_0-9]*', picture) or type(slot) is not int or not 93 <= slot <= 255:
            raise ValueError('Trainer portraits need safe original assets and appended native byte-sized slots.')
    if tuple(entry[3] for entry in PORTRAITS) != (93, 94, 95):
        raise ValueError('Keep the reviewed Scott, Walden and Steven portrait allocation stable.')
    return PORTRAITS


def portrait_cleanup(pixels, document, source, palette):
    """Apply a bounded, hash-pinned native drawing pass to one original frame."""
    digest=lambda value:hashlib.sha256(value).hexdigest()
    fields={'format','intent','source_sha256','palette_sha256','before_sha256','after_sha256','changes'}
    if not isinstance(document,dict) or set(document)!=fields or type(document['format']) is not int or document['format']!=1 or not isinstance(document['intent'],str) or not document['intent'].strip():
        raise ValueError('Portrait cleanup needs its format and drawing intent.')
    if len(pixels)!=4096 or max(pixels)>15 or len(palette)!=32 or any(
            document[key]!=digest(value) for key,value in
            [('source_sha256',source),('palette_sha256',palette),('before_sha256',pixels)]):
        raise ValueError('Portrait cleanup source, palette or native input changed.')
    changes=document['changes']
    if not isinstance(changes,list) or not 1<=len(changes)<=4096:
        raise ValueError('Portrait cleanup must declare bounded pixel edits.')
    result=bytearray(pixels);seen=set()
    for edit in changes:
        if not isinstance(edit,dict) or set(edit)!={'x','y','old','new'} or any(
                type(edit[key]) is not int or not 0<=edit[key]<limit
                for key,limit in [('x',64),('y',64),('old',16),('new',16)]):
            raise ValueError('Portrait cleanup leaves the native frame or palette.')
        index=edit['y']*64+edit['x']
        if index in seen or edit['old']==edit['new'] or result[index]!=edit['old']:
            raise ValueError('Portrait cleanup repeats a point or changes an unexpected pixel.')
        seen.add(index);result[index]=edit['new']
    if document['after_sha256']!=digest(result):
        raise ValueError('Portrait cleanup differs from its reviewed native output.')
    return bytes(result)


def replace_once(source,anchor,replacement):
    if source.count(anchor)!=1:raise ValueError('Pinned trainer portrait source anchor changed.')
    return source.replace(anchor,replacement,1)


def encode_portrait(root, asset=ASSET):
    from PIL import Image
    directory=root/asset
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
    palette,pal,palette_policy_sha256=cast_palette(directory,colors)
    pixels=bytearray(4096);left=(64-size[0])//2;top=63-size[1]
    for y in range(size[1]):
        for x in range(size[0]):
            if mask.getpixel((x,y)):
                rgb=cell.getpixel((x,y))
                pixels[(top+y)*64+left+x]=min(range(1,16),key=lambda i:
                    sum((rgb[c]-palette[i][c])**2 for c in range(3)))
    cleanup=directory/'native-cleanup.json'
    cleanup_bytes=cleanup.read_bytes() if cleanup.exists() else None
    if cleanup_bytes:
        pixels=portrait_cleanup(bytes(pixels),json.loads(cleanup_bytes),
                                (directory/'source.png').read_bytes(),pal)
    preview=Image.new('P',(64,64),0)
    preview.putpalette([c for rgb in palette for c in rgb]+[0]*720)
    preview.putdata(pixels);preview.save(directory/'portrait.png',transparency=0,bits=4)
    data=pack4(tiles8(pixels,64,64,8,8))
    files={'portrait.4bpp':data,'portrait.gbapal':pal,
           'portrait.png':(directory/'portrait.png').read_bytes()}
    for name,value in files.items():(directory/name).write_bytes(value)
    (directory/'conversion.json').write_text(json.dumps({
        'source_sha256':hashlib.sha256((directory/'source.png').read_bytes()).hexdigest(),
        'native_size':[64,64],'source_alpha_bounds':list(bounds),'figure_size':list(size),
        'baseline':62,'palette_colors':16,'quality_approval':'pending','pixel_cleanup':'pending',
        'palette_policy_sha256':palette_policy_sha256,
        'native_cleanup_sha256':hashlib.sha256(cleanup_bytes).hexdigest() if cleanup_bytes else None,
        'files':{name:hashlib.sha256(value).hexdigest() for name,value in files.items()}},indent=2)+'\n')


def verified_portrait(root, asset):
    directory=root/asset
    metadata=json.loads((directory/'conversion.json').read_text())
    if set(metadata['files']) != {'portrait.png', 'portrait.4bpp', 'portrait.gbapal'} or \
       metadata['native_size'] != [64, 64] or metadata['baseline'] != 62 or metadata['palette_colors'] != 16:
        raise ValueError('Trainer portrait metadata must describe one native 64x64 frame.')
    for name,digest in dict(metadata['files'],**{'source.png':metadata['source_sha256']}).items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Regenerate original trainer portrait after changing '+name)
    if (directory/'portrait.4bpp').stat().st_size!=2048 or (directory/'portrait.gbapal').stat().st_size!=32:
        raise ValueError('Trainer portrait must fit one64x64 four-bit frame and sixteen colors.')
    for name, key in (('palette-policy.json', 'palette_policy_sha256'),
                      ('native-cleanup.json', 'native_cleanup_sha256')):
        path = directory/name
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if actual != metadata.get(key):
            raise ValueError('Regenerate trainer portrait after changing ' + name)
    return directory


def apply_portrait(root,engine,original):
    entries = portrait_registry()
    directories = [verified_portrait(root, entry[0]) for entry in entries]
    paths=['include/constants/trainers.h','include/graphics.h','src/data/graphics/trainers.h',
           'src/data/trainer_graphics/front_pic_tables.h','src/data/trainer_graphics/front_pic_anims.h']
    constants=original(paths[0])
    if '#define TRAINER_PIC_RS_MAY                92' not in constants:
        raise ValueError('Pinned trainer picture allocation changed.')
    additions = '\n'.join('#define TRAINER_PIC_%s %d' % (picture, slot)
                          for asset, symbol, picture, slot in entries)
    constants=replace_once(constants, '#define TRAINER_PIC_RS_MAY                92',
                           '#define TRAINER_PIC_RS_MAY                92\n' + additions)
    (engine/paths[0]).write_text(constants)
    header=(engine/paths[1]).read_text()
    graphics=original(paths[2])
    for (asset, symbol, picture, slot), directory in zip(entries, directories):
        relative = 'graphics/trainers/front_pics/sf_' + picture.lower() + '/portrait.png'
        destination=engine/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(directory/'portrait.png',destination)
        header += '\nextern const u32 gTrainerFrontPic_%s[];\nextern const u32 gTrainerPalette_%s[];\n' % (symbol, symbol)
        graphics += '\nconst u32 gTrainerFrontPic_%s[] = INCGFX_U32("%s", ".4bpp.lz");\n' % (symbol, relative)
        graphics += 'const u32 gTrainerPalette_%s[] = INCGFX_U32("%s", ".gbapal.lz");\n' % (symbol, relative)
    (engine/paths[1]).write_text(header)
    (engine/paths[2]).write_text(graphics)
    tables=original(paths[3])
    for anchor,entry in (
        ('const struct MonCoords gTrainerFrontPicCoords[] =\n{', '\n    '.join(
         '[TRAINER_PIC_%s] = {.size = 8, .y_offset = 1},' % picture for asset, symbol, picture, slot in entries)),
        ('const struct CompressedSpriteSheet gTrainerFrontPicTable[] =\n{', '\n    '.join(
         'TRAINER_SPRITE(%s, gTrainerFrontPic_%s, TRAINER_PIC_SIZE),' % (picture, symbol)
         for asset, symbol, picture, slot in entries)),
        ('const struct CompressedSpritePalette gTrainerFrontPicPaletteTable[] =\n{', '\n    '.join(
         'TRAINER_PAL(%s, gTrainerPalette_%s),' % (picture, symbol) for asset, symbol, picture, slot in entries))):
        tables=replace_once(tables,anchor,anchor+'\n    '+entry)
    (engine/paths[3]).write_text(tables)
    anchor='const union AnimCmd *const *const gTrainerFrontAnimsPtrTable[] =\n{'
    declarations = ''.join('static const union AnimCmd *const sAnims_%s[] = {sAnim_GeneralFrame0};\n' % symbol
                           for asset, symbol, picture, slot in entries)
    animations = '\n    '.join('[TRAINER_PIC_%s] = sAnims_%s,' % (picture, symbol)
                                for asset, symbol, picture, slot in entries)
    (engine/paths[4]).write_text(replace_once(original(paths[4]),anchor,
        declarations+'\n'+anchor+'\n    '+animations))
    return paths


if __name__=='__main__':
    for asset, symbol, picture, slot in portrait_registry():
        encode_portrait(Path(__file__).resolve().parents[2], asset)
