"""Readable neighborhood wayfinding and shop notices; no persistent state."""
from world_people import native_text

NOTICES={
    'presidio':'Visitor desk. Water, maps and a place to rest. Please leave muddy shoes on the mat.',
    'dogpatch':'Repair counter open. Please bring the broken thing, not just a photo of it.',
    'potrero_hill':'Neighborhood library. Quiet voices. Dramatic sighs after the hill are fine.',
    'mission':'Community studio. Make something. It does not have to become a company.',
    'castro':'Corner cafe. Your friend is probably at the other corner cafe. Ask before ordering.',
    'outer_sunset':'Rest stop. Sandy shoes welcome. Please leave the entire beach outside.',
    'marina':'Corner bar. Lost jackets: ask inside. Lost dignity: we cannot help with that.',
    'pacific_heights':'Neighbors welcome. The dog has already announced your arrival.',
    'noe_valley':'Repair cafe. Coffee first. Then we can discuss the mysterious clicking noise.',
    'mission_bay':'Neighborhood cafe. Lunch is a meal. A calendar invite is not a meal.',
    'giants_stadium':'Guest services. Ask us where to go. We also accept extremely detailed baseball opinions.',
    'financial_district':'Corner cafe. You may sit here without turning lunch into a meeting.',
    'north_beach':'Reading room. Books may be borrowed. The good chair is a shared resource.',
    'treasure_island':'Community room. Check the noticeboard before declaring that nothing happens here.',
}


def add_signs(plans,manifest):
    if not manifest.get('town_finishing'):return plans
    labels={area['id']:area['label'] for area in manifest['areas']}
    for plan in plans:
        identifier=plan['world_id']
        if identifier not in NOTICES:continue
        directions=[]
        for route in manifest['routes']:
            if route['from']==identifier:direction,other=route['from_port'],route['to']
            elif route['to']==identifier:direction,other=route['to_port'],route['from']
            else:continue
            compass={'left':'West','right':'East','up':'North','down':'South'}[direction]
            directions.append(compass+': '+labels[other]+'.')
        if identifier==manifest['league']['from_area']:
            directions.append('North: Angel Island. Surf and Waterfall access required.')
        texts={'wayfinder':labels[identifier]+'. '+' '.join(directions),
               'shop_board':NOTICES[identifier]}
        signs=[]
        for detail in plan.get('street_details',[]):
            style=detail['name']
            if style not in texts:continue
            x,y=detail['x'],detail['y']
            if style=='wayfinder':obj=(x,y+1);standing=(x,y+2)
            else:obj=(x,y);standing=(x,y+1)
            label='WBStreet_'+identifier+'_'+style
            sign={'style':style,'object':list(obj),'standing':list(standing),
                  'script':label,'text':texts[style]}
            signs.append(sign)
            plan.setdefault('bg_events',[]).append({'type':'sign','x':obj[0],'y':obj[1],
                'elevation':0,'player_facing_dir':'BG_EVENT_PLAYER_FACING_ANY','script':label})
            plan['access_points'].append({'kind':'checkpoint','name':style,
                'activation':'interact','x':standing[0],'y':standing[1]})
        if len(signs)!=2:raise ValueError('Neighborhood needs both visible sign fixtures')
        plan['street_signs']=signs
    return plans


def scripts(plan):
    result=[]
    for sign in plan.get('street_signs',[])+plan.get('extra_street_signs',[]):
        label=sign['script']
        result += [label+'::','    lockall',f'    msgbox {label}_Text, MSGBOX_DEFAULT',
                   '    releaseall','    end',label+'_Text::',
                   '    .string "'+native_text(sign['text'])+'"']
    return '\n'.join(result)+'\n' if result else ''
