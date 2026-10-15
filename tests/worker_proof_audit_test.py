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
        native=cls.directory/'sources';native.mkdir()
        for name in ('capture.gba','capture.state','capture.sav'):(native/name).write_bytes(('Synthetic '+name).encode())
        rom_hash=module.hash_file(native/'capture.gba')
        metadata={'controller_only':True,'rom_sha256':rom_hash,'mgba_revision':'unit-core'}
        (native/'capture.json').write_text(json.dumps(metadata))
        shutil.copyfile(native/'capture.json',cls.directory/'state.metadata.json')
        cls.identity={'rom_sha256':rom_hash,'mgba_revision':'unit-core',
            'inputs':{str(p):module.hash_file(p) for p in native.iterdir()},
            'files':{alias:module.hash_file(native/name) for alias,name in
                     (('rom.gba','capture.gba'),('state.bin','capture.state'),('battery.sav','capture.sav'))},
            'source_state_metadata_sha256':module.hash_file(native/'capture.json'),
            'private_runtime_override':True,'private_page_override':True,'public_progress_touched':False,
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
            'inputs':[],'pendingInputAtEnd':False,'epoch':1,'audioFinalAcknowledged':True,'audioFinalError':None,'audioSnapshots':[],
            'audioFinalSnapshot':{'type':'diagnostics','epoch':1,'final':True,'firstOutputFrame':132352,
                'observedThroughOutputFrame':176512,'renderedOutputFrames':44160,'warmupOutputFrames':0,
                'underrunOutputFrames':0,'droppedSourceFrames':0,'processQuanta':345,'queueDepthFrames':2622.,
                'prefillTargetSourceFrames':2622,'outputSampleRate':44100,'playbackStarted':True}}
        main={'timeOrigin':1000000000.,'audioClockBefore':{'beforeMs':99.,'afterMs':99.1,'currentTime':3.,'state':'running','timeOrigin':1000000000.},
              'audioClockAfter':{'beforeMs':1101.,'afterMs':1101.1,'currentTime':4.002,'state':'running','timeOrigin':1000000000.},
              'mainBeginSentAt':1000000099.2,'mainResultReceivedAt':1000001101.2,
              'stalls':[{'requestedMs':200,'startedAt':1000000200.,'endedAt':1000000400.}],
              'submissions':[],'inputs':[],'visibility':[{'state':'visible','at':1000000099.}] }
        return {'boot':{'batteryVerified':True,'counter':999,'width':240,'height':160},'schema':2,'kind':'private-worker-proof-v1','context':{'identity':copy.deepcopy(self.identity)},
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

    def test_visibility_clock_binding_and_boot_cannot_be_vacuously_approved(self):
        for visibility in ([],[{'state':'bogus','at':1000000099.}],
                           [{'state':'visible','at':1000000199.}]):
            report=self.fixture();report['main']['visibility']=visibility
            with self.assertRaises(ValueError):self.audit(report)
        report=self.fixture();report['boot']['batteryVerified']=False
        with self.assertRaises(ValueError):self.audit(report)
        report=self.fixture();raw=report['worker']['audioFinalSnapshot']
        raw.update(firstOutputFrame=132352,observedThroughOutputFrame=132480,
                   renderedOutputFrames=128,processQuanta=1)
        with self.assertRaises(ValueError):self.audit(report)
        report=self.fixture();report['main']['audioClockBefore']['currentTime']=0.
        with self.assertRaises(ValueError):self.audit(report)

    def consumed_fixture(self):
        report=self.fixture();w=report['worker'];fps=w['framerate'];due=4+math.floor(5000/65536*fps)
        initial_due=due;counter=w['initialGuestCounter'];posted=due*1097;initial_posted=posted;rows=[]
        for elapsed in range(100,1100,5):
            consumed=5000+math.floor((elapsed-100)/1000*65536)
            next_due=4+math.floor(consumed/65536*fps);fresh=next_due-due;after=posted+fresh*1097
            rows.append([fresh,fresh,fresh,0,0,float(elapsed),counter,counter+fresh,consumed,posted,after])
            due=next_due;counter+=fresh;posted=after
        report['boot'].update(clockPolicy='consumed-source-v1',prefillLeadNativeFrames=4)
        w.update(clockPolicy='consumed-source-v1',prefillLeadNativeFrames=4,coreRate=65536,rawLedger=rows,
                 initialSourceFramesPosted=initial_posted,finalSourceFramesPosted=posted,sourceFramesPosted=posted-initial_posted,
                 initialDue=initial_due,finalGuestCounter=counter,
                 initialPacing=dict(due=initial_due,executed=initial_due,overflowDropped=0,backlog=0),
                 finalPacing=dict(due=due,executed=due,overflowDropped=0,backlog=0))
        return report

    def test_explicit_consumed_clock_replays_source_credits_without_wall_normalization(self):
        report=self.consumed_fixture();result=self.audit(report)
        self.assertEqual(result['clock_policy'],'consumed-source-v1');self.assertTrue(result['loss_free'])
        self.assertEqual(result['actual_frames'],report['worker']['finalGuestCounter']-report['worker']['initialGuestCounter'])
        mutations=[lambda w:w['rawLedger'][4].__setitem__(8,999999),
                   lambda w:w['rawLedger'][4].__setitem__(8,0),
                   lambda w:w['rawLedger'][4].__setitem__(9,0),
                   lambda w:w['rawLedger'][4].__setitem__(10,0),
                   lambda w:w.update(coreRate=65535),lambda w:w.update(prefillLeadNativeFrames=5),
                   lambda w:w.update(sourceFramesPosted=0),lambda w:w.update(clockPolicy='worker-wall-v1'),
                   lambda w:w['rawLedger'][4].pop()]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                changed=self.consumed_fixture();mutate(changed['worker'])
                with self.assertRaises(ValueError):self.audit(changed)

    def input_fixture(self):
        report=self.fixture();origin=1000000000.
        report['main']['inputs']=[{'sequence':1,'mask':16,'domAt':origin+102.,'sentAt':origin+102.5}]
        report['worker']['inputs']=[{'sequence':1,'mask':16,'domAt':origin+102.,
            'workerReceivedAt':origin+103.,'guestCounterAtReceipt':1000,'superseded':False,
            'firstGuestCounter':1001,'completedBatchAt':origin+106.2}]
        return report

    def test_input_transport_and_first_subsequent_counter_are_separate_from_consumption(self):
        report=self.input_fixture();facts=self.audit(report)['input_transport']
        self.assertTrue(facts['all_reported_edges_accounted_for'])
        self.assertEqual(facts['first_subsequent_counter_observed'],1)
        self.assertFalse(facts['guest_key_consumption_proven'])
        report['main']['inputs'].append({'sequence':2,'mask':0,'domAt':1000001100.4,'sentAt':1000001100.5})
        facts=self.audit(report)['input_transport'];self.assertEqual(facts['unmatched_main_sequences'],[2])
        self.assertFalse(facts['all_reported_edges_accounted_for'])
        for key,value in (('mask',0),('domAt',1000000101.),('workerReceivedAt',1000000107.),
                          ('guestCounterAtReceipt',1001),('firstGuestCounter',1002),
                          ('completedBatchAt',1000000102.),('superseded',True)):
            with self.subTest(key=key):
                report=self.input_fixture();report['worker']['inputs'][0][key]=value
                with self.assertRaises(ValueError):self.audit(report)

    def test_supersession_never_claims_guest_consumption_for_the_old_mask(self):
        report=self.input_fixture();first=report['worker']['inputs'][0]
        second=copy.deepcopy(first);second['sequence']=2;second['mask']=32
        report['worker']['inputs']=[first,second]
        first['superseded']=True;first.pop('firstGuestCounter');first.pop('completedBatchAt')
        report['main']['inputs'].append({**report['main']['inputs'][0],'sequence':2,'mask':32})
        facts=self.audit(report)['input_transport']
        self.assertEqual(facts['superseded_before_next_frame'],1)
        self.assertEqual(facts['first_subsequent_counter_observed'],1)

    def test_preserved_runtime_and_host_must_match_frozen_identity(self):
        for name in ('runtime/mgba.audio-worklet.js','web_performance.html','sources/capture.sav','state.metadata.json'):
            path=self.directory/name;before=path.read_bytes()
            try:
                path.write_bytes(before+b'\nunit corruption\n')
                with self.assertRaises(ValueError):self.audit(self.fixture())
            finally:path.write_bytes(before)


if __name__=='__main__':unittest.main()
