"""Fill six existing SF parcels with connected homes from the accepted art kit."""
from copy import deepcopy
import json
from pathlib import Path

# left, top, ordered attached house styles, clear an old fifth wall row.
BLOCKS=((1,1,('pair',),True),(1,12,('pair',),True),
        (1,20,('pair',),True),(9,13,('cafe','coral'),False),
        (9,20,('cafe','cream'),False),(25,11,('coral','cream','lilac'),False))
STYLES={'coral':(0,3,65,11),'cafe':(3,2,65,11),'cream':(5,3,65,11),
        'lilac':(8,3,65,11),'pair':(0,4,135,4)}
TOKENS={'V':[0,True,0],'v':[699,False,3]}
BASE=Path(__file__).resolve().parents[2]/'assets/tiles/park-density-v1/baseline-v78/source-plan.json'


def declaration():
    return [{'x':x,'y':y,'styles':list(styles),'clear_front':front}
            for x,y,styles,front in BLOCKS]


def footprint():
    result={}
    for left,top,styles,front in BLOCKS:
        x=left
        for name in styles:
            source,width,first,stride=STYLES[name]
            for row in range(4):
                for col in range(width):
                    point=(x+col,top+row)
                    if point in result:raise ValueError('Dense housing parcels overlap.')
                    result[point]=(first+row*stride+source+col,'V')
            x+=width
        if front:
            for col in range(left,x):
                if (col,top+4) in result:raise ValueError('Dense housing approach overlaps a wall.')
                result[col,top+4]=(531,'v')
    return result


def strip(plan):
    """Restore only the explicitly declared parcels for older source checks."""
    result=deepcopy(plan)
    if 'street_blocks' not in result:
        if any(token in result['legend'] for token in TOKENS):
            raise ValueError('Unregistered dense housing legend.')
        return result
    if result.pop('street_blocks')!=declaration() or any(result['legend'].get(t)!=v for t,v in TOKENS.items()):
        raise ValueError('Dense housing declarations or wall collision changed.')
    baseline=json.loads(BASE.read_text());cells=footprint()
    for y,row in enumerate(result['rows']):
        updated=list(row)
        for x,token in enumerate(row):
            cell=cells.get((x,y))
            if (cell is not None and token!=cell[1]) or (cell is None and token in TOKENS):
                raise ValueError('Dense housing token escaped its declared parcel.')
            if cell is not None:updated[x]=baseline['rows'][y][x]
        result['rows'][y]=''.join(updated)
    for token in TOKENS:result['legend'].pop(token)
    if result!=baseline:raise ValueError('Dense housing changes an unrelated map field.')
    return result


def decorate(plan):
    if plan!=json.loads(BASE.read_text()):
        raise ValueError('Dense housing must extend the frozen authored v78 plan.')
    result=deepcopy(plan);cells=footprint()
    events={(e['x'],e['y']) for key in ('npcs','warp_events','bg_events') for e in plan[key]}
    protected=events|{(x,y) for x in range(18,29) for y in range(2,7)}
    protected|={(13,6),(13,7),(32,6),(32,7),(21,7),(16,17),(7,26)}
    if protected & cells.keys():raise ValueError('Dense housing covers a protected entry, home or event.')
    for (x,y),(_,token) in cells.items():
        old=plan['rows'][y][x]
        if old not in 'PWXYabcdefghij':raise ValueError('Dense housing cannot replace a road, park, door or furnishing.')
        row=result['rows'][y];result['rows'][y]=row[:x]+token+row[x+1:]
    result['legend'].update(deepcopy(TOKENS));result['street_blocks']=declaration()
    if strip(result)!=plan:raise ValueError('Dense housing must preserve all other source fields.')
    return result


def tile(plan,x,y):
    if 'street_blocks' not in plan:return None
    cell=footprint().get((x,y))
    if cell is None:
        if plan['rows'][y][x] in TOKENS:raise ValueError('Unregistered dense housing cell.')
        return None
    record,token=cell
    if plan['rows'][y][x]!=token or plan['legend'].get(token)!=TOKENS[token]:
        raise ValueError('Dense housing wall/approach collision or elevation changed.')
    return record
