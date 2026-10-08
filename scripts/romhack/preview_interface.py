"""Private interface preview; normal release still requires the compiled build."""
import argparse
import hashlib
import json
import shutil
import subprocess
import uuid
from build_probe import ROOT, EMERALD, BASE, BASE_HASH, FLIPS, FLIPS_REVISION
from interface_text import apply_interface_text
from interface_graphics import apply_interface_graphics
from title_art import apply_title_art


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', required=True)
    args = parser.parse_args()
    content = json.loads((ROOT / 'romhack/content/engine-probe.json').read_text())
    labels = json.loads((ROOT / 'romhack/content/interface-text.json').read_text())
    source = ROOT / args.rom
    if hashlib.sha256(source.read_bytes()).hexdigest() != labels['preview_input_sha256']:
        parser.error('Preview needs the explicitly pinned previously compiled cartridge.')
    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_HASH:
        parser.error('Reference cartridge fingerprint changed.')
    revision = subprocess.check_output(['git', '-C', str(FLIPS), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != FLIPS_REVISION:
        parser.error('Patch encoder revision changed.')
    encoder = ROOT / '.tools/flips-macos'
    subprocess.run(['make', '-C', str(FLIPS), 'TARGET=cli', 'CFLAGS=-O2',
                    'FNAME_cli=' + str(encoder)], check=True)
    candidate = ROOT / '.tools' / ('interface-preview-' + uuid.uuid4().hex)
    candidate.mkdir()
    target = candidate / 'target.gba'
    shutil.copy2(source, target)
    receipt = apply_interface_text(ROOT, EMERALD, target)
    graphics_receipt = apply_interface_graphics(ROOT, EMERALD, target)
    title_receipt = apply_title_art(ROOT, EMERALD, target)
    target_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    output = ROOT / '.tools/romhack-drafts' / content['version'] / target_hash
    if output.exists():
        parser.error('Existing evidence is preserved; choose a new content revision.')
    output.mkdir(parents=True)
    shutil.copy2(target, output / 'target.gba')
    patch = output / 'sf-mini-monsters.bps'
    subprocess.run([str(encoder), '--create', '--bps', '--exact', str(BASE), str(target), str(patch)], check=True)
    verification = candidate / 'reapplied.gba'
    subprocess.run([str(encoder), '--apply', '--exact', str(patch), str(BASE), str(verification)], check=True)
    if verification.read_bytes() != target.read_bytes():
        raise ValueError('Text preview patch failed byte-identical reapplication.')
    manifest = {'version': content['version'], 'base_sha256': BASE_HASH,
        'target_sha256': target_hash, 'target_bytes': target.stat().st_size,
        'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'patch_bytes': patch.stat().st_size,
        'game_code': 'BPEE', 'status': 'Private interface preview; full compilation remains pending.',
        'patch_roundtrip': 'byte-identical', 'quality_approval': 'pending', 'interface_text': receipt,
        'interface_graphics': graphics_receipt,
        'title_art': title_receipt,
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_worktree_dirty': True, 'full_rebuild_verified': False}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Private interface preview:', output)


if __name__ == '__main__':
    main()
