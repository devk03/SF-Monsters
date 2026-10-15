"""Independently audit a private Worker transport proof, never full acceptance."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re


def num(value,name,*,integer=False,maximum=2**53-1):
    if type(value) not in (int,float) or integer and type(value) is not int:
        raise ValueError('Invalid numeric type: '+name)
    if value<0 or value>maximum or not math.isfinite(value):
        raise ValueError('Invalid numeric range: '+name)
    return value


def equal(value,expected,name):
    if type(value) is not type(expected) or value!=expected:
        raise ValueError('Observation differs: '+name)


def hash_file(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def audio(snapshot,epoch):
    if type(snapshot) is not dict or snapshot.get('type')!='diagnostics':
        raise ValueError('Missing raw worklet snapshot')
    equal(snapshot['epoch'],epoch,'audio epoch')
    for key in ('firstOutputFrame','observedThroughOutputFrame','renderedOutputFrames',
                'warmupOutputFrames','underrunOutputFrames','droppedSourceFrames','processQuanta'):
        num(snapshot[key],'audio.'+key,integer=True)
    num(snapshot['queueDepthFrames'],'audio queue',maximum=32768)
    num(snapshot['prefillTargetSourceFrames'],'audio prefill',integer=True,maximum=32767)
    num(snapshot['outputSampleRate'],'audio output sample rate',integer=True,maximum=192000)
    if snapshot['outputSampleRate']<8000 or type(snapshot['playbackStarted']) is not bool:
        raise ValueError('Invalid worklet playback observation')
    rendered=snapshot['observedThroughOutputFrame']-snapshot['firstOutputFrame']
    if rendered!=snapshot['renderedOutputFrames'] or rendered!=128*snapshot['processQuanta']:
        raise ValueError('Raw worklet output interval differs from rendered quanta')
    if snapshot['warmupOutputFrames']+snapshot['underrunOutputFrames']>rendered:
        raise ValueError('Worklet missing output exceeds rendered interval')
    return snapshot


def checkpoint(identity,directory):
    sources=identity['inputs']
    if type(sources) is not dict or not 4<=len(sources)<=5:
        raise ValueError('Require frozen ROM/state/Flash/metadata source hashes')
    by_suffix={}
    root=Path(__file__).resolve().parents[2]
    for name,expected in sources.items():
        path=Path(name)
        if not path.is_absolute():raise ValueError('Checkpoint source path must be absolute')
        path.resolve().relative_to(root)
        if not re.fullmatch('[0-9a-f]{64}',expected) or path.stat().st_size>32*1024*1024:
            raise ValueError('Invalid checkpoint source hash or byte bound')
        equal(hash_file(path),expected,'original checkpoint source')
        if path.suffix in ('.gba','.state','.sav','.json'):
            if path.suffix in by_suffix:raise ValueError('Ambiguous checkpoint source suffix')
            by_suffix[path.suffix]=(path,expected)
    for suffix,alias in (('.gba','rom.gba'),('.state','state.bin'),('.sav','battery.sav')):
        equal(by_suffix[suffix][1],identity['files'][alias],'source alias '+alias)
    equal(identity['rom_sha256'],identity['files']['rom.gba'],'cartridge identity alias')
    metadata_path,metadata_hash=by_suffix['.json']
    equal(metadata_hash,identity['source_state_metadata_sha256'],'source metadata hash')
    equal(hash_file(directory/'state.metadata.json'),metadata_hash,'preserved source metadata')
    metadata=json.loads(metadata_path.read_bytes())
    equal(metadata['controller_only'],True,'controller-only checkpoint provenance')
    equal(metadata['rom_sha256'],identity['rom_sha256'],'checkpoint cartridge provenance')
    equal(metadata['mgba_revision'],identity['mgba_revision'],'checkpoint core provenance')


def input_observations(report):
    """Cross-check message transport and first subsequent counters, not KEYINPUT."""
    worker=report['worker'];main=report['main'];rows=worker['rawLedger']
    dispatched=main['inputs'];observed=worker['inputs']
    if any(type(values)is not list or len(values)>40000 for values in (dispatched,observed)):
        raise ValueError('Invalid bounded Worker input ledger')
    pending=worker['pendingInputAtEnd']
    if type(pending)is not bool:raise ValueError('Missing closing input-pending observation')
    sent={};previous=0
    for event in dispatched:
        seq=num(event['sequence'],'main input sequence',integer=True)
        num(event['mask'],'main input mask',integer=True,maximum=1023)
        dom=num(event['domAt'],'main input DOM time');at=num(event['sentAt'],'main input send time')
        if seq<=previous or dom>at+1 or at>main['mainResultReceivedAt']:
            raise ValueError('Main input order or timestamp is inconsistent')
        previous=seq;sent[seq]=event
    boundaries={worker['initialGuestCounter']:worker['startedAt']};next_batch={}
    for row in rows:
        at=worker['workerTimeOrigin']+worker['clockOriginMs']+row[5]
        if row[2]:boundaries[row[7]]=at;next_batch[row[6]]=at
    matched=set();previous_seq=0;previous_ack=0;superseded=acknowledged=0
    transport=[];completion=[]
    for index,event in enumerate(observed):
        seq=num(event['sequence'],'Worker input sequence',integer=True)
        if seq<=previous_seq or seq not in sent:raise ValueError('Worker input has no ordered main dispatch')
        previous_seq=seq;source=sent[seq];matched.add(seq)
        equal(event['mask'],source['mask'],'input mask transport')
        equal(event['domAt'],source['domAt'],'input DOM timestamp transport')
        received=num(event['workerReceivedAt'],'Worker input receipt time')
        if not worker['startedAt']-1<=received<=worker['endedAt']+1 or received<source['sentAt']-1:
            raise ValueError('Worker input receipt is outside its window or precedes dispatch')
        cursor=num(event['guestCounterAtReceipt'],'input receipt counter',integer=True,maximum=0xFFFFFFFF)
        if cursor not in boundaries or received<boundaries[cursor]-1:
            raise ValueError('Input receipt counter is not a completed native batch boundary')
        if cursor in next_batch and received>next_batch[cursor]+1:
            raise ValueError('Input receipt counter is stale relative to native execution')
        transport.append(received-source['sentAt'])
        flag=event['superseded']
        if type(flag)is not bool:raise ValueError('Invalid input supersession flag')
        if flag:
            if 'firstGuestCounter'in event or index==len(observed)-1 and not pending:
                raise ValueError('Superseded input invents a first-frame acknowledgement')
            superseded+=1;continue
        first=num(event['firstGuestCounter'],'first subsequent guest counter',integer=True,maximum=0xFFFFFFFF)
        distance=(first-worker['initialGuestCounter'])&0xFFFFFFFF
        if first!=(cursor+1)&0xFFFFFFFF or distance<=previous_ack or cursor not in next_batch:
            raise ValueError('Input first subsequent counter does not match native progression')
        completed=num(event['completedBatchAt'],'input batch completion time')
        if completed<received or completed<next_batch[cursor]-1 or completed>worker['endedAt']+1:
            raise ValueError('Input completion is outside its acknowledged native batch window')
        previous_ack=distance;acknowledged+=1;completion.append(completed-received)
    def spread(values):
        if not values:return {'count':0}
        ordered=sorted(values);count=len(values)
        return {'count':count,'min':ordered[0],'max':ordered[-1],'p95':ordered[math.ceil(.95*count)-1]}
    return {'main_edges_reported':len(dispatched),'worker_edges_observed':len(observed),
        'superseded_before_next_frame':superseded,'first_subsequent_counter_observed':acknowledged,
        'unmatched_main_sequences':sorted(set(sent)-matched),'pending_worker_input_at_close':pending,
        'all_reported_edges_accounted_for':len(dispatched)==len(observed) and not pending,
        'reported_dispatch_to_worker_ms':spread(transport),'worker_receipt_to_batch_completion_ms':spread(completion),
        'cross_realm_clock_tolerance_ms':1,'guest_key_consumption_proven':False,
        'scope':'Matching main/Worker message sequences, masks, receipt batch boundaries and first subsequent native counter only; unmatched boundary edges remain explicit. No guest KEYINPUT or physical latency proof.'}


def audit(report,identity,directory):
    equal(report['schema'],2,'schema');equal(report['kind'],'private-worker-proof-v1','kind')
    equal(report['context']['identity'],identity,'frozen identity')
    equal(identity['private_runtime_override'],True,'private runtime')
    equal(identity['private_page_override'],True,'private host')
    equal(identity['public_progress_touched'],False,'public progress')
    for key,name in (('page_sha256','web_performance.html'),('server_source_sha256','server-source.py')):
        equal(hash_file(directory/name),identity[key],name+' hash')
    for name,expected in identity['runtime'].items():
        if not re.fullmatch(r'[A-Za-z0-9._-]+',name):raise ValueError('Invalid runtime path')
        equal(hash_file(directory/'runtime'/name),expected,name+' hash')
    pinned={'mgba.js':'4a19067b25b423d9b37ab41b8623e01a59c172dc856e6c03d827807df7b9ebe4',
            'mgba.wasm':'8554455ae6d70ae639e98c589fbf1340901a8c16b0303539366ff2575493f00c',
            'mgba.audio-worklet.js':'e886fb55131713940a1a396a99b2d9002a8a33cad1a3622470a7f9ae2b21727a'}
    for name,expected in pinned.items():equal(identity['runtime'][name],expected,'pinned '+name)
    checkpoint(identity,directory)
    boot=report['boot'];equal(boot['batteryVerified'],True,'verified boot Flash')
    equal(boot['width'],240,'boot GBA width');equal(boot['height'],160,'boot GBA height')
    num(boot['counter'],'boot guest counter',integer=True,maximum=0xFFFFFFFF)
    for key in ('physicalPaintProven','guestKeyConsumptionProven','productionCompatible'):
        equal(report['scope'][key],False,'scope.'+key)
    worker=report['worker'];main=report['main']
    equal(worker['reason'],'duration','completion reason')
    duration=num(worker['durationMs'],'duration',integer=True,maximum=600000)
    if duration==0:raise ValueError('Empty diagnostic duration')
    start=num(worker['startedAtMs'],'Worker start');end=num(worker['endedAtMs'],'Worker close')
    origin=num(worker['clockOriginMs'],'Worker clock origin');time_origin=num(worker['workerTimeOrigin'],'Worker time origin')
    fps=num(worker['framerate'],'native framerate')
    policy=worker.get('clockPolicy','worker-wall-v1')
    if policy not in ('worker-wall-v1','consumed-source-v1'):raise ValueError('Unknown private credit clock policy')
    equal(boot.get('clockPolicy','worker-wall-v1'),policy,'boot/measurement clock policy')
    source_clock=policy=='consumed-source-v1'
    posted=num(worker['initialSourceFramesPosted'],'initial posted PCM',integer=True) if source_clock else None
    previous_consumed=num(worker['initialConsumedSourceFrames'],'initial acknowledged source frames',integer=True) if source_clock else 0
    if source_clock:
        equal(worker['prefillLeadNativeFrames'],4,'declared lead')
        equal(boot['prefillLeadNativeFrames'],4,'boot lead')
        equal(worker['coreRate'],65536,'fixed native source clock')
        if previous_consumed>posted:raise ValueError('Initial consumed source clock exceeds posted PCM')
    if abs(fps-16777216/280896)>1e-6:raise ValueError('Framerate differs from native GBA clock')
    if not origin<=start<=end or end-start<duration or abs(worker['elapsedMs']-(end-start))>1e-6:
        raise ValueError('Worker diagnostic window regressed or ended early')
    for absolute,relative in (('startedAt',start),('endedAt',end)):
        if abs(num(worker[absolute],absolute)-(time_origin+relative))>1:
            raise ValueError('Worker absolute clock anchor differs')
    initial=worker['initialPacing'];final=worker['finalPacing']
    for value in (initial,final):
        for key in ('due','executed','overflowDropped','backlog'):num(value[key],'pacing.'+key,integer=True)
        if value['due']!=value['executed']+value['overflowDropped']+value['backlog'] or value['backlog']>30:
            raise ValueError('Global Worker credit conservation differs')
    for key,name in (('initialDue','due'),('initialBacklog','backlog')):equal(worker[key],initial[name],key)
    due=initial['due'];debt=initial['backlog'];counter=num(worker['initialGuestCounter'],'initial counter',integer=True,maximum=0xFFFFFFFF)
    initial_counter=counter;fresh_total=actual_total=drop_total=planned_total=0;max_pending=max_debt=mismatches=0
    previous_elapsed=start-origin;previous_tick=start;max_gap=0
    rows=worker['rawLedger']
    if type(rows) is not list or not 1<=len(rows)<=160000:raise ValueError('Invalid bounded raw tick ledger')
    tick_times=[]
    for i,row in enumerate(rows):
        if type(row) is not list or len(row)!=(11 if source_clock else 8):raise ValueError('Raw tick fields differ from declared clock policy')
        fresh,planned,actual,drop,after,elapsed,before_counter,after_counter=row[:8]
        for key,value in zip(('fresh','planned','actual','drop','after','beforeCounter','afterCounter'),
                             (fresh,planned,actual,drop,after,before_counter,after_counter)):
            num(value,f'{key} row{i}',integer=True,maximum=0xFFFFFFFF if 'Counter'in key else 65535)
        num(elapsed,'elapsed row'+str(i))
        if not previous_elapsed<=elapsed<=end-origin:raise ValueError('Worker tick clock outside ordered window')
        if source_clock:
            consumed,posted_before,posted_after=row[8:]
            for key,value in [('consumed',consumed),('posted before',posted_before),('posted after',posted_after)]:num(value,key,integer=True)
            if not previous_consumed<=consumed<=posted_before<=posted_after or posted_before!=posted:
                raise ValueError('Actual source clock or posted PCM sequence regressed')
            if actual==0 and posted_after!=posted_before:raise ValueError('PCM posted without native execution')
            previous_consumed=consumed;posted=posted_after
            next_due=4+math.floor(consumed/worker['coreRate']*fps)
        else:next_due=math.floor(elapsed/1000*fps)
        if next_due<due or fresh!=next_due-due:raise ValueError('Fresh Worker demand differs from raw clock')
        available=debt+fresh;expected_drop=max(0,available-30);available-=expected_drop
        if drop!=expected_drop or planned!=min(5,available) or actual>planned or after!=available-actual:
            raise ValueError('Worker bounded execution/debt policy differs')
        if before_counter!=counter or (after_counter-before_counter)&0xFFFFFFFF!=actual:
            raise ValueError('Worker guest counter sequence differs from actual execution')
        max_gap=max(max_gap,origin+elapsed-previous_tick);previous_tick=origin+elapsed
        previous_elapsed=elapsed;tick_times.append(time_origin+origin+elapsed)
        due=next_due;debt=after;counter=after_counter;max_pending=max(max_pending,available);max_debt=max(max_debt,after)
        fresh_total+=fresh;planned_total+=planned;actual_total+=actual;drop_total+=drop;mismatches+=planned!=actual
    if source_clock:
        equal(worker['finalSourceFramesPosted'],posted,'final native PCM posted')
        final_consumed=num(worker['finalConsumedSourceFrames'],'final acknowledged source frames',integer=True)
        if not previous_consumed<=final_consumed<=posted:raise ValueError('Closing source clock is outside posted PCM')
        equal(worker['sourceFramesPosted'],posted-worker['initialSourceFramesPosted'],'measured native PCM posted')
    equal(final['due'],due,'final due');equal(final['backlog'],debt,'final debt')
    equal(final['executed']-initial['executed'],actual_total,'global actual increment')
    equal(final['overflowDropped']-initial['overflowDropped'],drop_total,'global overflow increment')
    equal(worker['finalGuestCounter'],counter,'closing guest counter');equal(worker['finalBacklog'],debt,'closing debt')
    equal(worker['maxPending'],max_pending,'maximum pending');equal(worker['maxBacklog'],max_debt,'maximum backlog')
    if abs(worker['maxWorkerTickGapMs']-max_gap)>1e-6:raise ValueError('Maximum Worker tick gap differs')
    if initial['backlog']+fresh_total!=actual_total+drop_total+debt or (counter-initial_counter)&0xFFFFFFFF!=actual_total:
        raise ValueError('Independent Worker cumulative conservation failed')
    equal(worker['audioFinalAcknowledged'],True,'raw final audio acknowledgement')
    equal(worker['audioFinalError'],None,'raw final audio error')
    epoch=num(worker['epoch'],'audio diagnostic epoch',integer=True)
    final_audio=audio(worker['audioFinalSnapshot'],epoch);equal(final_audio['final'],True,'final audio flag')
    source_balance=None
    if source_clock:
        consumed_output=(final_audio['renderedOutputFrames']-final_audio['warmupOutputFrames']-final_audio['underrunOutputFrames'])*worker['coreRate']/final_audio['outputSampleRate']
        inferred_initial_queue=final_audio['queueDepthFrames']+consumed_output-worker['sourceFramesPosted']+final_audio['droppedSourceFrames']
        # Ordered messages: enable follows all prewindow PCM; disable follows
        # all measured PCM and precedes later PCM. Same unchanged fixed-rate ring.
        # Handlers run between whole quanta; no fabricated scheduling slack.
        if not 0<=inferred_initial_queue<=32768:
            raise ValueError('Measured native PCM cannot supply the actual worklet output interval')
        source_balance={'inferred_initial_queue_source_frames':inferred_initial_queue,
                        'handler_boundary_allowance_source_frames':0,
                        'ring_capacity_source_frames':32768,'measured_native_pcm_source_frames':worker['sourceFramesPosted'],
                        'actual_output_consumption_source_frames':consumed_output,
                        'scope':'Fixed-rate, unchanged same-port diagnostic/PCM ordering; source balance only, not a physical audio or speed approval.'}
    previous=None
    for observed in worker['audioSnapshots']:
        num(observed['workerReceivedAt'],'worklet receipt time')
        current=audio(observed['snapshot'],epoch)
        if current['firstOutputFrame']!=final_audio['firstOutputFrame'] or current['observedThroughOutputFrame']>final_audio['observedThroughOutputFrame']:
            raise ValueError('Periodic worklet snapshot differs from final interval')
        if previous:
            for key in ('observedThroughOutputFrame','warmupOutputFrames','underrunOutputFrames','droppedSourceFrames','processQuanta'):
                if current[key]<previous[key]:raise ValueError('Worklet counters regressed')
        previous=current
    if previous:
        for key in ('warmupOutputFrames','underrunOutputFrames','droppedSourceFrames','processQuanta'):
            if final_audio[key]<previous[key]:raise ValueError('Final worklet counters regressed')
    main_origin=num(main['timeOrigin'],'main time origin');before=main['audioClockBefore'];after=main['audioClockAfter']
    for anchor in (before,after):
        for key in ('beforeMs','afterMs','currentTime','timeOrigin'):num(anchor[key],'main audio.'+key)
        if anchor['beforeMs']>anchor['afterMs'] or anchor['timeOrigin']!=main_origin or anchor['state']!='running':
            raise ValueError('Invalid real main AudioContext read bracket')
    if before['afterMs']>after['beforeMs'] or before['currentTime']>after['currentTime']:
        raise ValueError('Main audio clock regressed')
    if not main_origin+before['afterMs']<=main['mainBeginSentAt']<=worker['startedAt']+1 or not worker['endedAt']-1<=main_origin+after['beforeMs']<=main['mainResultReceivedAt']:
        raise ValueError('Worker window is outside main RPC/audio clock brackets')
    # Bind both raw worklet endpoints to actual main AudioContext reads. A
    # disclosed50ms message/quantization allowance is receipt integrity only.
    # Measured main/Worker RPC prefix and suffix extend the respective brackets.
    allowance=.05;rate=final_audio['outputSampleRate']
    first_seconds=final_audio['firstOutputFrame']/rate
    final_seconds=final_audio['observedThroughOutputFrame']/rate
    prefix=max(0,(worker['startedAt']-(main_origin+before['beforeMs']))/1000)
    suffix=max(0,((main_origin+after['afterMs'])-worker['endedAt'])/1000)
    if not before['currentTime']-allowance<=first_seconds<=before['currentTime']+prefix+allowance:
        raise ValueError('Raw worklet start is not bound to the real AudioContext anchor')
    if not after['currentTime']-suffix-allowance<=final_seconds<=after['currentTime']+allowance:
        raise ValueError('Raw worklet close is not bound to the real AudioContext anchor')
    visibility=main['visibility']
    if type(visibility) is not list or not visibility:raise ValueError('Require initial visibility observation')
    previous_at=0
    for index,event in enumerate(visibility):
        at=num(event['at'],'visibility timestamp')
        if event['state']not in ('visible','hidden') or not previous_at<=at<=main['mainResultReceivedAt']:
            raise ValueError('Invalid or regressed visibility observation')
        if index==0 and not main_origin+before['beforeMs']-50<=at<=main['mainBeginSentAt']:
            raise ValueError('Initial visibility does not precede the measured window')
        previous_at=at
    input_facts=input_observations(report)
    replay_facts=None
    if identity.get('controller_route'):
        from audit_web_performance import controller_observation
        # Explicit clock-origin translation only; the raw Worker report stays
        # unchanged. Reuse the existing independent route-byte/timing auditor.
        projected={'controllerReplay':report.get('controllerReplay'),
            'startedAtMs':worker['startedAt']-main_origin,'endedAtMs':worker['endedAt']-main_origin}
        replay_facts=controller_observation(projected,identity,directory)
        masks=[int(line.split(',')[0]) for line in (directory/'route.csv').read_text().strip().splitlines()]
        replay_facts['all_planned_masks_reported']=masks==[event['mask'] for event in main['inputs']]
        replay_facts['clock_translation']='Worker absolute start/close minus explicit main time origin; no event-time rewriting.'
    overlap=[];overlap_frames=[]
    for stall in main['stalls']:
        begin=num(stall['startedAt'],'main stall start');finish=num(stall['endedAt'],'main stall finish')
        equal(stall['requestedMs'],200,'main stall duration')
        if not worker['startedAt']<=begin<=finish<=worker['endedAt'] or not 200<=finish-begin<=1000:
            raise ValueError('Main controlled stall is outside the Worker diagnostic interval')
        overlap.append(sum(begin<=t<=finish for t in tick_times))
        overlap_frames.append(sum(row[2] for row,t in zip(rows,tick_times) if begin<=t<=finish))
    if len(overlap)>1:raise ValueError('Repeated stall action is not this bounded experiment')
    return {'receipt_integrity':True,'scope':'Private Worker conservation and raw worklet transport observations only; no full performance, physical output, guest key consumption or production persistence approval.',
            'clock_policy':policy,'source_balance':source_balance,'native_seconds':actual_total/fps,'native_minus_worklet_seconds':actual_total/fps-final_audio['renderedOutputFrames']/final_audio['outputSampleRate'],
            'ticks':len(rows),'fresh_frames':fresh_total,'planned_frames':planned_total,'actual_frames':actual_total,
            'overflow_dropped_frames':drop_total,'closing_backlog':debt,'planned_mismatch_ticks':mismatches,
            'max_worker_tick_gap_ms':max_gap,'worker_ticks_during_each_main_stall':overlap,
            'frames_in_batches_admitted_during_each_main_stall':overlap_frames,
            'audio':{key:final_audio[key] for key in ('renderedOutputFrames','warmupOutputFrames','underrunOutputFrames','droppedSourceFrames','queueDepthFrames','outputSampleRate')},
            'main_audio_context_seconds':after['currentTime']-before['currentTime'],
            'main_canvas_submission_count':len(main['submissions']),'reported_main_input_count':len(main['inputs']),
            'audio_clock_binding_allowance_ms':50,'input_transport':input_facts,'controller_replay':replay_facts,
            'foreground_observed':all(v['state']=='visible' for v in main['visibility']),
            'loss_free':drop_total==0,'caught_up_at_close':debt==0}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--label',default='',help='Optional fresh audit label; preserves earlier audit receipts.')
    args=parser.parse_args();directory=args.report.parent
    if args.label and not re.fullmatch('[a-z0-9][a-z0-9-]{0,31}',args.label):parser.error('Use a bounded lowercase audit label')
    result=audit(json.loads(args.report.read_bytes()),json.loads((directory/'identity.json').read_bytes()),directory)
    result['report_sha256']=hash_file(args.report);result['auditor_sha256']=hash_file(Path(__file__))
    dependency=Path(__file__).with_name('audit_web_performance.py') if result['controller_replay']is not None else None
    if dependency:result['controller_auditor_sha256']=hash_file(dependency)
    suffix='.'+args.label if args.label else ''
    target=args.report.with_suffix(suffix+'.worker-audit.json')
    with target.open('x')as out:json.dump(result,out,indent=2,allow_nan=False);out.write('\n')
    with args.report.with_suffix(suffix+'.worker-auditor.py').open('xb')as out:out.write(Path(__file__).read_bytes())
    if dependency:
        with args.report.with_suffix(suffix+'.worker-controller-auditor.py').open('xb')as out:out.write(dependency.read_bytes())
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
