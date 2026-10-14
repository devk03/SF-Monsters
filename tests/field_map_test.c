// Production SF opener against independent native allocation/callback contracts.
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef uint8_t bool8;
#define TRUE 1
#define FALSE 0
#define _(s) s
static bool8 authored=TRUE, memoryAvailable=TRUE;
static int allocations, vblankChanges, mainChanges;
static void ReturnToMenu(void) {}
static void MCB2_InitRegionMapRegisters(void) {}
static void (*mainCallback)(void);
static bool8 SFMapUsesAuthoredLayout(void) {return authored;}
static const u8 gText_Hoenn[]="HOENN";
static struct Handler {void (*callback)(void);unsigned unused;unsigned char regionMap[0x884];unsigned state;} memory;
static struct Handler *sFieldRegionMapHandler;
static void *Alloc(unsigned long size) {
    assert(size==sizeof(memory));allocations++;
    return memoryAvailable?&memory:NULL;
}
static void SetVBlankCallback(void (*callback)(void)) {assert(callback==NULL);vblankChanges++;}
static void SetMainCallback2(void (*callback)(void)) {mainCallback=callback;mainChanges++;}
#include "../romhack/engine/field_map.h"

int main(void) {
    assert(strcmp((const char *)SFFieldMapTitle(),"SF MAP")==0);
    assert(strlen((const char *)SFFieldMapTitle())<=7);
    authored=FALSE;
    assert(SFFieldMapTitle()==gText_Hoenn);
    assert(!SFTryOpenFieldMap(ReturnToMenu) && allocations==0);
    authored=TRUE;
    assert(!SFTryOpenFieldMap(NULL) && allocations==0);
    memoryAvailable=FALSE;
    assert(!SFTryOpenFieldMap(ReturnToMenu));
    assert(sFieldRegionMapHandler==NULL && vblankChanges==0 && mainChanges==0);
    memoryAvailable=TRUE;memory.state=99;
    assert(SFTryOpenFieldMap(ReturnToMenu));
    assert(sFieldRegionMapHandler==&memory && memory.state==0 && memory.callback==ReturnToMenu);
    assert(mainCallback==MCB2_InitRegionMapRegisters && vblankChanges==1 && mainChanges==1);
    assert(!SFTryOpenFieldMap(ReturnToMenu) && allocations==2 && mainChanges==1);
    puts("SF map: local title, native return callback, allocation failure and reentry guards passed.");
}
