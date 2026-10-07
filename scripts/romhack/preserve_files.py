"""Preserve compiler cleanup targets by moving them inside ignored build storage."""
from pathlib import Path
import glob
import os
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / '.tools'
archive = TOOLS / 'preserved-build-files' / uuid.uuid4().hex
for argument in sys.argv[1:]:
    if argument.startswith('-'):
        continue
    for match in glob.glob(argument):
        source = Path(os.path.abspath(match))
        if not source.exists() and not source.is_symlink():
            continue
        relative = source.relative_to(TOOLS)
        source.parent.resolve().relative_to(TOOLS.resolve())
        if not relative.parts or relative.parts[0] == 'preserved-build-files':
            raise ValueError('Refusing to move the build root or its archive.')
        destination = archive / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
