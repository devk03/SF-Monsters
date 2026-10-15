"""Independent literal frame-debt vectors, without importing the SDK or probe."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
from audit_frame_debt import audit,audit_ledger


def fixture(rows=None):
    # Literal deadlines and consequences: twelve due, five run, seven remain;
    # one fresh frame then allows five plus three to drain on the same deadline.
    rows=rows if rows is not None else [(0,0,0,0,0,0.),(12,5,5,0,7,12.),
                                       (1,5,5,0,3,13.),(0,3,3,0,0,13.)]
    blob=b''.join(struct.pack('<HBHBd',new,(planned<<4)|actual,drop,after,time)
                  for new,planned,actual,drop,after,time in rows)
    return {'schema':2,'valid':True,'reason':'duration','durationMs':10000,'elapsedMs':10001,
        'context':{'identity':{},'framerate':1000,'diagnosticEpoch':7,'framePacing':{
            'strategy':'bounded-debt-v1','maxFramesPerTick':5,'maxPendingFrames':30,'clockOriginMs':1000,
            'initialDue':0,'initialBacklog':0,'initialGuestCounter':100}},
        'framePacing':{'ledgerEncoding':'u16-u4u4-u16-u8-f64le-v1','ledgerBase64':base64.b64encode(blob).decode(),
            'ledgerRows':4,'initialBacklog':0,'finalBacklog':0,'maxPendingFramesObserved':12,
            'maxBacklogAfter':7,'newlyDueOverTickCapFrames':7},
        'ticks':{'count':4,'visible':4,'hidden':0,'requestedFrames':13,'plannedFrames':13,'executedFrames':13,
            'actualVideoFrames':13,'discardedFrames':0,'videoFrameMismatchTicks':0,'renderSubmissions':3,
            'rafGapMs':{'count':0},'runMs':{'count':0},'renderMs':{'count':0},
            'oldestDebtAgeMs':{'count':4,'min':0,'max':6,'p50':0,'p95':6,'p99':6,'mean':2}},
        'input':{'count':0,'supersededBeforeFrame':0,'domToDispatchMs':{'count':0},
            'dispatchToFrameMs':{'count':0},'dispatchToSubmitMs':{'count':0}},
        'pendingInputAtEnd':False,'scope':{'foregroundOnly':True},'audioFinalAcknowledged':True,
        'audio':{'warmupOutputFrames':0,'underrunOutputFrames':1,'droppedSourceFrames':0,
            'renderedOutputFrames':470000,'processQuanta':3600,'observedThroughOutputFrame':470100},
        'audioClockAtClose':{'guestCounter':113},
        'audioFinalSnapshot':{'type':'diagnostics','final':True,'epoch':7,'warmupOutputFrames':0,
            'underrunOutputFrames':2,'droppedSourceFrames':3,'renderedOutputFrames':480000,
            'processQuanta':3750,'firstOutputFrame':100,'observedThroughOutputFrame':480100,
            'outputSampleRate':48000,'queueDepthFrames':512.5}}


def replace_row(report,index,*,new=None,planned=None,actual=None,drop=None,after=None,time=None):
    raw=bytearray(base64.b64decode(report['framePacing']['ledgerBase64']))
    fresh,bits,dropped,backlog,elapsed=struct.unpack_from('<HBHBd',raw,index*14)
    values=(fresh if new is None else new,((bits>>4 if planned is None else planned)<<4)|(bits&15 if actual is None else actual),
            dropped if drop is None else drop,backlog if after is None else after,elapsed if time is None else time)
    struct.pack_into('<HBHBd',raw,index*14,*values);report['framePacing']['ledgerBase64']=base64.b64encode(raw).decode()


class FrameDebtAuditTest(unittest.TestCase):
    def setUp(self):self.report=fixture()
    def reject(self,report):
        with self.assertRaises(ValueError):audit_ledger(report)
    def test_literal_stall_catches_up_without_losing_or_double_counting_demand(self):
        result=audit_ledger(self.report)
        self.assertEqual((result['newly_due_frames'],result['planned_frames'],result['executed_frames']),(13,13,13))
        self.assertEqual((result['max_pending_frames'],result['max_backlog_after'],result['debt_ticks']),(12,7,2))
        self.assertTrue(result['loss_free']);self.assertTrue(result['caught_up_at_close'])
        self.assertIn('does not establish deadline',result['scope'])
    def test_retained_debt_is_not_dropped_and_common_projection_is_explicit_and_nonmutating(self):
        report=fixture([(0,0,0,0,0,0.),(12,5,5,0,7,12.)]);report['ticks'].update(count=2,visible=2,
            requestedFrames=12,plannedFrames=5,executedFrames=5,actualVideoFrames=5,renderSubmissions=1,
            oldestDebtAgeMs={'count':2,'min':0,'max':6,'p50':0,'p95':6,'p99':6,'mean':3})
        report['framePacing'].update(ledgerRows=2,finalBacklog=7);report['audioClockAtClose']['guestCounter']=105
        with self.subTest(scope='common projection'):
            runtime=Path(tempfile.mkdtemp(prefix='debt-audit-',dir=ROOT/'.tools'))
            payload=b'independently pinned runtime';(runtime/'sdk.js').write_bytes(payload)
            identity={'runtime':{'sdk.js':hashlib.sha256(payload).hexdigest()}}
            report['context']['identity']=identity;before=copy.deepcopy(report)
            result=audit(report,identity,runtime)
            self.assertEqual(report,before);self.assertTrue(result['frame_debt']['loss_free'])
            self.assertFalse(result['frame_debt']['caught_up_at_close'])
            self.assertEqual(result['normalization']['original_requested_frames'],12)
            self.assertEqual(result['normalization']['projected_requested_frames'],5)
            self.assertEqual(result['underrun_output_frames'],2);self.assertEqual(result['dropped_source_frames'],3)
            (runtime/'sdk.js').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'runtime bytes'):audit(report,identity,runtime)
    def test_overflow_is_real_loss_even_when_conservation_and_bounds_are_valid(self):
        report=fixture([(0,0,0,0,0,0.),(50,5,5,20,25,50.)]);report['ticks'].update(count=2,visible=2,
            requestedFrames=50,plannedFrames=5,executedFrames=5,actualVideoFrames=5,discardedFrames=20,
            oldestDebtAgeMs={'count':2,'min':0,'max':24,'p50':0,'p95':24,'p99':24,'mean':12})
        report['framePacing'].update(ledgerRows=2,finalBacklog=25,maxPendingFramesObserved=30,maxBacklogAfter=25,newlyDueOverTickCapFrames=45)
        report['audioClockAtClose']['guestCounter']=105;result=audit_ledger(report)
        self.assertFalse(result['loss_free']);self.assertEqual(result['overflow_dropped_frames'],20)
    def test_actual_shortfall_stays_in_backlog_and_reports_mismatch(self):
        report=fixture([(5,5,3,0,2,5.)]);report['ticks'].update(count=1,visible=1,requestedFrames=5,plannedFrames=5,
            executedFrames=3,actualVideoFrames=3,videoFrameMismatchTicks=1,
            oldestDebtAgeMs={'count':1,'min':1,'max':1,'p50':1,'p95':1,'p99':1,'mean':1})
        report['framePacing'].update(ledgerRows=1,finalBacklog=2,maxPendingFramesObserved=5,maxBacklogAfter=2,newlyDueOverTickCapFrames=0)
        report['audioClockAtClose']['guestCounter']=103;result=audit_ledger(report)
        self.assertFalse(result['planned_execution_matches']);self.assertEqual(result['final_backlog'],2)
    def test_initial_debt_and_counter_wrap_are_accounted_once(self):
        report=fixture([(1,5,5,0,3,13.),(0,3,3,0,0,13.)]);report['context']['framePacing'].update(
            initialDue=12,initialBacklog=7,initialGuestCounter=0xFFFFFFFE)
        report['ticks'].update(count=2,visible=2,requestedFrames=1,plannedFrames=8,executedFrames=8,actualVideoFrames=8,
            oldestDebtAgeMs={'count':2,'min':0,'max':2,'p50':0,'p95':2,'p99':2,'mean':1})
        report['framePacing'].update(ledgerRows=2,initialBacklog=7,maxPendingFramesObserved=8,maxBacklogAfter=3,newlyDueOverTickCapFrames=0)
        report['audioClockAtClose']['guestCounter']=6;result=audit_ledger(report)
        self.assertEqual(result['newly_due_frames'],1);self.assertEqual(result['executed_frames'],8)
    def test_fractional_rate_and_elapsed_age_are_derived_without_frame_rounding(self):
        report=copy.deepcopy(self.report);report['context']['framerate']=2.5
        replace_row(report,1,time=4800.25);replace_row(report,2,time=5200.25);replace_row(report,3,time=5200.25)
        report['ticks']['oldestDebtAgeMs'].update(max=2400.25,p95=2400.25,p99=2400.25,mean=800.125)
        result=audit_ledger(report);self.assertEqual(result['oldest_debt_age_ms']['mean'],800.125)
        wrong=copy.deepcopy(report);wrong['ticks']['oldestDebtAgeMs']['max']=2400
        self.reject(wrong)
    def test_optional_input_debt_is_bounded_and_guest_counters_never_claim_acknowledgement(self):
        report=copy.deepcopy(self.report);report['input'].update(count=3,supersededBeforeFrame=1,
            firstGuestCounters=[101,113],debtFramesAtDispatch={'count':3,'min':0,'p50':0,'p95':7,'p99':7,'max':7,'mean':7/3},
            oldestDebtAgeAtDispatchMs={'count':3,'min':0,'p50':0,'p95':6,'p99':6,'max':6,'mean':2})
        result=audit_ledger(report)['input_debt_observation']
        self.assertEqual(result['first_guest_counters_checked'],2)
        self.assertIn('no raw input timing ledger',result['scope'])
        for values in ([100,113],[101,114],[113,101],[101,101],[101.0,113],[True,113],[101,2**32],[101],(101,113)):
            invalid=copy.deepcopy(report);invalid['input']['firstGuestCounters']=values
            with self.subTest(counters=values):self.reject(invalid)
        for field,key,value in (('debtFramesAtDispatch','count',4),('debtFramesAtDispatch','max',65536),
                ('debtFramesAtDispatch','p95',1.5),('debtFramesAtDispatch','mean',31),
                ('oldestDebtAgeAtDispatchMs','mean',float('nan')),('oldestDebtAgeAtDispatchMs','p50',7)):
            invalid=copy.deepcopy(report);invalid['input'][field][key]=value;self.reject(invalid)
        report['context']['framePacing']['initialGuestCounter']=0xFFFFFFFE
        report['audioClockAtClose']['guestCounter']=11;report['input']['firstGuestCounters']=[0xFFFFFFFF,11]
        self.assertTrue(audit_ledger(report)['ledger_well_formed'])
    def test_input_before_a_delayed_raf_may_observe_more_than_the_post_plan_cap(self):
        report=copy.deepcopy(self.report)
        report['input'].update(count=1,supersededBeforeFrame=0,firstGuestCounters=[101],
            debtFramesAtDispatch={'count':1,'min':47,'p50':47,'p95':47,'p99':47,'max':47,'mean':47},
            oldestDebtAgeAtDispatchMs={'count':1,'min':100,'p50':100,'p95':100,'p99':100,'max':100,'mean':100})
        result=audit_ledger(report)['input_debt_observation']
        self.assertEqual(result['debtFramesAtDispatch']['max'],47)
    def test_raw_policy_faults_cannot_be_hidden_by_plausible_summaries(self):
        for changes in ({'new':11},{'drop':1},{'planned':4},{'actual':6},{'after':0},{'time':11.999},
                        {'time':float('nan')},{'time':float('inf')},{'time':-1}):
            report=copy.deepcopy(self.report);replace_row(report,1,**changes)
            with self.subTest(changes=changes):self.reject(report)
        report=copy.deepcopy(self.report);replace_row(report,3,time=12.5);self.reject(report)
        # This recreates retiring all due work: the seven-frame debt disappears.
        report=copy.deepcopy(self.report);replace_row(report,1,after=0)
        report['framePacing']['maxBacklogAfter']=0;self.reject(report)
    def test_every_aggregate_and_exact_age_rank_is_independently_rederived(self):
        for group,names in (('ticks',('count','requestedFrames','plannedFrames','executedFrames','actualVideoFrames',
                'discardedFrames','videoFrameMismatchTicks')),('framePacing',('initialBacklog','finalBacklog',
                'maxPendingFramesObserved','maxBacklogAfter','newlyDueOverTickCapFrames'))):
            for name in names:
                report=copy.deepcopy(self.report);report[group][name]+=1
                with self.subTest(group=group,name=name):self.reject(report)
        for name in ('count','min','max','p50','p95','p99','mean'):
            report=copy.deepcopy(self.report);report['ticks']['oldestDebtAgeMs'][name]+=0.1 if name=='mean' else 1
            with self.subTest(age=name):self.reject(report)
        report=copy.deepcopy(self.report);report['ticks']['oldestDebtAgeMs']['mean']+=1e-11
        self.assertTrue(audit_ledger(report)['ledger_well_formed'])
    def test_canonical_base64_encoding_and_bounded_exact_length_are_required(self):
        encoded=self.report['framePacing']['ledgerBase64']
        alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        single=fixture([(5,5,3,0,2,5.)])['framePacing']['ledgerBase64']
        noncanonical=single[:-2]+alphabet[alphabet.index(single[-2])+1]+single[-1]
        for value in (encoded+'\n',encoded+'=',encoded[:-4],encoded+'AAAA','☃',b'AA==',noncanonical,'A'*2986672):
            report=copy.deepcopy(self.report);report['framePacing']['ledgerBase64']=value
            with self.subTest(value=str(value)[:30]):self.reject(report)
        for rows in (-1,True,4.,160001):
            report=copy.deepcopy(self.report);report['framePacing']['ledgerRows']=rows;self.reject(report)
    def test_context_numbers_counter_binding_and_missing_fields_fail_closed(self):
        for name,value in (('strategy','other'),('maxFramesPerTick',6),('maxPendingFrames',31),
            ('clockOriginMs',-1),('clockOriginMs',True),('initialDue',True),('initialDue',2**53),
            ('initialBacklog',31),('initialBacklog',-1),('initialGuestCounter',2**32)):
            report=copy.deepcopy(self.report);report['context']['framePacing'][name]=value;self.reject(report)
        for value in (0,-1,True,float('nan'),float('inf')):
            report=copy.deepcopy(self.report);report['context']['framerate']=value;self.reject(report)
        for value in (114,True,-1,2**32):
            report=copy.deepcopy(self.report);report['audioClockAtClose']['guestCounter']=value;self.reject(report)
        for group,name in (('framePacing','ledgerEncoding'),('framePacing','ledgerBase64'),('context','framerate'),
                           ('ticks','oldestDebtAgeMs'),('audioClockAtClose','guestCounter')):
            report=copy.deepcopy(self.report);del report[group][name];self.reject(report)
        report=copy.deepcopy(self.report);report['schema']=1;self.reject(report)
    def test_projection_cannot_skip_invalid_ledger_or_final_audio_integrity(self):
        runtime=Path(tempfile.mkdtemp(prefix='debt-common-',dir=ROOT/'.tools'));identity={'runtime':{}}
        report=copy.deepcopy(self.report);report['context']['identity']=identity
        for group,key,value in (('audioFinalSnapshot','epoch',8),('audioFinalSnapshot','final',False),
                               ('audioFinalSnapshot','observedThroughOutputFrame',480099)):
            bad=copy.deepcopy(report);bad[group][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):audit(bad,identity,runtime)
        bad=copy.deepcopy(report);bad['ticks']['requestedFrames']=999
        with self.assertRaisesRegex(ValueError,'Ledger summary'):audit(bad,identity,runtime)
    def test_cli_reads_standard_identity_and_runtime_and_preserves_auditor(self):
        directory=Path(tempfile.mkdtemp(prefix='debt-cli-',dir=ROOT/'.tools'));(directory/'runtime').mkdir()
        identity={'runtime':{}};report=copy.deepcopy(self.report);report['context']['identity']=identity
        path=directory/'report.json';path.write_text(json.dumps(report));(directory/'identity.json').write_text(json.dumps(identity))
        run=subprocess.run([sys.executable,str(ROOT/'scripts/quality/audit_frame_debt.py'),'--report',str(path)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(path.with_suffix('.audit.json').read_bytes())
        self.assertEqual(result['schema'],2);self.assertTrue(result['frame_debt']['ledger_well_formed'])
        self.assertEqual(path.with_suffix('.auditor.py').read_bytes(),(ROOT/'scripts/quality/audit_frame_debt.py').read_bytes())


if __name__=='__main__':unittest.main()
