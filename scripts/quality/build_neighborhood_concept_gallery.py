"""Build the review gallery for original generated neighborhood concepts."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / 'output/imagegen/neighborhood-ideals-v1'
NATURE = {'golden-gate-park', 'twin-peaks', 'lands-end', 'sutro-tower', 'angel-island', 'treasure-island', 'presidio'}


def main():
    manifest = json.loads((DIRECTORY / 'prompts.json').read_text())
    rows = manifest['images']
    cards, links = [], []
    readme = ['# Ideal SF neighborhood concepts', '',
              '18 campaign destinations plus a Presidio / Presidio Heights bonus. Generated from scratch with the built-in image_gen tool; no current-game screenshots were supplied.', '',
              '**Design concepts, not implementation screenshots or ready-to-use GBA assets.** These explore architecture, landmarks, street composition and planting. Perspective, detail and geography need review before conversion.', '',
              '[Offline review gallery with notes](index.html) · [Exact generation prompts and image hashes](prompts.json)', '',
              'Click any image to inspect it at full size. The gallery keeps notes locally where browser storage is available; export them to share.', '']
    for number, row in enumerate(rows, 1):
        if not (DIRECTORY / row['file']).is_file():
            raise ValueError('Missing generated concept: ' + row['file'])
        name = html.escape(row['name'].title())
        filename = html.escape(row['file'], quote=True)
        identifier = html.escape(row['id'], quote=True)
        brief = row['brief'].split('. ')[0].rstrip('.') + '.'
        label = 'Bonus geography' if row.get('bonus') else f'Campaign destination {number:02d}'
        category = 'nature' if row['id'] in NATURE else 'urban'
        links.append(f'<a href="#{identifier}">{name}</a>')
        cards.append(f'''<article id="{identifier}" data-category="{category}">
<header><span class="eyebrow">{label} · CONCEPT</span><h2>{name}</h2></header>
<a class="art" href="{filename}" target="_blank" rel="noopener" aria-label="Open {name} at full size"><img src="{filename}" width="1536" height="1024" loading="lazy" alt="Ideal {name} neighborhood concept, generated from scratch"></a>
<div class="body"><p>{html.escape(brief)}</p><label for="note-{identifier}">Keep / change</label><textarea id="note-{identifier}" data-note="{identifier}" rows="3" placeholder="Which ideas should shape the game?"></textarea>
<details><summary>Generation prompt</summary><p class="prompt">{html.escape(row['prompt'])}</p></details></div></article>''')
        readme.extend([f'## {number:02d}. {row["name"].title()}' + (' — bonus concept' if row.get('bonus') else ''), '',
                       f'![Ideal {row["name"].title()} concept]({row["file"]})', '', brief, ''])
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SF neighborhood concepts</title><style>
:root{color-scheme:light;font-family:system-ui,-apple-system,sans-serif;color:#25342e;background:#f4f3ee}*{box-sizing:border-box}body{margin:0}main{max-width:1440px;margin:auto;padding:40px 24px 64px}.intro{max-width:850px}.eyebrow{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#5e7166}h1{font-size:clamp(28px,4vw,46px);line-height:1.1;letter-spacing:-.035em;margin:12px 0 16px}h2{font-size:21px;margin:7px 0 0}p{line-height:1.6}.intro p{color:#58665d}.tools{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:26px 0}button,select{font:inherit;padding:10px 14px;border:1px solid #c7cfc7;border-radius:5px;background:#fff;color:inherit;cursor:pointer}button{background:#284b3b;color:#fff;border-color:#284b3b}button:focus-visible,select:focus-visible,a:focus-visible,textarea:focus-visible{outline:3px solid #c68138;outline-offset:3px}.help{font-size:12px;color:#657269}.jump{display:flex;flex-wrap:wrap;gap:8px 18px;margin:0 0 30px;padding:15px 0;border-block:1px solid #d4dad1}.jump a{color:#46644f;font-size:12px;text-decoration:none}.jump a:hover{text-decoration:underline}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{background:white;border:1px solid #d5dcd3;border-radius:6px;overflow:hidden;scroll-margin-top:20px}article header{padding:20px}.art{display:block;background:#d9e2dc;line-height:0}.art img{display:block;width:100%;height:auto}.body{padding:0 20px 20px}.body>p{font-size:13px;color:#536456}.body label{font-size:12px;font-weight:600;display:block;margin:16px 0 7px}textarea{display:block;width:100%;resize:vertical;border:1px solid #c9d1c7;border-radius:4px;padding:10px;font:14px/1.5 system-ui;background:#fdfdfa;color:#263c2d}details{margin-top:16px;font-size:12px;color:#607266}summary{cursor:pointer}.prompt{font-size:12px;white-space:pre-wrap}.bottom{font-size:12px;color:#637267;margin-top:28px}a{color:#2d6547}[hidden]{display:none!important}@media(max-width:760px){main{padding:26px 14px 40px}.grid{grid-template-columns:1fr;gap:18px}article header{padding:16px}.body{padding:0 16px 16px}.tools>*{max-width:100%}.help{flex-basis:100%}}@media print{.tools,.jump,details,.bottom{display:none}.grid{display:block}main{padding:0}article{break-inside:avoid;page-break-after:always;margin:0;border:0}textarea{height:70px}.intro{page-break-after:always}}
</style><main><div class="intro"><span class="eyebrow">SF Mini Monsters / art direction / October 24, 2026</span><h1>SF neighborhood concepts</h1><p>18 campaign destinations + a Presidio bonus. Ideal designs generated from scratch, independent of the current game maps.</p><p><strong>Concept art, not current gameplay.</strong> Use these to choose architecture, street layouts, landmarks and planting. Their detail and perspective still need adaptation for the GBA game.</p></div>
<div class="tools"><select id="filter" aria-label="Filter concepts"><option value="all">All 19 concepts</option><option value="urban">Urban neighborhoods</option><option value="nature">Parks, coast & islands</option></select><button id="export">Export my notes</button><span class="help" id="note-status">Notes stay in this browser when available. Export to share.</span></div>
<nav class="jump" aria-label="Jump to a neighborhood">@@LINKS@@</nav><div class="grid">@@CARDS@@</div><p class="bottom">Built-in image_gen · <a href="prompts.json">Exact prompts and image hashes</a> · Click an image for its full-size PNG. No change to the public game.</p></main>
<script>
const key='sf-neighborhood-ideals-v1-notes';let notes={};try{notes=JSON.parse(localStorage.getItem(key)||'{}')}catch{}
for(const field of document.querySelectorAll('[data-note]')){field.value=notes[field.dataset.note]||'';field.addEventListener('input',()=>{notes[field.dataset.note]=field.value;try{localStorage.setItem(key,JSON.stringify(notes))}catch{document.querySelector('#note-status').textContent='Browser storage unavailable. Export your notes before closing.'}})}
document.querySelector('#filter').addEventListener('change',event=>{for(const card of document.querySelectorAll('article'))card.hidden=event.target.value!=='all'&&card.dataset.category!==event.target.value});
for(const link of document.querySelectorAll('.jump a'))link.addEventListener('click',()=>{document.querySelector('#filter').value='all';for(const card of document.querySelectorAll('article'))card.hidden=false});
document.querySelector('#export').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({collection:'sf-neighborhood-ideals-v1',exported_at:new Date().toISOString(),notes},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='sf-neighborhood-concept-notes.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
</script></html>'''
    (DIRECTORY / 'index.html').write_text(page.replace('@@LINKS@@', ''.join(links)).replace('@@CARDS@@', ''.join(cards)))
    (DIRECTORY / 'README.md').write_text('\n'.join(readme) + '\n')
    print(f'Built gallery and README for {len(rows)} concepts in {DIRECTORY}')


if __name__ == '__main__':
    main()
