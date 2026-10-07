#include "game.h"
#include "render.h"
#include "assets.h"
#define REG16(address) (*(volatile u16*)(address))
static const char save_type[] __attribute__((used)) = "SRAM_V113";
static Game game;
static Save disk, previous_disk;
static void read_save(void) {
    volatile const u8 *ram=(volatile const u8*)0x0e000000;
    u8 *out=(u8*)&disk;
    for(unsigned i=0;i<sizeof(Save);i++)out[i]=ram[i];
    out=(u8*)&previous_disk;
    for(unsigned i=0;i<sizeof(Save);i++)out[i]=ram[2048+i];
    if(save_valid(&previous_disk) && (!save_valid(&disk) ||
       (int)(previous_disk.sequence-disk.sequence)>0))disk=previous_disk;
}
static void write_save(void) {
    if(!game.save.party_count)return;
    save_prepare(&game.save);
    volatile u8 *ram=(volatile u8*)(0x0e000000+(game.save.sequence&1)*2048);
    const u8 *in=(const u8*)&game.save;
    /* Write magic last so interrupted writes are rejected. */
    for(int i=0;i<4;i++)ram[i]=0;
    for(unsigned i=4;i<sizeof(Save);i++)ram[i]=in[i];
    for(int i=0;i<4;i++)ram[i]=in[i];
}
static void tone(int frequency) {
    REG16(0x04000060)=0;
    REG16(0x04000062)=0x70b0;
    REG16(0x04000064)=(u16)(0xc000|frequency);
}
static void present(void) {
    volatile u16 *vram=(volatile u16*)0x06000000;
    const u16 *frame=(const u16*)framebuffer;
    for(int i=0;i<240*160/2;i++)vram[i]=frame[i];
}
int main(void) {
    (void)save_type;
    REG16(0x04000000)=0x0404;
    REG16(0x04000084)=0x0080;
    REG16(0x04000080)=0x1177;
    REG16(0x04000082)=0x0002;
    REG16(0x04000020)=256; REG16(0x04000022)=0;
    REG16(0x04000024)=0; REG16(0x04000026)=256;
    volatile u16 *palette=(volatile u16*)0x05000000;
    for(int i=0;i<256;i++)palette[i]=art_palette[i];
    /* A preserving write initializes SRAM auto-detection in GBA emulators. */
    volatile u8 *sram=(volatile u8*)0x0e000000;
    u8 tail=sram[32767];sram[32767]=tail;
    read_save();game_init(&game,&disk);game_render(&game);present();
    u16 previous=0;int repeat=0;
    for(;;) {
        while(REG16(0x04000006)>=160);
        while(REG16(0x04000006)<160);
        u16 held=(u16)(~REG16(0x04000130))&0x03ff;
        u16 pressed=held&~previous;
        if(held==previous&&held) {if(++repeat>=8){pressed=held&0x00f0;repeat=0;}}
        else repeat=0;
        previous=held;
        if(pressed) {
            u16 old_flags=game.save.flags;
            game_input(&game,pressed);
            if((game.save.flags&BADGE)&&!(old_flags&BADGE))tone(1900);
            else if(pressed&(KEY_A|KEY_START))tone(1750);
            if(game.scene==WORLD||game.scene==TALK||game.scene==MENU)write_save();
            game_render(&game);present();
        }
    }
}
