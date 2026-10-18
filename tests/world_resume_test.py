"""Small independent geometry: sealed pockets, counters, doors and water gates."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from world_resume import return_mask


class ReturnPaths(unittest.TestCase):
    def test_pocket_and_moving_actor_do_not_count_as_escape(self):
        plan = dict(rows=['#######','#..#..#','#..#..#','#.....#','#######'],
                    legend={'#':[11,True,3],'.':[1,False,3]}, connections=[],
                    npcs=[dict(x=3,y=3,range_x=1)], coord_events=[dict(x=1,y=3)],
                    access_points=[dict(kind='room_exit',x=1,y=3)])
        mask=return_mask(plan,0)
        def bit(x,y):return bool(mask[(y*7+x)//8] & 1<<((y*7+x)%8))
        self.assertTrue(bit(1,1))
        self.assertTrue(bit(1,3))
        self.assertFalse(bit(5,1))
        self.assertFalse(bit(2,3))

    def test_water_and_fall_open_at_their_earned_stage(self):
        plan=dict(rows=['.WV.'],legend={'.':[1,False,3],'W':[368,False,1],'V':[179,False,1]},
                  npcs=[],connections=[],coord_events=[dict(x=0,y=0),dict(x=3,y=0)],
                  access_points=[dict(kind='gym_exit',x=0,y=0),dict(kind='room_entry',x=3,y=0)])
        self.assertEqual(return_mask(plan,0),bytes([1]))
        self.assertEqual(return_mask(plan,5),bytes([3]))
        self.assertEqual(return_mask(plan,8),bytes([7]))


if __name__=='__main__':unittest.main()
