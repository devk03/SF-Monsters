"""Causal storage corruption cases; synthetic observations are not browser proof."""
from pathlib import Path
import copy
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/quality'))
from audit_saved_frames import storage_observation


def fixture():
    identity={'frameId':1,'saveEpoch':1,'counter':100,'rawRevision':1,'sha256':'a'*64}
    return {'worker':{'startedAt':100.,'endedAt':200.},'main':{'submissions':[
        {'frameId':2,'saveEpoch':1,'counter':101,'rawRevision':1,'storageWriteSerial':1,'receivedAt':120.},
        {'frameId':3,'saveEpoch':1,'counter':102,'rawRevision':1,'storageWriteSerial':1,'receivedAt':201.}]},
        'saveProtocol':{'storageKind':'isolated localStorage','store':{'writeSerial':1},'saveActions':[],
            'storageEvents':[{'type':'write','attempt':1,'at':90.,'encodedLength':174764,**identity},
                             {'type':'read','attempt':1,'at':91.,'encodedLength':174764,'matchesWrite':True,**identity}]}}


class SavedFrames(unittest.TestCase):
    def test_write_before_draw_and_rpc_tail_are_separate_observations(self):
        result=storage_observation(fixture())
        self.assertTrue(result['storage_reference_integrity'])
        self.assertEqual(result['submitted_inside_worker_window'],1)
        self.assertEqual(result['submitted_after_worker_window'],1)
        self.assertNotIn('performance_passed',result)

    def test_false_readback_hash_owner_time_and_frame_claims_are_rejected(self):
        changes=[lambda r:r['saveProtocol']['storageEvents'][1].__setitem__('matchesWrite',False),
                 lambda r:r['saveProtocol']['storageEvents'][1].__setitem__('sha256','b'*64),
                 lambda r:r['main']['submissions'][0].__setitem__('storageWriteSerial',2),
                 lambda r:r['main']['submissions'][0].__setitem__('receivedAt',80.),
                 lambda r:r['main']['submissions'][0].__setitem__('rawRevision',2),
                 lambda r:r['main']['submissions'][0].__setitem__('saveEpoch',2),
                 lambda r:r['main']['submissions'][0].__setitem__('counter',99),
                 lambda r:r['main']['submissions'][1].__setitem__('frameId',2),
                 lambda r:r['saveProtocol']['store'].__setitem__('writeSerial',2)]
        for i,change in enumerate(changes):
            with self.subTest(i=i):
                value=fixture();change(value)
                with self.assertRaises(ValueError):storage_observation(value)

    def test_denied_frame_cannot_be_smuggled_into_submissions(self):
        value=fixture();entry=copy.deepcopy(value['saveProtocol']['storageEvents'][0])
        entry.update(type='denied',attempt=2,at=92.,frameId=2)
        value['saveProtocol']['storageEvents'].append(entry)
        with self.assertRaises(ValueError):storage_observation(value)

    def test_fault_success_booleans_need_matching_cached_draw_and_worker_receipt(self):
        value=fixture();value['saveProtocol']['saveActions']=[
            {'type':'quota-armed','storedSha256':'a'*64,'drawCount':3,'presentedFrameId':3},
            {'type':'presentation-failure','error':'Injected private quota failure','quotaStorageUnchanged':True,
             'quotaPresentationUnchanged':True,'quotaWorkerReceiptUnchanged':True,'workerPaused':True,
             'storedAfterSha256':'a'*64,'store':{'drawCount':3},'cachedPresented':{'frameId':3},'workerLastReceipt':{'frameId':3}}]
        self.assertEqual(len(storage_observation(value)['observed_fault_cases']),1)
        value['saveProtocol']['saveActions'][1]['store']['drawCount']=4
        with self.assertRaises(ValueError):storage_observation(value)


if __name__=='__main__':unittest.main()
