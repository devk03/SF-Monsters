"""Faithful connection-margin atlases; no changed map cells, warps or scenery."""
import json
import struct
from pathlib import Path


def margin_points(plan, direction):
    width, height = len(plan['rows'][0]), len(plan['rows'])
    return [(x, y) for y in range(height) for x in range(width)
            if (direction == 'left' and x >= width - 7)
            or (direction == 'right' and x < 8)
            or (direction == 'up' and y >= height - 7)
            or (direction == 'down' and y < 7)]


def flip(tile, flags):
    return bytes(tile[(7-y if flags & 0x800 else y)*8 +
                      (7-x if flags & 0x400 else x)] for y in range(8) for x in range(8))


def primary_reservations(plans, engine):
    raw = (engine/'data/tilesets/primary/general/metatiles.bin').read_bytes()
    ids = {p['legend'][t][0] for p in plans for row in p['rows'] for t in row
           if p['legend'][t][0] < 512}
    # General water/sand/land-edge/waterfall/flower animations and the native
    # door scratch region live at432..511. Keep that entire range unavailable.
    tiles, banks = set(range(16)) | set(range(432,512)), set()
    bank_zero_tiles = set()
    for identifier in ids:
        for word in struct.unpack_from('<8H', raw, identifier*16):
            tiles.add(word & 1023); banks.add(word >> 12)
            if word >> 12 == 0:bank_zero_tiles.add(word & 1023)
    # Stock world terrain only addresses transparent tile0 through bank0.
    # Its backdrop color is retained; the other15 entries can hold seam colors.
    from PIL import Image
    image=Image.open(engine/'data/tilesets/primary/general/tiles.png')
    if bank_zero_tiles == {0} and all(image.getpixel((x,y))==0 for y in range(8) for x in range(8)):
        banks.discard(0)
    return tiles, banks


def make_atlases(plans, kits, reserved_tiles, reserved_banks):
    by_native = {p['native_id']:p for p in plans}
    pool = [i for i in range(432) if i not in reserved_tiles]
    result = []
    for plan in plans:
        if not plan['connections']:
            continue
        kit = kits[plan['tile_profile']]
        palettes = dict(kit['palettes'])
        free_banks = [i for i in range(14) if i not in reserved_banks and i not in palettes]
        packed_palettes = {}
        lookup = {}
        def register(tile, identifier):
            for flags in (0,0x400,0x800,0xc00):
                lookup.setdefault(flip(tile,flags),(identifier,flags))
        for i, tile in enumerate(kit['tiles']):register(tile,512+i)
        extra_tiles = []
        records, attributes = [], []
        record_ids = {(tuple(r),a):512+i for i,(r,a) in enumerate(zip(kit['records'],kit['attributes']))}
        def paint(pixels, palette):
            if not any(pixels):return pixels,6
            for bank,other in palettes.items():
                if other[2:]==palette[2:]:return pixels,bank
            colors=struct.unpack('<16H',palette)
            needed={colors[index] for index in set(pixels) if index}
            # Pack only colors actually used by this8x8 quadrant. This preserves
            # exact RGB555 pixels and avoids wasting a bank per source palette.
            for bank,other in palettes.items():
                available=struct.unpack('<16H',other)
                if needed <= set(available[1:]):
                    mapping={i:available.index(colors[i],1) for i in set(pixels) if i}
                    return bytes(mapping[p] if p else 0 for p in pixels),bank
            candidates=[(len(needed-set(values[1:])),bank) for bank,values in packed_palettes.items()
                        if len(needed-set(values[1:]))<=values[1:].count(None)]
            if candidates:_,bank=min(candidates)
            elif free_banks:
                bank=free_banks.pop(0);packed_palettes[bank]=[0]+[None]*15
            else:
                raise ValueError(f"{plan['world_id']}: faithful seam exceeds unused palette colors")
            values=packed_palettes[bank]
            for color in sorted(needed-set(values[1:])):values[values.index(None)]=color
            mapping={i:values.index(colors[i],1) for i in set(pixels) if i}
            return bytes(mapping[p] if p else 0 for p in pixels),bank
        neighbors = []
        for link in plan['connections']:
            other = by_native[link['map']]
            if other['tile_profile'] == plan['tile_profile']:
                continue
            foreign = kits[other['tile_profile']]
            used = {other['legend'][other['rows'][y][x]][0]
                    for x,y in margin_points(other,link['direction'])}
            mapping = list(range(512,1024))
            for metatile in sorted(used):
                if metatile < 512:continue  # Native water/falls/ground remain untouched.
                words = []
                for word in foreign['records'][metatile-512]:
                    pixels,bank = paint(foreign['tiles'][(word & 1023)-512],foreign['palettes'][word >> 12])
                    if pixels not in lookup:
                        if len(extra_tiles) >= len(pool):
                            raise ValueError(f"{plan['world_id']}: faithful seam exceeds free primary graphics slots")
                        register(pixels,pool[len(extra_tiles)]);extra_tiles.append(pixels)
                    tile, flags = lookup[pixels]
                    words.append(tile | ((word & 0xc00) ^ flags) | bank << 12)
                attribute = foreign['attributes'][metatile-512]
                key = tuple(words),attribute
                if key not in record_ids:
                    if len(kit['records'])+len(records) >= 512:
                        raise ValueError(f"{plan['world_id']}: faithful seam exceeds secondary metatile IDs")
                    record_ids[key] = 512+len(kit['records'])+len(records)
                    records.append(words);attributes.append(attribute)
                mapping[metatile-512] = record_ids[key]
            neighbors.append({'native_id':other['native_id'],'mapping':mapping,'used':sorted(used)})
        result.append({'world_id':plan['world_id'],'native_id':plan['native_id'],
                       'first':512+len(kit['records']),'records':records,'attributes':attributes,
                       'tiles':extra_tiles,'tile_slots':pool[:len(extra_tiles)],
                       'palettes':{b:struct.pack('<16H',*(v if v is not None else 0 for v in values))
                                   for b,values in packed_palettes.items()},'neighbors':neighbors})
    return result


def c_array(name, kind, values, width=16):
    values = list(values) or [0]
    return f'static const {kind} {name}[] = {{\n'+''.join(
        '    '+','.join(hex(v) for v in values[i:i+width])+',\n'
        for i in range(0,len(values),width))+'};\n'


def header(atlases):
    out = ['// Generated faithful connection margins. Primary terrain/animation slots are reserved.\n',
           '''struct SFSeamNeighbor { u8 group,num; const u16 *mapping; };
struct SFSeamAtlas {
    u8 group,num,neighborCount,paletteCount;
    u16 first,count,tileCount;
    const u16 *records,*attributes,*tileSlots,*paletteSlots,*palettes;
    const u8 *graphics;
    const struct SFSeamNeighbor *neighbors;
};
''']
    entries = []
    for i,a in enumerate(atlases):
        prefix = f'sSFSeam{i}'
        raw = bytes(v for tile in a['tiles'] for row in range(8) for x in range(0,8,2)
                    for v in [tile[row*8+x] | tile[row*8+x+1] << 4])
        out += [c_array(prefix+'Graphics','u8 ALIGNED(4)',raw),
                c_array(prefix+'Tiles','u16',a['tile_slots']),
                c_array(prefix+'Records','u16',(w for r in a['records'] for w in r)),
                c_array(prefix+'Attributes','u16',a['attributes']),
                c_array(prefix+'PaletteSlots','u16',a['palettes']),
                c_array(prefix+'Palettes','u16',(v for p in a['palettes'].values() for v in struct.unpack('<16H',p)))]
        neighbors = []
        for j,n in enumerate(a['neighbors']):
            name = prefix+f'Map{j}'
            out.append(c_array(name,'u16',n['mapping']))
            neighbors.append('{MAP_GROUP('+n['native_id']+'),MAP_NUM('+n['native_id']+'),'+name+'}')
        out.append('static const struct SFSeamNeighbor '+prefix+'Neighbors[] = {'+
                   ','.join(neighbors or ['{0,0,NULL}'])+'};\n')
        entries.append('{MAP_GROUP('+a['native_id']+'),MAP_NUM('+a['native_id']+'),'+
                       ','.join(map(str,(len(a['neighbors']),len(a['palettes']),a['first'],len(a['records']),len(a['tiles']))))+','+
                       ','.join(prefix+n for n in ('Records','Attributes','Tiles','PaletteSlots','Palettes','Graphics','Neighbors'))+'}')
    out.append('static const struct SFSeamAtlas sSFSeamAtlases[] = {\n'+',\n'.join(entries)+'\n};\n')
    out.append(RUNTIME)
    return ''.join(out)


RUNTIME = r'''
EWRAM_DATA static const struct SFSeamAtlas *sSFSeamCurrent = NULL;
EWRAM_DATA static bool8 sSFSeamRedraw = FALSE;
static void SFSeamSelect(void)
{
    u16 i;
    sSFSeamCurrent = NULL;
    for (i=0;i<ARRAY_COUNT(sSFSeamAtlases);i++)
        if (sSFSeamAtlases[i].group==gSaveBlock1Ptr->location.mapGroup
         && sSFSeamAtlases[i].num==gSaveBlock1Ptr->location.mapNum)
            sSFSeamCurrent=&sSFSeamAtlases[i];
}
static u16 SFSeamTranslate(const struct MapHeader *other,u16 block)
{
    u16 i,id=block & MAPGRID_METATILE_ID_MASK;
    if (!sSFSeamCurrent || id<512) return block;
    for (i=0;i<sSFSeamCurrent->neighborCount;i++)
    {
        const struct SFSeamNeighbor *n=&sSFSeamCurrent->neighbors[i];
        if (Overworld_GetMapHeaderByGroupAndId(n->group,n->num)==other)
            return (block & ~MAPGRID_METATILE_ID_MASK) | n->mapping[id-512];
    }
    return block;
}
const u16 *SFSeamMetatile(u16 id)
{
    if (sSFSeamCurrent && id>=sSFSeamCurrent->first && id-sSFSeamCurrent->first<sSFSeamCurrent->count)
        return sSFSeamCurrent->records+(id-sSFSeamCurrent->first)*8;
    return NULL;
}
static u16 SFSeamAttribute(u16 id)
{
    return sSFSeamCurrent->attributes[id-sSFSeamCurrent->first];
}
bool8 SFSeamTakeRedraw(void)
{
    bool8 result=sSFSeamRedraw;
    sSFSeamRedraw=FALSE;
    return result;
}
static void SFSeamLoadGraphics(void)
{
    u16 start,end;
    if (!sSFSeamCurrent) return;
    for (start=0;start<sSFSeamCurrent->tileCount;start=end)
    {
        for (end=start+1;end<sSFSeamCurrent->tileCount
             && sSFSeamCurrent->tileSlots[end]==sSFSeamCurrent->tileSlots[end-1]+1;end++);
        LoadBgTiles(2,sSFSeamCurrent->graphics+start*32,(end-start)*32,sSFSeamCurrent->tileSlots[start]);
    }
}
static void SFSeamLoadPalettes(void)
{
    u16 i;
    if (!sSFSeamCurrent) return;
    for (i=0;i<sSFSeamCurrent->paletteCount;i++)
        LoadPalette(sSFSeamCurrent->palettes+i*16+1,BG_PLTT_ID(sSFSeamCurrent->paletteSlots[i])+1,30);
}
'''


def apply_seams(engine, plans):
    from world_tiles import compile_kit
    kits = {p:compile_kit(profile=p) for p in {m.get('tile_profile','residential') for m in plans}}
    reserved_tiles,reserved_banks = primary_reservations(plans,engine)
    atlases = make_atlases(plans,kits,reserved_tiles,reserved_banks)
    (engine/'src/sf_world_seams.h').write_text(header(atlases))
    path = engine/'src/fieldmap.c'
    source = path.read_text()
    patches = [
        ('static void InitMapLayoutData(const struct MapHeader *mapHeader);',
         '#include "sf_world_seams.h"\n\nstatic void InitMapLayoutData(const struct MapHeader *mapHeader);'),
        ('    const struct MapLayout *mapLayout = mapHeader->mapLayout;\n',
         '    const struct MapLayout *mapLayout = mapHeader->mapLayout;\n    SFSeamSelect();\n'),
        ('    s32 i;\n    const u16 *src;\n    u16 *dest;\n    s32 mapWidth;',
         '    s32 i,j;\n    const u16 *src;\n    u16 *dest;\n    s32 mapWidth;'),
        ('        CpuCopy16(src, dest, width * 2);',
         '        for (j=0;j<width;j++) dest[j]=SFSeamTranslate(connectedMapHeader,src[j]);'),
        ('u16 GetMetatileAttributesById(u16 metatile)\n{',
         'u16 GetMetatileAttributesById(u16 metatile)\n{\n    if (SFSeamMetatile(metatile)) return SFSeamAttribute(metatile);'),
        ('        MoveMapViewToBackup(direction);',
         '        if (sSFSeamCurrent) {ClearSavedMapView();sSFSeamRedraw=TRUE;}\n'
         '        else MoveMapViewToBackup(direction);'),
        ('\n    CopyTilesetToVram(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);',
         '\n    CopyTilesetToVram(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);\n    SFSeamLoadGraphics();'),
        ('\n    CopyTilesetToVramUsingHeap(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);',
         '\n    CopyTilesetToVramUsingHeap(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);\n    SFSeamLoadGraphics();'),
        ('\n        CopyTilesetToVramUsingHeap(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);',
         '\n        CopyTilesetToVramUsingHeap(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);\n        SFSeamLoadGraphics();'),
        ('    LoadTilesetPalette(mapLayout->secondaryTileset, BG_PLTT_ID(NUM_PALS_IN_PRIMARY), (NUM_PALS_TOTAL - NUM_PALS_IN_PRIMARY) * PLTT_SIZE_4BPP);',
         '    LoadTilesetPalette(mapLayout->secondaryTileset, BG_PLTT_ID(NUM_PALS_IN_PRIMARY), (NUM_PALS_TOTAL - NUM_PALS_IN_PRIMARY) * PLTT_SIZE_4BPP);\n    SFSeamLoadPalettes();'),
    ]
    for before,after in patches:
        if source.count(before)!=1:raise ValueError('Pinned seam anchor changed: '+before)
        source=source.replace(before,after,1)
    path.write_text(source)
    path=engine/'src/field_camera.c';source=path.read_text()
    source=source.replace('EWRAM_DATA bool8 gUnusedBikeCameraAheadPanback',
        'const u16 *SFSeamMetatile(u16 id);\nbool8 SFSeamTakeRedraw(void);\n\nEWRAM_DATA bool8 gUnusedBikeCameraAheadPanback',1)
    before='        RedrawMapSlicesForCameraUpdate(&sFieldCameraOffset, deltaX * 2, deltaY * 2);'
    if source.count(before)!=1:raise ValueError('Pinned seam camera anchor changed')
    source=source.replace(before,'        if (SFSeamTakeRedraw()) DrawWholeMapView();\n        else '+before.strip(),1)
    before='    DrawMetatile(MapGridGetMetatileLayerTypeAt(x, y), metatiles + metatileId * NUM_TILES_PER_METATILE, offset);'
    after='''    {
        const u16 *seam=SFSeamMetatile(MapGridGetMetatileIdAt(x,y));
        DrawMetatile(MapGridGetMetatileLayerTypeAt(x,y),seam ? seam : metatiles+metatileId*NUM_TILES_PER_METATILE,offset);
    }'''
    if source.count(before)!=1:raise ValueError('Pinned seam metatile draw anchor changed')
    path.write_text(source.replace(before,after,1))
    summary = {'atlases':len(atlases),'reserved_primary_tiles':sorted(reserved_tiles),
               'reserved_primary_palettes':sorted(reserved_banks),
               'maps':[{'id':a['world_id'],'extra_tiles':len(a['tiles']),
                        'extra_metatiles':len(a['records']),'palette_slots':list(a['palettes'])}
                       for a in atlases]}
    (engine/'sf-world-seams.json').write_text(json.dumps(summary,indent=2)+'\n')
    return ['src/fieldmap.c','src/field_camera.c','src/sf_world_seams.h']
