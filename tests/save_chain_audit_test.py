"""Pure linked-receipt graph corruption tests; no actual cycle audits."""
from pathlib import Path
import copy
import sys
import tempfile
import unittest
from unittest import mock
HERE=Path(__file__).resolve().parent
SOURCE=HERE if (HERE/'audit_save_chain.py').is_file() else HERE.parent/'scripts/quality'
sys.path.insert(0,str(SOURCE))
import audit_save_chain as audit


def digest(number):return format(number,'064x')


def fixture():
    nodes=[]
    for index in range(10):
        nodes.append(dict(directory='cycle-'+str(index),rom=audit.native.ROM,core=audit.native.REV,
                          worker_sha256=digest(900),freshly_reaudited=True,
                          before_sha256=digest(index+1),after_sha256=digest(index+2),
                          native_flash_sha256=digest(index+2),native_state_sha256=digest(100+index),
                          native_metadata_sha256=digest(200+index),source_state_sha256=digest(99+index),
                          source_metadata_sha256=digest(199+index),source_battery_sha256=digest(index+1),
                          before_counter=13+index,after_counter=14+index,native_counter=14+index,
                          checks={name:True for name in audit.CHECKS},party_count=3,boxed_count=0))
    return nodes


class ChainTests(unittest.TestCase):
    def test_ten_linked_successes_keep_fixture_and_attempt_limits_explicit(self):
        result=audit.verify_graph(fixture())
        self.assertEqual((result['first_counter'],result['last_counter']),(13,23))
        self.assertEqual(result['successful_linked_cycles'],10)
        self.assertFalse(result['consecutive_attempts_claimed']);self.assertFalse(result['public_gate_qualified'])
        self.assertEqual(result['fixture'],{'party_monsters':3,'boxed_monsters':0})

    def test_gaps_duplicates_and_wrong_order_are_rejected(self):
        for change in [lambda n:n.pop(),lambda n:n.__setitem__(4,copy.deepcopy(n[3])),
                       lambda n:n.reverse(),lambda n:n[4].update(before_counter=99)]:
            nodes=fixture();change(nodes)
            with self.assertRaises(ValueError):audit.verify_graph(nodes)

    def test_all_four_forward_edges_and_worker_identity_are_independent(self):
        for field in ['before_sha256','source_state_sha256','source_battery_sha256',
                      'source_metadata_sha256','worker_sha256','native_flash_sha256','rom','core']:
            nodes=fixture();nodes[5][field]=digest(999)
            with self.subTest(field=field),self.assertRaises(ValueError):audit.verify_graph(nodes)

    def test_every_cold_check_must_be_present_strict_true_and_fresh(self):
        for name in audit.CHECKS:
            for value in [False,1,'true']:
                nodes=fixture();nodes[3]['checks'][name]=value
                with self.subTest(name=name,value=value),self.assertRaises(ValueError):audit.verify_graph(nodes)
        nodes=fixture();nodes[3]['checks'].pop('loaded_save_counter_exact')
        with self.assertRaises(ValueError):audit.verify_graph(nodes)
        nodes=fixture();nodes[3]['freshly_reaudited']=False
        with self.assertRaises(ValueError):audit.verify_graph(nodes)

    def test_party_and_empty_box_scope_cannot_be_silently_broadened(self):
        for field,value in [('party_count',6),('boxed_count',1),('native_counter',12)]:
            nodes=fixture();nodes[8][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):audit.verify_graph(nodes)

    def test_missing_cold_receipt_fails_once_before_any_real_reaudit(self):
        base=Path(tempfile.mkdtemp(prefix='synthetic-chain-',dir=HERE if SOURCE==HERE else audit.R/'.tools'))
        directories=[]
        for index in range(10):
            directory=base/str(index);directory.mkdir();directories.append(directory)
            for name in ['browser.json','before.sav','after.sav']:(directory/name).write_bytes(b'fixture')
            if index<9:(directory/'native.final.json').write_bytes(b'fixture')
        with mock.patch.object(audit,'load_cycle') as load:
            with self.assertRaisesRegex(ValueError,'missing native cold proof'):audit.audit_chain(directories)
            load.assert_not_called()

    def test_loader_freshly_reaudits_and_rejects_stale_cold_state(self):
        directory=Path(tempfile.mkdtemp(prefix='synthetic-loader-',dir=HERE if SOURCE==HERE else audit.R/'.tools'))
        for name in ['native.final.json','browser.json','after.sav','identity.json']:(directory/name).write_bytes(b'fixture')
        checks={name:True for name in audit.CHECKS}
        stored=dict(kind='private-native-cold-cycle',passed=True,capture_directory=str(directory/'capture'),
                    checks=checks,counter=14,full_flash_sha256=digest(2),state_sha256=digest(100),
                    capture_metadata_sha256=digest(200),browser_proof_sha256=digest(800),rom=audit.native.ROM,core=audit.native.REV)
        browser=dict(save_report=str(directory/'save.json'),before_sha256=digest(1),after_sha256=digest(2),before_counter=13,after_counter=14)
        identity=dict(files={'state.bin':digest(99),'battery.sav':digest(1)},source_state_metadata_sha256=digest(199),runtime={'worker-proof.js':digest(900)})
        def read(path):return stored if path.name=='native.final.json' else browser if path.name=='browser.json' else identity
        with mock.patch.object(audit.native,'read_json',side_effect=read), \
             mock.patch.object(audit.native,'audit_cold',return_value=stored) as fresh, \
             mock.patch.object(audit.native.flash_audit,'audit_bytes',return_value={'domains':{'party_count':3},'stored':[]}):
            node=audit.load_cycle(directory);self.assertTrue(node['freshly_reaudited'])
            fresh.assert_called_once_with(directory,directory/'capture')
        altered={**stored,'state_sha256':digest(999)}
        with mock.patch.object(audit.native,'read_json',side_effect=read),mock.patch.object(audit.native,'audit_cold',return_value=altered):
            with self.assertRaisesRegex(ValueError,'stale'):audit.load_cycle(directory)


if __name__=='__main__':unittest.main()
