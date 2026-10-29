"""Faithful connection-margin atlases; no changed map cells, warps or scenery."""
import json
import struct
from pathlib import Path
from world_shared_primary import REQUIRED_METATILES, validate_general


def margin_points(plan, direction, source=None, offset=0):
    width, height = len(plan['rows'][0]), len(plan['rows'])
    points = [(x, y) for y in range(height) for x in range(width)
            if (direction == 'left' and x >= width - 7)
            or (direction == 'right' and x < 8)
            or (direction == 'up' and y >= height - 7)
            or (direction == 'down' and y < 7)]
    if source is None:
        return points
    # Mirror fieldmap.c's clipped copy into the source map's padded buffer.
    # A small connector cannot display an entire96-tile neighbor edge. Loading
    # off-buffer artwork wastes scarce native metatile/palette allocations.
    vertical = direction in ('left','right')
    span = len(source['rows']) if vertical else len(source['rows'][0])
    extra = 7 if vertical else 8
    return [(x,y) for x,y in points if -7 <= (y if vertical else x)+offset < span+extra]


def flip(tile, flags):
    return bytes(tile[(7-y if flags & 0x800 else y)*8 +
                      (7-x if flags & 0x400 else x)] for y in range(8) for x in range(8))


def primary_reservations(plans, engine):
    raw = (engine/'data/tilesets/primary/general/metatiles.bin').read_bytes()
    validate_general(raw)
    ids = {p['legend'][t][0] for p in plans for row in p['rows'] for t in row
           if p['legend'][t][0] < 512}
    ids.update(p.get('border_tile',11) for p in plans if p.get('border_tile',11)<512)
    ids.add(1)  # General grass can also be referenced beneath SF composite art.
    ids.update(REQUIRED_METATILES)
    # General water/sand/land-edge/waterfall/flower animations and the native
    # door scratch region live at432..511. Keep that entire range unavailable.
    # The NORMAL renderer also draws implicit background word0x3014: tile20,
    # palette3. It is not listed in any metatile record and must be reserved too.
    tiles, banks = set(range(16)) | {20} | set(range(432,512)), set()
    bank_zero_tiles = set();bank_usage={}
    for identifier in ids:
        bank_usage[identifier]=set()
        for word in struct.unpack_from('<8H', raw, identifier*16):
            tiles.add(word & 1023); banks.add(word >> 12)
            bank_usage[identifier].add(word >> 12)
            if word >> 12 == 0:bank_zero_tiles.add(word & 1023)
    # Stock world terrain only addresses transparent tile0 through bank0.
    # Its backdrop color is retained; the other15 entries can hold seam colors.
    from PIL import Image
    image=Image.open(engine/'data/tilesets/primary/general/tiles.png')
    if bank_zero_tiles == {0} and all(image.getpixel((x,y))==0 for y in range(8) for x in range(8)):
        banks.discard(0)
    partial={}
    rows=(engine/'data/tilesets/primary/general/palettes/03.pal').read_text().splitlines()[3:]
    colors=[sum((v>>3)<<(5*j) for j,v in enumerate(map(int,row.split()))) for row in rows]
    indices={image.getpixel((4*8+x,8+y)) for y in range(8) for x in range(8)}
    partial[3]={index:colors[index] for index in indices}
    return tiles, banks, partial, bank_usage


def make_atlases(plans, kits, reserved_tiles, reserved_banks, palette_locks=None, primary_banks=None):
    by_native = {p['native_id']:p for p in plans}
    native_metatiles=REQUIRED_METATILES|{p['legend'][t][0] for p in plans for row in p['rows'] for t in row
                                      if p['legend'][t][0]<512}
    native_metatiles|={p.get('border_tile',11) for p in plans if p.get('border_tile',11)<512}
    result = []
    for plan in plans:
        kit = kits[plan.get('tile_profile','residential')]
        own_all=kit.get('primary_tiles',{})
        own_ids={plan['legend'][t][0] for row in plan['rows'] for t in row if plan['legend'][t][0]>=512}
        if plan.get('border_tile',11)>=512:own_ids.add(plan['border_tile'])
        for link in plan['connections'] or []:
            other=by_native[link['map']]
            if other.get('tile_profile','residential')==plan.get('tile_profile','residential'):
                own_ids|={other['legend'][other['rows'][y][x]][0]
                          for x,y in margin_points(other,link['direction'],plan,link['offset'])
                          if other['legend'][other['rows'][y][x]][0]>=512}
        slots={word&1023 for identifier in own_ids for word in kit['records'][identifier-512]
               if word&1023<512 and word>>12>=6}
        if not slots<=own_all.keys():raise ValueError('Own map references unloaded SF primary art')
        own={slot:own_all[slot] for slot in sorted(slots)}
        if not plan['connections'] and not own:continue
        if set(own)&reserved_tiles:raise ValueError(plan['world_id']+': own SF art overwrites native primary graphics')
        used_secondary={word&1023 for identifier in own_ids for word in kit['records'][identifier-512]
                        if word&1023>=512}
        # A route only renders a subset of its district kit. Reuse secondary
        # slots absent from BOTH its layout and same-profile connection margins.
        pool=[i for i in range(432) if i not in reserved_tiles and i not in own]
        pool += [i for i in range(512,1024) if i not in used_secondary and i not in reserved_tiles]
        used_own_banks={word>>12 for identifier in own_ids for word in kit['records'][identifier-512]}
        palettes = {bank:raw for bank,raw in kit['palettes'].items() if bank in used_own_banks}
        active_ids={plan['legend'][t][0] for row in plan['rows'] for t in row if plan['legend'][t][0]<512}
        if plan.get('border_tile',11)<512:active_ids.add(plan.get('border_tile',11))
        if kit.get('uses_native_grass'):active_ids.add(1)
        for link in plan['connections'] or []:
            other=by_native[link['map']]
            if kits[other.get('tile_profile','residential')].get('uses_native_grass'):active_ids.add(1)
            active_ids|={other['legend'][other['rows'][y][x]][0] for x,y in margin_points(other,link['direction'],plan,link['offset'])
                         if other['legend'][other['rows'][y][x]][0]<512}
        active_banks=set(reserved_banks) if primary_banks is None else set().union(*(primary_banks[i] for i in active_ids))
        if 0 not in reserved_banks:active_banks.discard(0)
        free_banks = [i for i in range(14) if i not in active_banks and i not in palettes]
        packed_palettes = {}
        for bank,entries in (palette_locks or {}).items():
            if bank in free_banks:
                free_banks.remove(bank);packed_palettes[bank]=[0]+[None]*15
                for index,color in entries.items():packed_palettes[bank][index]=color
        lookup = {}
        def register(tile, identifier):
            for flags in (0,0x400,0x800,0xc00):
                lookup.setdefault(flip(tile,flags),(identifier,flags))
        for i, tile in enumerate(kit['tiles']):
            if 512+i in used_secondary:register(tile,512+i)
        for slot,tile in own.items():register(tile,slot)
        extra_tiles = []
        records, attributes = [], []
        assigned_ids=[]
        # Foreign margin records may use otherwise-unused primary metatile IDs.
        # Graphics slots and metatile IDs are independent hardware resources.
        # Preserve every authored/required General ID, including border IDs.
        free_ids=list(range(512+len(kit['records']),1024))+[
            i for i in range(1,512) if i not in native_metatiles]
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
                raise ValueError(f"{plan['world_id']}: faithful seam exceeds unused palette colors; active={sorted(active_banks)}, packed={[(b,v.count(None)) for b,v in packed_palettes.items()]}, needed={sorted(needed)}")
            values=packed_palettes[bank]
            for color in sorted(needed-set(values[1:])):values[values.index(None)]=color
            mapping={i:values.index(colors[i],1) for i in set(pixels) if i}
            return bytes(mapping[p] if p else 0 for p in pixels),bank
        neighbors = []
        for link in plan['connections'] or []:
            other = by_native[link['map']]
            if other.get('tile_profile','residential') == plan.get('tile_profile','residential'):
                continue
            foreign = kits[other.get('tile_profile','residential')]
            used = {other['legend'][other['rows'][y][x]][0]
                    for x,y in margin_points(other,link['direction'],plan,link['offset'])}
            mapping = list(range(512,1024))
            for metatile in sorted(used):
                if metatile < 512:continue  # Native water/falls/ground remain untouched.
                words = []
                for word in foreign['records'][metatile-512]:
                    if word&1023<512 and word>>12<6:
                        words.append(word);continue  # Pinned General grass is shared unchanged.
                    slot=word&1023
                    raw=foreign['tiles'][slot-512] if slot>=512 else foreign.get('primary_tiles',{}).get(slot)
                    if raw is None:raise ValueError('Foreign SF art references an unloaded primary graphic')
                    pixels,bank = paint(raw,foreign['palettes'][word >> 12])
                    if pixels not in lookup:
                        if len(extra_tiles) >= len(pool):
                            raise ValueError(f"{plan['world_id']}: faithful seam exceeds free primary graphics slots")
                        register(pixels,pool[len(extra_tiles)]);extra_tiles.append(pixels)
                    tile, flags = lookup[pixels]
                    words.append(tile | ((word & 0xc00) ^ flags) | bank << 12)
                attribute = foreign['attributes'][metatile-512]
                key = tuple(words),attribute
                if key not in record_ids:
                    if len(records)>=len(free_ids):raise ValueError('Faithful seam exhausts safe metatile IDs')
                    record_ids[key] = free_ids[len(records)]
                    assigned_ids.append(record_ids[key])
                    records.append(words);attributes.append(attribute)
                mapping[metatile-512] = record_ids[key]
            neighbors.append({'native_id':other['native_id'],'mapping':mapping,'used':sorted(used)})
        result.append({'world_id':plan['world_id'],'native_id':plan['native_id'],
                       'profile':plan.get('tile_profile','residential'),
                       'reserved_palettes':sorted(active_banks),
                       'secondary_graphics':b''.join(bytes(tile[y*8+x] | tile[y*8+x+1]<<4
                                                       for y in range(8) for x in range(0,8,2))
                                                  for tile in kit['tiles'])+bytes((512-len(kit['tiles']))*32),
                       'first':512+len(kit['records']),'records':records,'attributes':attributes,
                       'record_ids':assigned_ids,
                       'own_primary_slots':list(own),'foreign_tile_count':len(extra_tiles),
                       'tiles':list(own.values())+extra_tiles,'tile_slots':list(own)+pool[:len(extra_tiles)],
                       'palettes':{b:struct.pack('<16H',*(v if v is not None else 0 for v in values))
                                   for b,values in packed_palettes.items()},'neighbors':neighbors})
    return result


def c_array(name, kind, values, width=16):
    values = list(values) or [0]
    return f'static const {kind} {name}[] = {{\n'+''.join(
        '    '+','.join(hex(v) for v in values[i:i+width])+',\n'
        for i in range(0,len(values),width))+'};\n'


def header(atlases, borrowed_tiles=None, borrowed_demands=None):
    out = ['// Generated faithful connection margins. Primary terrain/animation slots are reserved.\n',
           '#include "dma3.h"\n',
           'const u16 gSFSeamLookupVersion = 2;\n',
           '''struct SFSeamNeighbor { u8 group,num; const u16 *mapping; };
struct SFSeamAtlas {
    u8 group,num,neighborCount,paletteCount;
    u16 first,count,tileCount;
    const u16 *records,*attributes,*tileSlots,*paletteSlots,*palettes;
    const u8 *graphics;
    const struct SFSeamNeighbor *neighbors;
    const u8 *secondaryGraphics;
    const u16 *recordLookup;
};
''']
    entries = [];bases={}
    for i,a in enumerate(atlases):
        prefix = f'sSFSeam{i}'
        if a['profile'] not in bases:
            bases[a['profile']]='sSFSeamBase'+str(len(bases))
            out.append(c_array(bases[a['profile']],'u8 ALIGNED(4)',a['secondary_graphics']))
        raw = bytes(v for tile in a['tiles'] for row in range(8) for x in range(0,8,2)
                    for v in [tile[row*8+x] | tile[row*8+x+1] << 4])
        out += [c_array(prefix+'Graphics','u8 ALIGNED(4)',raw),
                c_array(prefix+'Tiles','u16',a['tile_slots']),
                c_array(prefix+'Records','u16',(w for r in a['records'] for w in r)),
                c_array(prefix+'Attributes','u16',a['attributes']),
                c_array(prefix+'PaletteSlots','u16',a['palettes']),
                c_array(prefix+'Palettes','u16',(v for p in a['palettes'].values() for v in struct.unpack('<16H',p)))]
        lookup=[0]*1024
        for index,identifier in enumerate(a['record_ids']):lookup[identifier]=index+1
        out.append(c_array(prefix+'Lookup','u16',lookup))
        neighbors = []
        for j,n in enumerate(a['neighbors']):
            name = prefix+f'Map{j}'
            out.append(c_array(name,'u16',n['mapping']))
            neighbors.append('{MAP_GROUP('+n['native_id']+'),MAP_NUM('+n['native_id']+'),'+name+'}')
        out.append('static const struct SFSeamNeighbor '+prefix+'Neighbors[] = {'+
                   ','.join(neighbors or ['{0,0,NULL}'])+'};\n')
        entries.append('{MAP_GROUP('+a['native_id']+'),MAP_NUM('+a['native_id']+'),'+
                       ','.join(map(str,(len(a['neighbors']),len(a['palettes']),a['first'],len(a['records']),len(a['tiles']))))+','+
                       ','.join(prefix+n for n in ('Records','Attributes','Tiles','PaletteSlots','Palettes','Graphics','Neighbors'))+','+bases[a['profile']]+','+prefix+'Lookup}')
    out.append('static const struct SFSeamAtlas sSFSeamAtlases[] = {\n'+',\n'.join(entries)+'\n};\n')
    runtime = RUNTIME
    if borrowed_tiles:
        slots = sorted(borrowed_tiles)
        raw = bytes(v for slot in slots for row in range(8) for x in range(0,8,2)
                    for v in [borrowed_tiles[slot][row*8+x] | borrowed_tiles[slot][row*8+x+1] << 4])
        out.append(c_array('sSFSeamBorrowedNative','u8 ALIGNED(4)',raw))
        guarded = []
        by_world={a['world_id']:a for a in atlases}
        for name,needed in sorted((borrowed_demands or {}).items()):
            atlas=by_world[name]
            indices=[i for i,slot in enumerate(slots) if slot in needed]
            if set(needed)-set(slots):raise ValueError('Missing borrowed native pixels')
            calls=[];start=0
            while start<len(indices):
                end=start+1
                while (end<len(indices) and indices[end]==indices[end-1]+1
                       and slots[indices[end]]==slots[indices[end-1]]+1):end+=1
                index=indices[start]
                calls.append(f'        RequestDma3Copy(sSFSeamBorrowedNative+{index*32},(u8 *)BG_CHAR_ADDR(0)+{slots[index]*32},{(end-start)*32},1);')
                start=end
            native=atlas['native_id']
            guarded.append('    if (sSFSeamCurrent->group==MAP_GROUP('+native+') && '
                           'sSFSeamCurrent->num==MAP_NUM('+native+'))\n    {\n'+
                           '\n'.join(calls)+'\n    }')
        guarded='\n'.join(guarded)
        anchor = '    if (!sSFSeamCurrent || sSFSeamTransition) return;\n    for (start=0;'
        if runtime.count(anchor) != 1: raise ValueError('Borrowed native graphics anchor changed')
        runtime = runtime.replace(anchor, anchor.split('\n')[0]+'\n'+guarded+'\n    for (start=0;', 1)
    out.append(runtime)
    return ''.join(out)


RUNTIME = r'''
EWRAM_DATA static const struct SFSeamAtlas *sSFSeamCurrent = NULL;
EWRAM_DATA static bool8 sSFSeamRedraw = FALSE;
EWRAM_DATA static bool8 sSFSeamTransition = FALSE;
EWRAM_DATA static bool8 sSFSeamPendingVBlank = FALSE;
bool8 SFSeamDeferVBlank(void)
{
    if (!sSFSeamPendingVBlank) return FALSE;
    // IME may be restored after the original VBlank edge. Hold ALL field
    // graphics until a fresh edge; transferring only part mixes map scenes.
    if (REG_VCOUNT != 160) return TRUE;
    sSFSeamPendingVBlank=FALSE;
    return FALSE;
}
static void LoadTilesetPalette(struct Tileset const *tileset,u16 destOffset,u16 size);
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
    if (sSFSeamCurrent && id<1024 && sSFSeamCurrent->recordLookup[id])
        return sSFSeamCurrent->records+(sSFSeamCurrent->recordLookup[id]-1)*8;
    return NULL;
}
static u16 SFSeamAttribute(u16 id)
{
    return sSFSeamCurrent->attributes[sSFSeamCurrent->recordLookup[id]-1];
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
    // All generated art is word-aligned. LoadBgTiles queues16-bit DMA, which
    // can exhaust VBlank before the final BG3 tilemap request. Queue32-bit
    // copies so art and all three tilemaps finish in the same VBlank.
    if (!sSFSeamCurrent || sSFSeamTransition) return;
    for (start=0;start<sSFSeamCurrent->tileCount;start=end)
    {
        for (end=start+1;end<sSFSeamCurrent->tileCount
             && sSFSeamCurrent->tileSlots[end]==sSFSeamCurrent->tileSlots[end-1]+1;end++);
        RequestDma3Copy(sSFSeamCurrent->graphics+start*32,(u8 *)BG_CHAR_ADDR(0)+sSFSeamCurrent->tileSlots[start]*32,(end-start)*32,1);
    }
}
static void SFSeamLoadSecondary(void)
{
    // The stock heap-decompression task takes several frames. Its old tiles
    // cannot be paired with new records/palettes during those frames. A frozen
    // raw copy queues the complete secondary bank for the same next VBlank.
    if (!sSFSeamTransition) RequestDma3Copy(sSFSeamCurrent->secondaryGraphics,(u8 *)BG_CHAR_ADDR(0)+16384,16384,1);
}
static void SFSeamLoadPalettes(void)
{
    u16 i;
    if (!sSFSeamCurrent || sSFSeamTransition) return;
    for (i=0;i<sSFSeamCurrent->paletteCount;i++)
        LoadPalette(sSFSeamCurrent->palettes+i*16+1,BG_PLTT_ID(sSFSeamCurrent->paletteSlots[i])+1,30);
}
void SFSeamCommit(void)
{
    u16 ime;
    if (!sSFSeamTransition || !sSFSeamCurrent) return;
    // Queue the entire scene only after its camera offsets and buffers are ready.
    // Otherwise VBlank can interrupt the map-loading code between texture and
    // tilemap updates, briefly rendering old records against new graphics.
    ime=REG_IME;REG_IME=0;
    sSFSeamTransition=FALSE;
    SFSeamLoadSecondary();SFSeamLoadGraphics();
    LoadTilesetPalette(gMapHeader.mapLayout->primaryTileset,BG_PLTT_ID(0),NUM_PALS_IN_PRIMARY*PLTT_SIZE_4BPP);
    LoadTilesetPalette(gMapHeader.mapLayout->secondaryTileset,BG_PLTT_ID(NUM_PALS_IN_PRIMARY),
                      (NUM_PALS_TOTAL-NUM_PALS_IN_PRIMARY)*PLTT_SIZE_4BPP);
    SFSeamLoadPalettes();
    DoScheduledBgTilemapCopiesToVram();
    sSFSeamPendingVBlank=TRUE;
    REG_IME=ime;
}
'''


def patch_vblank(source):
    """Gate field graphics as one transaction; retain sound/IRQ bookkeeping."""
    patches = [
        ('#include "global.h"', '#include "global.h"\nbool8 SFSeamDeferVBlank(void);'),
        ('static void VBlankIntr(void)\n{',
         'static void VBlankIntr(void)\n{\n    bool8 deferGraphics=SFSeamDeferVBlank();'),
        ('    if (gMain.vblankCallback)\n        gMain.vblankCallback();',
         '    if (!deferGraphics && gMain.vblankCallback)\n        gMain.vblankCallback();'),
        ('    CopyBufferedValuesToGpuRegs();\n    ProcessDma3Requests();',
         '    if (!deferGraphics)\n    {\n        CopyBufferedValuesToGpuRegs();\n        ProcessDma3Requests();\n    }'),
    ]
    for before, after in patches:
        if source.count(before) != 1:
            raise ValueError('Pinned atomic VBlank anchor changed: ' + before)
        source = source.replace(before, after, 1)
    return source


def apply_seams(engine, plans, prototype_borrowed_primary=False):
    from world_tiles import compile_kit
    kits = {p:compile_kit(profile=p) for p in {m.get('tile_profile','residential') for m in plans}}
    reserved_tiles,reserved_banks,palette_locks,bank_usage = primary_reservations(plans,engine)
    borrowed = {76,77,78,79,92,93,94,95,107,123} if prototype_borrowed_primary else set()
    from world_shared_primary import PINNED_RESERVED
    if borrowed & PINNED_RESERVED:raise ValueError('Experimental borrow overlaps pinned native graphics')
    atlases = make_atlases(plans,kits,reserved_tiles-borrowed,reserved_banks,palette_locks,bank_usage)
    borrowed_tiles = None
    borrowed_demands = {}
    if prototype_borrowed_primary:
        from world_primary_restore import relocate_visible_borrows
        from world_native_loft import checked_blobs, HASHES
        from PIL import Image
        import hashlib,io
        general = (engine/'data/tilesets/primary/general/metatiles.bin').read_bytes()
        if hashlib.sha256(general).hexdigest() != '17974b0ba1bb9d105d5ba255c69a3b80d8484a26ea0b8ff22c6c6567c6c22910':
            raise ValueError('Experimental General metatile data is not the pinned native resource')
        atlases,borrowed_demands=relocate_visible_borrows(
            plans,kits,atlases,general,borrowed,forced={'twin_peaks':borrowed})
        name='data/tilesets/primary/general/tiles.png'
        image=Image.open(io.BytesIO(checked_blobs(Path(__file__).resolve().parents[2],{name:HASHES[name]})[name]))
        borrowed_tiles={slot:bytes(image.getpixel(((slot%16)*8+x,(slot//16)*8+y))
                          for y in range(8) for x in range(8)) for slot in borrowed}
    if any(p['connections'] and p['metadata']['weather']!='WEATHER_SUNNY' for p in plans):
        raise ValueError('Review weather-aware seam palette commit before adding other authored weather')
    (engine/'src/sf_world_seams.h').write_text(header(atlases,borrowed_tiles,borrowed_demands))
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
        ('        LoadMapFromCameraTransition(connection->mapGroup, connection->mapNum);',
         '        sSFSeamTransition=sSFSeamCurrent!=NULL;\n        LoadMapFromCameraTransition(connection->mapGroup, connection->mapNum);'),
        ('\n    CopyTilesetToVram(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);',
         '\n    if (sSFSeamCurrent) SFSeamLoadSecondary();\n    else CopyTilesetToVram(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);\n    SFSeamLoadGraphics();'),
        ('\n    CopyTilesetToVramUsingHeap(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);',
         '\n    if (sSFSeamCurrent) SFSeamLoadSecondary();\n    else CopyTilesetToVramUsingHeap(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);\n    SFSeamLoadGraphics();'),
        ('\n        CopyTilesetToVramUsingHeap(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);',
         '\n        if (sSFSeamCurrent) SFSeamLoadSecondary();\n        else CopyTilesetToVramUsingHeap(mapLayout->secondaryTileset, NUM_TILES_TOTAL - NUM_TILES_IN_PRIMARY, NUM_TILES_IN_PRIMARY);\n        SFSeamLoadGraphics();'),
        ('    LoadTilesetPalette(mapLayout->secondaryTileset, BG_PLTT_ID(NUM_PALS_IN_PRIMARY), (NUM_PALS_TOTAL - NUM_PALS_IN_PRIMARY) * PLTT_SIZE_4BPP);',
         '    if (!sSFSeamTransition)\n        LoadTilesetPalette(mapLayout->secondaryTileset, BG_PLTT_ID(NUM_PALS_IN_PRIMARY), (NUM_PALS_TOTAL - NUM_PALS_IN_PRIMARY) * PLTT_SIZE_4BPP);\n    SFSeamLoadPalettes();'),
    ]
    for before,after in patches:
        if source.count(before)!=1:raise ValueError('Pinned seam anchor changed: '+before)
        source=source.replace(before,after,1)
    path.write_text(source)
    path=engine/'src/field_camera.c';source=path.read_text()
    source=source.replace('EWRAM_DATA bool8 gUnusedBikeCameraAheadPanback',
        'const u16 *SFSeamMetatile(u16 id);\nbool8 SFSeamTakeRedraw(void);\nvoid SFSeamCommit(void);\n\nEWRAM_DATA bool8 gUnusedBikeCameraAheadPanback',1)
    before='void CameraUpdate(void)\n{'
    helper='''// Keep the exiting partial row/column during the connection step.
// The logical tile anchor advances before its pixel scroll catches up.
static void SFSeamRedrawView(int dx,int dy)
{
    u8 x=sFieldCameraOffset.xTileOffset,y=sFieldCameraOffset.yTileOffset;
    if (dx>0) sFieldCameraOffset.xTileOffset=(x+30)%32;
    if (dy>0) sFieldCameraOffset.yTileOffset=(y+30)%32;
    DrawWholeMapViewInternal(gSaveBlock1Ptr->pos.x-(dx>0),gSaveBlock1Ptr->pos.y-(dy>0),gMapHeader.mapLayout);
    sFieldCameraOffset.xTileOffset=x;sFieldCameraOffset.yTileOffset=y;
    sFieldCameraOffset.copyBGToVRAM=TRUE;
}

'''
    if source.count(before)!=1:raise ValueError('Pinned seam camera-update declaration changed')
    source=source.replace(before,helper+before,1)
    before='        RedrawMapSlicesForCameraUpdate(&sFieldCameraOffset, deltaX * 2, deltaY * 2);'
    if source.count(before)!=1:raise ValueError('Pinned seam camera anchor changed')
    source=source.replace(before,'        if (SFSeamTakeRedraw()) SFSeamRedrawView(deltaX,deltaY);\n        else '+before.strip(),1)
    before='    gTotalCameraPixelOffsetY -= movementSpeedY;'
    if source.count(before)!=1:raise ValueError('Pinned seam pixel-offset commit anchor changed')
    source=source.replace(before,before+'\n    SFSeamCommit();',1)
    before='    DrawMetatile(MapGridGetMetatileLayerTypeAt(x, y), metatiles + metatileId * NUM_TILES_PER_METATILE, offset);'
    after='''    {
        const u16 *seam=SFSeamMetatile(MapGridGetMetatileIdAt(x,y));
        DrawMetatile(MapGridGetMetatileLayerTypeAt(x,y),seam ? seam : metatiles+metatileId*NUM_TILES_PER_METATILE,offset);
    }'''
    if source.count(before)!=1:raise ValueError('Pinned seam metatile draw anchor changed')
    path.write_text(source.replace(before,after,1))
    summary = {'borrowed_native_demands':borrowed_demands, 'atlases':len(atlases),'reserved_primary_tiles':sorted(reserved_tiles),
               'reserved_primary_palettes':sorted(reserved_banks),
               'reserved_primary_palette_entries':palette_locks,
               'primary_palette_banks_by_metatile':{i:sorted(b) for i,b in bank_usage.items()},
               'maps':[{'id':a['world_id'],'extra_tiles':len(a['tiles']),
                        'own_primary_slots':a['own_primary_slots'],
                        'foreign_tiles':a['foreign_tile_count'],
                        'tile_slots':a['tile_slots'],'record_ids':a['record_ids'],
                        'extra_metatiles':len(a['records']),'palette_slots':list(a['palettes']),
                        'reserved_primary_palettes':a['reserved_palettes']}
                       for a in atlases]}
    (engine/'sf-world-seams.json').write_text(json.dumps(summary,indent=2)+'\n')
    path=engine/'src/main.c'
    path.write_text(patch_vblank(path.read_text()))
    return ['src/fieldmap.c','src/field_camera.c','src/sf_world_seams.h','src/main.c']
