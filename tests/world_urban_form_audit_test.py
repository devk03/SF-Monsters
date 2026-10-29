"""Independent fixtures for source-map density and party-wall reporting."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
from audit_urban_form import joined,measure


class UrbanFormAuditTests(unittest.TestCase):
    def test_party_wall_requires_shared_edge_and_vertical_overlap(self):
        a=dict(x=0,y=0,width=2,height=2)
        self.assertTrue(joined(a,dict(x=2,y=1,width=2,height=2)))
        self.assertFalse(joined(a,dict(x=2,y=2,width=2,height=2)))
        self.assertFalse(joined(a,dict(x=3,y=0,width=2,height=2)))

    def test_counts_ignore_decor_and_measure_only_declared_grass(self):
        plan=dict(world_id='fixture',rows=['ggss','gsss'],
                  legend={'g':[512,False,3],'s':[513,False,3]},town_blocks=[
                      dict(style='a',x=0,y=0,width=1,height=1),
                      dict(style='a',x=1,y=0,width=1,height=1),
                      dict(style='a',x=3,y=1,width=1,height=1),
                      dict(style='tree',x=2,y=0,width=1,height=1)])
        kit=dict(catalog={'grass':{'tiles':[[512]]},
                          'a':{'architecture_type':'fixture'},'tree':{}})
        result=measure(plan,kit)
        self.assertEqual((result['grass_tiles'],result['grass_percent']),(3,37.5))
        self.assertEqual(result['largest_grass_patch'],3)
        self.assertEqual((result['building_count'],result['attached_count'],result['isolated_count']),(3,2,1))
        self.assertEqual(result['structural_families'],{'a':3})


if __name__=='__main__':unittest.main()
