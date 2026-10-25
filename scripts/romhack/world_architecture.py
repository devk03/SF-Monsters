"""Original native SF fronts: flat walkups, shop awnings and industrial lofts."""
import struct


def district_palette(original, profile):
    """Material families share roof/glass colors but have different wall paint."""
    colors=list(struct.unpack('<16H',original))
    materials={
        'industrial':{7:(22,11,9),10:(23,21,17)},
        'civic':{7:(24,25,26),10:(28,28,26)},
        'culture':{7:(27,16,14),10:(29,25,18)},
        'stadium':{7:(24,13,10),10:(28,24,18)},
    }
    for index,rgb in materials.get(profile,{}).items():
        colors[index]=sum(v<<(c*5) for c,v in enumerate(rgb))
    return struct.pack('<16H',*colors)


def paint_palette(original, scheme):
    colors=list(struct.unpack('<16H',original))
    paints={
        'sage':{5:(29,28,24),6:(18,19,16),7:(18,23,17),8:(10,15,11),
                9:(14,18,14),10:(25,28,23),11:(15,20,22)},
        'slate':{5:(28,28,27),6:(17,18,20),7:(17,21,25),8:(9,12,17),
                 9:(13,17,22),10:(23,25,28),11:(20,22,19)},
    }
    for i,rgb in paints[scheme].items():colors[i]=sum(v<<(c*5) for c,v in enumerate(rgb))
    # Preserve the original stone/cornice colors. Only wall-material indices
    # change; unchanged glass, roofs and trim can share exact metatile records.
    colors[5:7]=struct.unpack('<16H',original)[5:7]
    return struct.pack('<16H',*colors)


# Forms describe architecture, never a paint name. Repeated window/cornice
# modules align to native 8px boundaries so eight forms fit a GBA street kit.
FORMS = ('walkup', 'shophouse', 'workshop', 'gable', 'deco',
         'flats', 'arcade', 'duplex')


def fronts(profile):
    from world_rich_facades import fronts as detailed_fronts
    return detailed_fronts(profile)
