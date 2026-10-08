#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
mkdir -p build
clang -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined -g game/core.c game/content.c tests/core_test.c -o build/core-test
build/core-test
clang -std=c11 -Wall -Wextra -Werror game/content.c tests/map_test.c -o build/map-test
clang -std=c11 -Wall -Wextra -Werror tests/coastal_border_test.c -o build/coastal-border-test
build/coastal-border-test
build/map-test
clang -std=c11 -Wall -Wextra -Werror game/core.c game/content.c tests/save_fixture.c -o build/save-fixture
build/save-fixture build/save-fixture.sav
node --experimental-strip-types tests/save-format.test.mjs build/save-fixture.sav
node tests/emulator.test.cjs
node --experimental-strip-types tests/bps.test.mjs
node --experimental-strip-types tests/flash-save.test.mjs
python3 tests/romhack_maps_test.py
python3 tests/map_resume_test.py
python3 tests/romhack_battles_test.py
python3 tests/romhack_monsters_test.py
.tools/venv/bin/python tests/monster_atlas_test.py
python3 tests/evolution_fixture_test.py
python3 tests/creature_audio_test.py
python3 tests/field_music_test.py
python3 tests/frame_storage_test.py
python3 tests/interface_text_test.py
python3 tests/interface_graphics_test.py
python3 tests/native_resources_test.py
python3 tests/title_creature_test.py
python3 tests/title_song_overlay_test.py
python3 tests/house_art_test.py
.tools/venv/bin/python tests/courier_art_test.py
python3 tests/street_art_test.py
python3 tests/apartment_art_test.py
python3 tests/door_art_test.py
python3 tests/terrain_art_test.py
.tools/venv/bin/python tests/park_art_test.py
node tests/web_capture_test.cjs
cd web
npx tsc --noEmit
