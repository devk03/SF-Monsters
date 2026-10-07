/* Native cartridge layout fixture exercises the browser boundary, not a JS mock. */
#include <stdio.h>
#include "../game/game.h"
int main(int argc,char **argv) {
    if(argc!=2)return 1;
    Game g;game_init(&g,0);
    game_input(&g,KEY_A);game_input(&g,KEY_A);game_input(&g,KEY_A);game_input(&g,KEY_A);
    g.save.coins=222;g.save.flags|=PROTOTYPE;save_prepare(&g.save);
    unsigned char ram[32768]={0};
    const unsigned char *src=(const unsigned char*)&g.save;
    for(unsigned i=0;i<sizeof(Save);i++)ram[2048+i]=src[i];
    FILE *file=fopen(argv[1],"wb");if(!file)return 1;
    fwrite(ram,1,sizeof(ram),file);fclose(file);return 0;
}
