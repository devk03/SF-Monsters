"""The build command must refuse publishing synthetic evolution setups."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FixturePublication(unittest.TestCase):
    def test_fixture_build_requires_private_draft_mode(self):
        for fixture in ['cinder-15', 'ashrunner-35', 'reference-15', 'reference-35',
                        'brinepup-15', 'brinebull-35', 'reference-brine-15', 'reference-brine-35',
                        'sproutslug-15', 'fernslug-35', 'reference-sprout-15', 'reference-sprout-35']:
            with self.subTest(fixture=fixture):
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/romhack/build_probe.py'),
                    '--fixture', fixture], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn('Fixture cartridges must remain private --draft builds.', result.stderr)


if __name__ == '__main__': unittest.main()
