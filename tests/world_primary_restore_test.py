"""A destination must recover its native art after a previous scene overwrites it."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/romhack'))
from world_primary_restore import restoration


class PrimaryRestorationTests(unittest.TestCase):
    def test_transition_recovers_only_needed_native_tiles(self):
        original={7:bytes([2])*64, 11:bytes([3])*64, 15:bytes([4])*64}
        scene={7:bytes([9])*64,11:bytes([8])*64,15:original[15]}
        plan=restoration({7,11},{7,15},{20},original)
        self.assertEqual([slot for slot,_ in plan],[7])
        scene.update(plan)
        self.assertEqual(scene[7],original[7])
        self.assertEqual(scene[15],original[15])
        self.assertEqual(scene[11],bytes([8])*64)

    def test_rejects_collision_and_missing_native_data(self):
        with self.assertRaisesRegex(ValueError,'collide'):
            restoration({7},{7},{7},{7:bytes(64)})
        with self.assertRaisesRegex(ValueError,'Missing'):
            restoration({7},{7},{20},{})
        with self.assertRaises(ValueError):
            restoration({512},{7},set(),{})


if __name__=='__main__':unittest.main()
