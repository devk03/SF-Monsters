"""Pure receipt-corruption tests. No browser, native core or commercial data."""
import copy
import importlib.util
import sys
from pathlib import Path
from unittest import TestCase, main, mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/quality'))
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
        state=dict(running=False,counter=42,due=0,executed=0,overflowDropped=0,backlog=0,saveEpoch=1,
                   playbackEpoch=1,runDeadlineMs=100000,lifecycleFactOverflow=False,clockOriginMs=clock_origin,
                   pausedAtMs=ms,pausedPhase=dict(elapsedMs=ms-clock_origin,fractionalFrame=.5))
        resumed={**state,'running':True,'clockOriginMs':clock_origin+40,'phaseAnchorMs':ms+40,
                 'phaseAnchorElapsedMs':state['pausedPhase']['elapsedMs']}
        facts.append(dict(i=i,pauseBefore=anchor(ms,i*.06),pauseAfter=anchor(ms+1,i*.06,'suspended'),
                          resumeBefore=anchor(ms+39,i*.06,'suspended'),resumeAfter=anchor(ms+41,i*.06+.005),
                          paused=state,still=copy.deepcopy(state),resumed=resumed,packet=dict(counter=42,saveEpoch=1)))
        clock_origin+=40
    pinned={'mgba.js':'4a19067b25b423d9b37ab41b8623e01a59c172dc856e6c03d827807df7b9ebe4',
            'mgba.wasm':'8554455ae6d70ae639e98c589fbf1340901a8c16b0303539366ff2575493f00c',
            'mgba.audio-worklet.js':'e886fb55131713940a1a396a99b2d9002a8a33cad1a3622470a7f9ae2b21727a'}
    identity=dict(private_runtime_override=True,private_page_override=True,public_progress_touched=False,
                  page_sha256='page',server_source_sha256='server',runtime=pinned)
    first=dict(workerReceivedAt=origin+95,snapshot=periodic)
    report=dict(kind='private-audio-pause-watch-v1',schema=2,context=dict(identity=identity),
                scope=dict(physicalOutputProven=False,productionCompatible=False),visibility='visible',
                visibilityTrace=[dict(state='visible',at=origin)],firstAck=first,
                before=anchor(0,0),after=anchor(6000,186368/44100),observations=facts,
                watch=dict(reason='manual',epoch=1,finalAcknowledged=True,finalAudio=raw,snapshots=[first],
                           startedAt=origin+1,endedAt=origin+5999,initial=dict(runDeadlineMs=100000,saveEpoch=1,playbackEpoch=1),final=dict(saveEpoch=1,playbackEpoch=1)))
    hashes={**pinned,'web_performance.html':'page','server-source.py':'server'}
    return report,identity,hashes


class AuditTests(TestCase):
    def run_audit(self,value=None):
        report,identity,hashes=fixture()
        if value:value(report)
        with mock.patch.object(module,'checkpoint'),mock.patch.object(module,'hash_file',side_effect=lambda p:hashes[p.name]):
            return module.audit(report,identity,Path('/synthetic-private-proof'))
    def test_valid_and_losses_are_honest(self):
        self.assertTrue(self.run_audit()['zero_reported_audio_loss'])
        result=self.run_audit(lambda r:r['watch']['finalAudio'].update(underrunOutputFrames=7))
        self.assertFalse(result['zero_reported_audio_loss']);self.assertEqual(result['audio']['underrunOutputFrames'],7)
    def test_paused_core_clock_epoch_and_lease_corruption(self):
        for mutate in [lambda r:r['observations'][1]['still'].update(counter=43),
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

if __name__=='__main__':main()
