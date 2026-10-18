"""Package a private native town tour for human review; never infer approval."""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tour', required=True, type=Path)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if not args.name.replace('-', '').isalnum() or len(args.name) > 64:
        parser.error('Use a short alphanumeric review name')
    tour = args.tour.resolve()
    tour.relative_to(ROOT / '.tools/benchmarks')
    evidence = json.loads((tour / 'scene-tour.json').read_text())
    manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
    districts = json.loads((ROOT / 'romhack/world/districts.json').read_text())['areas']
    activities = json.loads((ROOT / 'romhack/world/discoveries.json').read_text())['areas']
    areas = manifest['areas'] + [dict(id=manifest['league']['venue'], label=manifest['league']['label'])]
    if evidence['controller_only'] is not True or evidence['areas'] != [a['id'] for a in areas]:
        parser.error('Review needs a complete controller-only tour in approved story order')
    output = ROOT / '.tools/benchmarks' / args.name
    output.mkdir(exist_ok=False)
    images, cards = [], []
    for number, area in enumerate(areas, 1):
        identifier = area['id']
        files = sorted(tour.glob(identifier + '-[0-9]*.png'))
        if not files:
            raise ValueError('No actual native view for ' + identifier)
        pictures = []
        for file in files:
            data = file.read_bytes()
            encoded = base64.b64encode(data).decode()
            pictures.append('<img alt="Native ' + html.escape(area['label']) + ' view" src="data:image/png;base64,' + encoded + '">')
            images.append(dict(area=identifier, file=str(file), sha256=hashlib.sha256(data).hexdigest()))
        room = next((r['label'] for r in manifest['interiors'] if r['area'] == identifier), 'Outdoor landmark / trail')
        gym = next((g['badge'] for g in manifest['gyms'] if g['area'] == identifier), None)
        details = [districts[identifier]['character'].capitalize(), room,
                   ('Gym ' + str(gym) + ' site reserved; encounter unbuilt') if gym else 'Non-gym destination',
                   'Local ' + activities[identifier]['kind'] + ' and revisit dialogue']
        cards.append('<section id="' + identifier + '"><h2>' + str(number) + '. ' + html.escape(area['label']) + '</h2>'
                     + '<p>' + ' · '.join(html.escape(s) for s in details) + '</p><div class="views">'
                     + ''.join(pictures) + '</div><label>Town composition / readability / feel '
                     + '<select data-area="' + identifier + '"><option value="">Not reviewed</option>'
                     + ''.join(f'<option value="{n}">{n} / 4</option>' for n in range(5))
                     + '</select></label><label>Largest gap or requested change<textarea data-area="'
                     + identifier + '" rows="2"></textarea></label></section>')
    navigation = ''.join('<a href="#' + a['id'] + '">' + str(i) + '. ' + html.escape(a['label']) + '</a>'
                         for i, a in enumerate(areas, 1))
    receipt = dict(rom_sha256=evidence['rom_sha256'], controller_only=True, images=images,
                   scope='Human town composition, readability and world-feel review; not full game or campaign approval',
                   human_approval='pending', source_tour=str(tour),
                   generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    page = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>SF world review</title>
<style>
*{box-sizing:border-box}body{font:16px/1.5 system-ui;margin:0;background:#eee;color:#242424}
header,main{max-width:1100px;margin:auto;padding:24px}header{background:#fff}
h1{font-size:30px;margin:0 0 12px}h2{font-size:22px;margin:0 0 8px}code{overflow-wrap:anywhere}
nav{display:flex;flex-wrap:wrap;gap:6px 18px;margin:20px 0}a{color:#174c8b}
section{background:white;padding:20px;margin:0 0 24px;scroll-margin-top:16px}
.views{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px}
img{width:min(480px,100%);height:auto;image-rendering:pixelated;object-fit:contain;align-self:flex-start}
label{display:block;margin:12px 0}select,textarea,button{font:inherit;padding:8px}
textarea{display:block;width:100%;margin-top:6px}button{cursor:pointer}footer{margin:24px 0}
</style><header><h1>SF Mini Monsters — 18-town review</h1>
<p>Actual native GBA views in story order. These are private development candidates.
The images show field composition; inspect matched walking clips separately for game feel.
Final gym encounters and contributor story missions remain unbuilt.</p>
<p><strong>Review scope:</strong> density, building fit, scenery, navigation and town character.
0 = far below reference; 1 = rough; 2 = recognizable but visibly unfinished;
3 = close with specific gaps; 4 = acceptable for this town subset.</p>
<p>A score does not approve the full art domain, battle systems or campaign.
Feedback stays in this page until you download it. It is not sent anywhere.</p>
<p>Screenshot cartridge: <code>ROM_HASH</code></p><nav>NAVIGATION</nav>
<button id="export">Download town feedback</button><p id="status" role="status"></p></header>
<main>CARDS<footer><a href="#">Back to town index</a></footer></main>
<script>
const metadata=METADATA;
document.querySelector('#export').onclick=()=>{
 const towns=[...document.querySelectorAll('section')].map(section=>({
  area:section.id,score:section.querySelector('select').value===''?null:Number(section.querySelector('select').value),
  feedback:section.querySelector('textarea').value.trim()
 }));
 const bytes=JSON.stringify({...metadata,towns,reviewed_at:new Date().toISOString()},null,2);
 const url=URL.createObjectURL(new Blob([bytes],{type:'application/json'}));
 const a=document.createElement('a');a.href=url;a.download='sf-town-feedback.json';a.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
 document.querySelector('#status').textContent='Feedback downloaded. Nothing was submitted or approved automatically.';
};
</script></html>'''
    page = page.replace('ROM_HASH', receipt['rom_sha256']).replace('NAVIGATION', navigation).replace('CARDS', ''.join(cards))
    page = page.replace('METADATA', json.dumps({k:receipt[k] for k in ('rom_sha256','scope')}).replace('<', '\\u003c'))
    (output / 'index.html').write_text(page)
    (output / 'review.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(output / 'index.html')


if __name__ == '__main__':
    main()
