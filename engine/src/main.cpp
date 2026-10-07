#include "bn_core.h"
#include "bn_color.h"
#include "bn_bg_palettes.h"
#include "bn_keypad.h"
#include "bn_music_items.h"
#include "bn_camera_ptr.h"
#include "bn_regular_bg_ptr.h"
#include "bn_sprite_ptr.h"
#include "bn_sprite_font.h"
#include "bn_sprite_text_generator.h"
#include "bn_vector.h"
#include "bn_sprite_items_courier.h"
#include "bn_sprite_items_ui_font.h"
#include "bn_regular_bg_items_sunset.h"
#include "bn_regular_bg_items_south_park.h"
#include "bn_regular_bg_items_cognition.h"
#include "telemetry.h"
extern "C"
{
#include "game.h"
volatile FoundationTelemetry foundation_telemetry = {0x53464654, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
}

namespace
{
    // Provisional timings. Replace with measured reference walking/running data.
    constexpr int tile_pixels = 16;
    constexpr int walk_frames = 16;
    constexpr int run_frames = 8;

    struct Walker
    {
        int x = 10 * 16 + 8;
        int y = 12 * 16 + 8;
        int from_x = 0;
        int from_y = 0;
        int direction = 0;
        int elapsed = 0;
        int duration = 0;
        int steps = 0;
        int map = 0;

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
                int target = game_tile(map, x / tile_pixels + dx, y / tile_pixels + dy);
                if((dx || dy) && target != 2 && target != 4)
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
            foundation_telemetry.step_duration = duration;
            foundation_telemetry.step_elapsed = elapsed;
            foundation_telemetry.completed_steps = steps;
            foundation_telemetry.world_x = sprite.x().integer();
            foundation_telemetry.world_y = sprite.y().integer() + 8;
            foundation_telemetry.map = map;
        }

        void reset(int next_map)
        {
            map = next_map;
            x = (map == 1 ? 4 : map == 2 ? 11 : 10) * tile_pixels + 8;
            y = (map == 1 ? 13 : map == 2 ? 15 : 12) * tile_pixels + 8;
            from_x = x;
            from_y = y;
            duration = elapsed = 0;
        }
    };

    int clamp(int value, int low, int high)
    {
        return value < low ? low : value > high ? high : value;
    }
}

int main()
{
    bn::core::init();
    bn::music_items::ocean_commute.play(bn::fixed(0.65));
    bn::bg_palettes::set_transparent_color(bn::color(9, 17, 22));
    auto camera = bn::camera_ptr::create(168, 200);
    auto background = bn::regular_bg_items::sunset.create_bg(256, 256);
    background.set_camera(camera);
    auto courier = bn::sprite_items::courier.create_sprite(168, 192);
    courier.set_camera(camera);
    bn::sprite_font font(bn::sprite_items::ui_font);
    bn::sprite_text_generator text(font);
    bn::vector<bn::sprite_ptr, 48> labels;
    text.set_center_alignment();
    text.generate(0, -68, "SF RENDERER / UNREVIEWED", labels);
    text.generate(0, 68, "B RUN  SELECT NEXT MAP", labels);
    Walker walker;
    while(true)
    {
        if(bn::keypad::select_pressed() && ! walker.duration)
        {
            walker.reset((walker.map + 1) % 3);
            const bn::regular_bg_item* maps[] = {&bn::regular_bg_items::sunset,
                &bn::regular_bg_items::south_park, &bn::regular_bg_items::cognition};
            background.set_item(*maps[walker.map]);
        }
        walker.update(courier);
        camera.set_position(clamp(courier.x().integer(), 120, 24 * 16 - 120),
                            clamp(courier.y().integer() + 8, 80, 18 * 16 - 80));
        bn::core::update();
        foundation_telemetry.updates = foundation_telemetry.updates + 1;
        foundation_telemetry.missed_frames = foundation_telemetry.missed_frames +
                                            bn::core::last_missed_frames();
        unsigned cpu = bn::core::last_cpu_usage().data();
        if(cpu > foundation_telemetry.peak_cpu_q12)
            foundation_telemetry.peak_cpu_q12 = cpu;
        unsigned keys = 0;
        for(unsigned bit = 1; bit <= 512; bit <<= 1)
            if(bn::keypad::held(static_cast<bn::keypad::key_type>(bit))) keys |= bit;
        foundation_telemetry.keys = keys;
    }
}
