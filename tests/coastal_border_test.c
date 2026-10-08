#include <assert.h>
#include <stdio.h>
#include "../romhack/engine/coastal_border.h"

int main(void)
{
    // Every real cell in the 32x32 Sunset keeps its authored graphic.
    for (int y = 7; y < 39; ++y)
        for (int x = 7; x < 39; ++x)
            assert(SFCoastalBorderGraphic(x, y, 32, 32) == -1);
    // West padding stays Pacific water, including both outside corners.
    for (int y = -7; y <= 46; ++y)
        assert(SFCoastalBorderGraphic(6, y, 32, 32) == 574);
    for (int y = 6; y <= 39; y += 33)
    {
        assert(SFCoastalBorderGraphic(9, y, 32, 32) == 574);
        assert(SFCoastalBorderGraphic(10, y, 32, 32) == 575);
        assert(SFCoastalBorderGraphic(11, y, 32, 32) == 573);
        assert(SFCoastalBorderGraphic(15, y, 32, 32) == 573);
        assert(SFCoastalBorderGraphic(16, y, 32, 32) == 572);
        assert(SFCoastalBorderGraphic(38, y, 32, 32) == 572);
    }
    assert(SFCoastalBorderGraphic(39, 20, 32, 32) == 572);
    assert(SFCoastalBorderGraphic(7, 7, 40, 20) == -1);
    assert(SFCoastalBorderGraphic(46, 26, 40, 20) == -1);
    assert(SFCoastalBorderGraphic(47, 26, 40, 20) == 572);
    puts("Coastal camera padding keeps authored cells and continuous shore strips.");
    return 0;
}
