"""Build a private PDF and self-contained feedback gallery from native captures."""
import argparse
import base64
import html
import json
import hashlib
import shutil
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
INK, MUTED = '#24342e', '#65736c'
PAPER, LINE = '#f5f4ef', '#d5d9d2'


def image_uri(path):
    return 'data:image/png;base64,'+base64.b64encode(Path(path).read_bytes()).decode()


def make_pdf(data, output, review_date):
    version=data['version'].split('-')[0].replace('0.0.','v')
    c = canvas.Canvas(str(output), pagesize=(792, 612), pageCompression=1)
    c.setTitle('SF Mini Monsters - all-town review - '+version)
    c.setAuthor('SF Mini Monsters development review')
    page = 0
    count=len(data['areas']);sheets=(count+5)//6
    has_presidio=any(a['id']=='presidio' for a in data['areas'])
    total_pages=1+sheets+1+count+int(not has_presidio)+1

    def text(value, x, y, size=10, color=INK, bold=False):
        c.setFillColor(HexColor(color))
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
        c.drawString(x, y, value)

    def paragraph(value, x, y, width, size=10, leading=14, color=INK):
        for line in simpleSplit(value, 'Helvetica', size, width):
            text(line, x, y, size, color)
            y -= leading
        return y

    def begin(title, subtitle, key):
        nonlocal page
        page += 1
        c.setFillColor(HexColor(PAPER)); c.rect(0, 0, 792, 612, fill=1, stroke=0)
        c.bookmarkPage(key); c.addOutlineEntry(title, key, 0)
        text(title, 28, 580, 19, bold=True)
        text(subtitle, 28, 560, 9, MUTED)
        c.setStrokeColor(HexColor(LINE)); c.line(28, 26, 764, 26)
        text('SF MINI MONSTERS / PRIVATE '+version+' / '+review_date, 28, 13, 7, MUTED)
        text(str(page)+' / '+str(total_pages), 734, 13, 7, MUTED)

    def picture(path, x, y, w, h):
        iw,ih=Image.open(path).size
        scale=min(w/iw,h/ih)
        c.drawImage(ImageReader(str(path)),x+(w-iw*scale)/2,y+(h-ih*scale)/2,width=iw*scale,height=ih*scale)

    def contacts(areas, title, key, missing=False):
        begin(title, 'Full backgrounds at a glance. Click a town to jump to its detailed page.', key)
        for i, area in enumerate(areas):
            x, y = 28+(i % 3)*248, 336-(i // 3)*236
            text(f"{area['order']:02d}  {area['label']}", x, y+181, 10, bold=True)
            picture(area['map'], x, y, 232, 174)
            text(area['category'].upper()+' / '+str(area['dimensions'][0])+' x '+str(area['dimensions'][1])+' tiles', x, y-13, 7, MUTED)
            c.linkRect('', 'area_'+area['id'], (x, y-16, x+232, y+194), thickness=0)
        if missing:
            x, y = 524, 100
            c.setStrokeColor(HexColor(LINE)); c.rect(x, y, 232, 174)
            text('PRESIDIO HEIGHTS', x+14, y+140, 11, bold=True)
            paragraph('Requested, but no playable map exists yet. It is not the Pacific Heights map.', x+14, y+112, 204, 11, 16)
            text('NOT BUILT', x+14, y+25, 9, '#99533b', True)
        c.showPage()

    begin('The SF world, as built.', 'A complete visual review of the current private cartridge - not a concept-art proposal.', 'cover')
    text(str(count)+' places to critique', 28, 501, 30, bold=True)
    y = paragraph('Every current destination has a full map and actual GBA views. The full maps show the background, without people; the gameplay images show the actors and camera scale.', 28, 451, 270, 12, 18)
    y = paragraph('Do the towns look different? Circulation, frontage mixes and native terrain now vary. Remaining gaps include landmark massing, neighborhood-specific parcels and believable elevation.', 28, y-20, 270, 12, 18)
    paragraph('Presidio / Presidio Heights is a separate playable destination with wooded campus and residential areas.' if has_presidio else 'Presidio Heights is not implemented. Pacific Heights is a different current destination. Neither is silently substituted for the other here.', 28, y-20, 270, 11, 16, '#99533b')
    guide = Path(data['areas'][0]['map'])
    picture(guide, 328, 190, 436, 291)
    text('Actual expanded Dogpatch background', 328, 173, 9, MUTED)
    urban=sum(a['category']=='urban' for a in data['areas']);nature=count-urban
    text(f'{urban} URBAN AREAS   /   {nature} NATURE OR HYBRID AREAS   /   8 RESERVED GYM SITES', 28, 99, 11, bold=True)
    paragraph('Start with the contact sheets. Then mark each detailed page: what works, what feels wrong, and the one change that would most improve its identity. Use the companion offline gallery to save and export typed feedback.', 28, 72, 736, 10, 14)
    c.showPage()
    for n in range(sheets):
        contacts(data['areas'][n*6:n*6+6], 'All destinations / '+str(n+1)+' of '+str(sheets), 'contact_'+str(n))
    contacts([a for a in data['areas'] if a['category']=='nature'], 'Nature, coast and wooded campus / compare current areas', 'nature', not has_presidio)
    for area in data['areas']:
        badge = ' / Gym '+str(area['gym'])+' site' if area['gym'] else ''
        begin(f"{area['order']:02d}  {area['label']}",
              area['category'].title()+' / '+' x '.join(map(str,area['dimensions']))+' tiles / '+str(area['residents'])+' current actors'+badge,
              'area_'+area['id'])
        picture(area['map'], 28, 168, 512, 384)
        text('ACTUAL GBA VIEWS', 560, 550, 7, MUTED, True)
        views = area['views']
        selected = area.get('featured_views') or [views[0],views[-1]]
        for i, path in enumerate(selected):
            picture(path, 560, 402-i*148, 204, 136)
        paragraph('Background map at left. People, animation and camera scale are represented by the actual gameplay captures above.', 560, 227, 204, 8, 11, MUTED)
        c.setFillColor(HexColor('#ffffff')); c.rect(28, 37, 736, 112, fill=1, stroke=0)
        text('CURRENT CRITIQUE', 40, 130, 8, MUTED, True)
        paragraph(area['critique'], 40, 113, 345, 10, 14)
        text('YOUR NOTES / strongest change first', 412, 130, 8, MUTED, True)
        c.setStrokeColor(HexColor(LINE))
        for y in (105, 82, 59): c.line(412, y, 750, y)
        c.showPage()
    if not has_presidio:
        begin('Requested, but missing: Presidio Heights', 'There is no current playable map to review for this destination.', 'presidio_missing')
        paragraph('Presidio Heights has no playable map in this candidate. Pacific Heights remains a separate destination.', 28, 510, 450, 14, 20)
        text('Planning notes for its eventual map', 28, 375, 18, bold=True)
        for label,y in [('Recognizable landmarks?',333),('Connections?',244),('Planting and activities?',155)]:
            text(label,28,y,12);c.setStrokeColor(HexColor(LINE));c.line(28,y-30,480,y-30)
        c.showPage()
    begin('Critique priorities', 'These are development observations, not user approval or a quality score.', 'priorities')
    priorities = [
        ('Street composition', 'Districts have distinct multi-block circulation, but many housing bands still repeat mechanically. Compose purposeful parcels, entrances and local gathering spaces.'),
        ('Nature and topography', 'Native forest and grass replace the invented checkerboard. Review trail widths, canopy edges, useful clearings, open ridges and believable terrain height.'),
        ('Building massing', 'Paint and window variations help, but Mission Bay, Financial District and the ballpark need stronger architectural differences and bigger landmark roles.'),
        ('Waterfront identity', 'Coast and island boundaries now include sea and piers. Their shore transitions, views and destination placement still need deliberate composition.'),
        ('Campus identity' if has_presidio else 'Missing geography',
         'The separate Presidio / Presidio Heights destination is now playable. Its campus landmark, stair gardens and overlooks still need a stronger composition.' if has_presidio else
         'Presidio Heights and the Presidio have no current playable maps. Their placement and scope need to be added explicitly before implementation.'),
        ('Keep improved basics', 'Keep neutral sidewalks, continuous crosswalk paint, complete facade edges, dense frontage and visible pedestrian paths. The user liked this direction; that is not whole-town approval.'),
    ]
    y = 513
    for title, body in priorities:
        text(title, 28, y, 13, bold=True)
        y = paragraph(body, 230, y, 525, 11, 15)-24
    paragraph('This packet uses private ' + version + '. The public website remains v92. Browser audio and full foreground-route acceptance are still open. Full maps are extracted from native VRAM/palettes and compiled geometry; gameplay views come from a matching controller-only tour. '+data.get('runtime_note',''), 28, 86, 736, 9, 13, MUTED)
    c.showPage()
    if page != total_pages: raise ValueError('Unexpected PDF page count')
    c.save()


def make_gallery(data, output, pdf_name, *, linked_images=False):
    cards, index = [], []
    esc = html.escape
    def source(path):
        if not linked_images:return image_uri(path)
        path=Path(path);asset=hashlib.sha256(path.read_bytes()).hexdigest()[:16]+'-'+path.name
        folder=output.parent/'assets';folder.mkdir(exist_ok=True)
        target=folder/asset
        if not target.exists():shutil.copyfile(path,target)
        return 'assets/'+asset
    for area in data['areas']:
        name, identifier = esc(area['label']), area['id']
        index.append(f'<a href="#{identifier}" data-category="{area["category"]}"><img src="{source(area["map"])}" alt=""><span>{area["order"]:02d} {name}</span></a>')
        photos = ''.join(f'<img src="{source(path)}" alt="Actual GBA view of {name}" loading="lazy">' for path in area['views'])
        notes = ''.join(f'<label>{label}<textarea data-note="{key}" rows="3"></textarea></label>' for key,label in [('works','What works?'),('wrong','What feels wrong?'),('change','What should change first?')])
        reference=area.get('concept_reference')
        concept=(f'<figure><img class="map" src="{source(reference)}" alt="Expanded design concept for {name}"><figcaption>Expanded concept reference - generated design, not gameplay.</figcaption></figure>' if reference else '')
        cards.append(f'''<section id="{identifier}" data-category="{area['category']}">
<div class="section-title"><div><small>{area['category'].upper()} / {area['order']:02d}</small><h2>{name}</h2></div><a href="#top">Back to index</a></div>
<div class="reference-pair"><figure><img class="map" src="{source(area['map'])}" alt="Full current map of {name}"><figcaption>Actual native background / {area['dimensions'][0]} x {area['dimensions'][1]} tiles. Actors appear in gameplay views below.</figcaption></figure>{concept}</div>
<div class="assessment"><h3>Current critique</h3><p>{esc(area['critique'])}</p><p class="muted">{esc(area['character'].capitalize())}</p><h3>Connections</h3><p class="muted">{esc('; '.join(area['connections']))}</p></div>
<details><summary>Actual in-game views ({len(area['views'])})</summary><div class="photos">{photos}</div></details><div class="notes">{notes}</div></section>''')
    template = Path(__file__).with_name('world_review_template.html').read_text()
    metadata = json.dumps({'version':data['version'],'rom_sha256':data['rom_sha256']}).replace('<','\\u003c')
    has_presidio=any(a['id']=='presidio' for a in data['areas'])
    if has_presidio:
        start=template.index('<section id="presidio_heights"');end=template.index('<footer>',start)
        template=template[:start]+template[end:]
    replacements={'@@INDEX@@':''.join(index),'@@CARDS@@':''.join(cards),'@@METADATA@@':metadata,
        '@@PDF@@':pdf_name,'@@VERSION@@':data['version'],'@@COUNT@@':str(len(data['areas'])),
        '@@URBAN@@':str(sum(a['category']=='urban' for a in data['areas'])),
        '@@NATURE@@':str(sum(a['category']=='nature' for a in data['areas'])),
        '@@PRESIDIO_NOTICE@@':('Presidio / Presidio Heights is now a separate playable wooded-campus destination. Visual acceptance remains pending.' if has_presidio else 'Presidio Heights is not implemented. Pacific Heights is a separate destination.'),
        '@@PRESIDIO_LINK@@':('<a class="button" href="#presidio">Presidio / Presidio Heights</a>' if has_presidio else '<a class="button" href="#presidio_heights">Presidio Heights - missing</a>')}
    replacements['@@RUNTIME_NOTE@@']=esc(data.get('runtime_note',''))
    for before,after in replacements.items():template=template.replace(before,after)
    output.write_text(template)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--review-date', required=True)
    parser.add_argument('--output-root',type=Path,default=ROOT/'output',help='Use an ignored private folder for native captures')
    parser.add_argument('--linked-images',action='store_true',help='Copy image assets beside the gallery instead of embedding large data URLs')
    parser.add_argument('--runtime-note',default='',help='Known runtime acceptance limitation to include in the review')
    args = parser.parse_args()
    data = json.loads(args.data.read_text())
    data['runtime_note']=args.runtime_note
    folder = args.output_root.resolve(); (folder/'pdf').mkdir(parents=True, exist_ok=True)
    (folder/'review').mkdir(parents=True, exist_ok=True)
    version=data['version'].split('-')[0].replace('0.0.','v')
    pdf = folder/'pdf'/('sf-world-review-'+version+'.pdf')
    make_pdf(data, pdf, args.review_date)
    gallery = folder/'review'/('sf-world-review-'+version+'.html')
    make_gallery(data, gallery, '../pdf/'+pdf.name,linked_images=args.linked_images)
    for category in ('urban', 'nature'):
        areas = [a for a in data['areas'] if a['category']==category]
        width, height = 256, 214
        sheet = Image.new('RGB', (width*3, height*((len(areas)+2)//3)), PAPER)
        draw = ImageDraw.Draw(sheet)
        for i, area in enumerate(areas):
            x, y = i%3*width, i//3*height
            image = Image.open(area['map']).resize((256,round(256*area['dimensions'][1]/area['dimensions'][0])), Image.Resampling.NEAREST)
            sheet.paste(image, (x,y+22))
            draw.text((x+4,y+5), area['label'], fill=INK)
        sheet.save(folder/'review'/f'{category}-overview.png')
    print(pdf); print(gallery)


if __name__ == '__main__':
    main()
