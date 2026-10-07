#ifndef SF_RENDER_H
#define SF_RENDER_H
#include "game.h"
extern u8 framebuffer[240*160];
void game_render(const Game *g);
#endif
