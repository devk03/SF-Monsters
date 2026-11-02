"""Visual review evidence cannot silently become stale or incomplete."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/quality/evaluate_town_visual.py'

class TownVisualEvaluationTest(unittest.TestCase):
    def setUp(self):
        (ROOT/'.tools').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/'.tools', prefix='visual-eval-test-')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.rom = 'a'*64
        images = []
        for i, role in enumerate(('full_map','arrival','landmark','secondary','ideal','baseline')):
            path = self.path/(role+'.png')
            Image.new('RGB',(240,160),(i*30,15,30)).save(path)
            item = {'id':role, 'role':role, 'path':str(path), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            if role != 'ideal':
                item.update(rom_sha256=('b'*64 if role=='baseline' else self.rom),capture_id='fixture')
            images.append(item)
        rating = {'score':2, 'reason':'Buildings repeat in the player view.', 'evidence':['arrival']}
        self.manifest = {'town':'Mission', 'reviewer':'Independent reviewer', 'candidate_rom_sha256':self.rom,
            'candidate_capture_id':'fixture', 'images':images,
            'ratings':{k:dict(rating) for k in ('composition','purposeful_space','architecture','scenery_activity','identity','readability')},
            'defects':[{'observation':'Empty blocks', 'location':'center', 'next_change':'Add enclosed blocks', 'evidence':['full_map']},
                       {'observation':'Repeated fronts', 'location':'east edge', 'next_change':'Vary facades', 'evidence':['arrival']},
                       {'observation':'Weak landmark', 'location':'north wall', 'next_change':'Build mural street', 'evidence':['landmark']}],
            'is_change':True, 'major_regression':False, 'decision':'revise',
            'baseline_comparison':'Earlier map remains sparse.', 'uncertainties':'Images do not prove movement.'}

    def run_cli(self):
        path = self.path/'manifest.json'; path.write_text(json.dumps(self.manifest))
        return subprocess.run([sys.executable,str(SCRIPT),str(path),'--output',str(self.path/'review.html')],capture_output=True,text=True)

    def test_complete_review_produces_report_and_preserves_human_decision(self):
        result = self.run_cli()
        self.assertEqual(result.returncode,0,result.stderr)
        report = (self.path/'review.html').read_text()
        self.assertIn('not user approval',report)
        self.assertIn('Empty blocks',report)
        self.assertIn('Decision: revise',report)

    def test_rejects_stale_or_wrong_rom_screenshots(self):
        (self.path/'arrival.png').write_bytes((self.path/'secondary.png').read_bytes())
        self.assertIn('hash mismatch',self.run_cli().stderr)
        self.manifest['images'][1]['sha256'] = hashlib.sha256((self.path/'arrival.png').read_bytes()).hexdigest()
        self.manifest['images'][1]['rom_sha256'] = 'c'*64
        self.assertIn('candidate ROM differs',self.run_cli().stderr)

    def test_rejects_missing_evidence_and_major_regression_advance(self):
        self.manifest['images'] = [x for x in self.manifest['images'] if x['role'] != 'baseline']
        self.assertIn('requires baseline',self.run_cli().stderr)
        self.manifest['is_change'] = False
        self.manifest['major_regression'] = True
        self.manifest['decision'] = 'advance'
        self.assertIn('major visible regression',self.run_cli().stderr)

    def test_ratings_need_candidate_evidence_and_three_distinct_views(self):
        self.manifest['ratings']['identity']['evidence'] = ['ideal']
        self.assertIn('evidence must include a candidate image',self.run_cli().stderr)
        self.manifest['ratings']['identity']['evidence'] = ['arrival']
        self.manifest['images'][2]['path'] = self.manifest['images'][1]['path']
        self.manifest['images'][2]['sha256'] = self.manifest['images'][1]['sha256']
        self.assertIn('views must be different images',self.run_cli().stderr)

    def test_defects_need_a_location_and_candidate_screenshot(self):
        self.manifest['defects'][0]['location'] = ' '
        self.assertIn('location or crop', self.run_cli().stderr)
        self.manifest['defects'][0]['location'] = 'central block'
        self.manifest['defects'][0]['evidence'] = ['ideal']
        self.assertIn('defect 1: evidence must include a candidate image', self.run_cli().stderr)

if __name__ == '__main__': unittest.main()
