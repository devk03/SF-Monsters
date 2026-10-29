"""Whole wide buildings remain bounded, complete native card allocations."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
import world_art_contract as art


class WideCardContractTests(unittest.TestCase):
    def card(self,width=14):
        return dict(first=512,width=width,height=7,blocked=True,behavior=0,layer=1,
                    cells=[[512+y*width+x for x in range(width)] for y in range(7)])

    def read(self,card):
        data=dict(schema_version=1,profiles=dict(industrial=dict(
            secondary='gTileset_SFIndustrial',cards=dict(hall=card))))
        with patch.object(art,'PATH',SimpleNamespace(read_text=lambda:json.dumps(data))):
            return art.load_profiles()

    def test_fourteen_wide_hall_requires_all_seven_complete_rows(self):
        card=self.card()
        self.assertEqual(len(self.read(card)['industrial']['metatiles']),98)
        card['cells'][3].pop()
        with self.assertRaisesRegex(ValueError,'cell matrix'):self.read(card)

    def test_wider_cards_still_reject_out_of_range_extents_and_native_ids(self):
        with self.assertRaisesRegex(ValueError,'extent'):self.read(self.card(17))
        card=self.card();card['cells'][6][13]=1024
        with self.assertRaisesRegex(ValueError,'cell matrix'):self.read(card)


if __name__=='__main__':unittest.main()
