"""A well-formed generic report cannot substitute for completed active input."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
from audit_active_field import qualify


class ActiveFieldQualification(unittest.TestCase):
    def setUp(self):
        # Classification unit fixtures only; the generic receipt auditor has its
        # own real-file tests. Real native/browser evidence is evaluated separately.
        self.directory=Path(tempfile.mkdtemp(prefix='sf-active-field-audit-'))
        route=(ROOT/'data/quality/park-active-field.csv').read_bytes()
        (self.directory/'route.csv').write_bytes(route)
        self.spec=json.loads((ROOT/'data/quality/park-active-field.json').read_text())
        self.identity={'rom_sha256':self.spec['target_sha256'],
            'controller_route':{'rows':310,'frames':35756},
            'files':{'route.csv':hashlib.sha256(route).hexdigest()}}
        self.report={'reason':'duration','durationMs':600000,'elapsedMs':600001,
            'context':{'audioState':'running'},'scope':{
                'valid':True,'uninterrupted':True,'foregroundOnly':True},
            'ticks':{'hidden':0,'discardedFrames':0,'executedFrames':35836,
                'actualVideoFrames':35836,'videoFrameMismatchTicks':0},
            'controllerReplay':{'reason':'complete','error':None,'appliedRows':310,'totalRows':310},
            'input':{'count':310},'pendingInputAtEnd':False,
            'audioFinalSnapshot':{'playbackStarted':True,'warmupOutputFrames':0,
                'underrunOutputFrames':0,'droppedSourceFrames':0}}

    def check(self,report=None,identity=None,spec=None,observation=None):
        report=self.report if report is None else report
        identity=self.identity if identity is None else identity
        if observation is None:
            observation={'receipt_well_formed':True,'controller_replay':{'status':'complete'}}
        with patch('audit_active_field.audit',return_value=observation) as generic:
            result=qualify(report,identity,self.directory,self.spec if spec is None else spec)
        generic.assert_called_once_with(report,identity,self.directory/'runtime')
        return result

    def test_completed_clean_input_qualifies_only_the_narrow_pipeline_scope(self):
        result=self.check()
        self.assertTrue(result['passed'])
        self.assertGreater(result['held_fraction'],0.96)
        self.assertIn('Actual scene/motion require separate',result['scope'])
        self.assertIn('No guest-key consumption',result['scope'])

    def test_aborted_hidden_incomplete_and_errored_replays_fail_despite_generic_validity(self):
        for change in ({'reason':'late-timer'},{'reason':'hidden'},{'reason':'in-progress'},
                       {'error':'dispatch unavailable'},{'appliedRows':17},{'totalRows':309}):
            report=deepcopy(self.report);report['controllerReplay'].update(change)
            with self.subTest(change=change):self.assertFalse(self.check(report)['passed'])

    def test_manual_short_and_early_stops_cannot_claim_the_full_window(self):
        for change in ({'reason':'manual'},{'durationMs':180000},{'elapsedMs':599998}):
            report=deepcopy(self.report);report.update(change)
            with self.subTest(change=change):self.assertFalse(self.check(report)['passed'])

    def test_foreground_pending_extra_keyboard_and_frame_loss_are_required(self):
        for change in ({'valid':False},{'uninterrupted':False},{'foregroundOnly':False}):
            report=deepcopy(self.report);report['scope'].update(change)
            self.assertFalse(self.check(report)['passed'])
        for group,change in [('ticks',{'hidden':1}),('ticks',{'discardedFrames':1}),
                ('ticks',{'videoFrameMismatchTicks':1}),('ticks',{'actualVideoFrames':35835}),
                ('input',{'count':311}),('input',{'count':309})]:
            report=deepcopy(self.report);report[group].update(change)
            with self.subTest(change=change):self.assertFalse(self.check(report)['passed'])
        report=deepcopy(self.report);report['pendingInputAtEnd']=True
        self.assertFalse(self.check(report)['passed'])

    def test_warmup_or_any_audio_loss_cannot_be_a_continuity_pass(self):
        for change in ({'playbackStarted':False},{'warmupOutputFrames':128},
                       {'underrunOutputFrames':1},{'droppedSourceFrames':1}):
            report=deepcopy(self.report);report['audioFinalSnapshot'].update(change)
            with self.subTest(change=change):self.assertFalse(self.check(report)['passed'])
        report=deepcopy(self.report);report['context']['audioState']='suspended'
        self.assertFalse(self.check(report)['passed'])

    def test_cartridge_route_and_declared_totals_must_match(self):
        identity=deepcopy(self.identity);identity['rom_sha256']='0'*64
        self.assertFalse(self.check(identity=identity)['passed'])
        for field in ('frames','held_frames','rows'):
            spec=deepcopy(self.spec);spec[field]+=1
            self.assertFalse(self.check(spec=spec)['passed'])
        (self.directory/'route.csv').write_bytes((self.directory/'route.csv').read_bytes()+b'\n')
        self.assertFalse(self.check()['checks']['exact_route_bytes'])

    def test_self_consistent_idle_route_is_not_an_active_workload(self):
        rows=[tuple(map(int,line.split(','))) for line in
              (self.directory/'route.csv').read_text().splitlines()]
        route=''.join(f'0,{frames}\n' for _,frames in rows).encode()
        (self.directory/'route.csv').write_bytes(route)
        spec=deepcopy(self.spec);spec.update(held_frames=0,input_sha256=hashlib.sha256(route).hexdigest())
        identity=deepcopy(self.identity);identity['files']['route.csv']=spec['input_sha256']
        result=self.check(identity=identity,spec=spec)
        self.assertFalse(result['passed'])
        self.assertTrue(result['checks']['exact_route_bytes'])
        self.assertFalse(result['checks']['nearly_full_directional_route'])

    def test_generic_integrity_failure_never_inherits_a_classification_pass(self):
        with patch('audit_active_field.audit',side_effect=ValueError('Final audio acknowledgement missing')):
            with self.assertRaisesRegex(ValueError,'acknowledgement'):
                qualify(self.report,self.identity,self.directory,self.spec)

    def test_generic_dispatch_validation_is_required(self):
        for observation in ({'receipt_well_formed':True},
                {'controller_replay':None},{'controller_replay':{'status':'not-run'}}):
            self.assertFalse(self.check(observation=observation)['passed'])
        identity=deepcopy(self.identity);identity.pop('controller_route')
        self.assertFalse(self.check(identity=identity)['passed'])

    def test_button_only_rehashed_route_cannot_count_as_directional_input(self):
        rows=[tuple(map(int,line.split(','))) for line in
              (self.directory/'route.csv').read_text().splitlines()]
        for mask in (1,2,8):
            route=''.join(f'{mask},{frames}\n' for _,frames in rows).encode()
            (self.directory/'route.csv').write_bytes(route)
            spec=deepcopy(self.spec);spec.update(held_frames=0,input_sha256=hashlib.sha256(route).hexdigest())
            identity=deepcopy(self.identity);identity['files']['route.csv']=spec['input_sha256']
            result=self.check(identity=identity,spec=spec)
            self.assertTrue(result['checks']['exact_route_bytes'])
            self.assertFalse(result['checks']['nearly_full_directional_route'])

    def test_declared_duration_has_no_short_window_allowance(self):
        for elapsed in (599999,599999.999):
            report=deepcopy(self.report);report['elapsedMs']=elapsed
            self.assertFalse(self.check(report)['passed'])


if __name__=='__main__':unittest.main()
