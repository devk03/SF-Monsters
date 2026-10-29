"""Original, modular GBA-scale Financial District building candidates.

The images vary some structural features, but remain too repetitive to meet the
30-distinct-design requirement. This is a source-art prototype, not game art.
"""
from pathlib import Path
import argparse

DESIGNS=tuple(dict(id=f'fidi_{i+1:02d}', family=i%10, crown=i%5, material=(i//5)%3,
                   width=2+i%3, height=5+i%4, windows=(i//3)%3,
                   entrance=(i//2)%3, shape=6 if i==14 else i%6) for i in range(30))


def facade(spec, closed=('left','right')):
    if not set(closed)<={'left','right'}:raise ValueError('Unknown exposed edge')
    width,height=spec['width']*16,spec['height']*16
    tw,th=width//8,height//8
    pixels=bytearray(width*height)
    family=spec['family']; material=family%3
    wall=(7,9,10)[material]; shade=(8,6,6)[material]
    def micro(kind,variant=0,edge=None):
        # Ground-level masonry is shared between office types. Upper stories
        # retain their own material; the shared plinth saves native graphics.
        a=bytearray([10 if kind=='base' or kind.startswith('door_') else wall]*64)
        def box(x0,y0,x1,y1,c):
            for y in range(max(0,y0),min(8,y1+1)):
                for x in range(max(0,x0),min(8,x1+1)):a[y*8+x]=c
        if kind=='empty':return bytes(64)
        if kind=='roof':
            box(0,0,7,1,1);box(0,2,7,3,5);box(0,6,7,7,shade)
            if variant==1:box(2,0,5,1,5)
            elif variant==2:box(0,3,7,4,6)
            elif variant==3:box(1,0,2,1,5);box(5,0,6,1,5)
            elif variant==4:box(0,3,7,3,1);box(2,0,5,2,2)
        elif kind=='window':
            box(0,0,7,0,shade);box(1,1,6,6,1);box(2,2,5,5,4)
            if variant==0:box(3,2,3,5,2)
            elif variant==1:box(2,3,5,3,2)
            elif variant==2:box(1,6,6,6,5)
            elif variant==3:box(2,1,5,1,5)
            else:box(0,1,0,7,5)
        elif kind=='glass':
            box(0,0,7,7,4);box(0,0,7,0,1);box(0,0,0,7,1)
            if variant:box(1,4,7,4,2)
            box(2,1,3,2,3)
        elif kind=='base':
            box(0,0,7,1,5);box(0,7,7,7,6)
            if variant==0:
                box(1,2,6,6,1);box(2,3,5,5,4)
            elif variant==1:
                box(1,2,6,6,1);box(2,3,5,6,4);box(2,2,5,2,5)
            else:
                box(0,2,7,3,7);box(0,2,3,3,5)
                box(1,4,6,6,1);box(2,4,5,6,4)
        elif kind.startswith('door_'):
            _,stage,side=kind.split('_')
            # Two 8px columns by three rows give a 16x24 entrance, scaled to
            # the player. Mirror the frame at the right half of the opening.
            box(0,0,7,7,1);box(2,0,7,7,4);box(2,0,2,7,5)
            box(7,0,7,7,1)
            if stage=='top':
                box(0,0,7,1,5)
                box(3,3,4,4,3)
                if variant==1:box(2,2,7,2,5)
                elif variant==2:box(0,0,3,2,7)
            elif stage=='middle':box(5,4,6,5,13)
            elif stage=='bottom':
                box(3,5,5,6,2);box(0,7,7,7,6)
            if side=='right':a=bytearray(a[y*8+7-x] for y in range(8) for x in range(8))
        if edge=='left':box(0,0,0,7,1)
        if edge=='right':box(7,0,7,7,1)
        return bytes(a)
    for ty in range(th):
        for tx in range(tw):
            shape=spec['shape']; left=right=0
            if shape==1 and ty<2:left=right=1
            elif shape==2 and ty<4:left=right=2 if ty<2 and tw>=6 else 1
            elif shape==3 and ty<3:left=1
            elif shape==4 and ty<3:right=1
            elif shape==5 and ty<th//2:left=right=1
            elif shape==6 and ty<th-2:
                left=right=max(0,(tw//2-1)-(ty*tw//(2*(th-2))))
            if tx<left or tx>=tw-right:kind='empty'
            elif ty==0:kind='roof'
            elif ty==th-4:kind='base'
            elif ty>=th-3:
                door_left=(tw//2//2)*2
                if tx in (door_left,door_left+1):
                    stage=('top','middle','bottom')[ty-(th-3)]
                    kind='door_'+stage+('_left' if tx==door_left else '_right')
                else:kind='base'
            elif family in (1,5,9):kind='glass'
            else:kind='window' if (tx+family)%2==0 else 'wall'
            edge=('left' if tx==0 and 'left' in closed else
                  'right' if tx==tw-1 and 'right' in closed else None)
            variant=spec['crown'] if kind=='roof' else spec['entrance'] if kind=='base' or kind.startswith('door_') else spec['windows']
            raw=micro(kind,variant,edge)
            for dy in range(8):
                pixels[(ty*8+dy)*width+tx*8:(ty*8+dy)*width+tx*8+8]=raw[dy*8:dy*8+8]
    return width,height,bytes(pixels)


def preview(output):
    from PIL import Image,ImageDraw
    from world_rich_facades import source
    import struct
    colors=struct.unpack('<16H',source()['block.gbapal'])
    palette=[tuple(((v>>shift)&31)*255//31 for shift in (0,5,10)) for v in colors]
    canvas=Image.new('RGB',(6*240,5*310),(233,230,218));draw=ImageDraw.Draw(canvas)
    for i,spec in enumerate(DESIGNS):
        w,h,p=facade(spec);image=Image.new('P',(w,h));image.putpalette([v for rgb in palette for v in rgb]+[0]*720)
        image.putdata(p);image.info['transparency']=0
        image=image.convert('RGBA').resize((w*2,h*2),Image.Resampling.NEAREST)
        left=(i%6)*240+(240-w*2)//2;top=(i//6)*310+285-h*2
        canvas.paste(image,(left,top),image);draw.text(((i%6)*240+10,(i//6)*310+8),spec['id'],fill=(40,44,50))
    output.parent.mkdir(parents=True,exist_ok=True);canvas.save(output)


def budget():
    """Measure original 8px graphics; this does not prove seam feasibility."""
    from world_rich_facades import tile_inventory
    from world_shared_primary import canonical_tile,PINNED_RESERVED
    from world_tiles import compile_kit
    kit=compile_kit(profile='civic')
    existing={canonical_tile(tile)[0] for tile in
              list(kit['tiles'])+list(kit['primary_tiles'].values())}
    variants=[(spec['id'],*facade(spec,closed)) for spec in DESIGNS
              for closed in (('left','right'),('left',),(),('right',))]
    pixels=tile_inventory(variants)
    return dict(candidate_images=len(DESIGNS),attachment_images=len(variants),
                incremental_graphics=len(pixels-existing),
                free_primary_before_connections=len(set(range(432))-PINNED_RESERVED)-len(kit['primary_tiles']),
                scope='source-only estimate; not compiled metatiles, live seams or visual acceptance')


if __name__=='__main__':
    import json
    parser=argparse.ArgumentParser();parser.add_argument('--preview',type=Path);parser.add_argument('--budget',action='store_true')
    args=parser.parse_args()
    if not args.preview and not args.budget:parser.error('Choose --preview or --budget')
    if args.preview:preview(args.preview)
    if args.budget:print(json.dumps(budget(),indent=2))
