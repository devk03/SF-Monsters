#!/usr/bin/env python3
"""Read-only source inventory, not a proof that any metatile is safe to reclaim."""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/romhack'))

from generate_world import generate
from world_tiles import FIRST_METATILE, PROFILES, compile_kit

LIMITATIONS = [
    'Generated source map rows and border IDs only; no native runtime or dynamic metatile proof.',
    'No connection-margin or seam allocation proof.',
    'No contributor module, future content, or saved-game compatibility proof.',
    'Unused map IDs and duplicate records are not automatically safe to remove or renumber.',
]


def audit_profile(kit, plans):
    records, attributes = kit['records'], kit['attributes']
    if len(records) != len(attributes):
        raise ValueError('Record and attribute counts differ')
    allocated = set(range(FIRST_METATILE, FIRST_METATILE + len(records)))
    groups = defaultdict(list)
    for index, (record, attribute) in enumerate(zip(records, attributes)):
        groups[(tuple(record), attribute)].append(FIRST_METATILE + index)
    duplicates = [dict(ids=ids, record=list(record), attribute=attribute)
                  for (record, attribute), ids in groups.items() if len(ids) > 1]
    duplicates.sort(key=lambda group: group['ids'][0])
    cards = {name: sorted({tile for row in card['tiles'] for tile in row})
             for name, card in sorted(kit['catalog'].items())}
    owned = set().union(*(set(ids) for ids in cards.values())) if cards else set()
    maps = {}
    for plan in sorted(plans, key=lambda item: item['world_id']):
        ids = {plan['legend'][token][0] for row in plan['rows'] for token in row}
        border = plan.get('border_metatiles', [plan.get('border_tile', 11)])
        ids.update(border)
        maps[plan['world_id']] = sorted(ids & allocated)
    used = set().union(*(set(ids) for ids in maps.values())) if maps else set()
    return {
        'record_count': len(records),
        'allocated_ids': sorted(allocated),
        'duplicate_records': duplicates,
        'map_used_ids': sorted(used),
        'map_unused_ids': sorted(allocated - used),
        'map_used_ids_by_map': maps,
        'card_owned_ids': sorted(owned),
        'card_unowned_ids': sorted(allocated - owned),
        'card_owned_ids_by_card': cards,
    }


def audit(manifest):
    plans = generate(manifest)
    profiles = {}
    for profile in sorted(PROFILES):
        selected = [plan for plan in plans if plan.get('tile_profile', 'residential') == profile]
        profiles[profile] = audit_profile(compile_kit(profile=profile), selected)
    return {'schema_version': 1, 'limitations': LIMITATIONS, 'profiles': profiles}


def main():
    manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
    print(json.dumps(audit(manifest), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
