#include "game.h"

const char *type_names[8] = {"TIDE","BLOOM","EMBER","FOG","SHADE","SPARK","STONE","ECHO"};
const char *map_names[3] = {"OUTER SUNSET", "SOMA / SOUTH PARK", "COGNITION LAB"};
const char *move_names[4] = {"TACKLE", "TYPE BURST", "FOCUS", "RECOVER"};
/* IDs are persistent save identities. Append new entries; never reorder them. */
const Species species[SPECIES_COUNT] = {
    {"BRINEPUP", "A sea-lion pup. Its favorite beach is whichever one has snacks.", TIDE, 28, 11, 9, 9, 255},
    {"SPROUTSLUG", "This garden slug dreams of flying. It evolves at level 10.", BLOOM, 30, 9, 11, 7, 7},
    {"CINDERCOY", "A tiny coyote that insists the Sunset is actually quite warm.", EMBER, 26, 13, 8, 12, 255},
    {"FOGGEON", "The forecast is pigeon. Carries its own personal microclimate.", FOG, 25, 10, 9, 13, 255},
    {"BINBANDIT", "This raccoon calls its dumpster a vertically integrated habitat.", SHADE, 29, 11, 11, 8, 255},
    {"TRAMBUG", "An electric beetle. Will become a Neonettle at level 10.", SPARK, 24, 12, 8, 14, 10},
    {"KELPCLAW", "A tide-pool crab. Has never agreed to share its seaweed.", TIDE, 30, 10, 13, 6, 255},
    {"BLOOMWING", "A flower moth that pollinates startups and actual plants.", BLOOM, 34, 14, 11, 15, 255},
    {"CRUSTHOG", "A sourdough hedgehog. Its starter is older than your startup.", STONE, 33, 10, 14, 5, 255},
    {"ECHOBAT", "A musical bat. Sound checks count as networking events.", ECHO, 26, 12, 8, 14, 255},
    {"NEONETTLE", "A jellyfish with electric lights and no subscription plan.", SPARK, 32, 15, 10, 15, 255},
    {"MISTFIN", "A little fog manta. Something much larger stirs in its dreams.", FOG, 32, 12, 12, 12, 255}
};

/* 0 sidewalk, 1 grass, 2 ocean, 3 sand, 4 building, 5 door, 6 transit, 7 relic. */
u8 game_tile(u8 map, int x, int y) {
    if(x<0 || x>=MAP_W || y<0 || y>=MAP_H) return 4;
    if(map==0) {
        if(x<3) return 2;
        if(x==4 && y==3) return 7;
        if(x==18 && y==13) return 6;
        if(x>=13 && x<=15 && y>=3 && y<=5) return 4;
        if(x>=18 && x<=20 && y>=4 && y<=6) return 4;
        if(x<=7) return 3;
        if(x==10 || x==11 || y==12 || y==13) return 0;
        return 1;
    }
    if(map==1) {
        if(x>=22) return 2;
        if(x==4 && y==13) return 6;
        if(x==14 && y==6) return 5;
        if(x>=12 && x<=16 && y>=3 && y<=5) return 4;
        if(x>=4 && x<=6 && y>=3 && y<=5) return 4;
        if(x>=17 && y>=8 && y<=12) return 1;
        return 0;
    }
    if(x==11 && y==15) return 5;
    if(x==0 || y==0 || x==23 || y==17) return 4;
    if((y==4 || y==8) && x>=5 && x<=17 && x!=11) return 4;
    return 0;
}
