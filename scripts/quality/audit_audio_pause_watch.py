"""Audit a private real-worklet readonly-pause receipt, not general performance."""
from pathlib import Path
import argparse
import json
from audit_worker_proof import audio, checkpoint, equal, hash_file, num


def audit(report, identity, directory):
    equal(report['kind'],'private-audio-pause-watch-v1','watch kind')
    equal(report['schema'],2,'schema');equal(report['context']['identity'],identity,'identity')
    equal(identity['private_runtime_override'],True,'private runtime')
    equal(identity['private_page_override'],True,'private page')
    equal(identity['public_progress_touched'],False,'public storage isolation')
    for field,name in [('page_sha256','web_performance.html'),('server_source_sha256','server-source.py')]:
        equal(hash_file(directory/name),identity[field],name)
    for name,digest in identity['runtime'].items():
        if Path(name).name!=name:raise ValueError('Runtime path is not a basename')
        equal(hash_file(directory/'runtime'/name),digest,'runtime '+name)
    for name,digest in {'mgba.js':'4a19067b25b423d9b37ab41b8623e01a59c172dc856e6c03d827807df7b9ebe4',
                        'mgba.wasm':'8554455ae6d70ae639e98c589fbf1340901a8c16b0303539366ff2575493f00c',
                        'mgba.audio-worklet.js':'e886fb55131713940a1a396a99b2d9002a8a33cad1a3622470a7f9ae2b21727a'}.items():
        equal(identity['runtime'][name],digest,'pinned '+name)
    checkpoint(identity,directory)
    equal(report['scope']['physicalOutputProven'],False,'physical scope')
    equal(report['scope']['productionCompatible'],False,'production scope')
    equal(report['visibility'],'visible','closing visibility')
    watch=report['watch'];equal(watch['reason'],'manual','watch completion')
    equal(watch['finalAcknowledged'],True,'worklet final acknowledgement')
    epoch=num(watch['epoch'],'epoch',integer=True)
    final=audio(watch['finalAudio'],epoch);equal(final['final'],True,'final flag')
    if not watch['snapshots']:raise ValueError('No periodic raw audio observations')
    previous=None;queues=[]
    for entry in watch['snapshots']:
        observed=audio(entry['snapshot'],epoch);queues.append(observed['queueDepthFrames'])
        equal(observed['firstOutputFrame'],final['firstOutputFrame'],'audio interval start')
        if observed['observedThroughOutputFrame']>final['observedThroughOutputFrame']:
            raise ValueError('Periodic audio lies after final interval')
        if previous:
            for key in ['observedThroughOutputFrame','warmupOutputFrames','underrunOutputFrames','droppedSourceFrames']:
                if observed[key]<previous[key]:raise ValueError('Audio counters regressed')
        previous=observed
    for key in ['observedThroughOutputFrame','warmupOutputFrames','underrunOutputFrames','droppedSourceFrames']:
        if final[key]<previous[key]:raise ValueError('Final audio counters regressed')
    queues.append(final['queueDepthFrames'])
    def anchor(value,state):
        for key in ['beforeMs','afterMs','currentTime','timeOrigin']:num(value[key],'audio '+key)
        if value['beforeMs']>value['afterMs']:raise ValueError('Audio read bracket regressed')
        equal(value['state'],state,'actual AudioContext state');return value
    before=anchor(report['before'],'running');after=anchor(report['after'],'running')
    equal(before['timeOrigin'],after['timeOrigin'],'main clock origin')
    elapsed=after['currentTime']-before['currentTime']
    if elapsed<=0 or abs(final['renderedOutputFrames']/final['outputSampleRate']-elapsed)>.05:
        raise ValueError('Actual AudioContext and worklet output differ by over50ms')
    if not before['timeOrigin']+before['afterMs']<=watch['startedAt']<=watch['endedAt']<=after['timeOrigin']+after['beforeMs']:
        raise ValueError('Watch lies outside actual main clock brackets')
    observations=report['observations']
    if len(observations)!=20:raise ValueError('Require exactly20readonly pause cycles')
    lease=watch['initial']['runDeadlineMs'];previous_after=before['afterMs'];previous_audio=before['currentTime'];frozen_ms=0
    for index,row in enumerate(observations):
        equal(row['i'],index,'cycle order')
        p0=anchor(row['pauseBefore'],'running');p1=anchor(row['pauseAfter'],'suspended')
        r0=anchor(row['resumeBefore'],'suspended');r1=anchor(row['resumeAfter'],'running')
        for value in [p0,p1,r0,r1]:equal(value['timeOrigin'],before['timeOrigin'],'cycle clock origin')
        if not previous_after<=p0['beforeMs']<=p0['afterMs']<=p1['beforeMs']<=p1['afterMs']<=r0['beforeMs']<=r0['afterMs']<=r1['beforeMs']:
            raise ValueError('Cycle AudioContext brackets are out of order')
        if not previous_audio<=p0['currentTime']<=p1['currentTime']<=r0['currentTime']<=r1['currentTime']<=after['currentTime']:
            raise ValueError('Actual AudioContext cycle clock regressed')
        previous_audio=r1['currentTime']
        equal(p1['currentTime'],r0['currentTime'],'suspended AudioContext clock')
        frozen_ms+=r0['beforeMs']-p1['afterMs'];previous_after=r1['afterMs']
        paused,still,resumed=row['paused'],row['still'],row['resumed']
        equal(paused['running'],False,'paused core');equal(still['running'],False,'still paused core')
        equal(resumed['running'],True,'resumed core')
        for key in ['counter','due','executed','overflowDropped','backlog','saveEpoch','playbackEpoch']:
            equal(still[key],paused[key],'no paused advance '+key)
            equal(resumed[key],paused[key],'retained resume '+key)
        equal(row['packet']['counter'],paused['counter'],'paused Flash counter')
        equal(row['packet']['saveEpoch'],paused['saveEpoch'],'paused Flash epoch')
        equal(still['pausedPhase'],paused['pausedPhase'],'frozen phase')
        for state in [paused,still,resumed]:
            if state['runDeadlineMs']>lease:raise ValueError('Finite wall lease was extended')
            if state['due']!=state['executed']+state['overflowDropped']+state['backlog']:
                raise ValueError('Snapshot frame credits are not conserved')
            equal(state['lifecycleFactOverflow'],False,'bounded lifecycle facts')
        if still['runDeadlineMs']!=paused['runDeadlineMs'] or resumed['runDeadlineMs']>paused['runDeadlineMs']:
            raise ValueError('Readonly operation extended or changed the paused lease')
        lease=resumed['runDeadlineMs']
        phase=paused['pausedPhase']
        if not 0<=phase['fractionalFrame']<1:raise ValueError('Invalid fractional phase')
        if abs(resumed['phaseAnchorElapsedMs']-phase['elapsedMs'])>1e-9:
            raise ValueError('Active phase was reset on readonly resume')
        shift=resumed['clockOriginMs']-paused['clockOriginMs']
        actual_pause=resumed['phaseAnchorMs']-paused['pausedAtMs']
        if actual_pause<0 or abs(shift-actual_pause)>1e-6:raise ValueError('Origin shift differs from actual paused time')
    equal(watch['initial']['saveEpoch'],watch['final']['saveEpoch'],'no save reset')
    equal(watch['initial']['playbackEpoch'],watch['final']['playbackEpoch'],'no playback reset')
    if previous_after>after['beforeMs']:raise ValueError('Cycles extend past the observation')
    first_ack=report.get('firstAck');trace=report.get('visibilityTrace')
    if first_ack is not None:
        equal(first_ack,watch['snapshots'][0],'first raw acknowledgement')
        if first_ack['workerReceivedAt']>before['timeOrigin']+observations[0]['pauseBefore']['beforeMs']:
            raise ValueError('First pause preceded raw worklet acknowledgement')
    if trace is not None:
        if not trace or any(row['state']!='visible' for row in trace):raise ValueError('Watch was not continuously visible')
    return {'receipt_integrity':True,'first_raw_ack_before_pause_proven':first_ack is not None,'visibility_trace_present':trace is not None,'cycles':20,'audio_context_seconds':elapsed,'suspended_bracket_ms':frozen_ms,
            'audio':final,'queue_min_source_frames':min(queues),'queue_max_source_frames':max(queues),
            'queue_first_to_final_change_source_frames':queues[-1]-queues[0],
            'zero_reported_audio_loss':all(final[k]==0 for k in ['warmupOutputFrames','underrunOutputFrames','droppedSourceFrames']),
            'scope':'One private real-worklet readonly-pause observation;50ms clock binding allowance. No speaker, listening, physical paint, persistence or general performance approval.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path,required=True);args=parser.parse_args()
    report=json.loads(args.report.read_bytes());directory=args.report.parent
    result=audit(report,json.loads((directory/'identity.json').read_bytes()),directory)
    result.update(report_sha256=hash_file(args.report),auditor_sha256=hash_file(Path(__file__)))
    target=args.report.with_suffix('.pause-audit.json')
    with target.open('x')as out:json.dump(result,out,indent=2);out.write('\n')
    with args.report.with_suffix('.pause-auditor.py').open('xb')as out:out.write(Path(__file__).read_bytes())
    with args.report.with_suffix('.pause-audit-dependency.py').open('xb')as out:out.write(Path(__file__).with_name('audit_worker_proof.py').read_bytes())
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
