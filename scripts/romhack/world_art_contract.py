"""Independent behavior/allocation contract for original SF native art profiles."""
import json
import re
from pathlib import Path

PATH=Path(__file__).resolve().parents[2]/'romhack/world/art-contract.json'


def load_profiles():
    data=json.loads(PATH.read_text())
    if data['schema_version']!=1:raise ValueError('Unsupported SF art contract')
    result={}
    for name,profile in data['profiles'].items():
        if not re.fullmatch('gTileset_[A-Za-z0-9]+',profile['secondary']):
            raise ValueError('Invalid native secondary tileset binding')
        cells={}
        for card in profile['cards'].values():
            first,w,h=card['first'],card['width'],card['height']
            if (any(type(n) is not int for n in (first,w,h)) or not 1<=w<=11 or not 1<=h<=5
                    or first<512 or first+w*h>1024 or type(card['blocked']) is not bool
                    or card['behavior'] not in (0,0x80) or card['layer']!=1):
                raise ValueError('Invalid SF card extent/behavior')
            if card['behavior']==0x80 and not card['blocked']:
                raise ValueError('A native service counter must have solid collision')
            for tile in range(first,first+w*h):
                if tile in cells:raise ValueError('SF card metatile allocations overlap')
                cells[tile]=(card['blocked'],card['behavior'] | card['layer']<<12)
        result[name]=dict(profile,metatiles=cells)
    return result
