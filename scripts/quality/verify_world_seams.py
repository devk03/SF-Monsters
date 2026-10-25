"""Read live margins, native VRAM and full viewport after real walk-only crossings."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from world_probe import Controller,ROOT
from world_cold_continue import cold_continue
from walk_world import Walker
from check_creature_resources import decode_lz
from flash_audit import ORDERS,decode_mon,unpack_slot


PORTS={'left':(0,12),'right':(31,12),'up':(16,0),'down':(16,23)}
OPPOSITE={'left':'right','right':'left','up':'down','down':'up'}


def center(w,identifier):
    if identifier=='angel_island':
        p=next(p for p in w.plans[identifier]['world_sections'] if p['id']=='summit_league_entry')
        return p['x'],p['y']
    plan=w.plans[identifier]
    if plan.get('green_route_design'):
        # Authored woodland routes need not pass through the old blank-map
        # center. Observe inward travel on their actual main trail instead.
        spine=plan['green_route_design']['spine']
        return tuple(min(spine,key=lambda p:(abs(p[0]-16)+abs(p[1]-12),p[1],p[0])))
    return (16,8) if identifier=='league_route' else (16,12)


def cross(c,w,audit,direction,target,name,stages,transient):
    if transient:
        source_scene=audit.scene_signature();seen_new=False;source_map=w.location()[0]
        for _ in range(48):
            c.step({'left':32,'right':16,'up':64,'down':128}[direction],1)
            if w.location()[0]==target:break
        else:raise ValueError('No transient native camera crossing')
        for frame in range(1,17):
            c.step(0,1)
            if audit.scene_signature()==source_scene:
                capture=f'{name}-coherent-source-frame-{frame:02d}';c.picture(capture)
                c.observations.append({'kind':'connection-animation-frame','frame':frame,'capture':capture,
                                       'rendered_map':source_map,'phase':'coherent-source','scene_sha256':source_scene})
            else:
                capture=f'{name}-frame-{frame:02d}'
                stages.append(audit.check(w,capture,settled=False));seen_new=True
                c.observations.append({'kind':'connection-animation-frame','frame':frame,'capture':capture,
                                       'rendered_map':target,'phase':'verified-destination'})
        if not seen_new:raise ValueError('No complete destination scene within the16-frame observation')
    else:w.walk(direction)
    c.step(0,60)


class RenderAudit:
    def __init__(self,c):
        self.c=c;self.rom=c.rom.read_bytes();self.graphics={};self.own_graphics={}

    def read(self,address,size):
        if 0x08000000<=address<0x08000000+len(self.rom):
            return self.rom[address-0x08000000:address-0x08000000+size]
        return b''.join(self.c.read(address+i,min(1024,size-i)) for i in range(0,size,1024))

    def unpack(self,address,fmt):return struct.unpack('<'+fmt,self.read(address,struct.calcsize('<'+fmt)))

    def protected(self):
        pointer,=self.unpack(self.c.symbols['gSaveBlock1Ptr'],'I')
        sb2,=self.unpack(self.c.symbols['gSaveBlock2Ptr'],'I')
        key,=self.unpack(sb2+0xac,'I');money,=self.unpack(pointer+0x490,'I')
        party=self.read(self.c.symbols['gPlayerParty'],600);count=self.read(self.c.symbols['gPlayerPartyCount'],1)
        identity=[];self.friendships=[]
        self.steps=self.unpack(pointer+0x159c+5*4,'I')[0]^key
        for slot in range(6):
            mon=party[slot*100:(slot+1)*100]
            if slot<count[0]:
                decode_mon(mon)  # Includes native encrypted-data checksum validation.
                pid,ot=struct.unpack_from('<2I',mon)
                plain=bytearray(struct.pack('<12I',*(v^pid^ot for v in struct.unpack_from('<12I',mon,32))))
                friendship=ORDERS[pid%24].index('G')*12+9
                self.friendships.append(plain[friendship])
                plain[friendship]=0  # Ordinary walking can legitimately raise friendship.
                identity.append(mon[:28]+mon[30:32]+plain+mon[80:])
            else:identity.append(mon)
        return (b''.join(identity),count,
                money^key,self.read(pointer+0x560,0x2b0),self.read(pointer+0x1270,0x12c),
                self.read(pointer+0x139c+0xf8*2,10))

    def scene_signature(self):
        data=self.read(0x06000000,432*32)+self.read(0x06004000,16384)
        data+=self.read(0x05000000,14*32)
        for bg in (1,2,3):
            control,=self.unpack(self.c.symbols['sGpuRegBuffer']+8+bg*2,'H')
            data+=self.read(0x06000000+((control>>8)&31)*2048,2048)
        data+=self.read(self.c.symbols['sGpuRegBuffer']+0x14,4)
        return hashlib.sha256(data).hexdigest()

    def layout(self,plan):
        pointer,=self.unpack(self.c.symbols[plan['engine_map']],'I')
        width,height,border,cells,primary,secondary=self.unpack(pointer,'6I')
        return {'width':width,'height':height,'border':self.unpack(border,'4H'),
                'cells':self.unpack(cells,str(width*height)+'H'),'primary':primary,'secondary':secondary}

    def original_record(self,layout,identifier):
        tileset=layout['primary'] if identifier<512 else layout['secondary']
        graphics,palettes,records,attrs=self.unpack(tileset+4,'4I')
        index=identifier if identifier<512 else identifier-512
        return self.unpack(records+index*16,'8H'),self.unpack(attrs+index*2,'H')[0],graphics,palettes

    def source_pixels(self,word,graphics,palettes):
        if word&1023<512:
            if word>>12>=6:
                own=self.primary_art(graphics)
                if word&1023 not in own:raise ValueError('Linked SF record references unloaded own-primary art')
                return self.pixels(word,own[word&1023],self.read(palettes+(word>>12)*32,32))
            graphics,palettes=self.unpack(self.c.symbols['gTileset_General']+4,'2I')
        if graphics not in self.graphics:
            self.graphics[graphics]=decode_lz(self.rom[graphics-0x08000000:graphics-0x08000000+32768])
        data=self.graphics[graphics];tile=word&1023
        offset=(tile-512 if tile>=512 else tile)*32
        return self.pixels(word,data[offset:offset+32],self.read(palettes+(word>>12)*32,32))

    def primary_art(self,graphics):
        if graphics not in self.own_graphics:
            result={}
            for name,address in self.c.symbols.items():
                if not name.startswith('gSFPrimaryCount_'):continue
                suffix=name.removeprefix('gSFPrimaryCount_')
                source,=self.unpack(self.c.symbols['gTileset_'+suffix]+4,'I')
                if source!=graphics:continue
                count,=self.unpack(address,'H')
                slots=self.unpack(self.c.symbols['gSFPrimarySlots_'+suffix],str(count)+'H')
                raw=self.read(self.c.symbols['gSFPrimaryGraphics_'+suffix],count*32)
                if len(set(slots))!=count:raise ValueError('Linked own-primary slots overlap')
                result={slot:raw[i*32:(i+1)*32] for i,slot in enumerate(slots)}
            self.own_graphics[graphics]=result
        return self.own_graphics[graphics]

    @staticmethod
    def pixels(word,raw,palette):
        colors=struct.unpack('<16H',palette);result=[]
        for y in range(8):
            for x in range(8):
                sx=7-x if word&0x400 else x;sy=7-y if word&0x800 else y
                index=(raw[sy*4+sx//2]>>((sx%2)*4))&15
                result.append(colors[index] if index else None)
        return result

    def check(self,w,name,settled=True):
        c=self.c;owner,position=w.location();plan=w.plans[owner];layout=self.layout(plan)
        width,height,pointer=self.unpack(c.symbols['gBackupMapLayout'],'3I')
        cells=self.unpack(pointer,str(width*height)+'H')
        if (width,height)!=(layout['width']+15,layout['height']+14):raise ValueError('Wrong live grid dimensions')
        for y in range(layout['height']):
            for x in range(layout['width']):
                if cells[(y+7)*width+x+7]!=layout['cells'][y*layout['width']+x]:
                    raise ValueError(f'{owner}: old map-view IDs overwrite authored cell{x},{y}')
        atlas=self.unpack(c.symbols['sSFSeamCurrent'],'I')[0] if 'sSFSeamCurrent' in c.symbols else 0
        first,count=self.unpack(atlas+4,'2H') if atlas else (1024,0)
        records,attributes=self.unpack(atlas+12,'2I') if atlas else (0,0)
        version=self.c.symbols.get('gSFSeamLookupVersion')
        if atlas and version:
            if self.unpack(version,'H')[0]!=2:raise ValueError('Unsupported seam lookup ABI')
            lookup_pointer=self.unpack(atlas+44,'I')[0]
            lookup=self.unpack(lookup_pointer,'1024H')
        else:
            lookup=tuple(i-first+1 if first<=i<first+count else 0 for i in range(1024))
        if any(index>count for index in lookup):raise ValueError('Invalid seam record lookup')
        def active(identifier):
            if lookup[identifier]:
                index=lookup[identifier]-1
                return self.unpack(records+index*16,'8H'),self.unpack(attributes+index*2,'H')[0]
            r,a,_,_=self.original_record(layout,identifier);return r,a
        vram=self.read(0x06000000,32768)
        palettes=self.read(c.symbols['gPlttBufferUnfaded'],512)
        primary_ids={b&1023 for b in cells if b&1023<512 and not lookup[b&1023]}
        primary_graphics,primary_palettes=self.unpack(layout['primary']+4,'2I')
        fallback=0x3014
        if self.pixels(fallback,vram[20*32:21*32],palettes[3*32:4*32])!=self.source_pixels(fallback,primary_graphics,primary_palettes):
            raise ValueError('Connection atlas overwrote the native NORMAL-layer background tile/colors')
        for identifier in primary_ids:
            words,_,graphics,original_palettes=self.original_record(layout,identifier)
            for word in words:
                tile=word&1023;bank=word>>12
                if tile<432:
                    if self.pixels(word,vram[tile*32:tile*32+32],palettes[bank*32:bank*32+32])!=self.source_pixels(word,graphics,original_palettes):
                        raise ValueError('Connection atlas overwrote primary terrain graphics/colors')
                elif palettes[bank*32+2:bank*32+32]!=self.read(original_palettes+bank*32+2,30):
                    raise ValueError('Connection atlas overwrote native water/Waterfall colors')
        secondary_graphics,=self.unpack(layout['secondary']+4,'I')
        own=self.primary_art(secondary_graphics)
        required_own={word&1023 for identifier in set(cell&1023 for cell in layout['cells'])
                      if identifier>=512 for word in self.original_record(layout,identifier)[0]
                      if word&1023<512 and word>>12>=6}
        if not required_own<=own.keys():raise ValueError('Linked own map references unloaded primary art')
        for slot in required_own:
            raw=own[slot]
            if vram[slot*32:(slot+1)*32]!=raw:raise ValueError(owner+': own-primary facade graphics not loaded')
        if secondary_graphics not in self.graphics:
            self.graphics[secondary_graphics]=decode_lz(self.rom[secondary_graphics-0x08000000:secondary_graphics-0x08000000+32768])
        # Compare every authored graphic/color. Unused secondary slots may hold
        # foreign margins; the margin audit below independently verifies those.
        for identifier in set(cell&1023 for cell in layout['cells']):
            if identifier<512:continue
            words,_,graphics,original_palettes=self.original_record(layout,identifier)
            for word in words:
                slot=word&1023;bank=word>>12
                if self.pixels(word,vram[slot*32:(slot+1)*32],palettes[bank*32:(bank+1)*32])!=self.source_pixels(word,graphics,original_palettes):
                    raise ValueError(owner+': authored SF graphics/colors differ from linked art')
        margin_cells=0
        margin_checks=[];owners={}
        for number,link in enumerate(plan['connections'] or []):
            foreign=w.plans[w.native[link['map']]];other=self.layout(foreign);d=link['direction']
            offset=link['offset']
            if d=='left':points=[(x,sy+offset+7,x+other['width']-7,sy) for sy in range(other['height']) for x in range(7)]
            elif d=='right':points=[(x+layout['width']+7,sy+offset+7,x,sy) for sy in range(other['height']) for x in range(8)]
            elif d=='up':points=[(sx+offset+7,y,sx,y+other['height']-7) for sx in range(other['width']) for y in range(7)]
            else:points=[(sx+offset+7,y+layout['height']+7,sx,y) for sx in range(other['width']) for y in range(7)]
            points=[p for p in points if 0<=p[0]<width and 0<=p[1]<height]
            margin_checks.append((number,foreign,other,points))
            for x,y,_,_ in points:owners[x,y]=number
        for number,foreign,other,points in margin_checks:
            for x,y,sx,sy in points:
                if owners[x,y]!=number:continue  # Later native connection copies own shared buffer corners.
                expected=other['cells'][sy*other['width']+sx];actual=cells[y*width+x]
                if expected&~1023!=actual&~1023:raise ValueError('Connection changed collision/elevation')
                identifier=expected&1023
                if identifier<512:
                    if actual!=expected:raise ValueError('Native terrain/water/fall ID changed')
                else:
                    old,old_attr,graphics,palette=self.original_record(other,identifier)
                    new,new_attr=active(actual&1023)
                    if old_attr!=new_attr:raise ValueError('Foreign margin behavior/layer changed')
                    for a,b in zip(new,old):
                        raw=vram[(a&1023)*32:(a&1023)*32+32]
                        if self.pixels(a,raw,palettes[(a>>12)*32:(a>>12)*32+32])!=self.source_pixels(b,graphics,palette):
                            raise ValueError(f'{owner}->{foreign["world_id"]}: wrong live foreign graphics/colors at{x},{y}')
                margin_cells+=1
        offsets=c.read(c.symbols['sFieldCameraOffset'],4);tx,ty=offsets[2:4]
        buffers={}
        for bg in (1,2,3):
            p,=self.unpack(c.symbols[f'gOverworldTilemapBuffer_Bg{bg}'],'I')
            raw=self.read(p,2048);buffers[bg]=struct.unpack('<1024H',raw)
            control,=self.unpack(0x04000008+bg*2,'H')
            visible=self.read(0x06000000+((control>>8)&31)*2048,2048)
            if settled and visible!=raw:
                raise ValueError('Queued field tilemap was not transferred to VRAM')
            buffers[bg]=struct.unpack('<1024H',visible)
        checked=0
        # Project the actual hardware scroll onto the logical map anchor.
        # During a step the exiting partial column/row remains visible too.
        #Scroll registers are write-only on GBA; read the engine's actual shadow.
        scroll_x,scroll_y=self.unpack(c.symbols['sGpuRegBuffer']+0x14,'2H')
        dx=(scroll_x-tx*8+128)%256-128;dy=(scroll_y-ty*8+128)%256-128
        left,top=dx//16,dy//16
        columns=(dx%16+240+15)//16;rows=(dy%16+160+15)//16
        for my in range(top,top+rows):
            for mx in range(left,left+columns):
                x,y=position[0]+mx,position[1]+my
                block=cells[y*width+x] if 0<=x<width and 0<=y<height else 1023
                identifier=(block&1023) if block!=1023 else layout['border'][((x+1)&1)+(((y+1)&1)<<1)]&1023
                words,attr=active(identifier);layer=attr>>12
                expected={1:words[4:],2:words[:4],3:(0x3014,)*4} if layer==0 else (
                    {1:(0,)*4,2:words[4:],3:words[:4]} if layer==1 else {1:words[4:],2:(0,)*4,3:words[:4]})
                base=((ty+my*2)%32)*32+(tx+mx*2)%32
                indices=[base,base+1,base+32,base+33]
                for bg in (1,2,3):
                    actual=tuple(buffers[bg][i] for i in indices)
                    if actual!=tuple(expected[bg]):raise ValueError(f'{owner}: stale viewport words at{mx},{my} BG{bg}')
                checked+=1
        c.picture(name)
        return {'capture':name,'map':owner,'position':list(position),'surf':bool(c.read(c.symbols['gPlayerAvatar'],1)[0]&8),
                'own_cells':layout['width']*layout['height'],'foreign_cells':margin_cells,'viewport_metatiles':checked,
                'secondary_vram_sha256':hashlib.sha256(vram[16384:]).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',required=True,type=Path);parser.add_argument('--battery',required=True,type=Path)
    parser.add_argument('--name',required=True);parser.add_argument('--group',choices=['urban','nature','water','all','transient'],default='urban')
    parser.add_argument('--start-trial',type=int,default=0);parser.add_argument('--trial-count',type=int,default=8)
    parser.add_argument('--check-menu',action='store_true',help='Separate post-trial palette13 restoration check')
    parser.add_argument('--frozen-inputs',type=Path,help='Immutable build-receipt inputs directory with world.json and generated plans')
    parser.add_argument('--transient-frames',action='store_true',help='Audit all16crossing frames even for other trial groups')
    args=parser.parse_args();engine=args.engine.resolve()
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',ROOT/'.tools/benchmarks'/args.name,battery=args.battery)
    dependencies=[Path(__file__)]+[Path(__file__).parent/n for n in
        ('world_probe.py','world_cold_continue.py','walk_world.py','check_creature_resources.py','flash_audit.py')]
    manifest_path=ROOT/'romhack/world/world.json'
    plans=None
    if args.frozen_inputs:
        manifest_path=args.frozen_inputs/'world.json'
        generated=args.frozen_inputs/'generated'
        content=json.loads((generated/'content.json').read_text())
        paths=[generated/Path(name).name for name in content['maps']]
        plans=[json.loads(path.read_text()) for path in paths]
        dependencies.extend([generated/'content.json']+paths)
    manifest=json.loads(manifest_path.read_text())
    dependencies.append(manifest_path)
    transient=args.group=='transient' or args.transient_frames
    frozen={}
    for source in dependencies:
        data=source.read_bytes();destination=c.output/'dependencies'/source.name
        destination.parent.mkdir(exist_ok=True);destination.write_bytes(data)
        frozen[source.name]=hashlib.sha256(data).hexdigest()
    stages=[]
    try:
        cold_continue(c);w=Walker(c,manifest,plans=plans);audit=RenderAudit(c)
        flash=args.battery.read_bytes();_,sections=max(s for n in (0,1) if(s:=unpack_slot(flash,n)))
        saved=b''.join(sections[n] for n in range(1,5))
        if audit.read(c.symbols['gPlayerParty'],600)!=saved[0x238:0x490]:
            raise ValueError('Ordinary cold Continue changed actual party bytes before any walking')
        groups={'urban':[('noe_valley','left'),('noe_valley','right'),('mission_bay','left'),('marina','down'),('financial_district','down')],
                'nature':[('twin_peaks','right'),('outer_sunset','up')],
                'water':[('north_beach','right'),('mission_bay','right'),('north_beach','up')],
                'transient':[('noe_valley','left'),('noe_valley','right'),('marina','down'),
                             ('pacific_heights','up'),('financial_district','up'),('mission_bay','right')]}
        pairs=set();groups['all']=[]
        for owner,plan in w.plans.items():
            for link in plan['connections'] or []:
                pair=frozenset((owner,w.native[link['map']]))
                if pair not in pairs:groups['all'].append((owner,link['direction']));pairs.add(pair)
        total=len(groups[args.group]);selected=groups[args.group][args.start_trial:args.start_trial+args.trial_count]
        if not selected or args.start_trial<0 or args.trial_count<1:raise ValueError('Empty or invalid bounded trial selection')
        for number,(owner,direction) in enumerate(selected,args.start_trial):
            w.travel(owner);w.go(center(w,owner));c.step(0,60)
            protected=audit.protected()
            friends=list(audit.friendships);steps=audit.steps
            stages.append(audit.check(w,f'{number}-source-center'))
            link=next(l for l in w.plans[owner]['connections'] if l['direction']==direction)
            target=w.native[link['map']]
            def port_for(identifier,side):
                rows=w.plans[identifier]['rows'];width,height=len(rows[0]),len(rows)
                return {'left':(0,height//2),'right':(width-1,height//2),
                        'up':(width//2,0),'down':(width//2,height-1)}[side]
            entry=port_for(target,OPPOSITE[direction])
            w.go(port_for(owner,direction));c.step(0,60);stages.append(audit.check(w,f'{number}-source-edge'))
            cross(c,w,audit,direction,target,f'{number}-forward',stages,transient)
            if w.location()[0]!=target:raise ValueError('Connection did not reach authored target')
            stages.append(audit.check(w,f'{number}-destination-edge'))
            inward=center(w,target)
            w.go(inward);c.step(0,60);stages.append(audit.check(w,f'{number}-destination-inward'))
            if target in ('route_17','route_18','league_route') and not stages[-1]['surf']:
                raise ValueError('Water crossing did not exercise genuine Surf')
            w.go(entry);cross(c,w,audit,OPPOSITE[direction],owner,f'{number}-reverse',stages,transient)
            stages.append(audit.check(w,f'{number}-reverse-edge'))
            if w.location()[0]!=owner:raise ValueError('Reverse connection returned to wrong map')
            w.go(center(w,owner));c.step(0,60);stages.append(audit.check(w,f'{number}-reverse-inward'))
            after=audit.protected()
            bound=4*((((audit.steps-steps)&0xffffffff)+127)//128)
            if any(new<old or new-old>bound for old,new in zip(friends,audit.friendships)):
                raise ValueError('Party friendship changed beyond native walking-step bounds')
            for i,label in enumerate(('party','party_count','money','bag','flags','chapter')):
                if protected[i]!=after[i]:
                    detail=[(n,a,b) for n,(a,b) in enumerate(zip(protected[i],after[i])) if a!=b] if isinstance(protected[i],bytes) else []
                    raise ValueError(f'Walk-only seam trial changed {label}: {detail[:20]}')
            print(owner,direction,target,flush=True)
        if args.check_menu:
            before=audit.read(c.symbols['gPlttBufferUnfaded']+13*32,32)+audit.read(c.symbols['gPlttBufferFaded']+13*32,32)
            before_position=c.position();c.tap(8,45)
            count=c.read(c.symbols['sNumStartMenuActions'],1)[0]
            actions=list(c.read(c.symbols['sCurrentStartMenuActions'],count));target=actions.index(13)
            cursor=c.read(c.symbols['sStartMenuCursorPos'],1)[0]
            for _ in range((target-cursor)%count):c.tap(128)
            c.tap(1,120)
            if c.read(c.symbols['sSFGuideWindow'],1)[0]==255:raise ValueError('Guide did not open over the connection atlas')
            c.tap(8,60)
            after=audit.read(c.symbols['gPlttBufferUnfaded']+13*32,32)+audit.read(c.symbols['gPlttBufferFaded']+13*32,32)
            if before!=after or c.position()!=before_position:raise ValueError('Guide did not restore both connection palette13 buffers and position')
            stages.append(audit.check(w,'separate-guide-return'))
        c.checkpoint('walk-only-returned')
        if (c.output/'walk-only-returned.sav').read_bytes()!=args.battery.read_bytes():raise ValueError('Seam traversal rewrote Flash')
        result={'passed':True,'rom_sha256':c.digest(),'group':args.group,'walk_only_trials':len(selected),
                'frozen_dependencies':frozen,'transient_frames':transient,
                'frozen_build_inputs':str(args.frozen_inputs.resolve()) if args.frozen_inputs else None,
                'start_trial':args.start_trial,'total_group_trials':total,
                'stages':stages,'flash_unchanged':True,'protected_state_unchanged':True,
                'separate_guide_palette_check':args.check_menu,
                'party_scope':'All native party fields and checksums preserved except ordinary walking friendship increases',
                'scope':'native live buffers/VRAM/art, both directions and inward walking; no human quality approval'}
        (c.output/'seams-result.json').write_text(json.dumps(result,indent=2)+'\n')
    except Exception:
        if c.process.poll() is None:
            try:c.picture('failure')
            except (BrokenPipeError,ValueError):pass
        raise
    finally:
        (c.output/'partial-stages.json').write_text(json.dumps(stages,indent=2)+'\n');c.close()


if __name__=='__main__':main()
