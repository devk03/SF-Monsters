"""Small, authored conversations on the intermediate SF walks."""
from world_routes import physical_routes

LINES = {
 'route_01_mid': ('The freight trains get right of way. My coffee has accepted this.','Head uphill for Potrero. If you can still finish a sentence, you have not reached the steep bit.'),
 'route_02_mid': ('I take these stairs to avoid the hill. Yes, I hear myself.','The Mission is past the next landing. You will smell lunch before you see it.'),
 'route_03_mid': ('Please leave the mural wall alone. That blank patch is spoken for.','I came out for one errand. Somehow I have a burrito and a secondhand lamp.'),
 'route_04_mid': ('The fog rolled in while I was deciding whether to bring a jacket.','The coast is a longer walk than it looks. The map leaves out the part where your legs complain.'),
 'route_05_mid': ('Shake the sand out here. Otherwise you are taking the whole beach home.','The wind has been giving my hair very specific instructions.'),
 'route_06_mid': ('I keep saying one more loop. The dog knows this is a lie.','The trees make the street sound farther away than it really is.'),
 'route_07_mid': ('I wore the nice shoes. The stairs were not consulted.','Down toward the Marina, up toward the houses. Very efficient geography, if you like stairs.'),
 'route_08_mid': ('That view gets better every time I stop to catch my breath.','I have been calling this a shortcut for years. Nobody believes me anymore.'),
 'route_09_mid': ('Going downhill is lovely until you remember you left something at the top.','The valley is down there. The wind is staying up here, apparently.'),
 'route_10_mid': ('There is a bench farther along. I am saving it for after this hill.','Quiet streets, loud birds. They start earlier than my alarm.'),
 'route_11_mid': ('I like the water here. It gives my eyes something to do besides look at a screen.','The ballpark is that way. On game days you can follow the hats.'),
 'route_12_mid': ('I bought a snack for the walk and finished it before starting.','If everyone stops in the middle of the path for a photo, the path becomes a queue.'),
 'route_13_mid': ('I am meeting someone near a cafe. We have established neither the cafe nor the time.','The blocks get smaller up ahead. Keep an eye out for the little bookshops.'),
 'route_14_mid': ('Stay on the path near the cliff. The good view does not require a better story.','The fog keeps revealing little pieces of the coast. Quite dramatic of it.'),
 'route_15_mid': ('I can see the tower from my kitchen. Somehow it looks even bigger from here.','I brought a jacket and still underestimated the wind. A local tradition.'),
}


def populate_routes(plans,manifest):
    sections={r['id']:r for r in physical_routes(manifest['routes']) if r.get('parent_route')}
    for plan in plans:
        identifier=plan['world_id']
        if identifier not in sections:continue
        rows=plan['rows'];legend=plan['legend']
        used=set();residents=[]
        for index,line in enumerate(LINES[identifier]):
            tx,ty=((9,9),(24,15))[index]
            candidates=[(x,y) for y in range(3,len(rows)-3) for x in range(3,len(rows[0])-3)
                if (x,y) not in used and all(not legend[rows[yy][xx]][1]
                    for xx,yy in ((x,y),(x-1,y),(x+1,y),(x,y-1),(x,y+1)))]
            if not candidates:raise ValueError(identifier+': route resident has no safe stopping point')
            x,y=min(candidates,key=lambda p:(abs(p[0]-tx)+abs(p[1]-ty),p[1],p[0]))
            used.add((x,y))
            plan['npcs'].append(dict(id=len(plan['npcs'])+1,x=x,y=y,
                graphics='OBJ_EVENT_GFX_'+('MAN_4' if index==0 else 'WOMAN_2'),
                script=f'WBTown_{identifier}_{index}',role='route passerby'))
            residents.append(dict(role='route passerby',dialogue=line,revisit=None))
        plan['ambient_residents']=residents
    return plans
