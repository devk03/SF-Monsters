"""Hand-authored regressions for a missing frontage and a working-but-wrong door."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from world_street_contract import check_streets


class StreetContractTests(unittest.TestCase):
    def fixture(self):
        cells={(x,y):(512,False,3) for x in range(32) for y in range(24)}
        frontage={(x,7) for x in list(range(1,14))+list(range(18,31))}
        frontage|={(x,16) for x in list(range(1,9))+list(range(11,31))}
        for p in frontage:cells[p]=(527,True,3)
        # A narrow cafe at x4 has its visible door in its second tile, x5.
        runs=[{'left':a,'right':b,'y':y} for a,b,y in
              ((1,13,7),(18,30,7),(1,8,16),(11,30,16))]
        plan={'world_id':'mission','connections':[],
              'access_points':[{'kind':'room_entry','x':5,'y':8}],
              'town_blocks':[{'style':'cafe','x':4,'y':4}],
              'street_design':{'frontage_runs':runs,
                'service_doorway':{'style':'cafe','x':4,'y':4,'entry':[5,8]},
                'south_passage':{'left':9,'right':10,'purpose':'rear residential garden'}}}
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
        p,cells,frontage,profile=self.fixture();cells[9,20]=(515,True,3)
        with self.assertRaisesRegex(ValueError,'passage is blocked'):
            check_streets(p,cells,frontage,profile)

    def test_shortening_run_does_not_hide_a_missing_house(self):
        p,cells,frontage,profile=self.fixture()
        p['street_design']['frontage_runs'][0]['right']=12;frontage.remove((13,7))
        with self.assertRaisesRegex(ValueError,'required district frontage'):
            check_streets(p,cells,frontage,profile)

    def test_actual_room_entry_must_match_visible_door(self):
        p,cells,frontage,profile=self.fixture();p['access_points'][0]['x']=6
        with self.assertRaisesRegex(ValueError,'actual room entry'):
            check_streets(p,cells,frontage,profile)

    def test_removing_door_metadata_does_not_bypass_binding(self):
        p,cells,frontage,profile=self.fixture();p['street_design']['service_doorway']=None
        with self.assertRaisesRegex(ValueError,'actual room entrance'):
            check_streets(p,cells,frontage,profile)

    def test_gym_entry_uses_the_drawn_door(self):
        p,cells,frontage,profile=self.fixture()
        p['town_blocks'].append({'style':'cream','x':14,'y':3,'height':4})
        p['access_points'].append({'kind':'gym_entry','x':16,'y':7})
        check_streets(p,cells,frontage,profile)
        p['access_points'][-1]['x']=17
        with self.assertRaisesRegex(ValueError,'Gym entry'):
            check_streets(p,cells,frontage,profile)

    def test_missing_street_design_cannot_bypass_all_checks(self):
        p,cells,frontage,profile=self.fixture();p.pop('street_design')
        with self.assertRaisesRegex(ValueError,'missing its street design'):
            check_streets(p,cells,frontage,profile)


if __name__=='__main__':unittest.main()
