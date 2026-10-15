"""Private runtime isolation, exact snapshots and finite collector boundaries."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import http.client
import json
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/quality'))
from serve_web_performance import runtime_config,page_source,report_byte_limit,snapshot,serve,MAX_REPORT_BYTES


def directory():
    return Path(tempfile.mkdtemp(prefix='pacer-harness-',dir=ROOT/'.tools'))


class PrivateRuntime(unittest.TestCase):
    def test_only_explicit_private_host_uses_its_larger_finite_report_bound(self):
        self.assertEqual(report_byte_limit({}),MAX_REPORT_BYTES)
        self.assertEqual(report_byte_limit({'performance_schema':2}),8*MAX_REPORT_BYTES)
        identity={'performance_schema':2,'private_page_override':True,'unit_fixture':True}
        self.assertEqual(report_byte_limit(identity),64*MAX_REPORT_BYTES)
        with self.assertRaises(ValueError):report_byte_limit({'private_page_override':True,'performance_schema':1})
        output=directory()
        with socket.socket()as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        thread=threading.Thread(target=serve,args=(SimpleNamespace(port=port,seconds=2),output,identity,{'/':b'fixture'}))
        thread.start()
        try:
            for _ in range(30):
                try:
                    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=.2)
                    connection.request('GET','/');connection.getresponse().read();connection.close();break
                except OSError:time.sleep(.01)
            payload={'schema':2,'context':{'identity':identity},'unit_padding':'x'*(9*MAX_REPORT_BYTES)}
            body=json.dumps(payload).encode();connection=http.client.HTTPConnection('127.0.0.1',port,timeout=2)
            connection.request('POST','/report',body,{'Origin':f'http://127.0.0.1:{port}','Content-Type':'application/json'})
            response=connection.getresponse();self.assertEqual(response.status,200)
            receipt=json.loads(response.read());connection.close()
            self.assertEqual(json.loads((output/receipt['name']).read_bytes()),payload)
            connection=http.client.HTTPConnection('127.0.0.1',port,timeout=1)
            connection.putrequest('POST','/report');connection.putheader('Origin',f'http://127.0.0.1:{port}')
            connection.putheader('Content-Type','application/json');connection.putheader('Content-Length',str(64*MAX_REPORT_BYTES+1))
            connection.endheaders();response=connection.getresponse();self.assertEqual(response.status,400)
            response.read();connection.close()
        finally:thread.join(3);self.assertFalse(thread.is_alive())

    def test_private_host_requires_explicit_isolation_and_exact_bounded_html(self):
        root=directory();page=root/'host.html';page.write_bytes(b'<!doctype html>private host')
        args=SimpleNamespace(private_page=page,private_runtime=root,report_schema=2)
        self.assertEqual(page_source(args),(page.read_bytes(),True))
        for extra in ({'report_schema':1},{'private_runtime':None},{'controlled_stall':True},
                      {'private_page':ROOT/'scripts/quality/web_performance.html'}):
            with self.subTest(extra=extra):
                with self.assertRaises(ValueError):page_source(SimpleNamespace(**(vars(args)|extra)))
        link=root/'link.html';link.symlink_to(page)
        with self.assertRaises(ValueError):page_source(SimpleNamespace(**(vars(args)|{'private_page':link})))
        for content in (b'',b'x'*131073):
            page.write_bytes(content)
            with self.assertRaises(ValueError):page_source(args)
        self.assertEqual(page_source(SimpleNamespace()),
                         ((ROOT/'scripts/quality/web_performance.html').read_bytes(),False))

    def test_default_runtime_and_schema_stay_public_and_unchanged(self):
        path,schema=runtime_config(SimpleNamespace())
        self.assertEqual(path,ROOT/'web/public/emulator');self.assertEqual(schema,1)

    def test_schema2_requires_explicit_private_workspace_runtime(self):
        root=directory()
        self.assertEqual(runtime_config(SimpleNamespace(private_runtime=root,report_schema=2)),(root,2))
        for args in (SimpleNamespace(report_schema=2),SimpleNamespace(report_schema=True),
                     SimpleNamespace(report_schema=3),SimpleNamespace(private_runtime=ROOT/'web/public/emulator'),
                     SimpleNamespace(private_runtime=root/'missing')):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):runtime_config(args)
        link=root/'outside';link.symlink_to(ROOT/'web/public/emulator',target_is_directory=True)
        with self.assertRaises(ValueError):runtime_config(SimpleNamespace(private_runtime=link))

    def test_collector_checks_schema_origin_and_its_larger_opted_in_bound(self):
        output=directory();identity={'performance_schema':2,'unit_fixture':True}
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        args=SimpleNamespace(port=port,seconds=2)
        thread=threading.Thread(target=serve,args=(args,output,identity,{'/':b'unit fixture'}))
        thread.start();origin=f'http://127.0.0.1:{port}'
        def post(payload,*,origin_value=origin,declared=None):
            connection=http.client.HTTPConnection('127.0.0.1',port,timeout=1)
            body=json.dumps(payload).encode()
            connection.putrequest('POST','/report');connection.putheader('Origin',origin_value)
            connection.putheader('Content-Type','application/json')
            connection.putheader('Content-Length',str(len(body) if declared is None else declared))
            connection.endheaders(body if declared is None else None)
            response=connection.getresponse();data=response.read();status=response.status;connection.close()
            return status,data
        try:
            # Bounded readiness wait; the server independently ends after2seconds.
            for _ in range(30):
                try:
                    c=http.client.HTTPConnection('127.0.0.1',port,timeout=.2)
                    c.request('GET','/');c.getresponse().read();c.close();break
                except OSError:time.sleep(.01)
            payload={'schema':2,'context':{'identity':identity}}
            self.assertEqual(post({**payload,'schema':1})[0],400)
            self.assertEqual(post({**payload,'schema':True})[0],400)
            self.assertEqual(post(payload,origin_value='http://unrelated.invalid')[0],403)
            self.assertEqual(post({'schema':2,'context':{'identity':{}}})[0],400)
            self.assertEqual(post(payload,declared=8*MAX_REPORT_BYTES+1)[0],400)
            # A raw ledger may exceed the old1MiB limit; this opt-in collector
            # stores it without pretending to validate performance or ledger data.
            payload['unit_padding']='q'*(MAX_REPORT_BYTES+1)
            status,data=post(payload);self.assertEqual(status,200)
            receipt=json.loads(data);saved=(output/receipt['name']).read_bytes()
            self.assertEqual(json.loads(saved),payload)
            self.assertEqual(hashlib.sha256(saved).hexdigest(),receipt['sha256'])
        finally:
            thread.join(3);self.assertFalse(thread.is_alive(),'finite test collector did not stop')


TARGET=ROOT/'.tools/romhack-drafts/0.0.80-sunset-density-preview/9b5e6bc4fa5658ec686ab95cc3b1108feef0875393503c7adb5d210aaa0d1edd/target.gba'
STATE=ROOT/'.tools/benchmarks/sunset-v80-review-ready/capture.state'


@unittest.skipUnless(TARGET.exists() and STATE.exists(),'Pinned private native checkpoint required for snapshot provenance checks.')
class NativeSnapshot(unittest.TestCase):
    def args(self,**extra):
        return SimpleNamespace(rom=TARGET,state=STATE,input=None,seconds=600,port=18899,
                               name='pacer-harness-test-'+uuid.uuid4().hex[:8],**extra)

    def test_default_snapshot_and_explicit_private_experiment_record_exact_sources(self):
        output,identity,routes=snapshot(self.args())
        self.assertEqual(identity['performance_schema'],1);self.assertFalse(identity['private_runtime_override'])
        self.assertIsNone(identity['controlled_stall_ms'])
        self.assertEqual(routes['/'],(ROOT/'scripts/quality/web_performance.html').read_bytes())
        runtime=directory();shutil.copytree(ROOT/'web/public/emulator',runtime/'runtime')
        (runtime/'runtime/probe-marker.js').write_text('export const unitMarker=true;\n')
        output2,identity2,routes2=snapshot(self.args(private_runtime=runtime/'runtime',report_schema=2,controlled_stall=True))
        self.assertEqual(identity2['performance_schema'],2);self.assertTrue(identity2['private_runtime_override'])
        self.assertEqual(identity2['controlled_stall_ms'],200)
        self.assertEqual(routes2['/rom.gba'],routes['/rom.gba']);self.assertEqual(routes2['/state.bin'],routes['/state.bin'])
        self.assertEqual((output2/'web_performance.html').read_bytes(),routes2['/'])
        self.assertEqual(identity2['runtime']['probe-marker.js'],hashlib.sha256(routes2['/emulator/probe-marker.js']).hexdigest())
        self.assertEqual(identity2['page_sha256'],hashlib.sha256(routes2['/']).hexdigest())
        page=runtime/'custom.html';page.write_bytes(b'<!doctype html><title>Private Worker proof</title>')
        output3,identity3,routes3=snapshot(self.args(private_runtime=runtime/'runtime',report_schema=2,private_page=page))
        self.assertTrue(identity3['private_page_override'])
        self.assertEqual(routes3['/'],page.read_bytes())
        self.assertEqual((output3/'web_performance.html').read_bytes(),page.read_bytes())
        self.assertEqual(identity3['page_sha256'],hashlib.sha256(page.read_bytes()).hexdigest())
        self.assertEqual(routes3['/state.bin'],routes['/state.bin'])

    def test_runtime_symlinks_fail_before_evidence_is_written(self):
        runtime=directory();(runtime/'linked.js').symlink_to(ROOT/'web/public/emulator/mgba.options.js')
        args=self.args(private_runtime=runtime,report_schema=2)
        with self.assertRaises(ValueError):snapshot(args)
        self.assertFalse((ROOT/'.tools/benchmarks'/args.name).exists())


if __name__=='__main__':unittest.main()
