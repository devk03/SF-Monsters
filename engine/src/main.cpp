#include "bn_core.h"
#include "bn_color.h"
#include "bn_bg_palettes.h"
#include "bn_keypad.h"
#include "bn_sprite_ptr.h"
#include "bn_sprite_font.h"
#include "bn_sprite_text_generator.h"
#include "bn_vector.h"
#include "bn_sprite_items_courier.h"
#include "bn_sprite_items_ui_font.h"

namespace
{
    // Provisional timings. Replace with measured reference walking/running data.
    constexpr int tile_pixels = 16;
    constexpr int walk_frames = 16;
    constexpr int run_frames = 8;

    struct Walker
    {
        int x = 0;
        int y = 0;
        int from_x = 0;
        int from_y = 0;
        int direction = 0;
        int elapsed = 0;
        int duration = 0;
        int steps = 0;

        void update(bn::sprite_ptr& sprite)
        {
            if(! duration)
            {
                int dx = 0;
                int dy = 0;
                if(bn::keypad::down_held()) { dy = 1; direction = 0; }
                else if(bn::keypad::up_held()) { dy = -1; direction = 1; }
                else if(bn::keypad::left_held()) { dx = -1; direction = 2; }
                else if(bn::keypad::right_held()) { dx = 1; direction = 3; }
                if((dx || dy) && x + dx * tile_pixels >= -96 && x + dx * tile_pixels <= 96 &&
                   y + dy * tile_pixels >= -40 && y + dy * tile_pixels <= 48)
                {
                    from_x = x;
                    from_y = y;
                    x += dx * tile_pixels;
                    y += dy * tile_pixels;
                    elapsed = 0;
                    duration = bn::keypad::b_held() ? run_frames : walk_frames;
                }
            }
            int pose = 0;
            if(duration)
            {
                ++elapsed;
                // Idle at the contact points, alternate the leading foot per tile.
                if(elapsed > duration / 4 && elapsed <= duration * 3 / 4)
                    pose = 1 + (steps & 1);
                sprite.set_position(from_x + (x - from_x) * elapsed / duration,
                                    from_y + (y - from_y) * elapsed / duration - 8);
                if(elapsed == duration)
                {
                    duration = 0;
                    ++steps;
                }
            }
            else
            {
                sprite.set_position(x, y - 8);
            }
            sprite.set_tiles(bn::sprite_items::courier.tiles_item(), direction * 3 + pose);
        }
    };
}

int main()
{
    bn::core::init();
    bn::bg_palettes::set_transparent_color(bn::color(9, 17, 22));
    auto courier = bn::sprite_items::courier.create_sprite(0, -8);
    bn::sprite_font font(bn::sprite_items::ui_font);
    bn::sprite_text_generator text(font);
    bn::vector<bn::sprite_ptr, 48> labels;
    text.set_center_alignment();
    text.generate(0, -68, "SF RENDERER / UNREVIEWED", labels);
    text.generate(0, 68, "PAD WALK   B RUN", labels);
    Walker walker;
    while(true)
    {
        walker.update(courier);
        bn::core::update();
    }
}
