#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../game/game.h"

static void start(Game *g, int starter) {
    game_init(g,0);
    game_input(g,KEY_A);
    game_input(g,KEY_A);
    assert(g->scene==STARTER);
    for(int i=0;i<starter;i++)game_input(g,KEY_RIGHT);
    game_input(g,KEY_A);
    game_input(g,KEY_A);
    assert(g->scene==WORLD);
}
static void finish_message(Game *g) {
    assert(g->scene==TALK);
    game_input(g,KEY_A);
}
static void save_round_trip(void) {
    Game a,b;
    start(&a,2);
    a.save.flags|=PROTOTYPE|COURIER_FOUND;
    a.save.coins=222;
    a.save.map=1;a.save.x=4;a.save.y=13;
    save_prepare(&a.save);
    unsigned char bytes[sizeof(Save)];
    memcpy(bytes,&a.save,sizeof(Save));
    Save disk;
    memcpy(&disk,bytes,sizeof(Save));
    assert(save_valid(&disk));
    game_init(&b,&disk);
    game_input(&b,KEY_A);
    assert(b.scene==WORLD&&b.save.coins==222&&b.save.map==1);
    assert(b.save.roster[0].species==2);
    assert(b.save.flags&COURIER_FOUND);
    bytes[sizeof(Save)-1]^=1;
    memcpy(&disk,bytes,sizeof(Save));
    assert(!save_valid(&disk));
    disk=a.save;disk.version=2;disk.checksum=save_checksum(&disk);
    assert(!save_valid(&disk));
    disk=a.save;disk.roster[0].species=SPECIES_COUNT;disk.checksum=save_checksum(&disk);
    assert(!save_valid(&disk));
    disk=a.save;disk.party_count=7;disk.checksum=save_checksum(&disk);
    assert(!save_valid(&disk));
}
static void quest_order(void) {
    Game g;
    start(&g,0);
    g.save.x=18;g.save.y=13;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.save.map==0);
    g.save.x=4;g.save.y=3;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.save.flags&PROTOTYPE);
    g.save.x=6;g.save.y=9;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.save.flags&COURIER_FOUND);
    g.save.x=18;g.save.y=13;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.save.map==1);
    g.save.x=14;g.save.y=7;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.save.map==2);
    g.save.x=11;g.save.y=2;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.save.flags&DELIVERED);
    g.save.x=17;g.save.y=10;
    game_input(&g,KEY_A);finish_message(&g);finish_message(&g);
    assert(!(g.save.flags&RELAY_B));
    g.save.x=5;g.save.y=6;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.save.flags&RELAY_A);
    g.save.x=17;g.save.y=10;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.save.flags&RELAY_B);
    g.save.x=11;g.save.y=2;
    game_input(&g,KEY_A);finish_message(&g);
    assert(g.scene==BATTLE&&g.trainer==2&&g.enemy_count==3);
}
static void collection_and_storage(void) {
    Game g;
    start(&g,0);
    g.save.capsules=100;
    for(int id=0;id<SPECIES_COUNT;id++) {
        game_encounter(&g,(u8)id,3,0);
        g.enemy.hp=1;g.enemy.status=1;
        game_capture(&g);
        assert(g.pending==2);
        game_input(&g,KEY_A);
        assert(g.scene==WORLD);
    }
    assert(g.save.caught==0xfff);
    assert(g.save.party_count==6&&g.save.roster_count==13);
    game_encounter(&g,2,3,2);
    int before=g.save.capsules;
    game_capture(&g);
    assert(g.save.capsules==before&&g.save.roster_count==13);
    g.scene=PARTY;g.party_mode=0;g.cursor=9;
    int stored=g.save.roster[9].species;
    game_input(&g,KEY_A);
    assert(g.save.roster[0].species==stored&&g.save.party_count==6);
}
static void gym_completion_and_recovery(void) {
    Game g;
    start(&g,0);
    /* A late-level team is a legitimate obtainable counter to early bosses. */
    g.save.roster[0].level=40;
    game_heal(&g);
    game_encounter(&g,8,7,2);
    for(int turn=0;turn<40 && !(g.save.flags&BADGE);turn++) {
        if(g.scene==BATTLE&&g.message_open)game_input(&g,KEY_A);
        else if(g.scene==BATTLE) {g.cursor=0;game_input(&g,KEY_A);}
        else if(g.scene==MOVES)game_input(&g,KEY_A);
    }
    assert(g.save.flags&BADGE);
    finish_message(&g);
    assert(g.scene==WORLD&&g.save.roster[0].hp==game_max_hp(&g.save.roster[0]));
    g.save.roster[0].level=1;g.save.roster[0].hp=1;
    game_encounter(&g,10,30,0);
    g.scene=MOVES;game_choose_move(&g,2);
    assert(g.scene==TALK&&g.save.map==0);
    finish_message(&g);
    assert(g.save.flags&BADGE);
    assert(g.save.roster[0].hp>0);
}
int main(void) {
    for(int i=0;i<3;i++) {Game g;start(&g,i);assert(g.save.roster[0].species==i);}
    save_round_trip();
    quest_order();
    collection_and_storage();
    gym_completion_and_recovery();
    puts("PASS: starters, save integrity, quest gates, all 12 entries, storage, gym completion, recovery");
    return 0;
}
