#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
mkdir -p build
clang -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined -g game/core.c game/content.c tests/core_test.c -o build/core-test
build/core-test
clang -std=c11 -Wall -Wextra -Werror game/content.c tests/map_test.c -o build/map-test
build/map-test
clang -std=c11 -Wall -Wextra -Werror game/core.c game/content.c tests/save_fixture.c -o build/save-fixture
build/save-fixture build/save-fixture.sav
node --experimental-strip-types tests/save-format.test.mjs build/save-fixture.sav
node tests/emulator.test.cjs
cd web
npx tsc --noEmit
