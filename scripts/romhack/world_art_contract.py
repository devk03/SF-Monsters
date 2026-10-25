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
            if (any(type(n) is not int for n in (first,w,h)) or not 1<=w<=11 or not 1<=h<=8
                    or first<512 or first>=1024 or type(card['blocked']) is not bool
                    or card['behavior'] not in (0,0x80) or card['layer']!=1):
                raise ValueError('Invalid SF card extent/behavior')
            if card['behavior']==0x80 and not card['blocked']:
                raise ValueError('A native service counter must have solid collision')
            matrix=card.get('cells')
            if matrix is not None:
                if (not isinstance(matrix,list) or len(matrix)!=h
                        or any(not isinstance(row,list) or len(row)!=w for row in matrix)
                        or matrix[0][0]!=first
                        or any(type(tile) is not int or not 512<=tile<1024 for row in matrix for tile in row)):
                    raise ValueError('Invalid explicit SF card cell matrix')
                allocation=[tile for row in matrix for tile in row]
            else:
                if first+w*h>1024:raise ValueError('SF card allocation leaves native metatile range')
                allocation=range(first,first+w*h)
            semantics=(card['blocked'],card['behavior'] | card['layer']<<12)
            for tile in allocation:
                if tile in cells and (matrix is None or cells[tile]!=semantics):
                    raise ValueError('SF card metatile allocations overlap with incompatible semantics')
                cells[tile]=semantics
        result[name]=dict(profile,metatiles=cells)
    return result
