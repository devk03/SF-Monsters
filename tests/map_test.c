#include <assert.h>
#include <stdio.h>
#include "../game/game.h"
static int reachable(int map,int startx,int starty,int targetx,int targety) {
    int qx[MAP_W*MAP_H],qy[MAP_W*MAP_H],head=0,tail=0;
    unsigned char seen[MAP_W*MAP_H]={0};
    qx[tail]=startx;qy[tail++]=starty;seen[starty*MAP_W+startx]=1;
    while(head<tail) {
        int x=qx[head],y=qy[head++];if(x==targetx&&y==targety)return 1;
        const int dx[]={1,-1,0,0},dy[]={0,0,1,-1};
        for(int i=0;i<4;i++) {
            int nx=x+dx[i],ny=y+dy[i];
            if(nx<0||nx>=MAP_W||ny<0||ny>=MAP_H)continue;
            int tile=game_tile(map,nx,ny),index=ny*MAP_W+nx;
            if(tile==2||tile==4||seen[index])continue;
            seen[index]=1;qx[tail]=nx;qy[tail++]=ny;
        }
    }
    return 0;
}
int main(void) {
    assert(reachable(0,10,12,4,3));
    assert(reachable(0,4,3,6,9));
    assert(reachable(0,6,9,18,13));
    assert(reachable(1,4,13,14,7));
    assert(reachable(1,14,7,6,8));
    assert(reachable(1,4,13,18,10));
    assert(reachable(2,11,14,11,2));
    assert(reachable(2,11,2,5,6));
    assert(reachable(2,5,6,17,10));
    assert(reachable(2,17,10,11,2));
    assert(reachable(2,11,2,11,15));
    puts("PASS: quest locations, clinics, wild habitats, and both gym relays are reachable");
}
