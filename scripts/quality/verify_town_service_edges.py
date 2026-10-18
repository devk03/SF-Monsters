"""Native injured-party healing, purchase and full-bag reward retry in isolated QA."""
import argparse
import json
import re
import struct
import sys
from pathlib import Path
from world_probe import Controller, ROOT
from walk_world import Walker
from verify_town_life import close_dialogue
sys.path.insert(0,str(ROOT/'scripts/romhack'))
from world_discoveries import load


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',required=True,type=Path,help='Controller-derived service-fixture battle after one Tail Whip turn')
    parser.add_argument('--name',required=True)
    args=parser.parse_args();state=args.state.resolve();engine=ROOT/'.tools/pokeemerald-world-host'
    c=Controller(engine/'sf-town-services-qa.gba',engine/'sf-town-services-qa.elf',
                 ROOT/'.tools/benchmarks'/args.name,state=state,battery=state.with_suffix('.sav'))
    result={'rom_sha256':c.digest(),'fixture':True,'campaign_evidence':False}
    try:
        def pointer(name):return struct.unpack('<I',c.read(c.symbols[name],4))[0]
        def variable(n):return struct.unpack('<H',c.read(pointer('gSaveBlock1Ptr')+0x139c+n*2,2))[0]
        if variable(0xf8)!=0x5751:raise ValueError('Use only the explicitly isolated town-service fixture')
        source=(engine/'include/constants/items.h').read_text().split('enum {',1)[1].split('};',1)[0]
        ids={n:i for i,n in enumerate(re.findall(r'^\s+(ITEM_\w+),',source,re.M))}
        def key():return struct.unpack('<I',c.read(pointer('gSaveBlock2Ptr')+0xac,4))[0]
        def slots():return list(struct.iter_unpack('<HH',c.read(pointer('gSaveBlock1Ptr')+0x560,120)))
        def quantity(name):return sum(count^(key()&65535) for item,count in slots() if item==ids[name])
        def money():return struct.unpack('<I',c.read(pointer('gSaveBlock1Ptr')+0x490,4))[0]^key()
        def health():return struct.unpack('<HH',c.read(c.symbols['gPlayerParty']+86,4))
        # Complete the real native battle using Surf; no party or bag RAM writes.
        c.tap(1,60);c.tap(64,60);c.tap(1,900)
        for _ in range(24):
            if variable(0xfd)==1:break
            c.tap(1,120)
        else:raise ValueError('Fixture battle did not return to the field')
        close_dialogue(c);c.step(0,120);hp,maxhp=health()
        if not 0<hp<maxhp:raise ValueError('Healing check needs actual battle injury')
        w=Walker(c,json.loads((ROOT/'romhack/world/world.json').read_text()))
        w.travel('dogpatch_room');w.go((5,7));c.tap(64);c.tap(1,60);close_dialogue(c)
        if health()!=(maxhp,maxhp):raise ValueError('Native rest counter did not heal the injured party')
        result.update(hp_before=hp,hp_after=maxhp,max_hp=maxhp,counter_healing=True)
        w.go((10,7));c.tap(64);c.tap(1,60)
        for _ in range(12):
            if 0x02000000<=pointer('sShopData')<0x02040000:break
            c.tap(1,90)
        else:raise ValueError('Native buy list did not open')
        c.tap(128,60);c.tap(128,60);c.tap(1,90)
        before=money()
        for _ in range(12):
            if quantity('ITEM_REPEL')==1:break
            c.tap(1,90)
        else:raise ValueError('Native Repel purchase did not finish')
        # Item insertion precedes the thank-you text's money callback.
        c.step(0,240)
        if money()!=before-350:raise ValueError('Purchase did not deduct the native 350 price')
        result.update(money_before=before,money_after=money(),repel_purchased=1,repel_price=350)
        for _ in range(8):c.tap(2,60)
        w.travel('dogpatch');w.go((12,10));c.tap(64);c.tap(1,90);close_dialogue(c)
        if not all(item for item,_ in slots()) or quantity('ITEM_POTION')!=99:
            raise ValueError('Explicit fixture did not fill all30item slots and the Potion stack')
        specs,catalog=load();spec=specs['dogpatch'];values={f['name']:f['value'] for f in catalog['flags']}
        def flag(name):
            n=values[name];return bool(c.read(pointer('gSaveBlock1Ptr')+0x1270+n//8,1)[0]&1<<(n%8))
        def interact(standing,obj):
            w.go(tuple(standing));dx,dy=obj[0]-standing[0],obj[1]-standing[1]
            c.tap({(0,-1):64,(0,1):128,(1,0):16,(-1,0):32}[(dx,dy)])
            c.tap(1,60);close_dialogue(c)
        interact((8,14),(8,15));interact(spec['standing'],spec['object']);interact((8,14),(8,15))
        if not flag(spec['found_flag']) or flag(spec['done_flag']) or quantity('ITEM_POTION')!=99:
            raise ValueError('A full bag consumed or prematurely completed the pending reward')
        result.update(occupied_item_slots=30,reward_deferred=True,pending_favor_preserved=True)
        c.checkpoint('pending-full')
        def toss_one(item):
            c.tap(8,60);count=c.read(c.symbols['sNumStartMenuActions'],1)[0]
            actions=list(c.read(c.symbols['sCurrentStartMenuActions'],count));cursor=c.read(c.symbols['sStartMenuCursorPos'],1)[0]
            for _ in range((actions.index(2)-cursor)%count):c.tap(128)
            c.tap(1,120)
            pocket=c.read(c.symbols['gBagPosition']+5,1)[0]
            if pocket!=0:raise ValueError('Expected native Items pocket')
            pos=c.symbols['gBagPosition']
            current=struct.unpack('<H',c.read(pos+8,2))[0]+struct.unpack('<H',c.read(pos+18,2))[0]
            target=[i for i,_ in slots() if i].index(ids[item])
            for _ in range(abs(target-current)):c.tap(128 if target>current else 64,60)
            c.tap(1,60);c.tap(128,60);c.tap(128,60);c.tap(1,60);c.tap(1,60);c.tap(1,90)
            for _ in range(6):c.tap(2,60)
        toss_one('ITEM_POTION')
        if quantity('ITEM_POTION')!=98:raise ValueError('Native Toss did not free exactly one Potion space')
        interact((8,14),(8,15))
        if not flag(spec['done_flag']) or quantity('ITEM_POTION')!=99:
            raise ValueError('Pending full-bag reward did not grant after space became available')
        interact((8,14),(8,15))
        if quantity('ITEM_POTION')!=99:raise ValueError('Retry duplicated a completed local reward')
        # Fill the Antidote stack through an actual bulk purchase, then check
        # the other reward branch: an observation rather than a return favor.
        w.travel('dogpatch_room');w.go((10,7));c.tap(64);c.tap(1,60)
        for _ in range(12):
            callback=struct.unpack('<I',c.read(c.symbols['gMain']+4,4))[0]
            if callback&~1==c.symbols['CB2_BuyMenu']&~1:break
            c.tap(1,90)
        else:raise ValueError('Second native buy list did not open')
        c.step(0,240);c.tap(128,60);c.tap(1,90);c.tap(1,90)
        for _ in range(9):c.tap(16,24)
        for _ in range(7):c.tap(64,24)
        bulk_before=money()
        for _ in range(12):
            if quantity('ITEM_ANTIDOTE')==99:break
            c.tap(1,90)
        else:raise ValueError('Bulk98Antidote purchase did not finish')
        c.step(0,240)
        if money()!=bulk_before-9800:raise ValueError('Bulk purchase price or selected quantity differed')
        for _ in range(8):c.tap(2,60)
        w.travel('mission');observe=specs['mission']
        interact(observe['standing'],observe['object'])
        if flag(observe['done_flag']) or quantity('ITEM_ANTIDOTE')!=99:
            raise ValueError('Full bag consumed an observation reward')
        toss_one('ITEM_ANTIDOTE')
        if quantity('ITEM_ANTIDOTE')!=98:raise ValueError('Toss did not free observation reward space')
        interact(observe['standing'],observe['object'])
        if not flag(observe['done_flag']) or quantity('ITEM_ANTIDOTE')!=99:
            raise ValueError('Observation reward did not retry after freeing space')
        interact(observe['standing'],observe['object'])
        if quantity('ITEM_ANTIDOTE')!=99:raise ValueError('Observation retry duplicated reward')
        result.update(observation_full_bag_retry_once=True,bulk_quantity=98,bulk_price=9800)
        result.update(passed=True,retry_reward_granted_once=True,repeat_reward_rejected=True,
                      scope='Isolated native service-fixture controller proof, not normal campaign progress or balance')
        c.checkpoint('completed-retry')
        (c.output/'service-edges.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    except Exception:
        try:c.checkpoint('failure')
        except (ValueError,TimeoutError,BrokenPipeError):pass
        raise
    finally:
        (c.output/'partial-service-edges.json').write_text(json.dumps(result,indent=2)+'\n');c.close()


if __name__=='__main__':main()
