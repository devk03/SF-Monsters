"""Cold-continue older actors, then exercise all native SF map selections read-only."""
import argparse,json,struct,sys
from pathlib import Path
from world_probe import Controller,ROOT
from walk_world import Walker
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from world_discoveries import load


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--saved',required=True,type=Path)
    parser.add_argument('--name',required=True);args=parser.parse_args()
    expected=json.loads((args.saved/'save-result.json').read_text());engine=ROOT/'.tools/pokeemerald-world-host'
    battery=(args.saved/'saved.sav').read_bytes()
    c=Controller(engine/'sf-world-blockout.gba',engine/'sf-world-blockout.elf',ROOT/'.tools/benchmarks'/args.name,battery=args.saved/'saved.sav')
    try:
        c.step(0,180);c.tap(8,90);c.tap(8,90)
        for _ in range(4):c.tap(1,90)
        c.step(0,180);w=Walker(c,json.loads((ROOT/'romhack/world/world.json').read_text()))
        if c.position()!=expected['position']:raise ValueError('Actor refresh moved a still-valid saved player position')
        identifier,point=w.location();plan=w.plans[identifier]
        pointer,=struct.unpack('<I',c.read(c.symbols['gSaveBlock1Ptr'],4))
        def read_large(address,size):
            return b''.join(c.read(address+i,min(256,size-i)) for i in range(0,size,256))
        cache=read_large(pointer+0xc70,64*24)
        graphic_source=(engine/'include/constants/event_objects.h').read_text()
        import re
        graphics={n:int(v,0) for n,v in re.findall(r'^#define\s+(OBJ_EVENT_GFX_\w+)\s+(0x[0-9A-F]+|\d+)\b',graphic_source,re.M)}
        for index,npc in enumerate(plan['npcs']):
            offset=index*24;x,y=struct.unpack_from('<hh',cache,offset+4)
            if (cache[offset],cache[offset+1],x,y)!=(npc['id'],graphics[npc['graphics']],npc['x'],npc['y']):
                raise ValueError('Cold Continue retained an old actor template')
        if any(cache[i*24] for i in range(len(plan['npcs']),64)):raise ValueError('Removed actors survived in the save cache')
        _,catalog=load()
        for flag in catalog['flags']:
            n=flag['value']
            if not c.read(pointer+0x1270+n//8,1)[0]&(1<<(n%8)):raise ValueError('Completed local activity did not survive ordinary Save/Continue')
        stable=read_large(pointer+0x560,0x2b0)+read_large(pointer+0x1270,0x12c)
        c.checkpoint('continued');c.tap(8,60)
        count=c.read(c.symbols['sNumStartMenuActions'],1)[0]
        actions=list(c.read(c.symbols['sCurrentStartMenuActions'],count));target=actions.index(13)
        cursor=c.read(c.symbols['sStartMenuCursorPos'],1)[0]
        for _ in range((target-cursor)%count):c.tap(128)
        c.tap(1,90)
        if c.read(c.symbols['sSFGuideWindow'],1)[0]==255:raise ValueError('SF map did not open')
        c.picture('city-map');selected=[]
        for _ in range(18):
            c.tap(16,30);index=c.read(c.symbols['sSFGuideSelected'],1)[0]
            if index in selected:raise ValueError('SF map selection skipped or repeated a destination')
            selected.append(index);c.tap(1,30)
            if c.read(c.symbols['sSFGuideDetails'],1)[0]!=1:raise ValueError('SF place details did not open')
            c.picture(f'place-{index:02d}');c.tap(1,30)
        c.tap(2,60)
        if c.read(c.symbols['sSFGuideWindow'],1)[0]!=255:raise ValueError('B did not return from the guide')
        c.tap(2,60)
        if c.position()!=expected['position']:raise ValueError('Reading the guide moved the player')
        if read_large(pointer+0x560,0x2b0)+read_large(pointer+0x1270,0x12c)!=stable:raise ValueError('Reading the guide changed inventory or flags')
        c.checkpoint('returned')
        if (c.output/'returned.sav').read_bytes()!=battery:raise ValueError('Guide/Continue rewrote Flash')
        result={'passed':True,'rom_sha256':c.digest(),'old_rom_sha256':expected['rom_sha256'],
                'actor_templates_refreshed':len(plan['npcs']),'player_position_preserved':True,
                'saved_local_flags_preserved':len(catalog['flags']),'guide_destinations':len(selected),
                'inventory_flags_and_flash_unchanged':True,'scope':'native guide selection, details, return and older-save actor refresh; visual approval separate'}
        (c.output/'guide-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
    finally:c.close()


if __name__=='__main__':main()
