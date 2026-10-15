"""Audit a private real-worklet readonly-pause receipt, not general performance."""
from pathlib import Path
import argparse
import json
import re
from audit_worker_proof import audio, checkpoint, equal, hash_file, num


PRE_GUARD_WORKER_SHA256 = "104dc535af79e4e8cbb2c7c9eb6af38209137fe075567b9a4aeacb5688c67222"


def audit(report, identity, directory, *, allow_pre_guard=False):
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
    started=num(watch['startedAt'],'watch start');ended=num(watch['endedAt'],'watch close')
    duration=num(watch['durationMs'],'watch duration',integer=True,maximum=60000)
    if not duration or not started<ended<=started+duration+1:raise ValueError('Invalid finite watch interval')
    equal(watch['finalAcknowledged'],True,'worklet final acknowledgement')
    epoch=num(watch['epoch'],'epoch',integer=True)
    final=audio(watch['finalAudio'],epoch);equal(final['final'],True,'final flag')
    if type(watch['snapshots']) is not list or not 1<=len(watch['snapshots'])<=32000:raise ValueError('Require bounded periodic raw audio observations')
    previous=None;queues=[];previous_received=started
    for entry in watch['snapshots']:
        received=num(entry['workerReceivedAt'],'raw worklet receipt time')
        if not previous_received<=received<=ended+500:raise ValueError('Raw receipt time is outside ordered watch')
        previous_received=received
        observed=audio(entry['snapshot'],epoch);queues.append(observed['queueDepthFrames'])
        equal(observed['final'],False,'periodic flag')
        equal(observed['outputSampleRate'],final['outputSampleRate'],'unchanged output rate')
        equal(observed['prefillTargetSourceFrames'],final['prefillTargetSourceFrames'],'unchanged native prefill')
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
    # Same disclosed 50ms endpoint binding used by audit_worker_proof.py.
    allowance=.05;rate=final['outputSampleRate']
    first_seconds=final['firstOutputFrame']/rate
    final_seconds=final['observedThroughOutputFrame']/rate
    prefix=max(0,(started-(before['timeOrigin']+before['beforeMs']))/1000)
    suffix=max(0,((after['timeOrigin']+after['afterMs'])-ended)/1000)
    if not before['currentTime']-allowance<=first_seconds<=before['currentTime']+prefix+allowance:
        raise ValueError('Raw worklet start is not bound to the real AudioContext anchor')
    if not after['currentTime']-suffix-allowance<=final_seconds<=after['currentTime']+allowance:
        raise ValueError('Raw worklet close is not bound to the real AudioContext anchor')
    observations=report['observations']
    if len(observations)!=20:raise ValueError('Require exactly20readonly pause cycles')
    flash_hash=observations[0]['packet']['sha256']
    if not re.fullmatch('[0-9a-f]{64}',flash_hash):raise ValueError('Invalid paused raw Flash hash')
    initial=watch['initial'];policy=initial['clockPolicy']
    if policy not in ('worker-wall-v1','consumed-source-v1'):raise ValueError('Unknown pause credit policy')
    source_clock=policy=='consumed-source-v1'
    fps=num(initial['framerate'],'native FPS')
    if abs(fps-16777216/280896)>1e-6:raise ValueError('Native FPS differs from fixed GBA clock')
    if not num(initial['coreRate'],'native source rate',integer=True):raise ValueError('Native source rate must be positive')
    equal(initial['prefillLeadNativeFrames'],4 if source_clock else 0,'declared initial lead')
    if source_clock:equal(initial['coreRate'],65536,'fixed source clock')
    qualification_gaps=[];states=[];previous_state=None
    def worker_state(state):
        nonlocal previous_state
        for key in ['clockPolicy','prefillLeadNativeFrames','coreRate','framerate','saveEpoch','playbackEpoch']:
            equal(state[key],initial[key],'fixed watch metadata '+key)
        equal(state['playbackAcknowledged'],True,'playback reset acknowledged')
        equal(state['batteryVerified'],True,'verified native battery')
        equal(state['fatalSaveError'],None,'no fatal save error')
        equal(state['runExpired'],False,'finite run not expired')
        if 'fatalClockError' not in state:
            if not allow_pre_guard or identity['runtime'].get('worker-proof.js')!=PRE_GUARD_WORKER_SHA256:
                raise ValueError('Missing fatal clock observation; explicit pinned pre-guard mode required')
            if not qualification_gaps:qualification_gaps.append('Pinned pre-guard Worker did not expose fatalClockError')
        else:equal(state['fatalClockError'],None,'no fatal clock error')
        for key in ['due','executed','overflowDropped','backlog','enqueuedSourceFrames','consumedSourceFrames']:
            num(state[key],'worker '+key,integer=True)
        num(state['counter'],'native counter',integer=True,maximum=0xffffffff)
        num(state['workerAt'],'worker snapshot time');num(state['workerTimeOrigin'],'worker time origin')
        num(state['clockOriginMs'],'worker clock origin')
        equal(state['workerTimeOrigin'],initial['workerTimeOrigin'],'fixed worker origin')
        deadline=num(state['runDeadlineMs'],'finite wall deadline')
        remaining=state['workerTimeOrigin']+deadline-state['workerAt']
        if not 0<=remaining<=900000:raise ValueError('Snapshot exceeds bounded finite lease')
        if state['consumedSourceFrames']>state['enqueuedSourceFrames']:raise ValueError('Consumed source exceeds posted PCM')
        if state['due']!=state['executed']+state['overflowDropped']+state['backlog'] or state['backlog']>30:
            raise ValueError('Snapshot frame credits are not conserved')
        equal(state['lifecycleFactOverflow'],False,'bounded lifecycle facts')
        if previous_state:
            if state['workerAt']<previous_state['workerAt']:raise ValueError('Worker snapshot clock regressed')
            for key in ['due','executed','overflowDropped','enqueuedSourceFrames','consumedSourceFrames']:
                if state[key]<previous_state[key]:raise ValueError('Worker sequence regressed: '+key)
            if (state['counter']-previous_state['counter'])&0xffffffff!=state['executed']-previous_state['executed']:
                raise ValueError('Native counter differs from conserved execution')
            if deadline>previous_state['runDeadlineMs']:raise ValueError('Finite wall lease was extended')
        states.append(state);previous_state=state
    worker_state(initial)
    equal(initial['running'],True,'initial running state')
    if abs(initial['workerAt']-started)>1:raise ValueError('Initial Worker snapshot lies outside watch admission')
    lease=initial['runDeadlineMs'];previous_after=before['afterMs'];previous_audio=before['currentTime'];frozen_ms=0
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
        for state in [paused,still,resumed]:worker_state(state)
        # Producer pause/verification/resume snapshots must lie in actual RPC brackets.
        base=before['timeOrigin']
        if not base+p0['beforeMs']-1<=paused['workerAt']<=base+p1['afterMs']+1:
            raise ValueError('Worker pause is outside actual pause bracket')
        if not paused['workerAt']<=still['workerAt']<=base+r0['afterMs']+1:
            raise ValueError('Readonly verification lies outside suspended interval')
        if not base+r0['beforeMs']-1<=resumed['workerAt']<=base+r1['afterMs']+1:
            raise ValueError('Worker resume is outside actual resume bracket')
        equal(paused['running'],False,'paused core');equal(still['running'],False,'still paused core')
        equal(resumed['running'],True,'resumed core')
        for key in ['counter','due','executed','overflowDropped','backlog','saveEpoch','playbackEpoch','enqueuedSourceFrames']:
            equal(still[key],paused[key],'no paused advance '+key)
            equal(resumed[key],paused[key],'retained resume '+key)
        equal(row['packet']['sha256'],flash_hash,'readonly fixture Flash bytes')
        equal(row['packet']['counter'],paused['counter'],'paused Flash counter')
        equal(row['packet']['saveEpoch'],paused['saveEpoch'],'paused Flash epoch')
        equal(still['pausedPhase'],paused['pausedPhase'],'frozen phase')
        for state in [paused,still,resumed]:
            if state['runDeadlineMs']>lease:raise ValueError('Finite wall lease was extended')
        if still['runDeadlineMs']!=paused['runDeadlineMs'] or resumed['runDeadlineMs']>paused['runDeadlineMs']:
            raise ValueError('Readonly operation extended or changed the paused lease')
        lease=resumed['runDeadlineMs']
        phase=paused['pausedPhase']
        num(phase['fractionalFrame'],'fractional phase');num(phase['elapsedMs'],'paused active elapsed')
        num(resumed['phaseAnchorElapsedMs'],'resumed active elapsed');num(resumed['phaseAnchorMs'],'resumed phase anchor')
        num(paused['pausedAtMs'],'paused phase anchor')
        if not 0<=phase['fractionalFrame']<1:raise ValueError('Invalid fractional phase')
        if abs(resumed['phaseAnchorElapsedMs']-phase['elapsedMs'])>1e-9:
            raise ValueError('Active phase was reset on readonly resume')
        shift=resumed['clockOriginMs']-paused['clockOriginMs']
        actual_pause=resumed['phaseAnchorMs']-paused['pausedAtMs']
        if actual_pause<0 or abs(shift-actual_pause)>1e-6:raise ValueError('Origin shift differs from actual paused time')
    if final['observedThroughOutputFrame']/final['outputSampleRate']<=observations[-1]['resumeAfter']['currentTime']+1/59.7275:
        raise ValueError('Final worklet output does not include a post-resume tail')
    worker_state(watch['final']);equal(watch['final']['running'],True,'final running state')
    if abs(watch['final']['workerAt']-ended)>1:raise ValueError('Final Worker snapshot lies outside watch close')
    equal(watch['initial']['saveEpoch'],watch['final']['saveEpoch'],'no save reset')
    equal(watch['initial']['playbackEpoch'],watch['final']['playbackEpoch'],'no playback reset')
    if previous_after>after['beforeMs']:raise ValueError('Cycles extend past the observation')
    first_ack=report.get('firstAck');trace=report.get('visibilityTrace')
    if first_ack is None:raise ValueError('Require first raw worklet acknowledgement')
    equal(first_ack,watch['snapshots'][0],'first raw acknowledgement')
    first_received=num(first_ack['workerReceivedAt'],'first raw receipt time')
    if not started<=first_received<=before['timeOrigin']+observations[0]['pauseBefore']['beforeMs']:
        raise ValueError('First pause preceded raw worklet acknowledgement')
    if type(trace) is not list or not trace:raise ValueError('Require complete visibility trace')
    previous_at=0
    for index,event in enumerate(trace):
        at=num(event['at'],'visibility timestamp')
        equal(event['state'],'visible','continuous visibility')
        if not previous_at<=at<=after['timeOrigin']+after['afterMs']:raise ValueError('Visibility timestamp outside ordered window')
        if index==0 and not before['timeOrigin']+before['beforeMs']<=at<=started:
            raise ValueError('Initial visibility does not precede watch')
        previous_at=at
    inferred_initial_queue=None
    if source_clock:
        # FIFO enable/disable messages bracket precisely the posted PCM interval.
        # Only the consumed-source policy rejects native rate changes while running.
        posted=watch['final']['enqueuedSourceFrames']-initial['enqueuedSourceFrames']
        played=final['renderedOutputFrames']-final['warmupOutputFrames']-final['underrunOutputFrames']
        inferred_initial_queue=final['queueDepthFrames']+played*initial['coreRate']/rate-posted+final['droppedSourceFrames']
        if not 0<=inferred_initial_queue<=32768:
            raise ValueError('Measured native PCM and worklet output imply an impossible initial ring queue')
    zero_audio=all(final[k]==0 for k in ['warmupOutputFrames','underrunOutputFrames','droppedSourceFrames'])
    zero_guest=all(state['overflowDropped']==0 for state in states)
    return {'receipt_integrity':True,'first_raw_ack_before_pause_proven':True,'visibility_trace_present':True,'clock_policy':policy,'qualification_gaps':qualification_gaps,'qualified_pause_observation':zero_audio and zero_guest and not qualification_gaps,'zero_guest_credit_loss':zero_guest,'cycles':20,'paused_flash_sha256':flash_hash,'audio_context_seconds':elapsed,'suspended_bracket_ms':frozen_ms,
            'audio':final,'queue_min_source_frames':min(queues),'queue_max_source_frames':max(queues),
            'queue_first_to_final_change_source_frames':queues[-1]-queues[0],
            'queue_min_ms':min(queues)/initial['coreRate']*1000,'queue_max_ms':max(queues)/initial['coreRate']*1000,
            'queue_final_ms':queues[-1]/initial['coreRate']*1000,'audio_clock_binding_allowance_ms':50,
            'zero_reported_audio_loss':zero_audio,'inferred_initial_source_queue':inferred_initial_queue,'source_balance_roundoff_allowance_source_frames':0,
            'scope':'One private real-worklet readonly-pause observation;50ms clock binding allowance. No speaker, listening, physical paint, persistence or general performance approval.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--allow-pre-guard',action='store_true',
                        help='Audit only the pinned pre-guard Worker with explicit qualification gap')
    parser.add_argument('--label',default='',help='Fresh bounded audit label; earlier receipts are preserved')
    parser.add_argument('--output-directory',type=Path,help='Existing directory for audit artifacts')
    args=parser.parse_args()
    if args.label and not re.fullmatch('[a-z0-9][a-z0-9-]{0,31}',args.label):
        parser.error('Use a bounded lowercase audit label')
    if args.output_directory is not None and not args.output_directory.is_dir():
        parser.error('Output directory must already exist')
    report=json.loads(args.report.read_bytes());directory=args.report.parent
    result=audit(report,json.loads((directory/'identity.json').read_bytes()),directory,
                 allow_pre_guard=args.allow_pre_guard)
    dependency=Path(__file__).with_name('audit_worker_proof.py')
    result.update(report_sha256=hash_file(args.report),auditor_sha256=hash_file(Path(__file__)),
                  dependency_sha256=hash_file(dependency))
    base=(args.output_directory or directory)/args.report.name
    suffix='.'+args.label if args.label else ''
    with base.with_suffix(suffix+'.pause-audit.json').open('x')as out:
        json.dump(result,out,indent=2,allow_nan=False);out.write('\n')
    with base.with_suffix(suffix+'.pause-auditor.py').open('xb')as out:
        out.write(Path(__file__).read_bytes())
    with base.with_suffix(suffix+'.pause-audit-dependency.py').open('xb')as out:
        out.write(dependency.read_bytes())
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
