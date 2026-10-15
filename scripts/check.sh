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
node tests/audio_worklet_test.mjs
node --test tests/audio_playback_reset_test.mjs
node --test tests/state_serialization_test.mjs
node --test tests/web_performance_probe_test.mjs
node --test tests/controller_replay_test.mjs
node --test tests/field_observation_test.mjs
python3 tests/prepare_web_test.py
node --experimental-strip-types tests/bps.test.mjs
node --experimental-strip-types tests/flash-save.test.mjs
python3 tests/romhack_maps_test.py
python3 tests/seed_room_test.py
python3 tests/story_hints_test.py
python3 tests/field_journal_test.py
.tools/venv/bin/python tests/city_map_test.py
python3 tests/map_resume_test.py
python3 tests/romhack_battles_test.py
python3 tests/romhack_monsters_test.py
.tools/venv/bin/python tests/creature_resources_test.py
.tools/venv/bin/python tests/monster_atlas_test.py
python3 tests/evolution_fixture_test.py
python3 tests/creature_audio_test.py
python3 tests/field_music_test.py
python3 tests/music_loop_review_test.py
python3 tests/mechanics_fixture_test.py
python3 tests/turn_resolution_fixtures_test.py
.tools/venv/bin/python tests/trainer_class_fixtures_test.py
python3 tests/type_matrix_test.py
python3 tests/stat_fixture_test.py
python3 tests/action_fixture_test.py
python3 tests/accuracy_fixture_test.py
python3 tests/battle_command_fixture_test.py
python3 tests/capture_fixture_test.py
python3 tests/delivery_fixture_test.py
python3 tests/move_pipeline_fixture_test.py
python3 tests/residual_fixture_test.py
python3 tests/item_effect_fixture_test.py
python3 tests/flash_audit_test.py
python3 tests/frame_storage_test.py
python3 tests/input_profile_test.py
python3 tests/native_loop_analysis_test.py
python3 tests/web_performance_audit_test.py
python3 tests/active_field_audit_test.py
python3 tests/interface_text_test.py
python3 tests/interface_graphics_test.py
python3 tests/native_resources_test.py
python3 tests/title_creature_test.py
python3 tests/title_song_overlay_test.py
python3 tests/house_art_test.py
.tools/venv/bin/python tests/sunset_density_test.py
.tools/venv/bin/python tests/sunset_density_audit_test.py
.tools/venv/bin/python tests/courier_art_test.py
.tools/venv/bin/python tests/courier_battle_art_test.py
.tools/venv/bin/python tests/cast_art_test.py
.tools/venv/bin/python tests/cast_cleanup_test.py
.tools/venv/bin/python tests/cast_palette_test.py
python3 tests/portrait_cleanup_test.py
python3 tests/trainer_class_alias_test.py
python3 tests/cast_resume_test.py
python3 tests/street_art_test.py
python3 tests/apartment_art_test.py
python3 tests/door_art_test.py
.tools/venv/bin/python tests/seed_door_art_test.py
.tools/venv/bin/python tests/seed_door_audit_test.py
.tools/venv/bin/python tests/trainer_portrait_audit_test.py
python3 tests/terrain_art_test.py
.tools/venv/bin/python tests/park_frontage_test.py
.tools/venv/bin/python tests/sidewalk_thresholds_test.py
.tools/venv/bin/python tests/park_paving_test.py
.tools/venv/bin/python tests/park_paving_audit_test.py
.tools/venv/bin/python tests/park_infill_test.py
.tools/venv/bin/python tests/city_dressing_test.py
.tools/venv/bin/python tests/park_density_test.py
.tools/venv/bin/python tests/park_density_audit_test.py
.tools/venv/bin/python tests/city_furniture_audit_test.py
.tools/venv/bin/python tests/park_infill_audit_test.py
.tools/venv/bin/python tests/service_door_art_test.py
.tools/venv/bin/python tests/connected_frontage_audit_test.py
.tools/venv/bin/python tests/service_architecture_audit_test.py
.tools/venv/bin/python tests/park_art_test.py
.tools/venv/bin/python tests/park_tile_flips_test.py
.tools/venv/bin/python tests/office_art_test.py
.tools/venv/bin/python tests/clinic_art_test.py
node tests/web_capture_test.cjs
python3 tests/paired_review_test.py
cd web
npx tsc --noEmit
