"""Synthetic corruption cases for the private Worker proof auditor."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import math
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('worker_audit',ROOT/'scripts/quality/audit_worker_proof.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class WorkerReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory=Path(tempfile.mkdtemp(prefix='worker-proof-audit-',dir=ROOT/'.tools'))
        runtime=cls.directory/'runtime';runtime.mkdir()
        for name in ('mgba.js','mgba.wasm','mgba.audio-worklet.js'):
            shutil.copyfile(ROOT/'web/public/emulator'/name,runtime/name)
        for name in ('web_performance.html','server-source.py'):(cls.directory/name).write_text('Synthetic unit fixture\n')
        cls.identity={'private_runtime_override':True,'private_page_override':True,'public_progress_touched':False,
            'page_sha256':module.hash_file(cls.directory/'web_performance.html'),
            'server_source_sha256':module.hash_file(cls.directory/'server-source.py'),
            'runtime':{p.name:module.hash_file(p) for p in runtime.iterdir()}}

    def fixture(self,counter=1000):
        fps=59.727501;initial_due=math.floor(.1*fps);due=initial_due;rows=[];initial_counter=counter
        for elapsed in range(100,1100,5):
            next_due=math.floor(elapsed/1000*fps);fresh=next_due-due;new_counter=(counter+fresh)&0xFFFFFFFF
            rows.append([fresh,fresh,fresh,0,0,float(elapsed),counter,new_counter]);counter=new_counter;due=next_due
        worker={'reason':'duration','durationMs':1000,'startedAtMs':100.,'endedAtMs':1100.,'elapsedMs':1000.,
            'clockOriginMs':0.,'workerTimeOrigin':1000000000.,'startedAt':1000000100.,'endedAt':1000001100.,
            'framerate':fps,'initialPacing':{'due':initial_due,'executed':initial_due,'overflowDropped':0,'backlog':0},
            'finalPacing':{'due':due,'executed':due,'overflowDropped':0,'backlog':0},'initialDue':initial_due,
            'initialBacklog':0,'initialGuestCounter':initial_counter,'finalGuestCounter':counter,'finalBacklog':0,
            'maxPending':1,'maxBacklog':0,'maxWorkerTickGapMs':5.,'rawLedger':rows,
            'epoch':1,'audioFinalAcknowledged':True,'audioFinalError':None,'audioSnapshots':[],
            'audioFinalSnapshot':{'type':'diagnostics','epoch':1,'final':True,'firstOutputFrame':12800,
                'observedThroughOutputFrame':56960,'renderedOutputFrames':44160,'warmupOutputFrames':0,
                'underrunOutputFrames':0,'droppedSourceFrames':0,'processQuanta':345,'queueDepthFrames':2622.,
                'prefillTargetSourceFrames':2622,'outputSampleRate':44100,'playbackStarted':True}}
        main={'timeOrigin':1000000000.,'audioClockBefore':{'beforeMs':99.,'afterMs':99.1,'currentTime':3.,'state':'running','timeOrigin':1000000000.},
              'audioClockAfter':{'beforeMs':1101.,'afterMs':1101.1,'currentTime':4.002,'state':'running','timeOrigin':1000000000.},
              'mainBeginSentAt':1000000099.2,'mainResultReceivedAt':1000001101.2,
              'stalls':[{'requestedMs':200,'startedAt':1000000200.,'endedAt':1000000400.}],
              'submissions':[],'inputs':[],'visibility':[{'state':'visible'}]}
        return {'schema':2,'kind':'private-worker-proof-v1','context':{'identity':copy.deepcopy(self.identity)},
                'scope':{'productionCompatible':False,'physicalPaintProven':False,'guestKeyConsumptionProven':False},
                'worker':worker,'main':main}

    def audit(self,value):return module.audit(value,self.identity,self.directory)

    def test_counter_wrap_and_prior_overflow_preserve_separate_credit_facts(self):
        for counter in (1000,0xFFFFFFF0):
            report=self.fixture(counter);result=self.audit(report)
            self.assertTrue(result['loss_free']);self.assertEqual(result['overflow_dropped_frames'],0)
            self.assertGreater(result['frames_in_batches_admitted_during_each_main_stall'][0],0)
            self.assertFalse('full_performance_passed'in result)
        report=self.fixture()
        for part in ('initialPacing','finalPacing'):
            report['worker'][part]['executed']-=1;report['worker'][part]['overflowDropped']+=1
        self.assertTrue(self.audit(report)['loss_free'],'earlier overflow must remain separate from this window')

    def test_raw_credit_counter_clock_and_close_corruption_is_rejected(self):
        changes=[
            lambda w:w['rawLedger'][4].__setitem__(0,2),
            lambda w:w['rawLedger'][4].__setitem__(2,5),
            lambda w:w['rawLedger'][4].__setitem__(3,1),
            lambda w:w['rawLedger'][4].__setitem__(4,1),
            lambda w:w['rawLedger'][4].__setitem__(5,0.),
            lambda w:w['rawLedger'][4].__setitem__(6,12),
            lambda w:w['rawLedger'][4].__setitem__(7,12),
            lambda w:w.__setitem__('finalGuestCounter',w['finalGuestCounter']+1),
            lambda w:w.__setitem__('finalBacklog',1),
            lambda w:w.__setitem__('maxWorkerTickGapMs',0.),
            lambda w:w.__setitem__('elapsedMs',999.),
            lambda w:w.__setitem__('reason','ledger-capacity'),
            lambda w:w.__setitem__('framerate',60.),
            lambda w:w['rawLedger'].insert(5,w['rawLedger'][4]),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                report=self.fixture();change(report['worker'])
                with self.assertRaises(ValueError):self.audit(report)

    def test_audio_interval_acknowledgement_and_false_scope_claims_are_rejected(self):
        for key,value in (('underrunOutputFrames',50000),('processQuanta',344),('epoch',2),('final',False),('queueDepthFrames',40000)):
            with self.subTest(key=key):
                report=self.fixture();report['worker']['audioFinalSnapshot'][key]=value
                with self.assertRaises(ValueError):self.audit(report)
        for key in ('audioFinalAcknowledged','physicalPaintProven','productionCompatible'):
            report=self.fixture()
            if key=='audioFinalAcknowledged':report['worker'][key]=False
            else:report['scope'][key]=True
            with self.assertRaises(ValueError):self.audit(report)
        report=self.fixture();report['main']['stalls'][0]['endedAt']+=1000
        with self.assertRaises(ValueError):self.audit(report)

    def test_preserved_runtime_and_host_must_match_frozen_identity(self):
        for name in ('runtime/mgba.audio-worklet.js','web_performance.html'):
            path=self.directory/name;before=path.read_bytes()
            try:
                path.write_bytes(before+b'\nunit corruption\n')
                with self.assertRaises(ValueError):self.audit(self.fixture())
            finally:path.write_bytes(before)


if __name__=='__main__':unittest.main()
