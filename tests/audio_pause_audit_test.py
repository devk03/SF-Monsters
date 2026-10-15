"""Pure receipt-corruption tests. No browser, native core or commercial data."""
import copy
import importlib.util
import sys
from pathlib import Path
from unittest import TestCase, main, mock
HERE=Path(__file__).resolve().parents[1]/'scripts/quality'
AUDITOR_DIRECTORY=HERE if (HERE/'audit_audio_pause_watch.py').is_file() else HERE.parent/'scripts/quality'
sys.path.insert(0,str(AUDITOR_DIRECTORY))
import audit_audio_pause_watch as module


def fixture():
    origin=1700000000000
    def anchor(ms,audio,state='running'):
        return dict(beforeMs=ms,afterMs=ms,currentTime=audio,state=state,timeOrigin=origin)
    raw=dict(type='diagnostics',epoch=1,firstOutputFrame=0,observedThroughOutputFrame=186368,
             renderedOutputFrames=186368,warmupOutputFrames=0,underrunOutputFrames=0,
             droppedSourceFrames=0,processQuanta=1456,outputSampleRate=44100,
             queueDepthFrames=2000,prefillTargetSourceFrames=2622,playbackStarted=True,final=True)
    periodic={**raw,'observedThroughOutputFrame':4096,'renderedOutputFrames':4096,'processQuanta':32,'final':False}
    facts=[];clock_origin=0
    for i in range(20):
        ms=100+i*100
        executed=(i+1)*4
        state=dict(running=False,counter=100+executed,due=executed,executed=executed,overflowDropped=0,backlog=0,saveEpoch=1,
                   playbackEpoch=1,runDeadlineMs=100000,lifecycleFactOverflow=False,clockOriginMs=clock_origin,
                   clockPolicy='worker-wall-v1',prefillLeadNativeFrames=0,framerate=59.7275,coreRate=65536,
                   fatalClockError=None,fatalSaveError=None,playbackAcknowledged=True,batteryVerified=True,runExpired=False,
                   workerTimeOrigin=origin,workerAt=origin+ms+1,
                   enqueuedSourceFrames=6000+executed*1097,consumedSourceFrames=executed*1097,
                   pausedAtMs=ms,pausedPhase=dict(elapsedMs=ms-clock_origin,fractionalFrame=.5))
        resumed={**state,'running':True,'clockOriginMs':clock_origin+40,'phaseAnchorMs':ms+40,
                 'phaseAnchorElapsedMs':state['pausedPhase']['elapsedMs'],'workerAt':origin+ms+40}
        facts.append(dict(i=i,pauseBefore=anchor(ms,i*.06),pauseAfter=anchor(ms+1,i*.06,'suspended'),
                          resumeBefore=anchor(ms+39,i*.06,'suspended'),resumeAfter=anchor(ms+41,i*.06+.005),
                          paused=state,still={**state,'workerAt':origin+ms+38},resumed=resumed,packet=dict(counter=state['counter'],saveEpoch=1,sha256='a'*64)))
        clock_origin+=40
    pinned={'mgba.js':'4a19067b25b423d9b37ab41b8623e01a59c172dc856e6c03d827807df7b9ebe4',
            'mgba.wasm':'8554455ae6d70ae639e98c589fbf1340901a8c16b0303539366ff2575493f00c',
            'mgba.audio-worklet.js':'e886fb55131713940a1a396a99b2d9002a8a33cad1a3622470a7f9ae2b21727a'}
    identity=dict(private_runtime_override=True,private_page_override=True,public_progress_touched=False,
                  page_sha256='page',server_source_sha256='server',runtime=pinned)
    first=dict(workerReceivedAt=origin+95,snapshot=periodic)
    initial={**copy.deepcopy(facts[0]['paused']),'running':True,'counter':100,'due':0,'executed':0,
             'workerAt':origin+1,'enqueuedSourceFrames':6000,'consumedSourceFrames':0}
    final={**copy.deepcopy(facts[-1]['resumed']),'counter':352,'due':252,'executed':252,
           'workerAt':origin+5999,'enqueuedSourceFrames':282444,'consumedSourceFrames':280000}
    report=dict(kind='private-audio-pause-watch-v1',schema=2,context=dict(identity=identity),
                scope=dict(physicalOutputProven=False,productionCompatible=False),visibility='visible',
                visibilityTrace=[dict(state='visible',at=origin)],firstAck=first,
                before=anchor(0,0),after=anchor(6000,186368/44100),observations=facts,
                watch=dict(reason='manual',epoch=1,finalAcknowledged=True,finalAudio=raw,snapshots=[first],
                           startedAt=origin+1,endedAt=origin+5999,durationMs=6000,initial=initial,final=final))
    hashes={**pinned,'web_performance.html':'page','server-source.py':'server'}
    return report,identity,hashes


class AuditTests(TestCase):
    def run_audit(self,value=None,**kwargs):
        report,identity,hashes=fixture()
        if value:value(report)
        hashes.update(identity['runtime'])
        with mock.patch.object(module,'checkpoint'),mock.patch.object(module,'hash_file',side_effect=lambda p:hashes[p.name]):
            return module.audit(report,identity,Path('/synthetic-private-proof'),**kwargs)
    def test_valid_and_losses_are_honest(self):
        self.assertTrue(self.run_audit()['zero_reported_audio_loss'])
        result=self.run_audit(lambda r:r['watch']['finalAudio'].update(underrunOutputFrames=7))
        self.assertFalse(result['zero_reported_audio_loss']);self.assertFalse(result['qualified_pause_observation']);self.assertEqual(result['audio']['underrunOutputFrames'],7)
    def test_paused_core_clock_epoch_and_lease_corruption(self):
        for mutate in [lambda r:r['observations'][1]['still'].update(counter=43),
                       lambda r:r['observations'][1]['packet'].update(sha256='b'*64),
                       lambda r:r['observations'][1]['resumed'].update(playbackEpoch=2),
                       lambda r:r['observations'][1]['resumed'].update(runDeadlineMs=100001),
                       lambda r:r['observations'][1]['resumeBefore'].update(currentTime=.061)]:
            with self.assertRaises(ValueError):self.run_audit(mutate)
    def test_missing_final_early_ack_and_output_clock_corruption(self):
        for mutate in [lambda r:r['watch'].update(finalAcknowledged=False),
                       lambda r:r['firstAck'].update(workerReceivedAt=1700000000200),
                       lambda r:r['after'].update(currentTime=100),
                       lambda r:r['visibilityTrace'].append(dict(state='hidden',at=1700000000500))]:
            with self.assertRaises(ValueError):self.run_audit(mutate)

    def test_absolute_endpoint_shift_cannot_reuse_an_unrelated_audio_interval(self):
        def shift(report):
            for snapshot in [report['watch']['finalAudio'],report['watch']['snapshots'][0]['snapshot']]:
                snapshot['firstOutputFrame']+=441088
                snapshot['observedThroughOutputFrame']+=441088
        with self.assertRaises(ValueError):self.run_audit(shift)

    def test_every_cycle_uses_the_same_policy_rate_lead_and_epochs(self):
        def change_cycle(report,key,value):
            for name in ['paused','still','resumed']:
                report['observations'][5][name][key]=value
            if key=='saveEpoch':report['observations'][5]['packet']['saveEpoch']=value
        for key,value in [('saveEpoch',2),('playbackEpoch',2),('clockPolicy','unknown'),
                          ('coreRate',32768),('framerate',60),('prefillLeadNativeFrames',4)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                self.run_audit(lambda r:change_cycle(r,key,value))

    def test_source_policy_lead_and_rate_are_checked_at_admission(self):
        def source(report):
            for state in [report['watch']['initial'],report['watch']['final']]+[
                    row[name] for row in report['observations'] for name in ['paused','still','resumed']]:
                state['clockPolicy']='consumed-source-v1';state['prefillLeadNativeFrames']=4
        self.assertEqual(self.run_audit(source)['clock_policy'],'consumed-source-v1')
        for key,value in [('coreRate',32768),('prefillLeadNativeFrames',5),('clockPolicy','unknown')]:
            def mutate(report):
                source(report)
                report['watch']['initial'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.run_audit(mutate)

    def test_fatal_and_reset_failures_cannot_qualify(self):
        for key,value in [('fatalClockError','bad ACK'),('fatalSaveError','bad save'),
                          ('playbackAcknowledged',False),('batteryVerified',False),('runExpired',True)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                self.run_audit(lambda r:r['observations'][1]['still'].update({key:value}))
        def overflow(report):
            for state in [report['watch']['initial'],report['watch']['final']]+[
                    row[name] for row in report['observations'] for name in ['paused','still','resumed']]:
                state['overflowDropped']=1;state['due']+=1
        result=self.run_audit(overflow)
        self.assertFalse(result['zero_guest_credit_loss']);self.assertFalse(result['qualified_pause_observation'])

    def test_ack_and_visibility_are_required_and_chronological(self):
        mutations=[lambda r:r.pop('firstAck'),lambda r:r.pop('visibilityTrace'),
                   lambda r:r.update(visibilityTrace=[]),
                   lambda r:r['visibilityTrace'][0].update(at=1700000007000),
                   lambda r:r['visibilityTrace'].extend([dict(state='visible',at=1700000000500),dict(state='visible',at=1700000000400)]),
                   lambda r:r['firstAck'].update(workerReceivedAt=1700000000000),
                   lambda r:r['observations'][1]['pauseAfter'].update(beforeMs=170),
                   lambda r:r['observations'][1]['paused'].update(workerAt=1700000000000)]
        for index,mutate in enumerate(mutations):
            with self.subTest(case=index),self.assertRaises(ValueError):self.run_audit(mutate)

    def test_native_counter_and_posted_source_cannot_regress_between_cycles(self):
        for key,value in [('counter',0),('executed',0),('enqueuedSourceFrames',0),('consumedSourceFrames',999999)]:
            def mutate(report):
                for name in ['paused','still','resumed']:report['observations'][3][name][key]=value
                if key=='counter':report['observations'][3]['packet']['counter']=value
                if key=='executed':
                    for name in ['paused','still','resumed']:report['observations'][3][name]['due']=0
            with self.subTest(key=key),self.assertRaises(ValueError):self.run_audit(mutate)

    def test_pre_guard_gap_is_explicit_pinned_and_never_qualified(self):
        def legacy(report):
            report['context']['identity']['runtime']['worker-proof.js']=module.PRE_GUARD_WORKER_SHA256
            for state in [report['watch']['initial'],report['watch']['final']]+[
                    row[name] for row in report['observations'] for name in ['paused','still','resumed']]:state.pop('fatalClockError')
        with self.assertRaises(ValueError):self.run_audit(legacy)
        result=self.run_audit(legacy,allow_pre_guard=True)
        self.assertFalse(result['qualified_pause_observation']);self.assertEqual(len(result['qualification_gaps']),1)

    def test_nonfinite_phase_and_unbounded_lease_cannot_pass_comparisons(self):
        mutations=[lambda r:r['observations'][0]['paused']['pausedPhase'].update(elapsedMs=float('nan')),
                   lambda r:r['observations'][0]['resumed'].update(phaseAnchorMs=float('nan')),
                   lambda r:r['watch']['initial'].update(runDeadlineMs=10**9),
                   lambda r:r['watch'].update(durationMs=60001),
                   lambda r:r['watch'].update(durationMs=1)]
        for index,mutate in enumerate(mutations):
            with self.subTest(case=index),self.assertRaises(ValueError):self.run_audit(mutate)

    def test_consumed_clock_pcm_must_cover_actual_output_within_ring_capacity(self):
        def impossible(report):
            states=[report['watch']['initial'],report['watch']['final']]+[
                    row[name] for row in report['observations'] for name in ['paused','still','resumed']]
            for state in states:
                state['clockPolicy']='consumed-source-v1';state['prefillLeadNativeFrames']=4
                state['enqueuedSourceFrames']=6000;state['consumedSourceFrames']=0
        with self.assertRaises(ValueError):self.run_audit(impossible)

if __name__=='__main__':main()
