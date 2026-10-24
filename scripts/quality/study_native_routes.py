"""Render original private reference routes for map-composition study.

Outputs contain base-game pixels: keep them under ignored .tools, never Git.
"""
import argparse,json,struct
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]


def render(engine,layout):
    primary=engine/'data/tilesets/primary/general'
    secondary=engine/'data/tilesets/secondary'/layout['secondary_tileset'].removeprefix('gTileset_').lower()
    tiles=[Image.open(p/'tiles.png') for p in (primary,secondary)]
    records=[(p/'metatiles.bin').read_bytes() for p in (primary,secondary)]
    palettes={}
    for bank in range(13):
        directory=primary if bank<6 else secondary
        palettes[bank]=[tuple(map(int,row.split())) for row in (directory/f'palettes/{bank:02d}.pal').read_text().splitlines()[3:]]
    width,height=layout['width'],layout['height']
    raw=(engine/layout['blockdata_filepath']).read_bytes()
    cells=struct.unpack('<'+'H'*(len(raw)//2),raw)
    image=Image.new('RGB',(width*16,height*16));cache={}
    for i,cell in enumerate(cells):
        identifier=cell&1023
        if identifier not in cache:
            side=int(identifier>=512);number=identifier-512 if side else identifier
            words=struct.unpack_from('<8H',records[side],number*16)
            piece=Image.new('RGB',(16,16),(180,205,164))
            for layer in (0,4):
                for q,word in enumerate(words[layer:layer+4]):
                    tile=word&1023;source=tiles[int(tile>=512)];tile=tile-512 if tile>=512 else tile
                    for y in range(8):
                        for x in range(8):
                            color=source.getpixel((tile%16*8+(7-x if word&1024 else x),tile//16*8+(7-y if word&2048 else y)))
                            if color:piece.putpixel((q%2*8+x,q//2*8+y),palettes[word>>12][color])
            cache[identifier]=piece
        image.paste(cache[identifier],(i%width*16,i//width*16))
    return image,Counter(cell&1023 for cell in cells)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',type=Path,default=ROOT/'.tools/pokeemerald')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--maps',default='Route101,Route102,Route104,PetalburgWoods',help='Original reference layouts to study')
    args=parser.parse_args();output=args.output.resolve();output.relative_to(ROOT/'.tools/benchmarks')
    output.mkdir(parents=True,exist_ok=False)
    layouts=json.loads((args.engine/'data/layouts/layouts.json').read_text())['layouts']
    result=[]
    for name in args.maps.split(','):
        layout=next(l for l in layouts if l['name']==name+'_Layout')
        image,counts=render(args.engine,layout);image.save(output/(name+'.png'))
        result.append(dict(name=name,width=layout['width'],height=layout['height'],
                           metatile_counts={hex(k):v for k,v in counts.most_common()}))
        print(name,flush=True)
    (output/'reference.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
