"""Capture complete map backgrounds from a matching native GBA tour.

These are the compiled map cells and live GBA tiles/palettes, without actors.
Keep all captures private; this does not generate new game art or approve it.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from world_probe import Controller, ROOT
from walk_world import Walker
from verify_world_seams import RenderAudit


CRITIQUE = {
    'presidio': 'New wooded campus and residential transition; landmark, stair-garden and overlook composition still need review.',
    'dogpatch': 'The warehouse and crane distinguish it, but the street still needs a convincing working-waterfront composition.',
    'potrero_hill': 'The stair overlook helps. Most of the street remains flat; the hill and changes in grade barely read.',
    'mission': 'The mural and shop mix help, but the same straight residential block dominates. Alleys and community spaces need stronger placement.',
    'castro': 'The theater is a recognizable anchor. The surrounding block still resembles North Beach and needs more local signage and gathering space.',
    'outer_sunset': 'The ocean edge and surf shop make this one easier to identify. Housing rhythm and the abrupt seawall still need refinement.',
    'golden_gate_park': 'The windmill and conservatory give it identity, but the rectangular tree fill and standard loop feel schematic. Richmond is not a distinct town here.',
    'marina': 'The bar marker, bar interior and paint balance help. The exterior still needs a legible sequence of venues rather than another generic home row.',
    'pacific_heights': 'The mansion is distinct; the street shares too much geometry with Marina and Noe Valley. Formal gardens and height changes need more work.',
    'twin_peaks': 'The benches and gym clearing suggest a lookout. The terrain needs two clear summits and a more convincing exposed ridge.',
    'noe_valley': 'The book box, gardens and small shops suggest a quieter neighborhood. The common street template remains obvious.',
    'mission_bay': 'The clinic and tower are anchors, but low historic fronts dominate. Modern lab blocks and a waterfront edge are underdeveloped.',
    'giants_stadium': 'The stadium gate is readable, but the surrounding area feels like a residential street. The ballpark and fan plaza need a larger visual role.',
    'financial_district': 'One tower does not yet create an office canyon. Building massing and the public-space layout are still too similar to residential towns.',
    'north_beach': 'The cafe and theater palette works, but the common layout competes with district identity. Bookshops, alleys and tighter corners need emphasis.',
    'treasure_island': 'The industrial props work, but this map does not yet read strongly as an island. Its shoreline and open views need a dedicated pass.',
    'sutro_tower': 'The tower is a strong landmark. The reused wooded loop needs a ridge-specific trail and more deliberate lookout clearings.',
    'lands_end': 'The sea and bath ruins are distinct. The forest loop and straight coastal boundary need more cliff and cove variation.',
    'angel_island': 'The switchbacks differ from the park loop. Summit scenery and the reused conservatory/League placeholder remain unfinished.',
}
NATURE = {'golden_gate_park', 'twin_peaks', 'sutro_tower', 'lands_end', 'angel_island', 'presidio'}
EXPANDED_CRITIQUE = {
 'presidio':'The separate campus/residential hybrid has forest edges, a visitor desk and two optional walking links. It still needs a stronger campus landmark, stair gardens and purposeful overlooks.',
 'dogpatch':'Workshop rows, a loading court and planted cut-throughs add industrial identity. The waterfront, rail-yard composition and remaining long frontage bands still need refinement.',
 'potrero_hill':'The stepped network and two native stair courts add grade. Short rock rims still read as barriers; larger slope composition and deliberate overlooks need work.',
 'mission':'A mural/community court, attached shops and planted passages break the housing rhythm. More deliberate corner spaces and richer district-scale composition remain open.',
 'castro':'The branching streets help. The theater needs a stronger plaza, with lighting and signage connecting it to the rest of the district.',
 'outer_sunset':'The long parallel streets fit the district better. Ocean frontage, dune edges and smaller garden lots need a dedicated pass.',
 'golden_gate_park':'Native forest, a two-lobed joined-bank lake and12attached Richmond-edge homes/shops form a park/residential transition. Garden/conservatory staging, rigid forest borders and simple mews still fall short of the concept; facade doors are scenery.',
 'marina':'An attached cafe/bar corridor now has two harbor approaches and furnished pockets. Repeat awnings, broad road surfaces and thin waterfront space remain; boats, docks, palms, patios and distinct clubhouse architecture are absent.',
 'pacific_heights':'The offset streets distinguish the layout. Formal gardens, slopes and a stronger mansion approach remain underdeveloped.',
 'twin_peaks':'Two stair-stack outlooks, saddle trails and17attached lower homes add ridge identity. Rock rims still fail to form convincing hill masses; oversized paving and rigid forest borders need refinement.',
 'noe_valley':'Interior housing rows add density. Smaller civic pockets and planted pedestrian lanes should make it feel less mechanical.',
 'mission_bay':'Broader lab and tower blocks plus eastern/southern water add campus identity. Specialized research architecture and a convincing creek transition still need work.',
 'giants_stadium':'A playable field, sand infield and fan walk give the ballpark a footprint. A full stadium shell, bleachers and stronger fan-plaza composition remain absent.',
 'financial_district':'Broader office blocks, tower clusters and a lunch court add commercial massing. Repeated window/cornice geometry still falls short of a varied office canyon.',
 'north_beach':'The branching blocks offer better exploration. The bookshop/cafe identity and small alleys should shape more of the map.',
 'treasure_island':'The new loop has room to explore. A convincing shoreline, piers and open-water views are still essential.',
 'sutro_tower':'The larger winding trails need ridge-specific vegetation, tower approaches and lookout clearings rather than repeated forest fill.',
 'lands_end':'The trails are more varied, but coves, cliffs and the bath ruins need stronger placement across the enlarged coast.',
 'angel_island':'Switchbacks extend across a larger island. The summit, shoreline and League staging still need distinctive terrain and scenery.',
}


def background(audit, plan):
    """Composite native background layers using live VRAM, including flips."""
    layout = audit.layout(plan)
    graphics = audit.read(0x06000000, 32768)
    palette = audit.read(0x05000000, 512)
    cache = {}

    def tile(word):
        if word not in cache:
            index = word & 1023
            values = audit.pixels(word, graphics[index*32:(index+1)*32],
                                  palette[(word >> 12)*32:((word >> 12)+1)*32])
            pixels = []
            for color in values:
                if color is None:
                    pixels.append((0, 0, 0, 0))
                else:
                    rgb = [(color >> shift) & 31 for shift in (0, 5, 10)]
                    pixels.append(tuple((v << 3) | (v >> 2) for v in rgb) + (255,))
            image = Image.new('RGBA', (8, 8))
            image.putdata(pixels)
            cache[word] = image
        return cache[word]

    width, height = layout['width'], layout['height']
    image = Image.new('RGB', (width*16, height*16))
    fallback = tile(0x3014)
    for y in range(0, height*16, 8):
        for x in range(0, width*16, 8):
            image.paste(fallback, (x, y), fallback)
    for index, block in enumerate(layout['cells']):
        words, _, _, _ = audit.original_record(layout, block & 1023)
        left, top = index % width * 16, index // width * 16
        for layer in (0, 4):
            for quadrant, word in enumerate(words[layer:layer+4]):
                part = tile(word)
                image.paste(part, (left+quadrant%2*8, top+quadrant//2*8), part)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tour', type=Path, required=True)
    parser.add_argument('--areas',help='Audit an explicit destination subset captured in its own matching tour')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--engine',type=Path,default=ROOT/'.tools/pokeemerald-world-host')
    parser.add_argument('--supplementary-tour',type=Path,action='append',default=[])
    parser.add_argument('--checkpoint-tour',action='store_true',
                        help='Audit saved native checkpoints from an interrupted tour; no uninterrupted-route claim')
    args = parser.parse_args()
    tour, output = args.tour.resolve(), args.output.resolve()
    tour.relative_to(ROOT / '.tools/benchmarks')
    output.relative_to(ROOT / '.tools/benchmarks')
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((ROOT/'romhack/world/world.json').read_text())
    evidence = json.loads((tour/('session.json' if args.checkpoint_tour else 'scene-tour.json')).read_text())
    areas = manifest['areas'] + [dict(id=manifest['league']['venue'], label=manifest['league']['label'])]
    if args.areas:
        selected=set(args.areas.split(','))
        if not selected<={a['id'] for a in areas}:raise ValueError('Unknown destination selection')
        areas=[a for a in areas if a['id'] in selected]
    if (not args.checkpoint_tour and evidence['areas'] != [a['id'] for a in areas]) or not evidence['controller_only']:
        raise ValueError('A complete controller-only town tour is required')
    districts = json.loads((ROOT/'romhack/world/districts.json').read_text())['areas']
    concept_root=ROOT/'output/imagegen/neighborhood-ideals-v2-expanded'
    references={item['id'].replace('-','_'):item for item in json.loads((concept_root/'prompts.json').read_text())['images']}
    engine = args.engine.resolve()
    digest = hashlib.sha256((engine/'sf-world-blockout.gba').read_bytes()).hexdigest()
    if digest != evidence['rom_sha256']:
        raise ValueError('Tour and native cartridge differ')
    tours=[tour]+[p.resolve() for p in args.supplementary_tour]
    for folder in tours:
        folder.relative_to(ROOT/'.tools/benchmarks')
        identity=json.loads((folder/'session.json').read_text())
        if not identity['controller_only'] or identity['rom_sha256']!=digest:
            raise ValueError('Supplementary checkpoints do not match the native cartridge')
    result = []
    for number, area in enumerate(areas, 1):
        identifier = area['id']
        folder=next((p for p in tours if (p/(identifier+'-0.state')).is_file()),None)
        if folder is None:raise ValueError('Missing native destination checkpoint: '+identifier)
        state = folder/(identifier+'-0.state')
        c = Controller(engine/'sf-world-blockout.gba', engine/'sf-world-blockout.elf',
                       output/'native-checks'/identifier, state=state, battery=state.with_suffix('.sav'))
        try:
            w = Walker(c, manifest)
            if w.location()[0] != identifier:
                raise ValueError('Tour snapshot is not in its labeled destination')
            plan = w.plans[identifier]
            audit = RenderAudit(c)
            audit.check(w, 'native-context')
            image = background(audit, plan)
            path = output/(identifier+'-full-map.png')
            image.resize((image.width*2, image.height*2), Image.Resampling.NEAREST).save(path)
            routes = [w.plans[w.native[link['map']]]['label'] for link in plan['connections'] or []]
            views = sorted(folder.glob(identifier+'-[0-9]*.png'),key=lambda p:int(p.stem.rsplit('-',1)[1]))
            preferred={'golden_gate_park':'Pond rest','twin_peaks':'South lookout','sutro_tower':'Fog break',
                       'lands_end':'Coastal lookout','angel_island':'Landing view'}
            if plan.get('parcel_notices'):target=plan['parcel_notices'][0]['standing']
            elif identifier in preferred:
                point=next(p for p in plan['scenic_viewpoints'] if p['name']==preferred[identifier]);target=(point['x'],point['y'])
            elif plan.get('pedestrian_courts'):target=plan['pedestrian_courts'][0]['rest']
            else:target=(76,42)
            def distance(path):
                position=json.loads(path.with_suffix('.json').read_text())['position']
                return abs(position['x']-target[0])+abs(position['y']-target[1])
            featured=[str(views[0]),str(min(views,key=distance))]
            reference=references[identifier];concept=concept_root/reference['file']
            if hashlib.sha256(concept.read_bytes()).hexdigest()!=reference['sha256']:
                raise ValueError('Expanded reference image changed: '+identifier)
            result.append(dict(id=identifier, label=area['label'], order=number,
                category='nature' if identifier in NATURE else 'urban', map=str(path),
                map_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                views=[str(p) for p in views],featured_views=featured, character=districts[identifier]['character'],
                critique=(EXPANDED_CRITIQUE if plan.get('expanded_design') else CRITIQUE)[identifier], connections=routes,
                landmarks=[p['name'] for p in plan.get('landmarks', [])],
                gym=next((g['badge'] for g in manifest['gyms'] if g['area']==identifier), None),
                residents=len(plan['npcs']), dimensions=[image.width//16, image.height//16],
                concept_reference=str(concept),concept_sha256=reference['sha256']))
            print(identifier, flush=True)
        finally:
            c.close()
    receipt = dict(version=manifest['version'], rom_sha256=digest, areas=result,
        full_map_scope='Live native GBA background tiles/palettes and compiled map geometry; actors and animation are shown in the adjacent gameplay views.',
        missing=[] if any(a['id']=='presidio' for a in result) else ['Presidio Heights', 'Presidio'], public_version='0.0.92', human_approval='pending',
        evidence_scope='Native checkpoint composition, with live render audits; not an uninterrupted route claim' if args.checkpoint_tour else ('Complete controller-only selected destination tour' if args.areas else 'Complete controller-only destination tour'))
    (output/'maps.json').write_text(json.dumps(receipt, indent=2)+'\n')


if __name__ == '__main__':
    main()
