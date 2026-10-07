/* Navigation data for controller-only emulator acceptance checks. */
#include <stdio.h>
#include "../game/game.h"
int main(void) {
    printf("local maps = {\n");
    for(int m=0;m<3;m++) {
        printf("{\n");
        for(int y=0;y<MAP_H;y++) {
            printf("{");
            for(int x=0;x<MAP_W;x++)printf("%d,",game_tile(m,x,y));
            printf("},\n");
        }
        printf("},\n");
    }
    printf("}\n");return 0;
}
