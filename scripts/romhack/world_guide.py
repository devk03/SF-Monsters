"""Compile an SF-only map and place guide from the actual world topology."""
import json,re,shutil,textwrap
from world_people import load_people


def apply_guide(root,engine,original,manifest,plans):
    from generate_world import records,native_id
    from world_guide_layout import chart_positions,route_path,path_midpoint
    from world_guide_art import compile_art
    areas,routes=records(manifest,physical=False);index={area['id']:i for i,area in enumerate(areas)}
    positions=manifest['city_guide']['positions'];people=load_people()
    discoveries=json.loads((root/'romhack/world/discoveries.json').read_text())['areas']
    if set(positions)!=set(index):raise ValueError('The city map must include every approved destination')
    def string(value,capacity=40):
        if (any(c in value for c in '$"\\\n') or not value.isascii()
                or len(value)+1>capacity):raise ValueError('Native guide field exceeds its encoded destination capacity')
        return '_("'+value+'")'
    pixels=chart_positions(manifest)
    gyms_by_area={gym['area']:gym['badge'] for gym in manifest['gyms']}
    nodes=[]
    for area in areas:
        identifier=area['id'];x,y=positions[identifier]
        if type(x) is not int or type(y) is not int or not 0<=x<=100 or not 0<=y<=100:raise ValueError('City map position out of bounds')
        connections=[]
        for route in routes:
            if identifier not in (route['from'],route['to']):continue
            other=route['to'] if identifier==route['from'] else route['from']
            label=next(a['label'] for a in areas if a['id']==other).split(' / ')[0]
            connections.append(('Walk: ' if route['mode']=='walk' else 'Surf: ' if route['mode']=='surf' else 'Surf+Falls: ')+label)
        lines=connections
        if any(r['mode']!='walk' and identifier in (r['from'],r['to']) for r in routes):
            lines.append('Surf: badge 5 / Falls: badge 8')
        if len(lines)>4:raise ValueError('City guide needs shorter connection labels')
        lines+=['']*(4-len(lines))
        flags=discoveries[identifier]
        nodes.append('    {'+f'{pixels[identifier][0]}, {pixels[identifier][1]}, '+
                     string(area['label'])+', '+string(people[identifier]['character'].capitalize(),60)+', '+
                     '{'+', '.join(map(string,lines))+'}, '+str(gyms_by_area.get(identifier,0))+', '+flags['done_flag']+', '+
                     (flags['found_flag'] or '0')+'}')
    edges=[]
    for route in routes:
        points=route_path(route,pixels)
        edges.append('    {'+', '.join(map(str,(index[route['from']],index[route['to']],
                     route['requires_badge'],int(route['mode']!='walk'),len(points))))+', {'+
                     ', '.join('{'+str(x)+', '+str(y)+'}' for x,y in points)+'}}')
    bindings=[]
    gyms={g['id']:g['area'] for g in manifest['gyms']};rooms={r['id']:r['area'] for r in manifest.get('interiors',[])}
    connectors={r['id']:r['from'] for r in routes}
    route_index={r['id']:r for r in routes}
    for plan in plans:
        identifier=plan['world_id'];route_id=plan.get('parent_route',identifier)
        parent=gyms.get(identifier,rooms.get(identifier,connectors.get(route_id,identifier)))
        x,y=pixels[parent];kind=2 if identifier in gyms or identifier in rooms else 0
        if route_id in route_index:
            route=route_index[route_id]
            x,y=path_midpoint(route_path(route,pixels));kind=1
        bindings.append('    {MAP_GROUP('+plan['native_id']+'), MAP_NUM('+plan['native_id']+'), '+
                        ', '.join(map(str,(index[parent],x,y,kind)))+'}')
    header='// Generated from the authoritative world manifest and state reservations.\n'
    header+='static const struct SFGuidePlace sSFGuidePlaces[] = {\n'+',\n'.join(nodes)+'\n};\n'
    header+='static const struct SFGuideEdge sSFGuideEdges[] = {\n'+',\n'.join(edges)+'\n};\n'
    header+='static const u8 sSFGuideBindings[][6] = {\n'+',\n'.join(bindings)+'\n};\n'
    (engine/'src/sf_world_guide_data.h').write_text(header)
    (engine/'src/sf_world_guide_pixels.h').write_text(compile_art())
    shutil.copyfile(root/'romhack/engine/world_guide.h',engine/'src/sf_world_guide.h')
    shutil.copyfile(root/'romhack/engine/world_guide_art.h',engine/'src/sf_world_guide_art.h')
    path='src/start_menu.c';source=original(path)
    changes=[('    MENU_ACTION_PYRAMID_BAG\n','    MENU_ACTION_PYRAMID_BAG,\n    MENU_ACTION_SF_GUIDE\n'),
             ('static bool8 StartMenuPokedexCallback(void);','static bool8 StartMenuSFGuideCallback(void);\nstatic const u8 sSFGuideLabel[];\nstatic bool8 StartMenuPokedexCallback(void);'),
             ('    [MENU_ACTION_POKEDEX]         =','    [MENU_ACTION_SF_GUIDE]        = {sSFGuideLabel, {.u8_void = StartMenuSFGuideCallback}},\n    [MENU_ACTION_POKEDEX]         ='),
             ('void SetDexPokemonPokenavFlags(void) // unused','#include "sf_world_guide.h"\n\nvoid SetDexPokemonPokenavFlags(void) // unused'),
             ('    AddStartMenuAction(MENU_ACTION_SAVE);\n    AddStartMenuAction(MENU_ACTION_OPTION);\n    AddStartMenuAction(MENU_ACTION_EXIT);',
              '    AddStartMenuAction(MENU_ACTION_SAVE);\n    AddStartMenuAction(MENU_ACTION_OPTION);\n    if (SFMapUsesAuthoredLayout())\n        AddStartMenuAction(MENU_ACTION_SF_GUIDE);\n    AddStartMenuAction(MENU_ACTION_EXIT);'),
             ('        if (gMenuCallback != StartMenuSaveCallback\n','        if (gMenuCallback != StartMenuSFGuideCallback\n            && gMenuCallback != StartMenuSaveCallback\n')]
    for before,after in changes:
        if source.count(before)!=1:raise ValueError('Pinned SF guide Start menu anchor changed')
        source=source.replace(before,after,1)
    (engine/path).write_text(source)
    sections_path='src/data/region_map/region_map_sections.json'
    sections=json.loads(original(sections_path))
    for area in areas:
        section=next(s for s in sections['map_sections'] if s['id']==manifest['city_guide']['native_sections'][area['id']])
        section['name']=area['label'].split(' / ')[0].replace(' / ','-').replace(': Victory Road + League','')
    (engine/sections_path).write_text(json.dumps(sections,indent=2)+'\n')
    return [path,sections_path,'src/sf_world_guide.h','src/sf_world_guide_data.h','src/sf_world_guide_art.h','src/sf_world_guide_pixels.h']
