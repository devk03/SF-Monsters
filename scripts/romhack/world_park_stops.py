"""Small authored destinations for park branches; no persistent-state allocation."""
STOPS={
 'golden_gate_park':(
  ('Garden court','Sit for a bit. Nobody needs a photo of you having a relaxing time.','bench_grass'),
  ('Pond rest','You can take the long way home. That is allowed.','bench_grass'),
  ('Windmill trail rest','Water break. Checking your step count is optional.','bin_grass')),
 'twin_peaks':(
  ('North lookout','The climb was real. The urgent email can wait.','bench_grass'),
  ('South lookout','Different view. Same wind. Hold onto your hat.','bench_grass'),
  ('Ridge shelter','Catch your breath before deciding the next hill looks easy.','rocks')),
 'sutro_tower':(
  ('Tower trail rest','If the fog hid your destination, it has not moved.','bench_grass'),
  ('Fog break','Sit down. Wait for the city to reappear. Repeat as necessary.','bench_grass'),
  ('Ridge rest','Please take your snack wrapper back down the hill with you.','bin_grass')),
 'lands_end':(
  ('Coastal lookout','The view is better without walking closer to the edge.','bench_grass'),
  ('Ruins trail rest','Old things deserve a little care. So do tired knees.','rocks'),
  ('Wind shelter','A quiet place to reconsider your choice of jacket.','bench_grass')),
 'angel_island':(
  ('Landing view','Take a moment before the next climb. Your boat is not a rideshare.','bench_grass'),
  ('Island rest','You came all this way. You can stop looking at the time.','rocks'),
  ('League approach rest','Rest here. The next challenge will still be there.','bench_grass')),
}


def add_park_stops(plan,grid,cards,glades,lanes,protected):
    width,height=len(grid[0]),len(grid);legend=plan['legend']
    sign=chr(0x803);legend[sign]=[3,True,3]
    stops=[]
    for index,((cx,cy,rx,ry),(title,text,prop)) in enumerate(zip(glades,STOPS[plan['world_id']])):
        glade={(x,y) for y in range(cy-ry,cy+ry+1) for x in range(cx-rx,cx+rx+1)
               if (x-cx)**2*ry**2+(y-cy)**2*rx**2<=rx**2*ry**2}
        candidates=sorted(glade,
                          key=lambda p:(abs(p[0]-(cx-2))+abs(p[1]-(cy-1)),p[1],p[0]))
        for x,y in candidates:
            if not(1<x<width-2 and 1<y<height-2):continue
            if {(x,y),(x,y+1)} & protected or (x,y) in lanes:continue
            if any(legend[grid[yy][xx]][1] for xx,yy in ((x,y),(x,y+1))):continue
            grid[y][x]=sign;break
        else:raise ValueError(plan['world_id']+': clearing has no readable stop')
        label=f'WBPark_{plan["world_id"]}_{index}'
        record=dict(style='park_stop_'+str(index),name=title,object=[x,y],standing=[x,y+1],
                    script=label,text=title+'. '+text)
        stops.append(record)
        plan.setdefault('extra_street_signs',[]).append(record)
        plan.setdefault('bg_events',[]).append(dict(type='sign',x=x,y=y,elevation=0,
            player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=label))
        plan['access_points'].append(dict(kind='checkpoint',name='park_stop_'+str(index),
            activation='interact',x=x,y=y+1))
        protected|={(x,y),(x,y+1)}
        rows=cards[prop]['tiles'];placed=False
        for px,py in sorted(candidates,key=lambda p:(abs(p[0]-(cx+1))+abs(p[1]-(cy-1)),p[1],p[0])):
            cells={(px+dx,py+dy) for dy,row in enumerate(rows) for dx,_ in enumerate(row)}
            approach={(xx,py+len(rows)) for xx in range(px,px+len(rows[0]))}
            if cells & (protected|lanes):continue
            if any(not 1<xx<width-2 or not 1<yy<height-2 or legend[grid[yy][xx]][1] for xx,yy in cells|approach):continue
            for dy,row in enumerate(rows):
                for dx,tile in enumerate(row):grid[py+dy][px+dx]=chr(0x100+tile-512)
            plan['town_blocks'].append(dict(style=prop,x=px,y=py,width=len(rows[0]),height=len(rows),first_metatile=rows[0][0]))
            protected|=cells|approach;record['fixture']=dict(style=prop,x=px,y=py);placed=True;break
        if not placed:raise ValueError(plan['world_id']+': '+title+' fixture cannot fit its clearing')
        plan.setdefault('scenic_viewpoints',[]).append(dict(name=title,x=x,y=y+1))
    plan['park_stops']=stops
