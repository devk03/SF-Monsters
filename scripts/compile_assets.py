"""Convert the original atlases into palette-indexed GBA resources."""
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build'
OUT.mkdir(exist_ok=True)
UI = ['000000','102333','eff6f2','dce8cd','849a9d','234c3f','70a267','308ba5',
      'd8bd89','405b6b','f5b75c','c95454','80c9bd','687d90','396378','abc9dc']
frames = []
for name, cols, rows in [('monsters-atlas.png',4,3),('world-atlas.png',4,4)]:
    image = Image.open(ROOT/'assets'/name).convert('RGBA')
    for i in range(cols*rows):
        c,r=i%cols,i//cols
        cell=image.crop((round(c*image.width/cols),round(r*image.height/rows),
                         round((c+1)*image.width/cols),round((r+1)*image.height/rows)))
        box=cell.getchannel('A').point(lambda p:255 if p>90 else 0).getbbox()
        if box: cell=cell.crop(box)
        if name.startswith('monsters'): size=(48,48)
        elif i<8: size=(16,24)
        elif i<12: size=(64,48)
        else: size=(16,16)
        cell.thumbnail(size,Image.Resampling.NEAREST)
        result=Image.new('RGBA',size)
        result.alpha_composite(cell,((size[0]-cell.width)//2,size[1]-cell.height))
        frames.append(result)
# Learn the sprite palette once, reserving the first 16 UI colors.
strip=Image.new('RGB',(64*len(frames),64),(0,0,0))
for i,frame in enumerate(frames):strip.paste(frame,(i*64,0),frame)
learned=strip.quantize(colors=240,method=Image.Quantize.MEDIANCUT).getpalette()[:720]
colors=[]
for code in UI:colors.extend(bytes.fromhex(code))
colors.extend(learned)
colors=colors[:768]+[0]*max(0,768-len(colors))
palette=Image.new('P',(1,1));palette.putpalette(colors)
data=[]; offsets=[]; widths=[]; heights=[]
for frame in frames:
    offsets.append(len(data));widths.append(frame.width);heights.append(frame.height)
    indexed=frame.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE)
    alpha=list(frame.getchannel('A').get_flattened_data())
    data.extend(pixel if alpha[i]>90 else 0 for i,pixel in enumerate(indexed.get_flattened_data()))
words=[]
for i in range(0,768,3):
    r,g,b=colors[i:i+3];words.append((r>>3)|((g>>3)<<5)|((b>>3)<<10))
def array(name,kind,values):
    return f'const {kind} {name}[{len(values)}] = {{\n'+''.join(
        '  '+','.join(map(str,values[i:i+32]))+',\n' for i in range(0,len(values),32))+'};\n'
source='#include "game.h"\n'
source+=array('art_palette','u16',words)+array('art_pixels','u8',data)
source+=array('art_offsets','u32',offsets)+array('art_widths','u8',widths)+array('art_heights','u8',heights)
(OUT/'assets.c').write_text(source)
(OUT/'assets.h').write_text('''#include "game.h"
extern const u16 art_palette[256];
extern const u8 art_pixels[];
extern const u32 art_offsets[28];
extern const u8 art_widths[28], art_heights[28];
''')
print(f'Compiled {len(frames)} sprite/tile frames, {len(data)} indexed pixels.')
