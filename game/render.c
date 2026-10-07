#include "render.h"
#include "assets.h"
#define font8x8_basic game_font
#include "../assets/font8x8_basic.h"

u8 framebuffer[240*160] __attribute__((aligned(4)));
static void pixel(int x,int y,u8 color) {
    if(x>=0&&x<240&&y>=0&&y<160)framebuffer[y*240+x]=color;
}
static void rect(int x,int y,int w,int h,u8 color) {
    for(int yy=y;yy<y+h;yy++)for(int xx=x;xx<x+w;xx++)pixel(xx,yy,color);
}
static void line(int x,int y,int w,u8 color) { rect(x,y,w,1,color); }
static void text(int x,int y,const char *s,u8 color) {
    int start=x;
    while(*s) {
        unsigned ch=(u8)*s++;
        if(ch=='\n') {y+=10;x=start;continue;}
        if(ch>=128)ch='?';
        for(int yy=0;yy<8;yy++)for(int xx=0;xx<7;xx++)
            if(game_font[ch][yy]&(1<<xx))pixel(x+xx,y+yy,color);
        x+=8;
    }
}
static void number(int x,int y,int value,u8 color) {
    char buf[12]={0};text_number(buf,value);text(x,y,buf,color);
}
static void wrapped(int x,int y,const char *s,int columns,int rows,u8 color) {
    int row=0,col=0;
    while(*s&&row<rows) {
        if(*s=='\n') {s++;row++;col=0;continue;}
        int len=0;while(s[len]&&s[len]!=' '&&s[len]!='\n')len++;
        if(col&&col+len>columns) {row++;col=0;if(row>=rows)break;}
        while(len--&&row<rows) {
            char c[2]={*s++,0};text(x+col*8,y+row*10,c,color);
            if(++col>=columns) {row++;col=0;}
        }
        if(*s==' ') {s++;if(col)col++;if(col>=columns){row++;col=0;}}
    }
}
static void sprite(int id,int x,int y,int scale) {
    if(id<0||id>=28)return;
    const u8 *data=art_pixels+art_offsets[id];
    for(int yy=0;yy<art_heights[id];yy++)for(int xx=0;xx<art_widths[id];xx++) {
        u8 color=data[yy*art_widths[id]+xx];
        if(color)rect(x+xx*scale,y+yy*scale,scale,scale,color);
    }
}
static int caught_count(const Game *g) {
    int n=0;for(int i=0;i<SPECIES_COUNT;i++)if(g->save.caught&(1<<i))n++;return n;
}
static void header(const char *name) { rect(0,0,240,16,1);text(8,4,name,3); }
static void footer(const char *hint) { rect(0,144,240,16,1);text(4,148,hint,4); }
static void panel(int x,int y,int w,int h) {
    rect(x,y,w,h,9);rect(x+1,y+1,w-2,h-2,1);
}
static void hp_bar(int x,int y,int hp,int max) {
    rect(x,y,64,4,9);rect(x,y,max?64*hp/max:0,4,hp>max/3?12:11);
}
static void world(const Game *g) {
    int cx=g->save.x-7,cy=g->save.y-4;
    if(cx<0)cx=0;
    if(cx>MAP_W-15)cx=MAP_W-15;
    if(cy<0)cy=0;
    if(cy>MAP_H-8)cy=MAP_H-8;
    for(int ty=0;ty<8;ty++)for(int tx=0;tx<15;tx++) {
        int x=tx*16,y=16+ty*16;
        u8 tile=game_tile(g->save.map,cx+tx,cy+ty);
        int art=tile==2?27:tile==3?24:tile==1?25:26;
        rect(x,y,16,16,tile==2?7:tile==3?8:tile==1?6:13);
        sprite(art,x,y,1);
        if(tile==4&&g->save.map==2) {rect(x,y,16,16,1);rect(x+2,y+2,12,10,14);}
        if(tile==5) {rect(x+3,y+1,10,15,10);text(x+4,y+4,"A",1);}
        if(tile==6) {rect(x+2,y+2,12,12,1);text(x+4,y+4,"M",10);}
        if(tile==7&&!(g->save.flags&PROTOTYPE)) {rect(x+4,y+3,8,10,10);rect(x+6,y+2,4,3,12);}
    }
    if(g->save.map==0) {
        sprite(20,(13-cx)*16,(3-cy)*16+16,1);
        sprite(21,(18-cx)*16,(4-cy)*16+16,1);
        sprite(17,(10-cx)*16,(8-cy)*16+8,1);
        sprite(18,(6-cx)*16,(9-cy)*16+8,1);
    } else if(g->save.map==1) {
        sprite(22,(12-cx)*16,(3-cy)*16+16,1);
        sprite(23,(4-cx)*16,(3-cy)*16+16,1);
        sprite(19,(6-cx)*16,(8-cy)*16+8,1);
        sprite(17,(10-cx)*16,(12-cy)*16+8,1);
    } else {
        sprite(16,(11-cx)*16,(2-cy)*16+8,1);
        rect((5-cx)*16,(6-cy)*16+16,16,16,g->save.flags&RELAY_A?12:11);
        rect((17-cx)*16,(10-cy)*16+16,16,16,g->save.flags&RELAY_B?12:11);
    }
    sprite(12+g->save.facing,(g->save.x-cx)*16,(g->save.y-cy)*16+8,1);
    header(map_names[g->save.map]);
    footer("A TALK   START MENU");
    if(g->save.flags&BADGE)text(192,4,"BADGE",10);
}
static void title(const Game *g) {
    rect(0,0,240,160,1);
    text(24,18,"SF MINI MONSTERS",3);
    text(52,34,"THE FOG SIGNAL",10);
    sprite(0,16,53,1);sprite(1,96,53,1);sprite(2,176,53,1);
    text(20,108,g->have_save?"A  CONTINUE DELIVERY":"A  START YOUR DELIVERY",2);
    text(32,127,"An original SF GBA game",4);
    text(40,145,"MVP / 12 mini monsters",4);
}
static void starters(const Game *g) {
    rect(0,0,240,160,1);header("CHOOSE YOUR COMPANION");
    for(int i=0;i<3;i++) {
        int x=i*80;
        if(g->cursor==i)panel(x+3,29,74,79);
        sprite(i,x+16,38,1);
        text(x+7,94,type_names[species[i].type],g->cursor==i?10:4);
    }
    text(8,118,species[g->cursor].name,3);
    footer("LEFT/RIGHT  A CHOOSE");
}
static void battle(const Game *g) {
    rect(0,16,240,128,3);
    rect(0,55,240,30,15);rect(0,85,240,25,6);
    sprite(g->enemy.species,164,29,1);
    sprite(g->save.roster[g->active].species,20,62,1);
    header(g->trainer==2?"COGNITION / SCOTT WU":g->trainer?"RIVAL / ROON":"WILD ENCOUNTER");
    text(8,23,species[g->enemy.species].name,1);
    text(8,35,"Lv",9);number(32,35,g->enemy.level,1);
    hp_bar(8,48,g->enemy.hp,game_max_hp(&g->enemy));
    const Monster *m=&g->save.roster[g->active];
    text(88,66,species[m->species].name,1);
    text(88,77,"Lv",9);number(112,77,m->level,1);
    number(152,77,m->hp,1);text(176,77,"/",9);number(184,77,game_max_hp(m),1);
    hp_bar(88,90,m->hp,game_max_hp(m));
    panel(2,101,236,57);
    if(g->message_open) {wrapped(8,106,g->text,28,4,3);text(216,147,"A",10);return;}
    const char *actions[]={"FIGHT","CAPTURE","SWITCH","POTION","RUN"};
    if(g->scene==MOVES) {
        for(int i=0;i<4;i++) {
            int x=8+(i%2)*116,y=108+(i/2)*20;
            text(x,y,i==g->cursor?">":" ",10);text(x+8,y,move_names[i],i==g->cursor?10:3);
            number(x+88,y+9,m->pp[i],4);
        }
    } else {
        for(int i=0;i<5;i++) {
            int x=8+(i%3)*76,y=108+(i/3)*17;
            text(x,y,i==g->cursor?">":" ",10);text(x+8,y,actions[i],i==g->cursor?10:3);
        }
        text(8,145,"UP/DOWN SELECT  A CONFIRM",4);
    }
}
static void dialogue(const Game *g) {
    world(g);panel(3,23,234,117);
    text(10,29,g->speaker,10);line(10,40,220,9);
    wrapped(10,47,g->text,27,8,3);
    text(188,129,"A NEXT",10);
}
static void menu(const Game *g) {
    world(g);panel(54,21,181,121);
    const char *items[]={"TEAM / STORAGE","FIELD GUIDE","QUEST JOURNAL","SAVE GAME","POTION / HEAL"};
    for(int i=0;i<5;i++) {text(62,30+i*19,i==g->cursor?">":" ",10);text(74,30+i*19,items[i],i==g->cursor?10:3);}
    footer("A SELECT   B BACK");
}
static void party(const Game *g) {
    rect(0,0,240,160,1);header("TEAM / STORAGE");
    int first=g->cursor>5?g->cursor-5:0;
    for(int n=0;n<7&&first+n<g->save.roster_count;n++) {
        int i=first+n,y=24+n*15;const Monster *m=&g->save.roster[i];
        text(4,y,i==g->cursor?">":" ",10);
        text(16,y,species[m->species].name,i==g->cursor?10:3);
        number(112,y,m->level,4);number(144,y,m->hp,12);
        text(182,y,i<g->save.party_count?"TEAM":"BOX",4);
    }
    footer(g->party_mode?"A SWITCH   B BACK":"A LEAD  SELECT RELEASE BOX");
}
static void dex(const Game *g) {
    rect(0,0,240,160,1);header("MINI MONSTER FIELD GUIDE");
    int id=g->cursor;int seen=g->save.seen&(1<<id);
    sprite(id,12,28,1);number(80,25,id+1,10);
    text(80,39,seen?species[id].name:"UNDISCOVERED",3);
    text(80,54,seen?type_names[species[id].type]:"???",4);
    text(80,70,g->save.caught&(1<<id)?"CAUGHT":seen?"SEEN":"???",12);
    if(seen)wrapped(10,91,species[id].description,27,4,3);
    text(8,132,"CAUGHT",4);number(64,132,caught_count(g),10);text(80,132,"/12",4);
    footer("LEFT/RIGHT BROWSE  B BACK");
}
static void journal(const Game *g) {
    rect(0,0,240,160,1);header("COURIER JOURNAL");
    const char *next;
    if(!(g->save.flags&PROTOTYPE))next="Find the glowing parcel on Ocean Beach, northwest of your starting point.";
    else if(!(g->save.flags&COURIER_FOUND))next="Return the parcel to Roon near the sand. His directions are better than his posts.";
    else if(!(g->save.flags&DELIVERED))next="Take Muni at the east Sunset stop to SoMa. Enter Cognition north of South Park.";
    else if(!(g->save.flags&RELAY_A))next="Restore the left safety relay in Cognition's lab.";
    else if(!(g->save.flags&RELAY_B))next="Restore the right isolation relay after the monitor is running.";
    else if(!(g->save.flags&BADGE))next="Challenge Scott at the north of the lab. Heal your team and bring potions.";
    else next="Build Badge earned. An external overclock signal is affecting SF. MVP complete! Explore and catch all 12.";
    wrapped(10,26,next,27,8,3);
    text(10,112,"COINS",4);number(66,112,g->save.coins,10);
    text(10,124,"CAPSULES",4);number(82,124,g->save.capsules,10);
    text(124,124,"POTIONS",4);number(192,124,g->save.potions,10);
    footer("A/B BACK");
}
void game_render(const Game *g) {
    if(g->scene==TITLE)title(g);
    else if(g->scene==STARTER)starters(g);
    else if(g->scene==WORLD)world(g);
    else if(g->scene==TALK)dialogue(g);
    else if(g->scene==BATTLE||g->scene==MOVES)battle(g);
    else if(g->scene==PARTY)party(g);
    else if(g->scene==DEX)dex(g);
    else if(g->scene==JOURNAL)journal(g);
    else menu(g);
}
