"""Optional local favors and discoveries, separate from contributor mission hooks."""
import json,re
from pathlib import Path
from world_people import native_text
ROOT=Path(__file__).resolve().parents[2]


def load():
    data=json.loads((ROOT/'romhack/world/discoveries.json').read_text())
    state=json.loads((ROOT/'romhack/world/core-state.json').read_text())
    if data['schema_version']!=1 or state['schema_version']!=1:raise ValueError('Unknown local activity schema')
    names={}
    for flag in state['flags']:
        if not re.fullmatch(r'FLAG_UNUSED_0x[0-9A-F]+',flag['name']) or flag['name'] in names:
            raise ValueError('Local activity flags overlap or use an unreserved name')
        if type(flag['value']) is not int or int(flag['name'].split('0x')[1],16)!=flag['value']:
            raise ValueError('Local activity flag numeric binding changed')
        names[flag['name']]=flag
    used=set()
    for area,spec in data['areas'].items():
        if spec['kind'] not in ('favor','observe') or spec['item'] not in ('ITEM_POTION','ITEM_ANTIDOTE','ITEM_REPEL'):
            raise ValueError('Unsupported bounded local activity/reward')
        flags=[spec['done_flag']]+([spec['found_flag']] if spec['kind']=='favor' else [])
        if used.intersection(flags) or any(names[f]['owner']!=area for f in flags):raise ValueError('Local activity state ownership changed')
        used.update(flags)
        for key in ('request','found','thanks','look'):
            text=spec[key]
            if text is not None and (not isinstance(text,str) or not 8<=len(text)<=320 or any(c in text for c in '$"\\\n')):
                raise ValueError('Local activity needs bounded native text')
    if used!=set(names):raise ValueError('Unused or missing local activity state reservation')
    return data['areas'],state


def verify_flags(engine):
    _,state=load();source=(engine/'include/constants/flags.h').read_text()
    for flag in state['flags']:
        match=re.search(r'^#define\s+'+flag['name']+r'\s+(0x[0-9A-F]+)\b',source,re.M)
        if not match or int(match[1],16)!=flag['value']:raise ValueError('Pinned unused state slot changed')


def place(plans,manifest):
    if not manifest.get('town_finishing'):return plans
    areas,_=load()
    if set(areas)!={a['id'] for a in manifest['areas']}|{manifest['league']['venue']}:
        raise ValueError('Every approved destination needs one local activity')
    for plan in plans:
        area=plan['world_id']
        if area not in areas:continue
        spec=areas[area];x,y=spec['object'];sx,sy=spec['standing']
        plan['local_discovery']=spec
        plan['bg_events']=[{'type':'sign','x':x,'y':y,'elevation':0,
                           'player_facing_dir':'BG_EVENT_PLAYER_FACING_ANY',
                           'script':'WBLocal_'+area+'_Inspect'}]
        plan['access_points'].append({'kind':'checkpoint','name':'local_discovery',
                                      'activation':'interact','x':sx,'y':sy})
    return plans


def text(label,value):return [label+'::','    .string "'+native_text(value)+'"']


def npc_script(plan,index,prefix):
    spec=plan.get('local_discovery')
    if not spec or spec['kind']!='favor' or index!=spec['resident_index']:return None
    p='WBLocal_'+plan['world_id'];done=spec['done_flag'];found=spec['found_flag']
    result=[prefix+'::','    lock','    faceplayer',f'    goto_if_set {done}, {p}_Thanks',
            f'    goto_if_set {found}, {p}_Reward',f'    msgbox {p}_Request, MSGBOX_DEFAULT','    release','    end',
            p+'_Reward::',f'    checkitemspace {spec["item"]}, 1','    compare VAR_RESULT, 0',
            f'    goto_if_eq {p}_Full',f'    giveitem {spec["item"]}, 1',f'    setflag {done}',
            p+'_Thanks::',f'    msgbox {p}_ThanksText, MSGBOX_DEFAULT','    release','    end',
            p+'_Full::',f'    msgbox {p}_FullText, MSGBOX_DEFAULT','    release','    end']
    person=plan['ambient_residents'][index]
    result+=text(p+'_Request',person['dialogue']+' '+spec['request'])
    result+=text(p+'_ThanksText',spec['thanks'])
    result+=text(p+'_FullText','Your bag is full. Come back when you have room; I will keep your thank-you here.')
    return result


def scripts(plan):
    spec=plan.get('local_discovery')
    if not spec:return ''
    p='WBLocal_'+plan['world_id'];result=[p+'_Inspect::','    lockall',
            f'    goto_if_set {spec["done_flag"]}, {p}_Seen']
    if spec['kind']=='favor':result+=[f'    goto_if_set {spec["found_flag"]}, {p}_Seen']
    result += [f'    msgbox {p}_FoundText, MSGBOX_DEFAULT']
    if spec['kind']=='observe':
        result += [f'    checkitemspace {spec["item"]}, 1','    compare VAR_RESULT, 0',
                   f'    goto_if_eq {p}_ObjectFull',f'    giveitem {spec["item"]}, 1',f'    setflag {spec["done_flag"]}']
    else:result += [f'    setflag {spec["found_flag"]}']
    result += ['    releaseall','    end',p+'_Seen::',f'    msgbox {p}_LookText, MSGBOX_DEFAULT','    releaseall','    end']
    result+=text(p+'_FoundText',spec['found'])
    result+=text(p+'_LookText',spec['thanks'] if spec['kind']=='observe' else 'You already checked this spot. Nothing else has turned up.')
    if spec['kind']=='observe':
        result += [p+'_ObjectFull::',f'    msgbox {p}_ObjectFullText, MSGBOX_DEFAULT','    releaseall','    end']
        result+=text(p+'_ObjectFullText','Your bag is full. The supply can stay here until you have room.')
    return '\n'.join(result)+'\n'
