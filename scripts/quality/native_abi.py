"""Compile fixture offsets with the pinned cartridge frontend, never host layout."""
import re
import subprocess
from pathlib import Path
from mechanics_fixtures import digest


def verify_native_layout(engine, output, source, expected):
    preprocessed = output / (source.stem + '.i')
    assembly = output / (source.stem + '.s')
    compiler = engine / 'tools/agbcc/bin/agbcc'
    subprocess.run(['arm-none-eabi-cpp', '-I', 'include', '-I', 'tools/agbcc/include',
        '-I', 'tools/agbcc', '-nostdinc', '-undef', '-std=gnu89', '-DMODERN=0',
        str(source), '-o', str(preprocessed)], cwd=engine, check=True, timeout=10)
    subprocess.run([str(compiler), '-mthumb-interwork', '-O2', '-fhex-asm',
        '-o', str(assembly), str(preprocessed)], cwd=engine, check=True, timeout=10)
    values = [int(word, 0) for word in re.findall(r'\.word\s+(0x[0-9a-f]+|\d+)', assembly.read_text())]
    if values != expected:
        raise ValueError('Pinned fixture ABI changed; do not guess scratch offsets.')
    return {'values': values, 'source_sha256': digest(source), 'compiler_sha256': digest(compiler),
            'verifier_sha256': digest(Path(__file__)),
            'method': 'Pinned agbcc compiler sizeof/offsetof; not modern GCC or host layout'}
