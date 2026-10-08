"""Separate native-host compiler/engine checkout, gated by exact base reproduction."""
import hashlib
import json
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
import bootstrap

ROOT = bootstrap.ROOT
ENGINE = ROOT / '.tools/pokeemerald-host'


def host_make(directory, *arguments):
    preserve = shlex.quote(sys.executable) + ' ' + shlex.quote(str(
        ROOT / 'scripts/romhack/preserve_files.py'))
    subprocess.run(['make', '-j8', 'RM=' + preserve, *arguments], cwd=directory,
                   check=True, timeout=5400)


def ensure_baseline(info):
    cartridge = ENGINE / 'pokeemerald.gba'
    if hashlib.sha1(cartridge.read_bytes()).hexdigest() != bootstrap.REFERENCE_SHA1:
        raise ValueError('Cached native host baseline no longer matches the reference.')
    destination = ROOT / '.tools/romhack-baseline'
    destination.mkdir(exist_ok=True)
    base = destination / 'emerald-matching.gba'
    if base.exists() and base.read_bytes() != cartridge.read_bytes():
        raise ValueError('Existing private baseline differs; preserve and inspect it.')
    if not base.exists():
        shutil.copy2(cartridge, base)
    proof = destination / 'build-host.json'
    if not proof.exists():
        proof.write_text(json.dumps(info, indent=2) + '\n')


def prepare_host():
    for name in ('arm-none-eabi-as', 'arm-none-eabi-ar', 'arm-none-eabi-cpp',
                 'arm-none-eabi-ld', 'arm-none-eabi-objcopy', 'pkg-config'):
        if not shutil.which(name):
            raise ValueError('Missing native-host build dependency: ' + name)
    bootstrap.checkout(bootstrap.EMERALD, 'https://github.com/pret/pokeemerald.git', bootstrap.EMERALD_REVISION)
    bootstrap.checkout(ENGINE, str(bootstrap.EMERALD), bootstrap.EMERALD_REVISION)
    bootstrap.checkout(bootstrap.AGBCC, 'https://github.com/pret/agbcc.git', bootstrap.AGBCC_REVISION)
    bootstrap.EMERALD = ENGINE
    bootstrap.build_compilers('-host-' + platform.system().lower())
    bootstrap.preserve_cleanup(ENGINE)
    marker = ENGINE / 'sf-host-build.json'
    compiler_dir = ENGINE / 'tools/agbcc/bin'
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in compiler_dir.iterdir() if path.is_file()}
    libraries = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in (ENGINE / 'tools/agbcc/lib').glob('*.a')}
    versions = {name: subprocess.check_output([name, '--version'], text=True).splitlines()[0]
                for name in ('arm-none-eabi-as', 'arm-none-eabi-ld', 'arm-none-eabi-cpp', 'make')}
    if marker.exists():
        info = json.loads(marker.read_text())
        if info['compiler_sha256'] != hashes or info.get('library_sha256') != libraries or \
           info.get('tool_versions') != versions or (info['system'], info['machine']) != (
                platform.system(), platform.machine()):
            raise ValueError('Native host compiler identity changed; preserve and inspect its build.')
        if info['baseline_sha1'] != bootstrap.REFERENCE_SHA1:
            raise ValueError('Native host baseline has not reproduced the pinned reference.')
        ensure_baseline(info)
        return ENGINE
    # A fresh checkout must reproduce Emerald before any SF overlay is applied.
    host_make(ENGINE)
    baseline = (ENGINE / 'pokeemerald.gba').read_bytes()
    digest = hashlib.sha1(baseline).hexdigest()
    if digest != bootstrap.REFERENCE_SHA1:
        raise ValueError('Native host base reproduction mismatch: ' + digest)
    info = {'system': platform.system(), 'machine': platform.machine(),
        'emerald_revision': bootstrap.EMERALD_REVISION, 'agbcc_revision': bootstrap.AGBCC_REVISION,
        'compiler_sha256': hashes, 'library_sha256': libraries, 'tool_versions': versions,
        'baseline_sha1': digest,
        'baseline_sha256': hashlib.sha256(baseline).hexdigest(),
        'cleanup': 'preserved; no destructive clean targets'}
    marker.write_text(json.dumps(info, indent=2) + '\n')
    ensure_baseline(info)
    return ENGINE


if __name__ == '__main__':
    print('Verified native-host engine:', prepare_host())
