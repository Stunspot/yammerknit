"""Counterexamples retained from the estate audit; isolated synthetic records only."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_yammerknit_tool import tool, complete_yammerknit

class EstateCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.workspace = self.root/'workspace'
        self.record = tool.create_source_record(workspace=self.workspace, original=b'fictional source', normalized='fictional source',post_date='N/A',channel='Teaching fixture',title='A bounded claim',source_kind='text',origin=None,url=None,acquisition_method='fixture',rights_basis=None,original_filename='source.txt',transformations=[])
        self.id = self.record['record_id']; self.artifact=self.root/'artifact.md'
        self.artifact.write_text(complete_yammerknit(),encoding='utf-8')
        self.base=tool.store_artifact(self.artifact,self.workspace,self.id,False)
    def tearDown(self): self.temp.cleanup()
    def change(self,path,edit):
        p=Path(path); value=json.loads(p.read_text('utf-8')); edit(value); p.write_text(json.dumps(value),encoding='utf-8')
    def revision(self): return tool.store_artifact(self.artifact,self.workspace,self.id,True)
    def test_changed_original_and_normalized_rejected(self):
        for filename in ('source.original.txt','source.txt'):
            with self.subTest(filename=filename):
                path=Path(self.record['source_directory'])/filename; original=path.read_bytes(); path.write_bytes(b'changed')
                with self.assertRaises(tool.YammerknitError): tool.inspect_record(self.workspace,self.id)
                path.write_bytes(original)
    def test_missing_current_artifact_rejected(self):
        rev=self.revision(); Path(rev['artifact']).unlink()
        with self.assertRaises(tool.YammerknitError): tool.inspect_record(self.workspace,self.id)
    def test_unknown_parent_rejected(self):
        rev=self.revision(); self.change(rev['manifest'],lambda v:v.update(parent={'kind':'revision','revision_id':'unknown','artifact_sha256':'0'*64}))
        with self.assertRaises(tool.YammerknitError): tool.inspect_record(self.workspace,self.id)
    def test_parent_kind_and_base_alias_are_controlled(self):
        rev=self.revision();path=Path(rev['manifest']);original=path.read_bytes()
        for parent in ({'kind':[]},{'kind':'revision','revision_id':'base','artifact_sha256':tool.sha256_path(Path(self.base['artifact']))}):
            self.change(path,lambda v:v.update(parent=parent))
            with self.assertRaises(tool.YammerknitError):tool.inspect_record(self.workspace,self.id)
            path.write_bytes(original)
    def test_cycle_rejected(self):
        first=self.revision();second=self.revision()
        self.change(first['manifest'],lambda v:v.update(parent={'kind':'revision','revision_id':second['revision_id'],'artifact_sha256':tool.sha256_path(Path(second['artifact']))}))
        with self.assertRaises(tool.YammerknitError):tool.inspect_record(self.workspace,self.id)
    def test_fork_rejected(self):
        first=self.revision(); second=self.revision()
        self.change(second['manifest'],lambda v:v.update(parent={'kind':'base','artifact_sha256':tool.sha256_path(Path(self.base['artifact']))}))
        with self.assertRaises(tool.YammerknitError): tool.inspect_record(self.workspace,self.id)
    def test_timestamp_sort_does_not_choose_current(self):
        first=self.revision(); second=self.revision()
        self.change(first['manifest'],lambda v:v.update(created_at='2099-01-01T00:00:00Z'))
        self.assertEqual(tool.inspect_record(self.workspace,self.id)['current']['revision_id'],second['revision_id'])
    def test_receipt_contradiction_and_wrong_hash_rejected(self):
        path=Path(self.base['validation']); original=path.read_bytes()
        for edit in (lambda v:v.update(valid=False),lambda v:v.update(artifact_sha256='0'*64),lambda v:v.update(checks={'one':1}),lambda v:v.update(errors=['failed'])):
            self.change(path,edit)
            with self.assertRaises(tool.YammerknitError): tool.inspect_record(self.workspace,self.id)
            path.write_bytes(original)
    def test_source_binding_catches_manifest_rewrite(self):
        self.change(self.record['manifest'],lambda v:v.update(title='Changed meaning'))
        with self.assertRaises(tool.YammerknitError): tool.inspect_record(self.workspace,self.id)
    def test_legacy_source_binding_is_not_invented(self):
        self.change(self.base['manifest'],lambda v:v.pop('source_binding'))
        status=tool.inspect_record(self.workspace,self.id)
        self.assertEqual(status['current']['kind'],'base'); self.assertIn('legacy',status['warnings'][0])
    def test_identifiers_cannot_escape(self):
        for identifier in ('../../outside','CON','x/y','x\\y','A.','A:stream',''):
            with self.subTest(identifier=identifier), self.assertRaises(tool.YammerknitError): tool.inspect_record(self.workspace,identifier)
    def test_single_snapshot_not_validate_then_reread(self):
        original=self.artifact.read_bytes(); validate=tool.validate_text
        def swap(text,*args):
            result=validate(text,*args); self.artifact.write_bytes(b'UNVALIDATED REPLACEMENT'); return result
        with patch.object(tool,'validate_text',side_effect=swap): rev=self.revision()
        self.assertEqual(Path(rev['artifact']).read_bytes(),original)
        self.assertEqual(json.loads(Path(rev['validation']).read_text())['artifact_sha256'],tool.sha256_bytes(original))
    def test_incomplete_stage_not_published(self):
        rename=tool.os.rename
        def fail(src,dest): raise OSError('injected publication failure')
        with patch.object(tool.os,'rename',side_effect=fail), self.assertRaises(OSError): self.revision()
        self.assertEqual(tool.inspect_record(self.workspace,self.id)['current']['kind'],'base')
    def test_inventory_and_portable_copy(self):
        source=Path(self.record['source_directory']); bad=source.parent/'broken'; bad.mkdir(); (bad/'source-manifest.json').write_text('[]')
        rows=tool.inspect_record(self.workspace)['records']; self.assertEqual(len(rows),2); self.assertEqual(sum(r['health']=='error' for r in rows),1)
        moved=self.root/'moved'; shutil.copytree(self.workspace,moved)
        self.assertTrue(tool.inspect_record(moved,self.id)['current']['artifact'].startswith(str(moved)))
    def test_strict_json_errors_are_controlled(self):
        path=Path(self.base['manifest']); original=path.read_bytes()
        for content in ('[]','{"record_id":1,"record_id":2}','{"x":1e400}'):
            path.write_text(content)
            with self.assertRaises((tool.YammerknitError,ValueError)): tool.inspect_record(self.workspace,self.id)
            path.write_bytes(original)
    @unittest.skipUnless(os.name=='nt','Windows junction control')
    def test_junction_rejected_before_canonicalization(self):
        linked=self.root/'junction'
        result=subprocess.run(['cmd','/c','mklink','/J',str(linked),str(self.workspace)],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        try:
            with self.assertRaises(tool.YammerknitError): tool.inspect_record(linked,self.id)
        finally: linked.rmdir()

class EstateRepresentationTests(unittest.TestCase):
    def test_missing_effect_and_dangling_endpoints_rejected(self):
        for text in (complete_yammerknit().replace('Effect: Retrieval power remains accountable.',''),complete_yammerknit().replace('Semantic Gravity ⇄ Custody Before Derivation','Ghost ⇄ Another Ghost')):
            self.assertFalse(tool.validate_text(text)['valid'])
    def test_wrapper_with_inner_fence_requires_longer_outer(self):
        artifact=complete_yammerknit().replace('Desc: A compact verification fixture.','Desc:\n```text\nA fixture.\n```')
        self.assertFalse(tool.validate_text(artifact)['valid'])
        artifact='`'+artifact+'`'
        self.assertTrue(tool.validate_text(artifact)['valid'])
    def test_empty_lexicon_definition_rejected(self):
        artifact=complete_yammerknit().replace('— conceptual gravity across a navigable mesh.','— ')
        self.assertFalse(tool.validate_text(artifact)['valid'])
    def test_one_honest_cluster_does_not_require_invention(self):
        text=complete_yammerknit(); a=text.index('### Cluster 2:'); b=text.index('## Relational Mesh'); text=text[:a]+text[b:]
        a=text.index('## Relational Mesh'); b=text.index('## Prompt Seeding Kit'); text=text[:a]+'## Relational Mesh\nNo supported bridge: only one cluster.\n\n'+text[b:]
        self.assertTrue(tool.validate_text(text)['valid'])
    def test_repeat_voice_range_retained(self):
        text='WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<v Alice>Keep the exception.\n\n00:00:20.000 --> 00:00:22.000\n<v Bob>Keep the exception.\n'
        out=tool.normalize_vtt_text(text); self.assertEqual(out.count('Keep the exception.'),2); self.assertIn('[Alice]',out); self.assertIn('[Bob]',out); self.assertIn('00:00:22.000',out)
    def test_bad_timing_rejected_and_overlap_preserved(self):
        for timing in ('00:99:01.000 --> 00:00:02.000','00:00:04.000 --> 00:00:02.000','00:00:01.000 --> 00:00:61.000','wrong --> timing'):
            with self.assertRaises(tool.YammerknitError): tool.normalize_vtt_text('WEBVTT\n\n'+timing+'\nword\n')
        self.assertEqual(tool.normalize_vtt_text('WEBVTT\n\n00:00:01.000 --> 00:00:04.000\none\n\n00:00:02.000 --> 00:00:03.000\ntwo\n').count('-->'),2)
    def test_single_video_boundary(self):
        for url in ('https://youtube.com/playlist?list=x','https://youtube.com/@channel','https://a:b@youtube.com/watch?v=abcdefghijk','https://youtube.com/watch?v=abcdefghijk&list=x'):
            with self.assertRaises(tool.YammerknitError): tool.validate_youtube_url(url)
        self.assertEqual(tool.validate_youtube_url('https://youtu.be/abcdefghijk?t=4'),'abcdefghijk')

if __name__=='__main__': unittest.main()
