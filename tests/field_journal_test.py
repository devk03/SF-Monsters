"""Sanitize the production journal's chapter routing and native modal lifecycle."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
parent = root / '.tools/field-journal-tests'
parent.mkdir(parents=True, exist_ok=True)
work = Path(tempfile.mkdtemp(prefix='case-', dir=parent))
# The generated authored-map predicate is exercised through the actual native menu.
(work / 'sf_authored_maps.h').write_text('')
(work / 'constants').mkdir()
(work / 'constants/vars.h').write_text(
    '#define VAR_UNUSED_0x40F7 0x40f7\n#define VAR_UNUSED_0x40DB 0x40db\n')
subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                '-fsanitize=address,undefined', '-I' + str(work),
                str(root / 'tests/field_journal_test.c'), '-o', str(work / 'test')], check=True)
subprocess.run([str(work / 'test')], check=True)
