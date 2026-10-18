"""Native resume relocation: keep valid positions; escape new collision safely."""
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
def check():
    output = root / '.tools/map-resume-tests'
    output.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix='case-', dir=output))
    # Isolate the existing authored-map predicate; test the production resolver.
    (folder / 'sf_authored_maps.h').write_text('''
#define SF_WORLD_RESUME_MASKS 1
static bool8 SFMapUsesAuthoredLayout(void) {
    return gSaveBlock1Ptr->location.mapGroup == 1
        && gSaveBlock1Ptr->location.mapNum == 2;
}
''')
    (folder / 'sf_resume_masks.h').write_text('''
static bool8 SFResumeCanReturn(s16 x, s16 y) {
    return x >= 0 && y >= 0 && x < 5 && y < 5 && sReturnable[y][x];
}
''')
    (folder / 'constants').mkdir()
    (folder / 'constants/flags.h').write_text('#define FLAG_BADGE05_GET 0x86B\n')
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-I' + str(folder),
                    str(root / 'tests/map_resume_test.c'), '-o', str(folder / 'test')],
                   check=True)
    subprocess.run([str(folder / 'test')], check=True)
check()
print('Native resume position, collision, NPC/warp avoidance and state preservation passed.')
