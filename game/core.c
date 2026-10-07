#include "game.h"

void text_copy(char *out, const char *in) { while((*out++=*in++)); }
void text_append(char *out, const char *in) { while(*out) out++; text_copy(out,in); }
void text_number(char *out, int value) {
    char buf[12]; int n=0; if(value<0) value=0;
    do { buf[n++]=(char)('0'+value%10); value/=10; } while(value);
    while(*out) out++;
    while(n) *out++=buf[--n];
    *out=0;
}
static u32 random_next(Game *g) {
    g->save.rng=g->save.rng*1664525u+1013904223u; return g->save.rng;
}
u32 save_checksum(const Save *s) {
    const u8 *p=(const u8*)s; u32 hash=2166136261u;
    for(unsigned i=0;i<sizeof(Save);i++) {
        /* checksum occupies bytes 8..11; exclude it from its own hash. */
        if(i<8 || i>=12) { hash^=p[i]; hash*=16777619u; }
    }
    return hash;
}
int game_max_hp(const Monster *m) { return species[m->species].hp+m->level*3; }
int save_valid(const Save *s) {
    if(s->magic!=0x53464d4d || s->version!=1 || s->checksum!=save_checksum(s)) return 0;
    if(s->roster_count<1 || s->roster_count>ROSTER_CAPACITY || s->party_count<1 ||
       s->party_count>PARTY_CAPACITY || s->party_count>s->roster_count) return 0;
    if(s->map>2 || s->x>=MAP_W || s->y>=MAP_H || s->facing>3) return 0;
    for(int i=0;i<s->roster_count;i++) {
        const Monster *m=&s->roster[i];
        if(m->species>=SPECIES_COUNT || m->level<1 || m->level>100) return 0;
        if(m->hp>game_max_hp(m) || m->status>1) return 0;
        for(int j=0;j<4;j++) if(m->pp[j]>20) return 0;
    }
    return 1;
}
void save_prepare(Save *s) {
    s->magic=0x53464d4d; s->version=1; s->sequence++; s->checksum=save_checksum(s);
}
static Monster make_monster(u8 id,u8 level) {
    Monster m={0}; m.species=id; m.level=level; m.hp=(u8)game_max_hp(&m);
    m.pp[0]=20; m.pp[1]=15; m.pp[2]=10; m.pp[3]=5; return m;
}
static void message(Game *g,const char *speaker,const char *text,u8 action) {
    text_copy(g->speaker,speaker); text_copy(g->text,text);
    g->action=action; g->scene=TALK; g->cursor=0;
}
static void battle_message(Game *g,const char *text) {
    text_copy(g->text,text); g->message_open=1;
}
void game_init(Game *g,const Save *saved) {
    u8 *p=(u8*)g; for(unsigned i=0;i<sizeof(Game);i++) p[i]=0;
    if(saved && save_valid(saved)) { g->save=*saved; g->have_save=1; }
    else {
        g->save.rng=0x53464d01; g->save.map=0; g->save.x=10; g->save.y=12;
        g->save.coins=120; g->save.capsules=12; g->save.potions=6;
    }
    g->scene=TITLE;
}
void game_heal(Game *g) {
    for(int i=0;i<g->save.roster_count;i++) {
        Monster *m=&g->save.roster[i]; m->hp=(u8)game_max_hp(m); m->status=0;
        m->pp[0]=20; m->pp[1]=15; m->pp[2]=10; m->pp[3]=5;
    }
}
int game_party_alive(const Game *g) {
    for(int i=0;i<g->save.party_count;i++) if(g->save.roster[i].hp) return i;
    return -1;
}
void game_encounter(Game *g,u8 id,u8 level,u8 trainer) {
    if(id>=SPECIES_COUNT) return;
    g->enemy=make_monster(id,level); g->trainer=trainer; g->enemy_index=0;
    g->enemy_count=trainer==2?3:1; g->enemy_team[0]=id;
    g->enemy_team[1]=5; g->enemy_team[2]=9;
    g->save.seen|=1u<<id; g->active=(u8)game_party_alive(g);
    if(g->active>=g->save.party_count) { game_heal(g); g->active=0; }
    g->scene=BATTLE; g->cursor=0; g->focus=0;
    text_copy(g->text,trainer==2?"Scott: A demo is not a deployment.":trainer?"Roon wants to test your team.":"A wild mini monster appears!");
    g->message_open=1;
}
int game_damage(Game *g,const Monster *a,const Monster *b,int move) {
    int attack=species[a->species].attack+a->level*2;
    int defense=species[b->species].defense+b->level;
    int damage=(attack*(move==1?14:9))/(defense+8)+2;
    int at=species[a->species].type,bt=species[b->species].type;
    if(move==1) {
        if((at==TIDE&&bt==EMBER)||(at==EMBER&&bt==BLOOM)||
           (at==BLOOM&&bt==TIDE)||(at==SPARK&&bt==TIDE)||
           (at==STONE&&bt==SPARK)||(at==ECHO&&bt==FOG)) damage=damage*3/2;
        if((at==TIDE&&bt==BLOOM)||(at==EMBER&&bt==TIDE)||
           (at==BLOOM&&bt==EMBER)||(at==SPARK&&bt==STONE)) damage=damage/2;
    }
    damage+=random_next(g)%3; return damage<1?1:damage;
}
static void apply_damage(Monster *m,int amount) { m->hp=amount>=m->hp?0:(u8)(m->hp-amount); }
static void award_xp(Game *g) {
    Monster *m=&g->save.roster[g->active];
    m->xp+=(u16)(g->enemy.level*8+12);
    if(m->xp>=m->level*20 && m->level<100) {
        m->xp-=m->level*20; m->level++; m->hp=(u8)game_max_hp(m);
        text_append(g->text," Level up!");
        if(m->level>=10 && species[m->species].evolve!=255) {
            m->species=species[m->species].evolve;
            g->save.caught|=1u<<m->species; g->save.seen|=1u<<m->species;
            m->hp=(u8)game_max_hp(m); text_append(g->text," Evolved!");
        }
    }
}
static void enemy_turn(Game *g) {
    Monster *m=&g->save.roster[g->active];
    if(!g->enemy.hp) return;
    if(g->enemy.status && random_next(g)%3==0) {
        text_append(g->text," Enemy is dazed!"); return;
    }
    int damage=game_damage(g,&g->enemy,m,(random_next(g)>>16)&1);
    apply_damage(m,damage); text_append(g->text," Enemy hits "); text_number(g->text,damage); text_append(g->text,".");
    if(!m->hp) {
        int next=game_party_alive(g);
        if(next<0) {
            game_heal(g); g->save.map=0; g->save.x=10; g->save.y=12;
            message(g,"RECOVERY","Your team rested at the Sunset clinic. Your monsters and quest progress are safe. Try again!",CLOSE);
        } else {
            g->active=(u8)next; g->focus=0; text_append(g->text," Next teammate joins!");
        }
    }
}
void game_choose_move(Game *g,u8 move) {
    if(move>3 || g->scene!=MOVES) return;
    Monster *m=&g->save.roster[g->active];
    if(!m->pp[move]) { g->scene=BATTLE; battle_message(g,"No uses left. Try another move or visit a clinic."); return; }
    m->pp[move]--; g->text[0]=0;
    if(move==2) { g->focus=1; text_copy(g->text,"Focused. Your next attack is stronger."); }
    else if(move==3) {
        int hp=m->hp+game_max_hp(m)/3; m->hp=(u8)(hp>game_max_hp(m)?game_max_hp(m):hp);
        text_copy(g->text,"Recovered health.");
    } else {
        int damage=game_damage(g,m,&g->enemy,move);
        if(g->focus) { damage=damage*3/2; g->focus=0; }
        apply_damage(&g->enemy,damage);
        text_copy(g->text,species[m->species].name); text_append(g->text," hits ");
        text_number(g->text,damage); text_append(g->text,"!");
        if(move==1 && random_next(g)%5==0) { g->enemy.status=1; text_append(g->text," Enemy dazed."); }
    }
    g->scene=BATTLE;
    if(!g->enemy.hp) {
        text_append(g->text," Won!"); award_xp(g); g->save.coins+=20;
        g->pending=1;
    } else enemy_turn(g);
    if(g->scene==BATTLE) g->message_open=1;
}
void game_capture(Game *g) {
    if(g->trainer) { battle_message(g,"You cannot capture a trainer's mini monster."); return; }
    if(!g->save.capsules) { battle_message(g,"No capsules. A clinic can resupply you."); return; }
    if(g->save.roster_count>=ROSTER_CAPACITY) { battle_message(g,"Storage is full. Release a stored duplicate outside battle."); return; }
    g->save.capsules--;
    int hp=game_max_hp(&g->enemy);
    int chance=30+(hp-g->enemy.hp)*70/hp+(g->enemy.status?20:0);
    if((int)(random_next(g)%100)<chance) {
        g->save.roster[g->save.roster_count++]=g->enemy;
        if(g->save.party_count<PARTY_CAPACITY) g->save.party_count++;
        g->save.caught|=1u<<g->enemy.species;
        text_copy(g->text,"Caught "); text_append(g->text,species[g->enemy.species].name);
        text_append(g->text,g->save.roster_count>6?"! Sent to storage.":"! Joined your team.");
        g->pending=2;
    } else {
        text_copy(g->text,"It escaped the capsule!"); enemy_turn(g);
    }
    if(g->scene==BATTLE) g->message_open=1;
}
static void resolve_battle(Game *g) {
    if(g->pending==1 && g->enemy_index+1<g->enemy_count) {
        g->enemy_index++; g->enemy=make_monster(g->enemy_team[g->enemy_index],8);
        g->save.seen|=1u<<g->enemy.species; g->pending=0;
        battle_message(g,"Scott sends his next mini monster!"); return;
    }
    if(g->pending==1 && g->trainer==2) {
        g->save.flags|=BADGE; g->save.coins+=200; game_heal(g); g->pending=0;
        message(g,"SCOTT WU","Build Badge earned! The prototype was hit by an external overclock signal. Follow the relays through SF. MVP complete - explore and collect all 12!",CLOSE);
    } else {
        if(g->trainer==1 && g->pending==1) g->save.flags|=TRAINER_WON;
        g->scene=WORLD; g->pending=0; g->message_open=0;
    }
}
static void interact(Game *g) {
    int x=g->save.x,y=g->save.y,map=g->save.map;
    if(map==0) {
        if(x>=8&&x<=12&&y>=6&&y<=9) {
            if(!(g->save.flags&QUEST_STARTED)) message(g,"KARPATHY","Roon dropped a prototype near Ocean Beach. Choose a companion, then find the glowing parcel on the sand. A to interact. Start opens your journal.",CHOOSE_STARTER);
            else { game_heal(g); if(g->save.capsules<6)g->save.capsules=6; message(g,"KARPATHY","Your team is healed. Training data: explore the grass and sand. Battle data: weaken monsters before throwing a capsule.",CLOSE); }
        } else if(x<=5&&y>=2&&y<=5) {
            if(g->save.flags&PROTOTYPE) message(g,"PARCEL","The ocean has stopped trying to deliver your parcel. Bring it to Roon by the beach.",CLOSE);
            else message(g,"DAMAGED PROTOTYPE","A humming parcel washes up. The nearby monsters flicker with a strange signal. This is definitely not normal fog.",PICKUP);
        } else if(x>=5&&x<=8&&y>=8&&y<=11) {
            if(!(g->save.flags&PROTOTYPE)) message(g,"ROON","My package has escaped into the coastal noosphere. Translation: look north, near the water.",CLOSE);
            else if(!(g->save.flags&COURIER_FOUND)) message(g,"ROON","You found it. Scott at Cognition can diagnose this. Take Muni from the stop east of here to SoMa. The company is in SF, unlike my directions.",FIND_COURIER);
            else if(!(g->save.flags&TRAINER_WON)) message(g,"ROON","Before you ship a prototype, test your team. A tiny benchmark battle?",TRAINER);
            else message(g,"ROON","Your team passed the vibe check. The damage points to something bigger than one startup. Next stop: SoMa.",CLOSE);
        } else if(x>=17&&x<=19&&y>=12&&y<=14) {
            if(g->save.flags&COURIER_FOUND) message(g,"MUNI","N Judah connection to downtown, then a walk to South Park. All destinations in this game are inside SF. A to travel.",TRANSIT);
            else message(g,"MUNI","Your delivery destination is still unknown. Recover the parcel and speak to Roon first.",CLOSE);
        } else message(g,"SUNSET","Ocean to the west. Startup drama to the east. The forecast is a playable amount of fog.",CLOSE);
    } else if(map==1) {
        if(x>=13&&x<=15&&y>=6&&y<=8) {
            g->save.map=2; g->save.x=11; g->save.y=14;
            message(g,"COGNITION","South Park, SoMa. Scott's lab is ahead. A courier delivery should probably not require a gym badge, but here we are.",CLOSE);
        } else if(x>=3&&x<=5&&y>=12&&y<=14) message(g,"MUNI","Return to Outer Sunset? Your team and progress travel with you.",TRANSIT);
        else if(x>=5&&x<=8&&y>=7&&y<=10) {
            game_heal(g); if(g->save.capsules<6)g->save.capsules=6;
            message(g,"PATIO11","The clinic is free. Someone finally found a business model that does not monetize recovery. Team healed, capsules resupplied.",CLOSE);
        } else if(x>=9&&x<=12&&y>=11&&y<=14) message(g,"JONATHAN LIU","I built a scheduler for dates. It turned out scheduling was not the main problem. 30 coins buys 5 capsules and 2 potions. A to buy.",SHOP);
        else message(g,"SOMA","Cognition is north of the central walkway. The South Park grass hides a different set of mini monsters.",CLOSE);
    } else {
        if(y>=14) { g->save.map=1; g->save.x=14; g->save.y=7; g->scene=WORLD; }
        else if(x<=6&&y>=5&&y<=7) { g->relay=RELAY_A; message(g,"SAFETY RELAY A","Enable the habitat monitor before the overclock circuit. A to restore the monitor.",RELAY); }
        else if(x>=16&&y>=9&&y<=11) { g->relay=RELAY_B; message(g,"SAFETY RELAY B","With monitoring restored, isolate the external signal. A to repair this relay.",RELAY); }
        else if(x>=9&&x<=13&&y<=4) {
            if(!(g->save.flags&DELIVERED)) message(g,"SCOTT WU","This is the habitat prototype. The fault is external. Restore relay A on the left, then B on the right. After that, test your team against mine.",DELIVERY);
            else if((g->save.flags&(RELAY_A|RELAY_B))!=(RELAY_A|RELAY_B)) message(g,"SCOTT WU","Repair the two relays first. Left monitor, then right isolation circuit. Ship safety before the demo.",CLOSE);
            else if(g->save.flags&BADGE) message(g,"SCOTT WU","You earned the Build Badge. Next chapter: find who overclocked the city. For now, finish your 12-entry field guide.",CLOSE);
            else message(g,"SCOTT WU","Relays stable. Let's see whether your team works outside the demo. A to challenge Cognition's gym.",GYM);
        } else message(g,"COGNITION","The prototype hums quietly. Two safety relays flank the lab. Scott waits at the north end.",CLOSE);
    }
}
static void close_talk(Game *g) {
    u8 action=g->action; g->scene=WORLD;
    if(action==CHOOSE_STARTER) { g->scene=STARTER; g->cursor=0; }
    if(action==PICKUP) g->save.flags|=PROTOTYPE;
    if(action==FIND_COURIER) g->save.flags|=COURIER_FOUND;
    if(action==SHOP) {
        if(g->save.coins>=30) { g->save.coins-=30; g->save.capsules+=5; g->save.potions+=2; }
        else message(g,"JONATHAN LIU","Bootstrapping means waiting until you have 30 coins. Win a few battles and come back.",CLOSE);
    }
    if(action==TRANSIT) {
        g->save.map=g->save.map?0:1; g->save.x=g->save.map?4:18; g->save.y=13;
    }
    if(action==DELIVERY) { g->save.flags|=DELIVERED; game_heal(g); }
    if(action==RELAY) {
        if(g->relay==RELAY_B && !(g->save.flags&RELAY_A)) message(g,"RELAY B","Restore the monitor first. Left relay A comes before right relay B.",CLOSE);
        else g->save.flags|=g->relay;
    }
    if(action==GYM) { game_heal(g); game_encounter(g,8,7,2); }
    if(action==TRAINER) game_encounter(g,3,5,1);
}
static void move_player(Game *g,int dx,int dy) {
    int x=g->save.x+dx,y=g->save.y+dy;
    g->save.facing=dx>0?3:dx<0?2:dy<0?1:0;
    u8 tile=game_tile(g->save.map,x,y);
    if(tile==2 || tile==4) return;
    g->save.x=(u8)x; g->save.y=(u8)y; g->save.steps++;
    if(!g->save.party_count || g->save.map==2 || (tile!=1&&tile!=3)) return;
    if((random_next(g)>>16)%6!=0) return;
    const u8 outer[]={0,1,2,3,4,6,7,8}; const u8 downtown[]={5,9,10,11,4,3};
    u8 id=g->save.map?downtown[(random_next(g)>>16)%6]:outer[(random_next(g)>>16)%8];
    game_encounter(g,id,(u8)(g->save.map?5+(random_next(g)>>16)%3:3+(random_next(g)>>16)%3),0);
}
void game_input(Game *g,u16 keys) {
    if(g->scene==TITLE) {
        if(keys&KEY_A) {
            if(g->have_save) g->scene=WORLD;
            else message(g,"KARPATHY","Welcome to the Sunset. You're a courier, not a chosen child. Roon misplaced a prototype at Ocean Beach. Let's get you a companion.",CHOOSE_STARTER);
        }
        return;
    }
    if(g->scene==STARTER) {
        if(keys&KEY_RIGHT)g->cursor=(g->cursor+1)%3;
        if(keys&KEY_LEFT)g->cursor=(g->cursor+2)%3;
        if(keys&KEY_A) {
            g->save.roster[0]=make_monster(g->cursor,5); g->save.roster_count=1; g->save.party_count=1;
            g->save.flags|=QUEST_STARTED; g->save.seen|=1u<<g->cursor; g->save.caught|=1u<<g->cursor;
            message(g,"KARPATHY","Companion ready. Find the parcel northwest on Ocean Beach, then speak to Roon southwest. Start opens your menu and journal.",CLOSE);
        }
        return;
    }
    if(g->scene==TALK) { if(keys&KEY_A) close_talk(g); if(keys&KEY_B) { if(g->action==GYM||g->action==SHOP||g->action==TRANSIT||g->action==TRAINER)g->scene=WORLD;else close_talk(g); } return; }
    if(g->scene==WORLD) {
        if(keys&KEY_START) { g->scene=MENU; g->cursor=0; return; }
        if(keys&KEY_A) { interact(g); return; }
        if(keys&KEY_RIGHT)move_player(g,1,0); else if(keys&KEY_LEFT)move_player(g,-1,0);
        else if(keys&KEY_UP)move_player(g,0,-1); else if(keys&KEY_DOWN)move_player(g,0,1);
        return;
    }
    if(g->scene==MENU) {
        if(keys&KEY_DOWN)g->cursor=(g->cursor+1)%5;
        if(keys&KEY_UP)g->cursor=(g->cursor+4)%5;
        if(keys&KEY_B)g->scene=WORLD;
        if(keys&KEY_A) {
            if(g->cursor==0) { g->scene=PARTY;g->cursor=0;g->party_mode=0; }
            else if(g->cursor==1) { g->scene=DEX;g->cursor=0; }
            else if(g->cursor==2)g->scene=JOURNAL;
            else if(g->cursor==3) { save_prepare(&g->save);g->have_save=1;message(g,"SAVE","Progress saved to cartridge memory. On the website, use Save backup before closing for a portable copy.",CLOSE); }
            else { if(g->save.potions && g->save.party_count) { g->save.potions--;game_heal(g);message(g,"BAG","Your team recovered. Capsules are used in wild battles. Clinics provide free healing.",CLOSE); } else message(g,"BAG","No potions left. Visit Karpathy or the SoMa clinic for free healing.",CLOSE); }
        }
        return;
    }
    if(g->scene==JOURNAL) { if(keys&(KEY_A|KEY_B|KEY_START))g->scene=MENU; return; }
    if(g->scene==DEX) {
        if(keys&(KEY_RIGHT|KEY_DOWN))g->cursor=(g->cursor+1)%SPECIES_COUNT;
        if(keys&(KEY_LEFT|KEY_UP))g->cursor=(g->cursor+SPECIES_COUNT-1)%SPECIES_COUNT;
        if(keys&KEY_B)g->scene=MENU;
        return;
    }
    if(g->scene==PARTY) {
        if(keys&KEY_DOWN)g->cursor=(g->cursor+1)%g->save.roster_count;
        if(keys&KEY_UP)g->cursor=(g->cursor+g->save.roster_count-1)%g->save.roster_count;
        if(keys&KEY_B)g->scene=g->party_mode?BATTLE:MENU;
        if(keys&KEY_A) {
            if(g->party_mode) {
                if(g->cursor<g->save.party_count && g->save.roster[g->cursor].hp) {
                    g->active=g->cursor;g->scene=BATTLE;g->focus=0;
                    text_copy(g->text,"Switched teammate.");enemy_turn(g);if(g->scene==BATTLE)g->message_open=1;
                }
            } else {
                Monster temp=g->save.roster[0];g->save.roster[0]=g->save.roster[g->cursor];g->save.roster[g->cursor]=temp;g->cursor=0;
            }
        }
        /* Stored duplicates can be released without touching the six-party slots. */
        if((keys&KEY_SELECT)&&!g->party_mode&&g->cursor>=g->save.party_count) {
            for(int i=g->cursor;i+1<g->save.roster_count;i++)g->save.roster[i]=g->save.roster[i+1];
            g->save.roster_count--;g->cursor=0;
        }
        return;
    }
    if(g->scene==MOVES) {
        if(keys&KEY_DOWN)g->cursor=(g->cursor+1)%4;
        if(keys&KEY_UP)g->cursor=(g->cursor+3)%4;
        if(keys&KEY_B) { g->scene=BATTLE;g->cursor=0; }
        if(keys&KEY_A)game_choose_move(g,g->cursor);
        return;
    }
    if(g->scene==BATTLE) {
        if(g->message_open) {
            if(keys&(KEY_A|KEY_B)) { g->message_open=0;if(g->pending)resolve_battle(g); }
            return;
        }
        if(keys&KEY_DOWN)g->cursor=(g->cursor+1)%5;
        if(keys&KEY_UP)g->cursor=(g->cursor+4)%5;
        if(keys&KEY_A) {
            if(g->cursor==0) { g->scene=MOVES;g->cursor=0; }
            else if(g->cursor==1)game_capture(g);
            else if(g->cursor==2) { g->scene=PARTY;g->party_mode=1;g->cursor=0; }
            else if(g->cursor==3) {
                if(g->save.potions) { g->save.potions--;g->save.roster[g->active].hp=(u8)game_max_hp(&g->save.roster[g->active]);text_copy(g->text,"Used a potion.");enemy_turn(g);if(g->scene==BATTLE)g->message_open=1; }
                else battle_message(g,"No potions left.");
            } else if(g->trainer)battle_message(g,"Finish the trainer battle. Your team can switch or use potions.");
            else { g->scene=WORLD;g->message_open=0; }
        }
    }
}
