// Visual camera padding only. Field collision and map connections stay native.
#ifndef SF_COASTAL_BORDER_H
#define SF_COASTAL_BORDER_H

static int SFCoastalBorderGraphic(int x, int y, int width, int height)
{
    // Native map coordinates include a seven-cell camera margin.
    if (x >= 7 && x < width + 7 && y >= 7 && y < height + 7)
        return -1;
    // Continue the authored west-to-east ocean / surf / dune / lawn strips.
    if (x < 10)
        return 574;
    if (x == 10)
        return 575;
    if (x < 16)
        return 573;
    return 572;
}

#endif
