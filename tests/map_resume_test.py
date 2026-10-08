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
static bool8 SFMapUsesAuthoredLayout(void) {
    return gSaveBlock1Ptr->location.mapGroup == 1
        && gSaveBlock1Ptr->location.mapNum == 2;
}
''')
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-I' + str(folder),
                    str(root / 'tests/map_resume_test.c'), '-o', str(folder / 'test')],
                   check=True)
    subprocess.run([str(folder / 'test')], check=True)
check()
print('Native resume position, collision, NPC/warp avoidance and state preservation passed.')
