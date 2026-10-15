"""Portable resource/return/side-effect guards; transcripts are not native proof."""
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/quality'),str(ROOT/'tests')]
import trainer_class_fixtures as fixture
from trainer_portrait_audit_test import MemoryFile,addresses,linked_pair

# Synthetic distinct class rows keep commercial table bytes out of public fixtures.
# Actual ROM runs independently enforce the original complete-table SHA256.
rows = [bytes([0xBB + index//26,0xBB + index%26,255]) + bytes(10) for index in range(66)]
rows[23] = bytes.fromhex('cac9c51bc7bbc8c3bbbdff0000')
rows[32] = bytes.fromhex('c6bfbbbebfccff000000000000')
TABLE = b''.join(rows)


def native_resources(aliased=True):
    records=bytearray(855*40)
    for index in range(855):records[index*40+1]=index%66
    records[265*40+1]=32
    for index in (143,145,147,148,149,150,711):records[index*40+1]=23
    resources={'gTrainerClassNames':TABLE,'gTrainers':bytes(records),
               'gFixtureWaldenTeam':bytes(range(32)),'gFixtureStevenTeam':bytes(range(32,64))}
    if aliased:resources['gSFBuilderClassName']=bytes.fromhex('bccfc3c6bebfccff')
    locations=addresses(resources)
    for index,name in [(320,'gFixtureWaldenTeam'),(321,'gFixtureStevenTeam')]:
        records[index*40]=3;records[index*40+1]=23;records[index*40+32]=2
        struct.pack_into('<I',records,index*40+28,7)
        struct.pack_into('<I',records,index*40+36,locations[name])
    resources['gTrainers']=bytes(records)
    return resources


def loaded(resources=None,aliased=True):
    with patch.object(fixture,'TABLE_HASH',fixture.sha(TABLE)):
        return fixture.resources(*linked_pair(native_resources(aliased) if resources is None else resources),aliased)


class ClassResources(unittest.TestCase):
    def test_exact_native_table_records_and_indirect_teams_pass(self):
        before,after=loaded(aliased=False),loaded()
        self.assertEqual(len(TABLE),858)
        self.assertEqual(fixture.TABLE_HASH,'745460e89506abe565d5353287129f91cab9b347248254289f546d1f489acdce')
        self.assertNotEqual(fixture.sha(TABLE),fixture.TABLE_HASH)
        self.assertTrue(all(fixture.compare_resources(before,after).values()))
        self.assertEqual(after['teams'][320],bytes(range(32)))
        self.assertEqual(after['teams'][321],bytes(range(32,64)))

    def test_every_class_row_and_alias_byte_is_protected(self):
        for name in ('gTrainerClassNames','gSFBuilderClassName'):
            for offset in range(len(native_resources()[name])):
                resources=native_resources();data=bytearray(resources[name]);data[offset]^=1;resources[name]=bytes(data)
                with self.subTest(name=name,offset=offset),self.assertRaises(ValueError):loaded(resources)

    def test_wrong_class_flags_party_count_and_indirect_pointer_are_rejected(self):
        for index,offset,value in [(320,1,22),(321,1,24),(320,0,1),(321,32,1),(20,1,66),(30,0,4),(40,32,7)]:
            resources=native_resources();records=bytearray(resources['gTrainers']);records[index*40+offset]=value;resources['gTrainers']=bytes(records)
            with self.subTest(index=index,offset=offset),self.assertRaises(ValueError):loaded(resources)
        for pointer in (0x02000000,0x08000001,0x09fffffe):
            resources=native_resources();records=bytearray(resources['gTrainers']);struct.pack_into('<I',records,320*40+36,pointer);resources['gTrainers']=bytes(records)
            with self.assertRaises(ValueError):loaded(resources)

    def test_scalar_mutation_and_relocated_team_mutation_fail_paired_checks(self):
        before=loaded(aliased=False)
        resources=native_resources();records=bytearray(resources['gTrainers']);records[711*40+28]^=2;resources['gTrainers']=bytes(records)
        self.assertFalse(fixture.compare_resources(before,loaded(resources))['all855_scalar_records'])
        resources=native_resources();team=bytearray(resources['gFixtureStevenTeam']);team[19]^=1;resources['gFixtureStevenTeam']=bytes(team)
        checks=fixture.compare_resources(before,loaded(resources))
        self.assertFalse(checks['all855_resolved_teams']);self.assertFalse(checks['walden_steven_team32'])

    def test_missing_truncated_stale_rom_elf_and_section_faults_fail_closed(self):
        for name in ('gTrainerClassNames','gTrainers','gSFBuilderClassName'):
            resources=native_resources();del resources[name]
            with self.assertRaises(ValueError):loaded(resources)
            resources=native_resources();resources[name]=resources[name][:-1]
            with self.assertRaises(ValueError):loaded(resources)
        rom,elf=linked_pair(native_resources());changed=bytearray(rom.data);changed[299]^=1
        with self.assertRaisesRegex(ValueError,'ROM/ELF'):fixture.resources(MemoryFile(changed),elf,True)
        changed=bytearray(elf.data);struct.pack_into('<I',changed,96,8)
        with self.assertRaises(ValueError):fixture.resources(rom,MemoryFile(changed),True)
        data=loaded()
        for address,length in ((0x02000000,8),(0x08000000,0),(0x0a000000,32)):
            with self.assertRaises(ValueError):fixture.span(data['cart'],address,length)


class GetterBoundaries(unittest.TestCase):
    def test_all857_expected_returns_have_only_two_aliases_and_invalid_id_fallback(self):
        data=loaded();aliases=[]
        for index in fixture.IDS:
            pointer,label=fixture.expected_label(data,index,True)
            if pointer==data['alias']:aliases.append(index);self.assertEqual(label,bytes.fromhex('bccfc3c6bebfccff'))
            else:
                actual=index if index<855 else 0
                category=data['trainers'][actual*40+1]
                self.assertEqual(pointer,data['table_address']+13*category)
        self.assertEqual(aliases,[320,321])
        for index in (143,145,147,148,149,150,711):self.assertEqual(fixture.expected_label(data,index,True)[1],bytes.fromhex('cac9c51bc7bbc8c3bbbdff'))
        self.assertEqual(fixture.expected_label(data,265,True)[1],bytes.fromhex('c6bfbbbebfccff'))
        for index in (855,65535):self.assertEqual(fixture.expected_label(data,index,True),fixture.expected_label(data,0,True))
        for invalid in (-1,65536,True):
            with self.assertRaises(ValueError):fixture.expected_label(data,invalid,True)

    def test_corrupted_native_return_wrong_index_and_wrong_alias_pointer_fail(self):
        data=loaded();expected=fixture.expected_label(data,320,True)
        self.assertTrue(fixture.assess_return('return %08x steps 30'%expected[0],expected,data)['passed'])
        pointer,_=fixture.expected_label(data,143,True)
        self.assertFalse(fixture.assess_return('return %08x steps 30'%pointer,expected,data)['passed'])
        expected=fixture.expected_label(data,143,True)
        self.assertFalse(fixture.assess_return('return %08x steps 30'%data['alias'],expected,data)['passed'])
        for line in ('garbage','return 08000000 steps 0','return 08000000 steps 512','return 08000000 steps 2000000'):
            with self.assertRaises(ValueError):fixture.assess_return(line,expected,data)
        with self.assertRaises(ValueError):fixture.assess_return('return 02000000 steps 30',(0x02000000,b'bad'),data)

    def test_native_transcript_rejects_fast_and_full_protected_side_effects(self):
        data=loaded();specs=[(0x02000000,4),*[(a,len(b)) for a,b in fixture.CANARIES.items()]]
        baseline=[bytes(4),*fixture.CANARIES.values()]
        class Returns:
            def __init__(self):self.index=0
            def exchange(self,commands,lines):
                if not lines:return []
                pointer,_=fixture.expected_label(data,fixture.IDS[self.index],True);self.index+=1
                return ['return %08x steps 30'%pointer]
        for fault in ('none','fast','protected'):
            fast=[bytes(4)]
            reads=[baseline]+[fast for _ in fixture.IDS]+[baseline]
            if fault=='fast':reads[201]=[b'\x01\0\0\0']
            if fault=='protected':reads[-1]=[b'\x01\0\0\0',*fixture.CANARIES.values()]
            with patch.object(fixture,'protected_specs',return_value=(specs,[(0x02000000,4)],fast)),patch.object(fixture,'read',side_effect=reads):
                result=fixture.run_getters(Returns(),data,{fixture.GETTER:(0x08000000,40)},True)
            self.assertEqual(result['passed'],fault=='none')

    def test_deadline_and_invalid_storage_snapshot_fail_before_calls(self):
        with patch.object(fixture,'read',return_value=[bytes(4)]*4+[bytes(1)]*2):
            syms={name:(0x02000000,4 if i<4 else 1) for i,name in enumerate(fixture.FAST)}
            with self.assertRaisesRegex(ValueError,'save/storage'):fixture.protected_specs(None,syms)
        class NoCall:
            def exchange(self,commands,lines):return []
        with patch.object(fixture,'protected_specs',return_value=([],[],[])),patch.object(fixture,'read',return_value=[]),patch.object(fixture.time,'monotonic',side_effect=[0,61]):
            with self.assertRaisesRegex(ValueError,'deadline'):fixture.run_getters(NoCall(),loaded(),{},True)


if __name__=='__main__':unittest.main()
