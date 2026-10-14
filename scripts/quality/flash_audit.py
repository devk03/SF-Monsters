"""Read-only semantic audit of supported SF Flash saves; never repair or rewrite them."""
import argparse
import hashlib
from itertools import permutations
import json
from pathlib import Path
import struct

PAYLOADS = [3884, 3968, 3968, 3968, 3848] + [3968] * 8 + [2000]
POCKETS = {'items': (0x560, 30), 'key_items': (0x5d8, 30), 'balls': (0x650, 16),
           'moves': (0x690, 64), 'berries': (0x790, 46)}
ORDERS = list(permutations('GAEM'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unpack_slot(data, slot):
    sections, counter = {}, None
    for index in range(14):
        sector = data[(slot * 14 + index) * 4096:(slot * 14 + index + 1) * 4096]
        ident, checksum, signature, current = struct.unpack_from('<HHII', sector, 4084)
        if ident >= 14 or ident in sections or signature != 0x08012025:
            return None
        if counter is not None and counter != current:
            return None
        counter = current
        payload = sector[:PAYLOADS[ident]]
        total = sum(struct.unpack('<' + 'I' * (len(payload) // 4), payload)) & 0xffffffff
        if (total + (total >> 16)) & 65535 != checksum:
            return None
        sections[ident] = payload
    return counter, sections


def decode_mon(data, boxed=False):
    if len(data) != (80 if boxed else 100):
        raise ValueError('Invalid native Pokemon size.')
    pid, owner = struct.unpack_from('<II', data)
    plain = struct.pack('<12I', *[word ^ pid ^ owner for word in struct.unpack_from('<12I', data, 32)])
    if (sum(struct.unpack('<24H', plain)) & 65535) != struct.unpack_from('<H', data, 28)[0]:
        raise ValueError('Pokemon encrypted-data checksum failed.')
    fields = {name: plain[index * 12:(index + 1) * 12] for index, name in enumerate(ORDERS[pid % 24])}
    species = struct.unpack_from('<H', fields['G'])[0]
    if species == 0:
        return None
    result = {'species': species, 'personality': pid, 'owner': owner,
              'held_item': struct.unpack_from('<H', fields['G'], 2)[0],
              'moves': list(struct.unpack('<4H', fields['A'][:8])), 'pp': list(fields['A'][8:12]),
              'all_native_bytes_sha256': sha(data)}
    if not boxed:
        result.update({'level': data[84], 'hp': struct.unpack_from('<H', data, 86)[0],
                       'max_hp': struct.unpack_from('<H', data, 88)[0], 'status': struct.unpack_from('<I', data, 80)[0]})
    return result


def audit_bytes(data):
    if len(data) != 131072:
        raise ValueError('Use a native128KiB Flash save.')
    choices = [(slot, parsed) for slot in (0, 1) if (parsed := unpack_slot(data, slot)) is not None]
    if not choices:
        raise ValueError('Neither rotating Flash slot is complete and valid.')
    selected, (counter, sections) = choices[0]
    if len(choices) == 2:
        other = choices[1][1][0]
        use_other = (counter == 0xffffffff and other == 0) or (
            {counter, other} != {0, 0xffffffff} and other > counter)
        if use_other:
            selected, (counter, sections) = choices[1]
    native_slot = counter % 2
    native = next((parsed for slot, parsed in choices if slot == native_slot), None)
    if native is None or native[0] != counter:
        raise ValueError('Selected Flash counter does not match the native physical slot.')
    selected, (counter, sections) = native_slot, native
    save2 = sections[0]
    save1 = b''.join(sections[index] for index in range(1, 5))
    pc = b''.join(sections[index] for index in range(5, 14))
    if struct.unpack_from('<HH', save1, 0x158c) != (0x5346, 1):
        raise ValueError('Latest valid slot is not a supported SF save.')
    key = struct.unpack_from('<I', save2, 0xac)[0]
    if struct.unpack_from('<H', save2, 14)[0] > 999 or any(save2[index] >= 60 for index in (16, 17, 18)):
        raise ValueError('Saved playtime exceeds native field bounds.')
    party_count = save1[0x234]
    if not 1 <= party_count <= 6:
        raise ValueError('This campaign audit requires one to six party monsters.')
    party_raw = save1[0x238:0x490]
    party = [decode_mon(party_raw[index * 100:(index + 1) * 100]) for index in range(party_count)]
    if any(mon is None for mon in party):
        raise ValueError('Saved party count includes an empty slot.')
    stored = []
    for index in range(420):
        mon = decode_mon(pc[4 + index * 80:4 + (index + 1) * 80], True)
        if mon:
            stored.append({'box': index // 30, 'slot': index % 30, **mon})
    bags = {name: [[item, quantity ^ (key & 65535)] for item, quantity in
             (struct.unpack_from('<HH', save1, offset + index * 4) for index in range(count))]
            for name, (offset, count) in POCKETS.items()}
    stats = [word ^ key for word in struct.unpack_from('<64I', save1, 0x159c)]
    owned, seen = save2[0x28:0x5c], save2[0x5c:0x90]
    first, second = save1[0x988:0x9bc], save1[0x3b24:0x3b58]
    flags = save1[0x1270:0x139c]
    flag = lambda ident: bool(flags[ident // 8] & (1 << (ident % 8)))
    domains = {'trainer': (save2[:9] + save2[10:14]).hex(), 'settings': save2[0x13:0x18].hex(),
        'warp_flags': save2[9], 'location_and_warps': save1[:0x34].hex(),
        'pokedex': save2[0x18:0x90].hex(), 'seen1': first.hex(), 'seen2': second.hex(),
        'party_count': party_count, 'party_all600_sha256': sha(party_raw),
        'storage_all33744_sha256': sha(pc), 'flags': flags.hex(), 'vars': save1[0x139c:0x159c].hex(),
        'money': struct.unpack_from('<I', save1, 0x490)[0] ^ key,
        'coins': struct.unpack_from('<H', save1, 0x494)[0] ^ (key & 65535),
        'registered_item': struct.unpack_from('<H', save1, 0x496)[0],
        'pc_items_plaintext_sha256': sha(save1[0x498:0x560]), 'bag_pockets': bags,
        'other63_game_stats': stats[1:], 'berry_powder': struct.unpack_from('<I', save2, 0x1f4)[0] ^ key}
    return {'source_sha256': sha(data), 'slot': selected, 'counter': counter, 'encryption_key': key,
        'play_frames': ((struct.unpack_from('<H', save2, 14)[0] * 60 + save2[16]) * 60 + save2[17]) * 60 + save2[18],
        'saved_game_stat': stats[0], 'preconditions': {'clock_set': flag(0x895), 'safari': flag(0x88c),
            'content_revision': struct.unpack_from('<H', save1, 0x1590)[0],
            'dex_consistent': seen == first == second and all(not (a & ~b) for a, b in zip(owned, seen))},
        'domains': domains, 'party': party, 'stored': stored,
        'scope': 'Declared persistent game domains; not all opaque save bytes, public auth or device/performance proof.'}


def compare(before, after, saves):
    if type(saves) is not int or not 0 <= saves <= 20:
        raise ValueError('Declare zero to twenty ordinary in-game saves.')
    changed = [name for name in before['domains'] if before['domains'][name] != after['domains'][name]]
    prerequisites = all(not state['preconditions']['clock_set'] and not state['preconditions']['safari']
                        and state['preconditions']['content_revision'] >= 8
                        and state['preconditions']['dex_consistent'] for state in (before, after))
    checks = {'declared_domains_unchanged': not changed, 'stationary_preconditions': prerequisites,
              'counter_increment': after['counter'] == ((before['counter'] + saves) & 0xffffffff),
              'save_stat_increment': after['saved_game_stat'] == min(before['saved_game_stat'] + saves, 0xffffff),
              'play_time_nondecreasing': after['play_frames'] >= before['play_frames']}
    return {'passed': all(checks.values()), 'checks': checks, 'changed_domains': changed,
            'before_sha256': before['source_sha256'], 'after_sha256': after['source_sha256'],
            'declared_in_game_saves': saves, 'full_save_roundtrip_proven': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('save', type=Path); parser.add_argument('--before', type=Path)
    parser.add_argument('--saves', type=int, default=0); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists(): parser.error('Preserve prior audit evidence; choose another output.')
    state = audit_bytes(args.save.read_bytes())
    result = {'state': state, 'auditor_sha256': sha(Path(__file__).read_bytes())}
    if args.before: result['comparison'] = compare(audit_bytes(args.before.read_bytes()), state, args.saves)
    args.out.parent.mkdir(parents=True, exist_ok=True); args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'counter': state['counter'], 'party': len(state['party']), 'stored': len(state['stored']),
                      'comparison': result.get('comparison')}))
    if args.before and not result['comparison']['passed']: raise SystemExit(1)


if __name__ == '__main__': main()
