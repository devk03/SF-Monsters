"""Hand-authored regressions for a missing frontage and a working-but-wrong door."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from world_street_contract import check_streets


class StreetContractTests(unittest.TestCase):
    def fixture(self):
        cells={(x,y):(512,False,3) for x in range(32) for y in range(24)}
        frontage={(x,y) for y in (7,16) for x in range(1,25)}
        for p in frontage:cells[p]=(527,True,3)
        # A narrow cafe at x4 has its visible door in its second tile, x5.
        plan={'world_id':'mission','connections':[],
              'town_blocks':[{'style':'cafe','x':4,'y':4}],
              'street_design':{'frontage_runs':[{'left':1,'right':24,'y':y} for y in (7,16)],
                'service_doorway':{'style':'cafe','x':4,'y':4,'entry':[5,8]},
                'south_passage':{'left':25,'right':26,'purpose':'rear residential garden'}}}
        return plan,cells,frontage,{'cards':{'cafe':{'height':4}}}

    def test_complete_wall_and_aligned_door(self):
        check_streets(*self.fixture())

    def test_one_missing_building_cell_is_not_a_complete_street_wall(self):
        p,cells,frontage,profile=self.fixture();frontage.remove((12,7))
        with self.assertRaisesRegex(ValueError,'street wall gap'):
            check_streets(p,cells,frontage,profile)

    def test_safe_warp_one_tile_beside_drawn_door_is_rejected(self):
        p,cells,frontage,profile=self.fixture()
        p['town_blocks'][0]['x']=3;p['street_design']['service_doorway']['x']=3
        with self.assertRaisesRegex(ValueError,'drawn facade doorway'):
            check_streets(p,cells,frontage,profile)

    def test_named_alley_must_reach_its_destination(self):
        p,cells,frontage,profile=self.fixture();cells[25,20]=(515,True,3)
        with self.assertRaisesRegex(ValueError,'passage is blocked'):
            check_streets(p,cells,frontage,profile)


if __name__=='__main__':unittest.main()
