#ifndef SF_GAME_H
#define SF_GAME_H

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
#define SPECIES_COUNT 12
#define ROSTER_CAPACITY 32
#define PARTY_CAPACITY 6
#define MAP_W 24
#define MAP_H 18
#define KEY_A 1
#define KEY_B 2
#define KEY_SELECT 4
#define KEY_START 8
#define KEY_RIGHT 16
#define KEY_LEFT 32
#define KEY_UP 64
#define KEY_DOWN 128
#define KEY_R 256
#define KEY_L 512

enum { TITLE, STARTER, WORLD, TALK, BATTLE, MOVES, PARTY, DEX, JOURNAL, MENU };
enum { TIDE, BLOOM, EMBER, FOG, SHADE, SPARK, STONE, ECHO };
enum { QUEST_STARTED=1, PROTOTYPE=2, COURIER_FOUND=4, DELIVERED=8,
       RELAY_A=16, RELAY_B=32, BADGE=64, TRAINER_WON=128 };
enum { CLOSE, CHOOSE_STARTER, FIND_COURIER, PICKUP, HEAL, SHOP,
       TRANSIT, DELIVERY, RELAY, GYM, TRAINER };

typedef struct {
    const char *name;
    const char *description;
    u8 type, hp, attack, defense, speed, evolve;
} Species;
typedef struct { u8 species, level, hp, pp[4], status; u16 xp; } Monster;
typedef struct {
    u32 magic, version, checksum, sequence, rng;
    u16 flags, seen, caught, coins, steps;
    u8 map, x, y, facing, roster_count, party_count, capsules, potions;
    Monster roster[ROSTER_CAPACITY];
} Save;
typedef struct {
    Save save;
    u8 scene, previous_scene, cursor, dex_page, party_mode, active;
    u8 trainer, enemy_index, enemy_count, action, relay, pending, have_save;
    u8 message_open, enemy_team[3], focus;
    Monster enemy;
    char text[256], speaker[32];
} Game;

extern const Species species[SPECIES_COUNT];
extern const char *type_names[8];
extern const char *map_names[3];
extern const char *move_names[4];
void game_init(Game *g, const Save *saved);
void game_input(Game *g, u16 keys);
void game_encounter(Game *g, u8 id, u8 level, u8 trainer);
void game_choose_move(Game *g, u8 move);
void game_capture(Game *g);
void game_heal(Game *g);
u8 game_tile(u8 map, int x, int y);
int game_max_hp(const Monster *m);
int game_damage(Game *g, const Monster *a, const Monster *b, int move);
u32 save_checksum(const Save *s);
int save_valid(const Save *s);
void save_prepare(Save *s);
int game_party_alive(const Game *g);
void text_copy(char *out, const char *in);
void text_append(char *out, const char *in);
void text_number(char *out, int value);
#endif
