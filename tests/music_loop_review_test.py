"""Observed loop boundaries must not confuse native pattern calls with GOTO."""
import copy
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/quality'))
from music_loop_review import loop_boundaries


class LoopEvidence(unittest.TestCase):
    def setUp(self):
        self.rom=bytearray(64)
        self.rom[32]=0xb2
        struct.pack_into('<I',self.rom,33,0x08000010)
        self.rows=[{'capture_frame':i,'clock':i,'status':1,'song':0x08000000,
                    'track':0x03001340,'command':0x08000010+(0,5,16)[i%3],
                    'wait':1,'pattern_level':0} for i in range(13)]

    def test_four_boundaries_prove_three_intervals(self):
        result=loop_boundaries(self.rows,self.rom,3)
        self.assertEqual([r['frame'] for r in result],[3,6,9,12])

    def test_backward_pattern_call_is_not_a_loop(self):
        self.rows[1].update(command=0x08000005,pattern_level=1)
        result=loop_boundaries(self.rows,self.rom,3)
        self.assertEqual([r['frame'] for r in result],[3,6,9,12])

    def test_arbitrary_cursor_jump_cannot_certify_a_loop(self):
        self.rom[32]=0xb3 # pattern call, not GOTO
        with self.assertRaisesRegex(ValueError,'GOTO opcode'):
            loop_boundaries(self.rows,self.rom,3)

    def test_incomplete_wrong_period_and_pause_are_rejected(self):
        cases=[(self.rows[:-1],3,'four observed'),(self.rows,4,'tick period')]
        paused=copy.deepcopy(self.rows);paused[4]['status']=0x80000001
        cases.append((paused,3,'paused'))
        for rows,ticks,message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError,message):
                loop_boundaries(rows,self.rom,ticks)


if __name__=='__main__':unittest.main()
