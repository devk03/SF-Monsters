"""Measure urban source maps; not a substitute for screenshots or playtests."""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/romhack'))

LANDMARK_BUILDINGS={'highrise','highrise_medium','highrise_tall','office_wide',
                    'lab_wide','theater','stadium_gate','mansion','mural',
                    'native_loft','native_studio','working_hall','garage_hall'}


def joined(a,b):
    """Two footprints share a vertical party wall, not merely a corner."""
    overlap=min(a['y']+a['height'],b['y']+b['height'])-max(a['y'],b['y'])
    return overlap>0 and (a['x']+a['width']==b['x'] or b['x']+b['width']==a['x'])


def measure(plan,kit):
    catalog=kit['catalog'];rows=plan['rows'];height=len(rows);width=len(rows[0])
    if any(len(row)!=width for row in rows):raise ValueError('Non-rectangular map')
    def building(block):
        style=block['style'];card=catalog.get(style,{})
        return bool(card.get('architecture_type') or style in LANDMARK_BUILDINGS)
    blocks=[b for b in plan.get('town_blocks',[]) if building(b)]
    grass_id=catalog['grass']['tiles'][0][0]
    grass_cells={(x,y) for y,row in enumerate(rows) for x,token in enumerate(row)
                 if plan['legend'][token][0]==grass_id}
    remaining=set(grass_cells);largest_grass=0
    while remaining:
        seed=remaining.pop();pending=[seed];size=0
        while pending:
            x,y=pending.pop();size+=1
            for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if point in remaining:remaining.remove(point);pending.append(point)
        largest_grass=max(largest_grass,size)
    grass=len(grass_cells)
    occupied={(x,y) for b in blocks for y in range(b['y'],b['y']+b['height'])
              for x in range(b['x'],b['x']+b['width'])}
    attached=[b for b in blocks if any(a is not b and joined(a,b) for a in blocks)]
    def family(block):
        style=block['style'].split('__')[0]
        return style.removesuffix('_l').removesuffix('_m').removesuffix('_r')
    by_family={}
    for block in blocks:
        name=family(block);by_family[name]=by_family.get(name,0)+1
    towers=[b for b in blocks if b['height']>=5 and
            ('highrise' in b['style'] or 'office' in b['style'] or 'tower' in b['style'])]
    return dict(id=plan['world_id'],size=[width,height],grass_tiles=grass,
        grass_percent=round(100*grass/(width*height),1),largest_grass_patch=largest_grass,
        building_count=len(blocks),
        building_footprint_tiles=len(occupied),attached_count=len(attached),
        isolated_count=len(blocks)-len(attached),structural_families=by_family,
        tall_office_count=len(towers))


def main():
    from generate_world import generate
    from world_towns import URBAN
    from world_tiles import compile_kit
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    manifest=json.loads((ROOT/'romhack/world/world.json').read_text())
    kits={};results=[]
    for plan in generate(manifest):
        if plan['world_id'] not in URBAN:continue
        profile=plan['tile_profile']
        if profile not in kits:kits[profile]=compile_kit(profile=profile)
        results.append(measure(plan,kits[profile]))
    report=dict(version=manifest['version'],districts=sorted(results,key=lambda r:r['id']),
        limitations=['Source-map counts only; art quality, visual party-wall joins, access and gameplay require independent review.',
                     'Grass counts only the canonical grass card, not plants or decorative green surfaces.',
                     'Building families count existing producer labels, not distinct visual designs.'])
    text=json.dumps(report,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    else:print(text,end='')


if __name__=='__main__':main()
