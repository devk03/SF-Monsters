// Original SF region map: native relief, broad corridors and beveled towns.
#include "constants/rgb.h"
#include "palette.h"
#include "sf_world_guide_pixels.h"

static void SFGuideRouteSegment(u8 x0,u8 y0,u8 x1,u8 y1,u8 color,u8 width,bool8 dashed)
{
    s16 x=x0,y=y0,dx=x1>x0?x1-x0:x0-x1,dy=y1>y0?y1-y0:y0-y1;
    s16 sx=x0<x1?1:-1,sy=y0<y1?1:-1,error=dx-dy,e2;
    u16 n=0;
    for (;;)
    {
        if (!dashed || n%5<2)
            FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(color),x-width/2,y-width/2,width,width);
        if (x==x1 && y==y1) break;
        e2=error*2;
        if (e2>-dy) {error-=dy;x+=sx;}
        if (e2<dx) {error+=dx;y+=sy;}
        n++;
    }
}

static void SFGuideRoute(const struct SFGuideEdge *edge)
{
    u8 n;
    bool8 locked=edge->badge && !FlagGet(FLAG_BADGE01_GET+edge->badge-1);
    for (n=1;n<edge->count;n++)
    {
        u8 x=edge->points[n-1][0],y=edge->points[n-1][1];
        u8 toX=edge->points[n][0],toY=edge->points[n][1];
        if (edge->water)
            SFGuideRouteSegment(x,y,toX,toY,locked?5:13,2,TRUE);
        else
        {
            SFGuideRouteSegment(x,y,toX,toY,10,3,FALSE);
            SFGuideRouteSegment(x,y,toX,toY,11,1,FALSE);
        }
    }
}

static void SFGuideTown(u8 x,u8 y,bool8 gym)
{
    if (gym)
    {
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),x-3,y-3,7,7);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),x-4,y-2,9,5);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(1),x-3,y-2,7,5);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(14),x-2,y-1,5,3);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),x-2,y-1,2,1);
    }
    else
    {
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),x-2,y-2,5,5);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(1),x-1,y-1,3,3);
        FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(5),x,y,1,1);
    }
}

static void SFGuideCursor(u8 x,u8 y)
{
    u8 left=x-6,right=x+4,top=y-5,bottom=y+3;
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),left-1,top-1,4,4);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),right,top-1,4,4);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),left-1,bottom,4,4);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),right,bottom,4,4);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),left,top,3,1);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),left,top,1,3);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),right,top,3,1);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),right+2,top,1,3);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),left,bottom+2,3,1);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),left,bottom,1,3);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),right,bottom+2,3,1);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),right+2,bottom,1,3);
}

static void SFGuidePlayerPin(u8 x,u8 y)
{
    // Tiny original cap/head marker above the actual player location.
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),x-2,y-11,5,6);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(14),x-1,y-10,3,2);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(1),x-1,y-8,3,2);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),x,y-5,1,2);
}

static void SFGuideMapArt(void)
{
    u8 i;
    // Copy complete tiles, avoiding thousands of per-pixel native draw calls.
    CopyToWindowPixelBuffer(sSFGuideWindow,sSFGuideRelief,sizeof(sSFGuideRelief),56);
    for (i=0;i<ARRAY_COUNT(sSFGuideEdges);i++) SFGuideRoute(&sSFGuideEdges[i]);
    for (i=0;i<ARRAY_COUNT(sSFGuidePlaces);i++)
        SFGuideTown(sSFGuidePlaces[i].x,sSFGuidePlaces[i].y,sSFGuidePlaces[i].gym);
    SFGuidePlayerPin(sSFGuideHereX,sSFGuideHereY);
    SFGuideCursor(sSFGuidePlaces[sSFGuideSelected].x,sSFGuidePlaces[sSFGuideSelected].y);
}
