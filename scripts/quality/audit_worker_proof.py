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
    for key in ('physicalPaintProven','guestKeyConsumptionProven','productionCompatible'):
        equal(report['scope'][key],False,'scope.'+key)
    worker=report['worker'];main=report['main']
    equal(worker['reason'],'duration','completion reason')
    duration=num(worker['durationMs'],'duration',integer=True,maximum=600000)
    if duration==0:raise ValueError('Empty diagnostic duration')
    start=num(worker['startedAtMs'],'Worker start');end=num(worker['endedAtMs'],'Worker close')
    origin=num(worker['clockOriginMs'],'Worker clock origin');time_origin=num(worker['workerTimeOrigin'],'Worker time origin')
    fps=num(worker['framerate'],'native framerate')
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
        if type(row) is not list or len(row)!=8:raise ValueError('Require eight raw fields per Worker tick')
        fresh,planned,actual,drop,after,elapsed,before_counter,after_counter=row
        for key,value in zip(('fresh','planned','actual','drop','after','beforeCounter','afterCounter'),
                             (fresh,planned,actual,drop,after,before_counter,after_counter)):
            num(value,f'{key} row{i}',integer=True,maximum=0xFFFFFFFF if 'Counter'in key else 65535)
        num(elapsed,'elapsed row'+str(i))
        if not previous_elapsed<=elapsed<=end-origin:raise ValueError('Worker tick clock outside ordered window')
        next_due=math.floor(elapsed/1000*fps)
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
            'ticks':len(rows),'fresh_frames':fresh_total,'planned_frames':planned_total,'actual_frames':actual_total,
            'overflow_dropped_frames':drop_total,'closing_backlog':debt,'planned_mismatch_ticks':mismatches,
            'max_worker_tick_gap_ms':max_gap,'worker_ticks_during_each_main_stall':overlap,
            'frames_in_batches_admitted_during_each_main_stall':overlap_frames,
            'audio':{key:final_audio[key] for key in ('renderedOutputFrames','warmupOutputFrames','underrunOutputFrames','droppedSourceFrames','queueDepthFrames','outputSampleRate')},
            'main_audio_context_seconds':after['currentTime']-before['currentTime'],
            'main_canvas_submission_count':len(main['submissions']),'main_input_count':len(main['inputs']),
            'foreground_observed':all(v['state']=='visible' for v in main['visibility']),
            'loss_free':drop_total==0,'caught_up_at_close':debt==0}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args();directory=args.report.parent
    result=audit(json.loads(args.report.read_bytes()),json.loads((directory/'identity.json').read_bytes()),directory)
    result['report_sha256']=hash_file(args.report);result['auditor_sha256']=hash_file(Path(__file__))
    target=args.report.with_suffix('.worker-audit.json')
    with target.open('x')as out:json.dump(result,out,indent=2,allow_nan=False);out.write('\n')
    with args.report.with_suffix('.worker-auditor.py').open('xb')as out:out.write(Path(__file__).read_bytes())
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
