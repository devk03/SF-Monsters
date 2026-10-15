"""Independently validate schema 2 bounded frame debt; never approve performance.

The raw ledger proves fresh demand, overflow and guest-frame conservation. After
validation, a documented schema 1 projection reuses only common receipt checks.
Existing schema 1 receipts and their auditor remain unchanged.
"""
import argparse
import base64
import binascii
import copy
import hashlib
import json
import math
from pathlib import Path
import struct

MAX_ROWS=160000
MAX_INTEGER=2**53-1
ROW=struct.Struct('<HBHBd')
ENCODING='u16-u4u4-u16-u8-f64le-v1'


def number(value,name,*,integer=False,maximum=MAX_INTEGER):
    if type(value) not in (int,float) or (integer and type(value) is not int):
        raise ValueError('Invalid numeric type: '+name)
    try:valid=math.isfinite(value) and 0<=value<=maximum
    except OverflowError:valid=False
    if not valid:raise ValueError('Nonfinite or out-of-range observation: '+name)
    return value


def same(actual,expected,name):
    number(actual,name,integer=True)
    if actual!=expected:raise ValueError('Ledger summary differs: '+name)


def distribution(values):
    if not values:return {'count':0}
    ordered=sorted(values);count=len(ordered)
    return {'count':count,'min':ordered[0],'max':ordered[-1],
            'p50':ordered[(50*count+99)//100-1],'p95':ordered[(95*count+99)//100-1],
            'p99':ordered[(99*count+99)//100-1],
            'mean':math.fsum(value/count for value in ordered)}


def input_observation(report,start,total):
    """Optional input summaries are bounded observations, not reconstructed timing."""
    inputs=report.get('input',{});facts={}
    names=('debtFramesAtDispatch','oldestDebtAgeAtDispatchMs','firstGuestCounters')
    if not any(name in inputs for name in names):return None
    count=number(inputs['count'],'input.count',integer=True,maximum=40000)
    superseded=number(inputs['supersededBeforeFrame'],'input.supersededBeforeFrame',integer=True,maximum=count)
    if 'firstGuestCounters' in inputs:
        counters=inputs['firstGuestCounters']
        if type(counters) is not list or len(counters)>40000 or len(counters)+superseded!=count:
            raise ValueError('Input guest counter count differs from unsuperseded observations.')
        previous=0
        for counter in counters:
            number(counter,'input first guest counter',integer=True,maximum=0xFFFFFFFF)
            distance=(counter-start)&0xFFFFFFFF
            if not 0<distance<=total or distance<=previous:
                raise ValueError('Input guest counter is outside the observed interval or regressed.')
            previous=distance
        facts['first_guest_counters_checked']=len(counters)
    for name in names[:2]:
        if name not in inputs:continue
        histogram=inputs[name];samples=number(histogram['count'],'input.'+name+'.count',integer=True,maximum=count)
        if samples:
            values=[number(histogram[key],'input.'+name+'.'+key,integer=name=='debtFramesAtDispatch',
                           maximum=65535 if name=='debtFramesAtDispatch' else float('inf'))
                    for key in ('min','p50','p95','p99','max')]
            mean=number(histogram['mean'],'input.'+name+'.mean',maximum=float('inf'))
            if values!=sorted(values) or not values[0]<=mean<=values[-1]:
                raise ValueError('Input debt histogram is inconsistent: '+name)
        facts[name]=histogram
    facts['scope']='Bounded reported input summaries and first subsequent guest counters only; '
    facts['scope']+='no raw input timing ledger, KEYINPUT acknowledgement, physical latency or paint proof.'
    return facts


def _audit_ledger(report):
    if type(report['schema']) is not int or report['schema']!=2:
        raise ValueError('Require schema 2; preserved schema 1 receipts are not converted.')
    context=report['context'];config=context['framePacing'];summary=report['framePacing'];ticks=report['ticks']
    if config['strategy']!='bounded-debt-v1':raise ValueError('Unknown pacing strategy.')
    same(config['maxFramesPerTick'],5,'maxFramesPerTick');same(config['maxPendingFrames'],30,'maxPendingFrames')
    origin=number(config['clockOriginMs'],'clockOriginMs',maximum=float('inf'))
    fps=number(context['framerate'],'framerate',maximum=float('inf'))
    if fps==0:raise ValueError('Framerate must be positive.')
    ordinal=number(config['initialDue'],'initialDue',integer=True)
    initial=number(config['initialBacklog'],'initialBacklog',integer=True,maximum=30)
    if initial>ordinal:raise ValueError('Initial debt exceeds all credits due in its epoch.')
    guest=number(config['initialGuestCounter'],'initialGuestCounter',integer=True,maximum=0xFFFFFFFF)
    same(summary['initialBacklog'],initial,'initialBacklog')
    if summary['ledgerEncoding']!=ENCODING:raise ValueError('Unknown ledger encoding.')
    count=number(summary['ledgerRows'],'ledgerRows',integer=True,maximum=MAX_ROWS)
    encoded=summary['ledgerBase64']
    if type(encoded) is not str or len(encoded)>4*math.ceil(MAX_ROWS*ROW.size/3):
        raise ValueError('Invalid or oversized base64 ledger.')
    try:raw=base64.b64decode(encoded,validate=True)
    except (ValueError,binascii.Error) as error:raise ValueError('Malformed base64 ledger.') from error
    if base64.b64encode(raw).decode('ascii')!=encoded:raise ValueError('Ledger base64 is not canonical.')
    if len(raw)!=count*ROW.size:raise ValueError('Ledger byte length differs from row count.')
    fresh_total=planned_total=actual_total=dropped_total=mismatches=over_cap=0
    max_pending=max_after=debt_ticks=0;before=initial;previous_elapsed=0.;ages=[]
    for index,(fresh,nibbles,dropped,after,elapsed) in enumerate(ROW.iter_unpack(raw)):
        number(elapsed,'RAF elapsed row '+str(index),maximum=float('inf'))
        if elapsed<previous_elapsed:raise ValueError('RAF elapsed time regressed at row '+str(index))
        due_value=(elapsed/1000)*fps
        number(due_value,'wall-clock ordinal row '+str(index))
        due=math.floor(due_value)
        if due<ordinal or fresh!=due-ordinal:raise ValueError('Fresh wall-clock demand differs at row '+str(index))
        pending=before+fresh;expected_drop=max(0,pending-30);pending-=expected_drop
        planned,actual=nibbles>>4,nibbles&15
        if dropped!=expected_drop or planned!=min(5,pending) or actual>planned:
            raise ValueError('Overflow or execution policy differs at row '+str(index))
        if after!=pending-actual or after>30:
            raise ValueError('Frame debt was lost or invented at row '+str(index))
        age=max(0.,elapsed-float(due-after+1)*1000/fps) if after else 0.
        number(age,'oldest debt age row '+str(index),maximum=float('inf'));ages.append(age)
        fresh_total+=fresh;planned_total+=planned;actual_total+=actual;dropped_total+=dropped
        mismatches+=planned!=actual;over_cap+=max(0,fresh-5)
        max_pending=max(max_pending,pending);max_after=max(max_after,after);debt_ticks+=after>0
        before=after;ordinal=due;previous_elapsed=elapsed
    derived={'count':count,'requestedFrames':fresh_total,'plannedFrames':planned_total,
             'executedFrames':actual_total,'actualVideoFrames':actual_total,'discardedFrames':dropped_total,
             'videoFrameMismatchTicks':mismatches}
    for name,value in derived.items():same(ticks[name],value,'ticks.'+name)
    for name,value in {'finalBacklog':before,'maxPendingFramesObserved':max_pending,
                       'maxBacklogAfter':max_after,'newlyDueOverTickCapFrames':over_cap}.items():
        same(summary[name],value,'framePacing.'+name)
    if initial+fresh_total!=actual_total+dropped_total+before:raise ValueError('Cumulative conservation failed.')
    observed=ticks['oldestDebtAgeMs'];expected=distribution(ages)
    same(observed['count'],count,'oldestDebtAgeMs.count')
    for name,value in expected.items():
        if name=='count':continue
        actual=number(observed[name],'oldestDebtAgeMs.'+name,maximum=float('inf'))
        matches=math.isclose(actual,value,rel_tol=1e-12,abs_tol=1e-9) if name=='mean' else actual==value
        if not matches:raise ValueError('Derived oldest debt age differs: '+name)
    end=number(report['audioClockAtClose']['guestCounter'],'closing guestCounter',integer=True,maximum=0xFFFFFFFF)
    if (end-guest)&0xFFFFFFFF!=actual_total:raise ValueError('Closing guest counter differs from actual ledger execution.')
    inputs=input_observation(report,guest,actual_total)
    return {'ledger_well_formed':True,'ledger_rows':count,'clock_origin_ms':origin,'initial_due':config['initialDue'],
            'initial_backlog':initial,'newly_due_frames':fresh_total,'planned_frames':planned_total,
            'executed_frames':actual_total,'overflow_dropped_frames':dropped_total,'final_backlog':before,
            'max_pending_frames':max_pending,'max_backlog_after':max_after,'debt_ticks':debt_ticks,
            'newly_due_over_tick_cap_frames':over_cap,'planned_mismatch_ticks':mismatches,
            'oldest_debt_age_ms':expected,'loss_free':dropped_total==0,'caught_up_at_close':before==0,
            'planned_execution_matches':mismatches==0,
            'input_debt_observation':inputs,
            'scope':'Exact frame ledger and guest-counter observations; retained debt is not loss, '
                    'and conservation does not establish deadline, audio, input, paint or full performance acceptance.'}


def audit_ledger(report):
    """Validate fresh demand before any compatibility projection is permitted."""
    try:return _audit_ledger(report)
    except (KeyError,TypeError,IndexError,OverflowError,struct.error) as error:
        raise ValueError('Missing or malformed schema 2 frame-debt receipt: '+str(error)) from error


def audit(report,identity,runtime):
    from audit_web_performance import audit as audit_common
    debt=audit_ledger(report)
    # The legacy auditor checks runtime identity, input timing and final audio.
    # Its old per-tick accounting cannot represent carried debt. Only after the
    # exact raw ledger has passed, project its accounting to an accepted total.
    projected=copy.deepcopy(report);projected['schema']=1
    projected['ticks']['requestedFrames']=debt['executed_frames']+debt['overflow_dropped_frames']
    try:result=audit_common(projected,identity,Path(runtime))
    except (KeyError,TypeError,IndexError,OverflowError) as error:
        raise ValueError('Malformed common diagnostic evidence: '+str(error)) from error
    result.update({'schema':2,'frame_debt':debt,'normalization':{
        'purpose':'Reuse unchanged schema 1 runtime, timing, input-scope and final-audio integrity checks only.',
        'validated_first':'Canonical raw schema 2 ledger, fresh clock-derived demand and all debt summaries.',
        'projected_schema':1,'original_requested_frames':report['ticks']['requestedFrames'],
        'projected_requested_frames':projected['ticks']['requestedFrames'],
        'projection':'requestedFrames = independently validated actual execution + overflow drops; '
                     'fresh demand and retained debt remain separately reported, with no full gate approval.'}})
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--identity',type=Path)
    parser.add_argument('--runtime',type=Path)
    args=parser.parse_args();identity_path=args.identity or args.report.parent/'identity.json'
    report_bytes=args.report.read_bytes();identity_bytes=identity_path.read_bytes();source=Path(__file__).read_bytes()
    result=audit(json.loads(report_bytes),json.loads(identity_bytes),args.runtime or args.report.parent/'runtime')
    result.update(report_sha256=hashlib.sha256(report_bytes).hexdigest(),
                  identity_sha256=hashlib.sha256(identity_bytes).hexdigest(),auditor_sha256=hashlib.sha256(source).hexdigest())
    with args.report.with_suffix('.audit.json').open('x') as target:target.write(json.dumps(result,indent=2)+'\n')
    with args.report.with_suffix('.auditor.py').open('xb') as target:target.write(source)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
