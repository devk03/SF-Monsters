"""Audit private browser write/readback references before canvas submission.

This validates a frozen, instrumented single-owner localStorage experiment.
It does not attest physical presentation, filesystem durability, unseen Worker
state, account isolation, general save compatibility or full quality approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from audit_worker_proof import audit as audit_worker, num, equal, hash_file


def _storage_observation(report):
    protocol=report['saveProtocol']
    equal(protocol['storageKind'],'isolated localStorage','storage backend scope')
    events=protocol['storageEvents'];submissions=report['main']['submissions']
    if type(events)is not list or not 1<=len(events)<=20000:
        raise ValueError('Missing or oversized browser storage history')
    if type(submissions)is not list or not 1<=len(submissions)<=160000:
        raise ValueError('Require bounded actual canvas submissions')
    fields=('frameId','saveEpoch','counter','rawRevision','sha256')
    writes={};confirmed={};used_reads=set();denied=set();previous_time=0;last_attempt=0
    for event in events:
        at=num(event['at'],'storage event time')
        if at<previous_time:raise ValueError('Storage event time regressed')
        previous_time=at
        attempt=num(event['attempt'],'storage attempt',integer=True)
        for key in fields[:-1]:num(event[key],'storage.'+key,integer=True,maximum=0xFFFFFFFF if key=='counter' else 2**53-1)
        if type(event['sha256'])is not str or not re.fullmatch('[a-f0-9]{64}',event['sha256']):
            raise ValueError('Invalid full-Flash storage hash')
        kind=event['type']
        if kind in ('write','denied'):
            if attempt<=last_attempt:raise ValueError('Storage attempt identifiers regressed')
            last_attempt=attempt
            if kind=='denied':denied.add((event['saveEpoch'],event['frameId']));continue
            if event['encodedLength']not in (43692,174764):raise ValueError('Unsupported raw Flash encoding size')
            writes[attempt]=event
        elif kind=='read':
            if attempt not in writes or attempt in used_reads:raise ValueError('Readback has no unique preceding write')
            write=writes[attempt];used_reads.add(attempt)
            for key in (*fields,'encodedLength'):equal(event[key],write[key],'readback '+key)
            equal(event['matchesWrite'],True,'actual full encoded readback')
            confirmed[len(confirmed)+1]={**write,'readAt':at}
        else:raise ValueError('Unknown storage observation type')
    if not confirmed:raise ValueError('No successful full-byte storage readback')
    equal(protocol['store']['writeSerial'],len(confirmed),'confirmed browser writes')
    prior_id=0;inside=before=after=0;seen=set()
    start=report['worker']['startedAt'];end=report['worker']['endedAt']
    for frame in submissions:
        frame_id=num(frame['frameId'],'submitted frame identifier',integer=True)
        if frame_id<=prior_id:raise ValueError('Canvas frame identifiers regressed or repeated')
        prior_id=frame_id
        serial=num(frame['storageWriteSerial'],'frame storage reference',integer=True)
        if serial not in confirmed:raise ValueError('Canvas frame references unverified storage')
        owner=confirmed[serial]
        for key in ('saveEpoch','rawRevision'):equal(frame[key],owner[key],'submitted '+key)
        counter=num(frame['counter'],'canvas guest counter',integer=True,maximum=0xFFFFFFFF)
        if ((counter-owner['counter'])&0xFFFFFFFF)>=0x80000000 or frame_id<owner['frameId']:
            raise ValueError('Canvas frame predates its referenced raw snapshot')
        received=num(frame['receivedAt'],'canvas submission time')
        if received<owner['readAt']:raise ValueError('Canvas submission precedes browser readback')
        if (frame['saveEpoch'],frame_id)in denied:raise ValueError('A denied storage frame was drawn')
        seen.add(serial)
        if received<start:before+=1
        elif received>end:after+=1
        else:inside+=1
    faults=[];armed=None
    for action in protocol['saveActions']:
        if action['type']=='quota-armed':armed=action
        if action['type']=='presentation-failure' and action.get('error')=='Injected private quota failure':
            if not armed:raise ValueError('Quota failure has no matching armed baseline')
            for key in ('quotaStorageUnchanged','quotaPresentationUnchanged','quotaWorkerReceiptUnchanged','workerPaused'):
                equal(action[key],True,'fault '+key)
            equal(action['storedAfterSha256'],armed['storedSha256'],'stored bytes after denial')
            equal(action['store']['drawCount'],armed['drawCount'],'draw count after denial')
            equal(action['cachedPresented']['frameId'],armed['presentedFrameId'],'cached frame after denial')
            equal(action['workerLastReceipt']['frameId'],armed['presentedFrameId'],'Worker receipt after denial')
            faults.append({'storage_unchanged':True,'canvas_not_advanced':True,'worker_paused':True,
                           'last_presented_frame_id':armed['presentedFrameId']})
            armed=None
    return {'storage_reference_integrity':True,'confirmed_full_byte_writes':len(confirmed),
        'referenced_storage_serials':sorted(seen),'raw_canvas_submissions':len(submissions),
        'submitted_inside_worker_window':inside,'submitted_before_worker_window':before,
        'submitted_after_worker_window':after,'denied_frame_count':len(denied),'observed_fault_cases':faults,
        'scope':'Instrumented single-owner browser write/readback precedes each referenced canvas submission. '
                'Main observations include explicitly counted RPC-boundary margins. No physical paint, OS-fsync, '
                'unseen Worker-tail, account concurrency, arbitrary save restore or full performance approval.'}


def storage_observation(report):
    try:return _storage_observation(report)
    except (KeyError,TypeError,IndexError,OverflowError) as error:
        raise ValueError('Missing or malformed saved-frame receipt: '+str(error)) from error


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args();directory=args.report.parent
    report=json.loads(args.report.read_bytes());identity=json.loads((directory/'identity.json').read_bytes())
    runtime=audit_worker(report,identity,directory)
    result={'runtime':runtime,'saved_frames':storage_observation(report),'report_sha256':hash_file(args.report),
            'auditor_sha256':hash_file(Path(__file__))}
    dependencies=['audit_worker_proof.py']
    if runtime['controller_replay']is not None:dependencies.append('audit_web_performance.py')
    result['dependencies']={name:hash_file(Path(__file__).with_name(name)) for name in dependencies}
    with args.report.with_suffix('.saved-frames.audit.json').open('x')as out:
        json.dump(result,out,indent=2,allow_nan=False);out.write('\n')
    for name in [Path(__file__).name,*dependencies]:
        with args.report.with_suffix('.saved-frames.'+name).open('xb')as out:
            out.write(Path(__file__).with_name(name).read_bytes())
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
