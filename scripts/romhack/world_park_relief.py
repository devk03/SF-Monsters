"""Authored rocky outlook frames, outside every mandatory walking approach."""


def outcrops(identifier,cards,lanes,protected):
    if identifier!='twin_peaks':return []
    rows=cards['rocks']['tiles'];result=[];used=set(protected)
    for group,(cx,cy) in enumerate(((45,18),(65,35))):
        count=0
        offsets=((-5,-4),(-2,-5),(2,-5),(5,-4),(6,0),(4,3),(-5,2)) if group==0 else ((3,1),(6,0),(4,3),(7,3),(-5,-7),(-2,-7))
        for dx,dy in offsets:
            x,y=cx+dx,cy+dy
            cells={(x+xx,y+yy) for yy,row in enumerate(rows) for xx,_ in enumerate(row)}
            if cells & (lanes|used):continue
            result.append(dict(group=group,x=x,y=y,cells=cells));used|=cells;count+=1
            if count==3:break
        if count<2:raise ValueError('Twin Peaks outcrop cannot frame its lookout safely')
    return result


def draw_outcrops(plan,grid,cards,groups):
    rows=cards['rocks']['tiles']
    for group in groups:
        x,y=group['x'],group['y']
        for dy,row in enumerate(rows):
            for dx,tile in enumerate(row):grid[y+dy][x+dx]=chr(0x100+tile-512)
        plan['town_blocks'].append(dict(style='rocks',x=x,y=y,width=len(rows[0]),height=len(rows),first_metatile=rows[0][0]))
    if groups:plan['ridge_outcrops']=[{k:v for k,v in g.items() if k!='cells'} for g in groups]
