"""Hand-authored regressions for a missing frontage and a working-but-wrong door."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from world_street_contract import check_streets,check_details,check_edges,check_variety


class StreetContractTests(unittest.TestCase):
    def test_middle_facade_can_only_end_at_an_attached_building(self):
        profile={'cards':{'front':{'closed_edges':['left']},
                          'complete':{'closed_edges':['left','right']}}}
        front={'style':'front','x':1,'y':4,'width':3,'height':4}
        other={'style':'complete','x':4,'y':4,'width':2,'height':4}
        plan={'world_id':'hand_block','town_blocks':[front,other]}
        check_edges(plan,profile)
        other['x']=5
        with self.assertRaisesRegex(ValueError,'unfinished right end'):
            check_edges(plan,profile)
        other['x']=4;other['y']=5;other['height']=2
        with self.assertRaisesRegex(ValueError,'unfinished right end'):
            check_edges(plan,profile)
        other['y']=10
        with self.assertRaisesRegex(ValueError,'unfinished right end'):
            check_edges(plan,profile)

    def test_paint_and_edge_caps_do_not_count_as_architectural_variety(self):
        names=('bay_house','walkup','shop','loft','gable','deco','arcade','duplex')
        cards={name:{'architecture_type':name} for name in names}
        plan={'world_id':'hand_block','town_blocks':[{'style':name} for name in names]}
        self.assertEqual(len(check_variety(plan,{'cards':cards})),8)
        for alias in ('bay_house__sage','bay_house__slate','bay_house_lr'):
            cards[alias]={'architecture_type':'bay_house'}
        plan['town_blocks'][-1]={'style':'bay_house__sage'}
        plan['town_blocks'] += [{'style':'bay_house__slate'},{'style':'bay_house_lr'}]
        with self.assertRaisesRegex(ValueError,'eight structural'):
            check_variety(plan,{'cards':cards})

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

    def sign_fixture(self):
        p={'street_signs':[],'bg_events':[],'access_points':[],'town_blocks':[],
           'street_details':[{'name':'shrub','x':21,'y':8},{'name':'succulent','x':22,'y':8}]}
        p['town_blocks']=[{'style':d['name'],'x':d['x'],'y':d['y'],'width':1,'height':1}
                          for d in p['street_details']]
        for style,x,y,h in [('wayfinder',11,8,2),('shop_board',3,9,1)]:
            bottom=y+h-1;script='Read_'+style
            p['street_signs'].append({'style':style,'object':[x,bottom],
                'standing':[x,bottom+1],'script':script})
            p['bg_events'].append({'x':x,'y':bottom,'script':script})
            p['access_points'].append({'name':style,'x':x,'y':bottom+1})
            p['town_blocks'].append({'style':style,'x':x,'y':y,'width':1,'height':h})
        return p

    def test_signs_bind_visible_posts_and_actual_reading_positions(self):
        p=self.sign_fixture();check_details(p)
        p['bg_events'][0]['x']=12
        with self.assertRaisesRegex(ValueError,'visible fixture'):
            check_details(p)

    def test_sign_event_outside_its_visible_fixture_is_rejected(self):
        p=self.sign_fixture()
        p['street_signs'][0]['object'][1]=10;p['street_signs'][0]['standing'][1]=11
        p['bg_events'][0]['y']=10;p['access_points'][0]['y']=11
        with self.assertRaisesRegex(ValueError,'visible fixture'):
            check_details(p)

    def test_removed_plant_cannot_survive_only_as_diversity_metadata(self):
        p=self.sign_fixture();p['town_blocks']=p['town_blocks'][1:]
        with self.assertRaisesRegex(ValueError,'no complete drawn fixture'):
            check_details(p)


if __name__=='__main__':unittest.main()
