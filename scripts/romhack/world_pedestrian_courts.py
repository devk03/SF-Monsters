"""Small planted cut-throughs interrupt long urban frontage bands."""


def propose(identifier,bands,width,height,unavailable,walks,lanes):
    result=[];used=set(unavailable)
    anchor=36+sum(map(ord,identifier))%40
    for zone in (0,1):
        target=7 if zone==0 else 42
        choices=sorted((b for b in bands if b[1]-b[0]>=52 and (b[2]>=32)==bool(zone)),
                       key=lambda b:(abs(b[2]-target),b[2],b[0],b[1]))
        found=None
        for left,right,top in choices:
            if top<4 or top+5>=height-1:continue
            center=anchor if zone==0 else width-1-anchor
            for x in sorted(range(max(4,left+3),min(width-5,right-5)),key=lambda x:(abs(x-center),x)):
                floor={(xx,y) for y in range(top-3,top+6) for xx in range(x,x+3)}
                neighbors={(xx,y) for y in range(top,top+4) for xx in range(x-3,x+6)}
                court={(xx,y) for y in range(top-3,top) for xx in range(x,x+3)}
                if any(xx<32 and y<24 for xx,y in floor):continue
                if floor & (used|lanes) or (neighbors|court) & (used|walks):continue
                found=dict(x=x,top=top,cells=floor,rest=[x+1,top-2],zone=zone);break
            if found:break
        if found:result.append(found);used|=found['cells']
    return result


NOTES={
 'dogpatch':'Someone from the workshops waters these before opening up. Please leave the passage clear.',
 'potrero_hill':'A small level spot. Enjoy it before the next hill.',
 'mission':'Neighbors planted this corner. Please leave the pots where they are.',
 'castro':'A quiet cut-through. Leave some space for the next person to sit.',
 'outer_sunset':'The plants are doing their best with the wind. So are the rest of us.',
 'marina':'The plants get watered on schedule. You should have some water too.',
 'pacific_heights':'This little garden belongs to the whole block.',
 'noe_valley':'Neighbors keep the pots here. Leave enough room for a stroller to pass.',
 'mission_bay':'A patch of green between meetings. Nobody has booked it.',
 'giants_stadium':'A quieter way around the block. You can talk baseball at normal volume here.',
 'financial_district':'A place to sit without turning lunch into a meeting.',
 'north_beach':'Bring your own book. Leave the good light for the plants.',
 'treasure_island':'Shared pots, shared passage. Please take your rubbish with you.',
}


def furnish(plan,grid,items,stamp,token,material):
    for index,p in enumerate(items):
        x,top=p['x'],p['top']
        for xx,y in p['cells']:grid[y][xx]=token(material,xx,y)
        if not stamp('flower_box',x+2,top-2,passage=True):
            raise ValueError(plan['world_id']+': planted court fixture cannot fit')
        sx,sy=p['rest']
        label=f'WBCourt_{plan["world_id"]}_{index}'
        notice=dict(style='pedestrian_court_'+str(index),object=[x+2,top-2],standing=[sx,sy],script=label,text=NOTES[plan['world_id']])
        plan.setdefault('court_notices',[]).append(notice)
        plan.setdefault('extra_street_signs',[]).append(notice)
        plan.setdefault('bg_events',[]).append(dict(type='sign',x=x+2,y=top-2,elevation=0,player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=label))
        plan['access_points'].append(dict(kind='checkpoint',name='pedestrian_court_'+str(index),activation='interact',x=sx,y=sy))
        plan.setdefault('scenic_viewpoints',[]).append(dict(name='Planted pedestrian court '+str(index+1),x=sx,y=sy))
    plan['pedestrian_courts']=[{k:v for k,v in p.items() if k!='cells'} for p in items]
