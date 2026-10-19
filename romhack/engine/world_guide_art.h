// Original SF region map: native relief, broad corridors and beveled towns.
#include "constants/rgb.h"
#include "palette.h"
#include "sf_world_guide_pixels.h"

static void SFGuideRouteSegment(u8 x,u8 y,u8 toX,u8 toY,u8 border,u8 fill)
{
    u8 left=x<toX?x:toX,top=y<toY?y:toY;
    u8 width=x<toX?toX-x+1:x-toX+1,height=y<toY?toY-y+1:y-toY+1;
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(border),left-2,top-2,width+4,height+4);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(fill),left-1,top-1,width+2,height+2);
}

static void SFGuideRoute(const struct SFGuideEdge *edge)
{
    u8 n;
    bool8 locked=edge->badge && !FlagGet(FLAG_BADGE01_GET+edge->badge-1);
    u8 border=edge->water?12:10,fill=edge->water?(locked?4:13):11;
    for (n=1;n<edge->count;n++)
        SFGuideRouteSegment(edge->points[n-1][0],edge->points[n-1][1],
                            edge->points[n][0],edge->points[n][1],border,fill);
}

static void SFGuideTown(u8 x,u8 y,bool8 gym)
{
    // Nine-by-seven native marker with a dark rim, pale bevel and colored core.
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),x-3,y-3,7,7);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(2),x-4,y-2,9,5);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(1),x-3,y-2,7,5);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(gym?14:4),x-2,y-1,5,3);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(15),x-2,y-1,2,1);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(gym?10:12),x+2,y,1,2);
}

static void SFGuideCursor(u8 x,u8 y)
{
    u8 left=x-7,right=x+5,top=y-5,bottom=y+3;
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
