import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from verification import build_release as builder
R=Path(__file__).parents[1]
sys.path.insert(0,str(R/'verification'))
import audit_release

class ReleaseBoundaryTests(unittest.TestCase):
    def test_audit_missing_and_changed_tree_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with self.assertRaises((ValueError,OSError)):audit_release.audit(root/'missing')
            built=builder.build(R,root/'kit');tree=Path(built['customer_root'])
            self.assertEqual(audit_release.audit(tree)['issues'],[])
            (tree/'START-HERE.md').write_text('changed')
            self.assertTrue(audit_release.audit(tree)['issues'])
    def test_included_source_rebuild_is_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);first=builder.build(R,root/'first');tree=Path(first['customer_root'])
            result=subprocess.run([sys.executable,'-B','-X','utf8',str(tree/'source/verification/build_release.py'),'--repo',str(tree/'source'),'--output-dir',str(root/'again')],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(Path(first['customer_zip']).read_bytes(),(root/'again'/builder.CUSTOMER_ZIP).read_bytes())
    def test_failed_build_publishes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'new'
            with patch.object(builder,'archive_customer_tree',side_effect=OSError('injected')),self.assertRaises(OSError):builder.build(R,output)
            self.assertFalse(output.exists())
    def test_raw_duplicate_and_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'manifest.json'
            for value in ('{"files":[],"files":[]}','{"number":1e400}','{"number":NaN}'):
                path.write_text(value)
                with self.assertRaises(ValueError):builder.load_json(path)
    def test_help_never_overwrites_historical_receipt(self):
        receipt=R/'verification/release-audit.json';before=receipt.read_bytes()
        for script in ('build_release.py','audit_release.py'):
            result=subprocess.run([sys.executable,'-B',str(R/'verification'/script),'--help'],capture_output=True)
            self.assertEqual(result.returncode,0)
        self.assertEqual(receipt.read_bytes(),before)
    @unittest.skipUnless(os.name=='nt','Windows junction boundary')
    def test_junction_source_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            linked=Path(temp)/'linked'
            result=subprocess.run(['cmd','/c','mklink','/J',str(linked),str(R)],capture_output=True)
            self.assertEqual(result.returncode,0)
            try:
                with self.assertRaises(RuntimeError):builder.build(linked,Path(temp)/'new')
            finally:linked.rmdir()
    def test_nonportable_tree_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'CON.txt').write_text('fixture') if os.name!='nt' else None
            if os.name=='nt':
                # A trailing-dot spelling aliases on Windows; exercise the same lexical preflight on a POSIX-only fixture in CI.
                self.skipTest('Reserved-name fixture cannot be created faithfully on Windows')
            with self.assertRaises(RuntimeError):builder.portable_tree(root)
if __name__=='__main__':unittest.main()
