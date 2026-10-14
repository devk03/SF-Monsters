"""Synthetic in-memory SF Flash contracts; these are not campaign/save-transfer proof."""
import hashlib
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
import flash_audit as audit

# Physical locations of G,A,E,M from pinned pokemon.c:3609–3632.
# Deliberately independent of the auditor's ORDERS/permutations implementation.
POSITIONS = [
    (0,1,2,3),(0,1,3,2),(0,2,1,3),(0,3,1,2),(0,2,3,1),(0,3,2,1),
    (1,0,2,3),(1,0,3,2),(2,0,1,3),(3,0,1,2),(2,0,3,1),(3,0,2,1),
    (1,2,0,3),(1,3,0,2),(2,1,0,3),(3,1,0,2),(2,3,0,1),(3,2,0,1),
    (1,2,3,0),(1,3,2,0),(2,1,3,0),(3,1,2,0),(2,3,1,0),(3,2,1,0)]
LENGTHS = [0xf2c,0xf80,0xf80,0xf80,0xf08]+[0xf80]*8+[0x7d0]
BAGS = [(0x560,30),(0x5d8,30),(0x650,16),(0x690,64),(0x790,46)]


def mon(pid=24000,boxed=False,pp=(35,25,15,5)):
    owner=0x89abcdef
    growth=struct.pack('<HHIBBH',277,200,12345,0x39,70,0)
    attacks=struct.pack('<4H4B',1,2,3,4,*pp)
    chunks=[growth,attacks,bytes(range(1,13)),bytes(range(21,33))]
    plain=bytearray(48)
    for chunk,position in zip(chunks,POSITIONS[pid%24]):plain[position*12:(position+1)*12]=chunk
    data=bytearray(80 if boxed else 100)
    struct.pack_into('<II',data,0,pid,owner)
    data[8:18]=bytes([187]*10);data[18:20]=bytes([2,2]);data[20:27]=bytes([188]*7)
    checksum=sum(int.from_bytes(plain[i:i+2],'little') for i in range(0,48,2))&65535
    struct.pack_into('<H',data,28,checksum)
    for offset in range(0,48,4):
        struct.pack_into('<I',data,32+offset,int.from_bytes(plain[offset:offset+4],'little')^pid^owner)
    if not boxed:
        struct.pack_into('<I',data,80,64);data[84]=7
        struct.pack_into('<7H',data,86,21,31,12,13,14,15,16)
    return data


def blocks(key=0x12345678,stat=10,play=(0,1,2,3)):
    one,two,pc=bytearray(0x3d88),bytearray(0xf2c),bytearray(0x83d0)
    struct.pack_into('<hh',one,0,8,4);struct.pack_into('<bbbBhh',one,4,11,3,-1,0,8,4)
    one[0x234]=1;one[0x238:0x29c]=mon()
    struct.pack_into('<IHH',one,0x490,123456^key,321^(key&65535),42)
    for index in range(50):struct.pack_into('<HH',one,0x498+index*4,50+index,index+1)
    for pocket,(offset,count) in enumerate(BAGS):
        for index in range(count):struct.pack_into('<HH',one,offset+index*4,1+pocket*64+index,(index+3)^(key&65535))
    one[0x988]=3;one[0x3b24]=3
    one[0x1270+0x867//8]|=1<<(0x867%8)
    struct.pack_into('<3H',one,0x158c,0x5346,1,8)
    struct.pack_into('<64I',one,0x159c,*[value^key for value in [stat]+[i*1000 for i in range(1,64)]])
    two[:8]=bytes([187,188,189,255,255,255,255,255]);two[8]=1
    struct.pack_into('<I',two,10,0x11223344)
    struct.pack_into('<H3B',two,14,*play)
    two[0x13:0x18]=bytes([2,0x52,3,0,0]);two[0x28]=1;two[0x5c]=3
    struct.pack_into('<I',two,0xac,key);struct.pack_into('<I',two,0x1f4,789^key)
    pc[4+31*80:4+32*80]=mon(pid=24007,boxed=True)
    return one,two,pc


def checksum(payload):
    value=sum(int.from_bytes(payload[i:i+4],'little') for i in range(0,len(payload),4))&0xffffffff
    return ((value>>16)+value)&65535


def image(contents=None,counters=(2,1),rotation=0):
    one,two,pc=contents or blocks()
    payloads=[two]+[one[i:i+3968] for i in range(0,len(one),3968)]+[pc[i:i+3968] for i in range(0,len(pc),3968)]
    assert [len(v) for v in payloads]==LENGTHS
    data=bytearray([255])*131072
    for slot,counter in enumerate(counters):
        if counter is None:continue
        for ident,payload in enumerate(payloads):
            address=(slot*14+(ident+rotation)%14)*4096
            data[address:address+4096]=bytes(4096)
            data[address:address+len(payload)]=payload
            struct.pack_into('<HHII',data,address+4084,ident,checksum(payload),0x08012025,counter)
    return data


def sector(data,slot,ident):
    return next((slot*14+i)*4096 for i in range(14)
                if struct.unpack_from('<H',data,(slot*14+i)*4096+4084)[0]==ident)


class PokemonContract(unittest.TestCase):
    def test_all24_native_substructure_positions_decode_party_and_box(self):
        for permutation in range(24):
            for boxed in (False,True):
                with self.subTest(permutation=permutation,boxed=boxed):
                    data=mon(pid=24000+permutation,boxed=boxed)
                    got=audit.decode_mon(data,boxed)
                    self.assertEqual((got['species'],got['held_item'],got['owner']),(277,200,0x89abcdef))
                    self.assertEqual(got['moves'],[1,2,3,4]);self.assertEqual(got['pp'],[35,25,15,5])
                    self.assertEqual(got['all_native_bytes_sha256'],hashlib.sha256(data).hexdigest())
                    if not boxed:self.assertEqual((got['hp'],got['max_hp'],got['status'],got['level']),(21,31,64,7))

    def test_encrypted_checksum_and_sizes_are_enforced(self):
        for pid in range(24):
            data=mon(pid=24000+pid);data[36]^=1
            with self.subTest(pid=pid),self.assertRaisesRegex(ValueError,'checksum'):audit.decode_mon(data)
        for size in (0,79,80,99,101):
            with self.subTest(size=size),self.assertRaises(ValueError):audit.decode_mon(bytes(size))
        self.assertIsNone(audit.decode_mon(bytes(80),True))


class FlashContract(unittest.TestCase):
    def test_a_fainted_party_member_and_paralysis_are_valid_persistent_state(self):
        contents=blocks();contents[0][0x234]=2
        fainted=mon(pid=24011);struct.pack_into('<H',fainted,86,0)
        contents[0][0x29c:0x300]=fainted
        got=audit.audit_bytes(image(contents))
        self.assertEqual(got['domains']['party_count'],2)
        self.assertEqual([(m['hp'],m['status']) for m in got['party']],[(21,64),(0,64)])
        self.assertTrue(audit.compare(got,got,0)['passed'])

    def test_rotation_reassembles_logical_sections_without_changing_domains(self):
        before=audit.audit_bytes(image())
        for rotation in range(14):
            with self.subTest(rotation=rotation):
                got=audit.audit_bytes(image(rotation=rotation))
                self.assertTrue(audit.compare(before,got,0)['passed'])
                self.assertEqual((got['party'][0]['species'],got['stored'][0]['box'],got['stored'][0]['slot']),(277,1,1))

    def test_per_save_rekey_preserves_every_pocket_stat_pc_item_and_powder(self):
        before=audit.audit_bytes(image())
        after=audit.audit_bytes(image(blocks(key=0xfedcba98,stat=11,play=(0,1,3,3)),counters=(2,3),rotation=9))
        result=audit.compare(before,after,1)
        self.assertTrue(result['passed'],result)
        self.assertNotEqual(before['encryption_key'],after['encryption_key'])
        self.assertEqual((after['domains']['money'],after['domains']['coins'],after['domains']['berry_powder']),(123456,321,789))
        self.assertEqual(after['domains']['other63_game_stats'],[i*1000 for i in range(1,64)])
        for name,count in [('items',30),('key_items',30),('balls',16),('moves',64),('berries',46)]:
            self.assertEqual([v[1] for v in after['domains']['bag_pockets'][name]],list(range(3,count+3)))
        self.assertEqual(before['domains']['pc_items_plaintext_sha256'],after['domains']['pc_items_plaintext_sha256'])

    def test_empty_bag_slots_rekey_but_their_quantities_cannot_hide_mutations(self):
        def empty_slots(key):
            contents=blocks(key=key)
            for offset,count in BAGS:struct.pack_into('<HH',contents[0],offset+(count-1)*4,0,key&65535)
            return contents
        before=audit.audit_bytes(image(empty_slots(0x12345678)))
        after=audit.audit_bytes(image(empty_slots(0xfedcba98)))
        self.assertTrue(audit.compare(before,after,0)['passed'])
        for offset,count in BAGS:
            contents=empty_slots(0xfedcba98);contents[0][offset+(count-1)*4+2]^=1
            after=audit.audit_bytes(image(contents))
            with self.subTest(pocket=offset):
                self.assertIn('bag_pockets',audit.compare(before,after,0)['changed_domains'])

    def test_checksum_is_native_additive_word_fold_not_crc_and_ignores_sector_padding(self):
        data=image();address=sector(data,0,1)
        data[address:address+3968]=bytes([255])*3968
        # 992 unsigned 0xffffffff words wrap to0xfffffc20; native folded16=0xfc1f.
        struct.pack_into('<H',data,address+4086,0xfc1f)
        self.assertIsNotNone(audit.unpack_slot(data,0))
        data=image();data[sector(data,0,0)+3884]^=1
        self.assertIsNotNone(audit.unpack_slot(data,0))

    def test_invalid_newer_sector_recovers_older_slot_but_no_valid_slot_rejects(self):
        data=image();data[sector(data,0,1)]^=1
        got=audit.audit_bytes(data)
        self.assertEqual((got['slot'],got['counter']),(1,1))
        data[sector(data,1,1)]^=1
        with self.assertRaisesRegex(ValueError,'Neither'):audit.audit_bytes(data)

    def test_duplicate_ids_mixed_counters_bad_signatures_and_truncation_reject(self):
        for kind in ('duplicate','mixed_counter','signature'):
            data=image(counters=(2,None));address=sector(data,0,1)
            if kind=='duplicate':struct.pack_into('<H',data,address+4084,0)
            if kind=='mixed_counter':struct.pack_into('<I',data,address+4092,4)
            if kind=='signature':struct.pack_into('<I',data,address+4088,0)
            with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'Neither'):audit.audit_bytes(data)
        for size in (0,32768,131071,131073):
            with self.subTest(size=size),self.assertRaises(ValueError):audit.audit_bytes(bytes(size))

    def test_native_counter_wrap_selects_zero_and_counts_one_save(self):
        before=audit.audit_bytes(image(counters=(0xfffffffe,0xffffffff)))
        after=audit.audit_bytes(image(blocks(stat=11,play=(0,1,3,3)),counters=(0,0xffffffff)))
        self.assertEqual((before['counter'],before['slot'],after['counter'],after['slot']),(0xffffffff,1,0,0))
        self.assertTrue(audit.compare(before,after,1)['passed'])

    def test_far_apart_counters_follow_pinned_native_unsigned_selection(self):
        # save.c:587–606 uses unsigned max except the explicit ffffffff/0 pair.
        state=audit.audit_bytes(image(counters=(2,0x80000003)))
        self.assertEqual((state['counter'],state['slot']),(0x80000003,1))

    def test_footer_parity_cannot_claim_native_loadability_from_the_wrong_slot(self):
        # CopySaveSlotData uses counter%2, not the physical slot chosen by an auditor.
        for counters in ((3,None),(None,2),(44,46)):
            with self.subTest(counters=counters),self.assertRaises(ValueError):audit.audit_bytes(image(counters=counters))

    def test_equal_counters_read_the_native_physical_slot_and_its_schema(self):
        first=blocks();second=blocks()
        struct.pack_into('<I',first[0],0x490,100000^0x12345678)
        struct.pack_into('<I',second[0],0x490,200000^0x12345678)
        for counter,wanted in [(1,200000),(2,100000)]:
            data=image(first,counters=(counter,None))
            other=image(second,counters=(None,counter))
            data[14*4096:28*4096]=other[14*4096:28*4096]
            with self.subTest(counter=counter):
                got=audit.audit_bytes(data)
                self.assertEqual((got['slot'],got['domains']['money']),(counter%2,wanted))
        struct.pack_into('<H',second[0],0x158e,2)
        data=image(first,counters=(1,None));other=image(second,counters=(None,1))
        data[14*4096:28*4096]=other[14*4096:28*4096]
        with self.assertRaisesRegex(ValueError,'supported SF'):audit.audit_bytes(data)

    def test_save_stat_saturates_and_playtime_cannot_reverse_or_exceed_native_bounds(self):
        before=audit.audit_bytes(image(blocks(stat=0xfffffe)))
        after=audit.audit_bytes(image(blocks(stat=0xffffff,play=(0,1,3,3)),counters=(4,3)))
        self.assertTrue(audit.compare(before,after,2)['passed'])
        after=audit.audit_bytes(image(blocks(stat=0xffffff,play=(0,1,1,3)),counters=(4,3)))
        self.assertFalse(audit.compare(before,after,2)['checks']['play_time_nondecreasing'])
        for play in ((1000,0,0,0),(0,60,0,0),(0,0,60,0),(0,0,0,60)):
            with self.subTest(play=play),self.assertRaisesRegex(ValueError,'playtime'):audit.audit_bytes(image(blocks(play=play)))

    def test_unsupported_schema_party_count_and_empty_active_party_reject(self):
        for offset,value in ((0x158c,0),(0x158e,2),(0x234,0),(0x234,7)):
            contents=blocks();struct.pack_into('<H' if offset!=0x234 else '<B',contents[0],offset,value)
            with self.subTest(offset=offset,value=value),self.assertRaises(ValueError):audit.audit_bytes(image(contents))
        contents=blocks();contents[0][0x238:0x29c]=bytes(100)
        with self.assertRaisesRegex(ValueError,'empty'):audit.audit_bytes(image(contents))

    def test_valid_flash_checksum_cannot_hide_a_corrupt_monster_checksum(self):
        for block,offset in [(0,0x238+32),(2,4+31*80+32)]:
            contents=blocks();contents[block][offset]^=1
            with self.subTest(block=block),self.assertRaisesRegex(ValueError,'Pokemon.*checksum'):
                audit.audit_bytes(image(contents))

    def test_latest_unsupported_save_cannot_fall_back_silently_to_an_older_sf_save(self):
        older=image(counters=(2,None));contents=blocks()
        struct.pack_into('<H',contents[0],0x158e,2)
        newer=image(contents,counters=(None,3))
        older[14*4096:28*4096]=newer[14*4096:28*4096]
        with self.assertRaisesRegex(ValueError,'supported SF'):audit.audit_bytes(older)

    def test_invalid_dex_clock_safari_or_migration_preconditions_fail_comparison(self):
        for block,offset,value in [(1,0x28,4),(0,0x988,1),(0,0x3b24,1),
                                   (0,0x1270+0x895//8,1<<(0x895%8)),
                                   (0,0x1270+0x88c//8,1<<(0x88c%8)),(0,0x1590,7)]:
            contents=blocks();contents[block][offset]=value
            got=audit.audit_bytes(image(contents))
            with self.subTest(block=block,offset=offset):
                result=audit.compare(got,got,0)
                self.assertFalse(result['passed']);self.assertFalse(result['checks']['stationary_preconditions'])

    def test_validly_checksummed_metadata_inventory_party_and_pc_changes_fail(self):
        before=audit.audit_bytes(image())
        changes=[(1,0,'trainer'),(1,10,'trainer'),(1,0x13,'settings'),(1,0x16,'settings'),
                 (1,9,'warp_flags'),(0,0,'location_and_warps'),(0,0x1270,'flags'),
                 (0,0x139c,'vars'),(0,0x490,'money'),(0,0x494,'coins'),
                 (0,0x496,'registered_item'),(0,0x49a,'pc_items_plaintext_sha256'),
                 (1,0x1f4,'berry_powder'),(0,0x159c+63*4,'other63_game_stats'),
                 (0,0x238+8,'party_all600_sha256'),(0,0x238+100+8,'party_all600_sha256'),
                 (2,0,'storage_all33744_sha256'),(2,1,'storage_all33744_sha256'),
                 (2,0x8344,'storage_all33744_sha256'),(2,0x83c2,'storage_all33744_sha256'),
                 (2,4+31*80+8,'storage_all33744_sha256'),(2,4+419*80+8,'storage_all33744_sha256')]
        changes += [(0,offset+2,'bag_pockets') for offset,count in BAGS]
        for block,offset,domain in changes:
            contents=blocks();contents[block][offset]^=1
            after=audit.audit_bytes(image(contents))
            with self.subTest(block=block,offset=offset,domain=domain):
                result=audit.compare(before,after,0)
                self.assertFalse(result['passed']);self.assertIn(domain,result['changed_domains'])
        for boxed in (False,True):
            contents=blocks();changed=mon(pid=24007 if boxed else 24000,boxed=boxed,pp=(34,25,15,5))
            if boxed:contents[2][4+31*80:4+32*80]=changed
            else:contents[0][0x238:0x29c]=changed
            after=audit.audit_bytes(image(contents))
            self.assertFalse(audit.compare(before,after,0)['passed'])

    def test_declared_save_count_and_counters_cannot_mask_extra_saves(self):
        before=audit.audit_bytes(image());after=audit.audit_bytes(image(blocks(stat=12),counters=(4,3)))
        result=audit.compare(before,after,1)
        self.assertFalse(result['checks']['counter_increment']);self.assertFalse(result['checks']['save_stat_increment'])
        for saves in (-1,21,True,1.0):
            with self.subTest(saves=saves),self.assertRaises(ValueError):audit.compare(before,after,saves)


if __name__=='__main__':unittest.main()
