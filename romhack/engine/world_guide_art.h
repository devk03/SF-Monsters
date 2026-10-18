// Original native city-map artwork. All coordinates are window pixels.
#include "constants/rgb.h"
#include "palette.h"

static const u8 sSFGuideAngelLabel[] = _("ANGEL");
static const u8 sSFGuideTreasureLabel[] = _("TREASURE");
static const u8 sSFGuideOcean[] = _("OCEAN");
static const u8 sSFGuideBay[] = _("BAY");
static const u8 sSFGuideWalk[] = _("walk");
static const u8 sSFGuideWater[] = _("water");
static const u8 sSFGuideLocked[] = _("locked");
static const u8 sSFGuideHere[] = _("here");

static const u16 sSFGuidePalette[16] = {
    RGB(0,0,0), RGB(30,30,29), RGB(7,10,12), RGB(20,22,22),
    RGB(13,20,27), RGB(11,17,24), RGB(26,27,23), RGB(16,21,14),
    RGB(10,16,10), RGB(23,24,21), RGB(9,14,16), RGB(16,16,15),
    RGB(26,29,31), RGB(23,17,12), RGB(27,10,8), RGB(31,23,6)
};
struct SFGuidePoint { s16 x,y; };
static const struct SFGuidePoint sSFGuideCoast[] = {
    {29,48},{42,40},{62,40},{76,42},{96,36},{112,35},{131,40},
    {144,49},{147,62},{150,76},{157,94},{153,112},{31,112},
    {28,94},{29,74},{26,59}
};
static const struct SFGuidePoint sSFGuideAngel[] = {
    {163,35},{169,30},{180,31},{188,37},{183,43},{165,43}
};
static const struct SFGuidePoint sSFGuideTreasure[] = {
    {168,61},{185,59},{190,70},{181,77},{164,73}
};

static void SFGuidePolygon(const struct SFGuidePoint *p,u8 count,u8 color)
{
    s16 y,x,hits[20];u8 i,j,n;
    for (y=29;y<=112;y++)
    {
        n=0;
        for (i=0;i<count;i++)
        {
            j=(i+1)%count;
            if ((p[i].y<=y && p[j].y>y)||(p[j].y<=y && p[i].y>y))
                hits[n++]=p[i].x+(y-p[i].y)*(p[j].x-p[i].x)/(p[j].y-p[i].y);
        }
        for (i=0;i<n;i++)
            for (j=i+1;j<n;j++)
                if (hits[j]<hits[i]) {x=hits[i];hits[i]=hits[j];hits[j]=x;}
        for (i=0;i+1<n;i+=2)
            FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(color),hits[i],y,hits[i+1]-hits[i]+1,1);
    }
    for (i=0;i<count;i++)
        SFGuideLine(p[i].x,p[i].y,p[(i+1)%count].x,p[(i+1)%count].y,10,FALSE);
}

static void SFGuideMapArt(void)
{
    u8 x;
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(4),4,29,216,84);
    // Small ocean ripples distinguish water without obscuring bay crossings.
    for (x=7;x<216;x+=23)
    {
        SFGuideLine(x,54,x+5,54,5,FALSE);
        SFGuideLine(x+3,92,x+8,92,5,FALSE);
    }
    SFGuidePolygon(sSFGuideCoast,ARRAY_COUNT(sSFGuideCoast),6);
    SFGuidePolygon(sSFGuideAngel,ARRAY_COUNT(sSFGuideAngel),6);
    SFGuidePolygon(sSFGuideTreasure,ARRAY_COUNT(sSFGuideTreasure),6);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(7),41,44,34,12);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(7),31,63,53,9);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(8),34,66,44,2);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(7),169,34,10,6);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(7),172,64,10,8);
    SFGuideLine(38,87,145,87,9,FALSE);
    SFGuideLine(41,97,137,55,9,FALSE); // Market's diagonal through the grid.
    SFGuideLine(79,50,79,109,9,FALSE);
    SFGuideLine(113,43,113,109,9,FALSE);
    SFGuideLine(37,76,146,76,9,FALSE);
    // The bridge and western hills are landmarks, not additional map exits.
    SFGuideLine(49,30,54,42,14,FALSE);
    SFGuideLine(51,30,56,42,14,FALSE);
    SFGuideLine(48,30,52,30,14,FALSE);
    SFGuideLine(52,41,57,41,14,FALSE);
    SFGuideLine(49,31,54,40,1,FALSE);
    SFGuideLine(58,103,62,95,8,FALSE);
    SFGuideLine(62,95,66,103,8,FALSE);
    SFGuideLine(39,105,39,99,10,FALSE);
    SFGuideLine(36,101,42,101,10,FALSE);
    SFGuideAt(sSFGuideOcean,4,91,sSFGuideWaterInk);
    SFGuideAt(sSFGuideBay,193,98,sSFGuideWaterInk);
    SFGuideAt(sSFGuideAngelLabel,165,44,sSFGuideWaterInk);
    SFGuideAt(sSFGuideTreasureLabel,163,78,sSFGuideWaterInk);
    SFGuideLine(8,121,17,121,11,FALSE);
    SFGuideAt(sSFGuideWalk,21,115,sSFGuideInk);
    SFGuideLine(62,121,71,121,12,TRUE);
    SFGuideAt(sSFGuideWater,75,115,sSFGuideInk);
    SFGuideLine(120,121,129,121,13,TRUE);
    SFGuideAt(sSFGuideLocked,133,115,sSFGuideInk);
    FillWindowPixelRect(sSFGuideWindow,PIXEL_FILL(14),181,119,4,4);
    SFGuideAt(sSFGuideHere,190,115,sSFGuideInk);
}
