#!/usr/bin/env python3
"""Validate an independent screenshot review and create a private HTML report.

The reviewer, not this script, inspects the images and assigns scores. Image
hashes bind a review to its evidence; declared ROM identity is not proof that
an image was captured from that ROM. Keep native captures and the report local.

Manifest (paths relative to the manifest, or absolute):
{
  "town": "Mission", "reviewer": "independent reviewer",
  "candidate_rom_sha256": "<64 hex>", "candidate_capture_id": "<receipt/session>",
  "images": [
    {"id":"map", "role":"full_map", "path":"...png", "sha256":"...",
     "rom_sha256":"...", "capture_id":"...", "note":"Background; NPCs omitted"},
    {"id":"arrival", "role":"arrival", "path":"...png", "sha256":"...",
     "rom_sha256":"...", "capture_id":"..."},
    {"id":"landmark", "role":"landmark", "path":"...png", "sha256":"...",
     "rom_sha256":"...", "capture_id":"..."},
    {"id":"street", "role":"secondary", "path":"...png", "sha256":"...",
     "rom_sha256":"...", "capture_id":"..."},
    {"id":"ideal", "role":"ideal", "path":"...png", "sha256":"..."}
  ],
  "ratings": {"composition":{"score":1,"evidence":["map"],"reason":"..."},
    "purposeful_space":{}, "architecture":{}, "scenery_activity":{},
    "identity":{}, "readability":{}},
  "defects":[{"evidence":["street"],"location":"east side", "observation":"...","next_change":"..."},
    {"evidence":["map"],"location":"central block", "observation":"...","next_change":"..."},
    {"evidence":["landmark"],"location":"above entrance", "observation":"...","next_change":"..."}],
  "is_change":true, "major_regression":false, "decision":"revise",
  "baseline_comparison":"...", "uncertainties":"..."
}
Optional images may use role `baseline` with their own ROM/capture IDs. A
review marked `advance` is a recommendation to iterate, not user acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
RATINGS = {'composition': 'Spatial composition and exploration',
           'purposeful_space': 'Density and purposeful space',
           'architecture': 'Architecture, scale and joins',
           'scenery_activity': 'Ground, scenery and activity',
           'identity': 'Neighborhood identity',
           'readability': 'Player-scale readability and visual defects'}
ROLES = {'full_map', 'arrival', 'landmark', 'secondary', 'ideal', 'baseline', 'additional'}
IMPLEMENTATION = {'full_map', 'arrival', 'landmark', 'secondary', 'baseline', 'additional'}
HEX = re.compile(r'^[0-9a-f]{64}$')

class EvidenceError(ValueError):
    pass

def nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f'{name} must be nonempty text')
    return value.strip()

def digest(value, name):
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise EvidenceError(f'{name} must be a lowercase SHA-256')
    return value

def validate(manifest, base):
    """Check evidence integrity, not image meaning or provenance authenticity."""
    if not isinstance(manifest, dict): raise EvidenceError('manifest must be an object')
    town = nonempty(manifest.get('town'), 'town')
    reviewer = nonempty(manifest.get('reviewer'), 'reviewer')
    rom = digest(manifest.get('candidate_rom_sha256'), 'candidate ROM')
    nonempty(manifest.get('candidate_capture_id'), 'candidate capture ID')
    images = manifest.get('images')
    if not isinstance(images, list): raise EvidenceError('images must be a list')
    by_id = {}; roles = {}
    for item in images:
        if not isinstance(item, dict): raise EvidenceError('image must be an object')
        ident = nonempty(item.get('id'), 'image ID')
        if ident in by_id: raise EvidenceError(f'duplicate image ID: {ident}')
        role = item.get('role')
        if role not in ROLES: raise EvidenceError(f'{ident}: invalid role')
        path = Path(nonempty(item.get('path'), f'{ident} path')).expanduser()
        path = (base / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_file(): raise EvidenceError(f'{ident}: image missing: {path}')
        expected = digest(item.get('sha256'), f'{ident} image hash')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise EvidenceError(f'{ident}: image hash mismatch')
        try:
            from PIL import Image
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
        except (ImportError, OSError, ValueError) as exc:
            raise EvidenceError(f'{ident}: unreadable image: {exc}') from exc
        if width < 1 or height < 1: raise EvidenceError(f'{ident}: empty image')
        if role in IMPLEMENTATION:
            image_rom = digest(item.get('rom_sha256'), f'{ident} ROM')
            nonempty(item.get('capture_id'), f'{ident} capture ID')
            if role != 'baseline' and image_rom != rom:
                raise EvidenceError(f'{ident}: candidate ROM differs')
        by_id[ident] = dict(item, resolved_path=path, width=width, height=height)
        roles.setdefault(role, []).append(ident)
    for role in ('full_map', 'arrival', 'landmark', 'secondary', 'ideal'):
        if not roles.get(role): raise EvidenceError(f'missing {role} evidence')
    if type(manifest.get('is_change')) is not bool or type(manifest.get('major_regression')) is not bool:
        raise EvidenceError('is_change and major_regression must be booleans')
    if manifest['is_change'] and not roles.get('baseline'):
        raise EvidenceError('a changed candidate requires baseline implementation evidence')
    views = [by_id[roles[role][0]] for role in ('arrival','landmark','secondary')]
    if len({v['sha256'] for v in views}) != 3:
        raise EvidenceError('player-scale views must be different images')
    if any(v['width'] < 240 or v['height'] < 160 or v['width'] * 2 != v['height'] * 3 for v in views):
        raise EvidenceError('player-scale views must be at least 240×160 with 3:2 aspect ratio')
    def references(value, name):
        if not isinstance(value, list) or not value or any(not isinstance(i, str) or i not in by_id for i in value):
            raise EvidenceError(f'{name} must reference supplied image IDs')
        return value
    ratings = manifest.get('ratings')
    if not isinstance(ratings, dict) or set(ratings) != set(RATINGS):
        raise EvidenceError('all six rating dimensions are required')
    for key, value in ratings.items():
        if not isinstance(value, dict) or type(value.get('score')) is not int or not 0 <= value['score'] <= 4:
            raise EvidenceError(f'{key}: score must be an integer 0–4')
        nonempty(value.get('reason'), f'{key} reason')
        references(value.get('evidence'), f'{key} evidence')
        if not any(by_id[i]['role'] in IMPLEMENTATION - {'baseline'} for i in value['evidence']):
            raise EvidenceError(f'{key}: evidence must include a candidate image')
    defects = manifest.get('defects')
    if not isinstance(defects, list) or len(defects) < 3:
        raise EvidenceError('at least three actionable defects are required')
    for i, defect in enumerate(defects):
        if not isinstance(defect, dict): raise EvidenceError(f'defect {i+1} must be an object')
        nonempty(defect.get('observation'), f'defect {i+1} observation')
        nonempty(defect.get('location'), f'defect {i+1} location or crop')
        nonempty(defect.get('next_change'), f'defect {i+1} next change')
        references(defect.get('evidence'), f'defect {i+1} evidence')
        if not any(by_id[j]['role'] in IMPLEMENTATION - {'baseline'} for j in defect['evidence']):
            raise EvidenceError(f'defect {i+1}: evidence must include a candidate image')
    if manifest.get('decision') not in ('advance', 'revise', 'insufficient evidence'):
        raise EvidenceError('decision must be advance, revise or insufficient evidence')
    if manifest['major_regression'] and manifest['decision'] == 'advance':
        raise EvidenceError('a major visible regression cannot advance')
    nonempty(manifest.get('baseline_comparison'), 'baseline comparison')
    nonempty(manifest.get('uncertainties'), 'uncertainties')
    return {'town':town, 'reviewer':reviewer, 'rom':rom, 'images':by_id}

def report(manifest, checked, output):
    esc = lambda x: html.escape(str(x), quote=True)
    def refs(ids): return ', '.join(f'<a href="#{esc(i)}">{esc(i)}</a>' for i in ids)
    sections = []
    for ident, item in checked['images'].items():
        rel = os.path.relpath(item['resolved_path'], output.parent)
        details = f"{item['role']} · {item['width']}×{item['height']} · SHA-256 {item['sha256']}"
        if item['role'] in IMPLEMENTATION:
            details += f" · declared ROM {item['rom_sha256']} · capture {item['capture_id']}"
        if item.get('note'): details += ' · ' + item['note']
        sections.append(f'<figure id="{esc(ident)}"><figcaption><strong>{esc(ident)}</strong> — {esc(details)}</figcaption>'
                        f'<a href="{esc(rel)}"><img loading="lazy" src="{esc(rel)}" alt="{esc(ident)}"></a></figure>')
    ratings = ''.join(f'<tr><th>{esc(label)}</th><td>{manifest["ratings"][key]["score"]}/4</td>'
                      f'<td>{esc(manifest["ratings"][key]["reason"])} ({refs(manifest["ratings"][key]["evidence"])})</td></tr>'
                      for key,label in RATINGS.items())
    defects = ''.join(f'<li><strong>{esc(d["observation"])}</strong> ({refs(d["evidence"])}, {esc(d["location"])})<br>Next: {esc(d["next_change"])}</li>' for d in manifest['defects'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(checked['town'])} visual review</title><style>body{{font:16px system-ui;max-width:1200px;margin:2rem auto;padding:0 1rem;background:#f5f4ef;color:#26323a}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #b6bcb9;padding:.5rem;text-align:left;vertical-align:top}}figure{{margin:1.5rem 0}}img{{max-width:100%;height:auto;image-rendering:pixelated}}figcaption{{overflow-wrap:anywhere;margin-bottom:.5rem}}li{{margin:.8rem 0}}a{{color:#135b75}}</style><h1>{esc(checked['town'])}: screenshot review</h1><p>Reviewer: {esc(checked['reviewer'])} · Candidate ROM: <code>{checked['rom']}</code></p><p><strong>Decision: {esc(manifest['decision'])}.</strong> This is independent visual triage, not user approval. The script verifies image bytes and declared identity, not image provenance, aesthetic quality, collision or browser behavior.</p><p><strong>Baseline:</strong> {esc(manifest['baseline_comparison'])}</p><p><strong>Uncertainty:</strong> {esc(manifest['uncertainties'])}</p><table><thead><tr><th>Dimension</th><th>Score</th><th>Observed evidence</th></tr></thead><tbody>{ratings}</tbody></table><h2>Three or more actionable defects</h2><ol>{defects}</ol><h2>Evidence</h2>{''.join(sections)}</html>'''

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='Private HTML path under .tools')
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / '.tools').resolve()) or output.suffix.lower() != '.html':
        parser.error('output must be an HTML file under this checkout’s .tools directory')
    try:
        source = args.manifest.resolve()
        data = json.loads(source.read_text())
        checked = validate(data, source.parent)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report(data, checked, output), encoding='utf-8')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Visual review invalid: {exc}', file=sys.stderr)
        return 1
    print(f'Private visual review: {output}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
