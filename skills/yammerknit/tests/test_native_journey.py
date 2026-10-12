import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from test_yammerknit_tool import tool,complete_yammerknit
S=Path(__file__).parents[1]

class NativeJourneyTests(unittest.TestCase):
    def test_first_task_revision_portable_return_and_recovery(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); work=root/'records';script=S/'scripts/yammerknit_tool.py'
            def run(*args,code=0):
                result=subprocess.run([sys.executable,'-B','-X','utf8',str(script),*map(str,args)],capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(result.returncode,code,result.stderr)
                self.assertNotIn('Traceback',result.stderr)
                return json.loads(result.stdout if code==0 else result.stderr)
            source=S/'examples/pilot-source.txt'; original=source.read_bytes()
            record=run('init-record','--source',source,'--workspace',work,'--title','Cooling pilot')
            rid=record['record_id'];self.assertIsNone(run('inspect-record','--workspace',work)['records'][0]['current'])
            base=run('store-artifact','--artifact',S/'examples/pilot-yammerknit.md','--workspace',work,'--record-id',rid)
            revised=root/'revised.md';revised.write_text((S/'examples/pilot-yammerknit.md').read_text('utf-8').replace('which comparison','which comparison').replace('Which simultaneous changes','Which supplier and staffing changes'),encoding='utf-8')
            rev=run('revise-artifact','--artifact',revised,'--workspace',work,'--record-id',rid)
            self.assertEqual(run('inspect-record','--workspace',work,'--record-id',rid)['current']['revision_id'],rev['revision_id'])
            moved=root/'portable';shutil.copytree(work,moved)
            status=run('inspect-record','--workspace',moved,'--record-id',rid)
            self.assertTrue(status['current']['artifact'].startswith(str(moved)))
            raw=moved/'sources'/rid/'source.original.txt';saved=raw.read_bytes();raw.write_bytes(b'altered')
            self.assertEqual(run('inspect-record','--workspace',moved,'--record-id',rid,code=2)['status'],'error')
            raw.write_bytes(saved);self.assertEqual(run('inspect-record','--workspace',moved,'--record-id',rid)['health'],'verified-present-bytes')
            self.assertEqual(source.read_bytes(),original)
            self.assertEqual(Path(base['artifact']).read_bytes(),(S/'examples/pilot-yammerknit.md').read_bytes())
    def test_help_is_read_only_and_malformed_state_controlled(self):
        for command in ('init-record','validate','store-artifact','revise-artifact','inspect-record','normalize-vtt','acquire-youtube'):
            result=subprocess.run([sys.executable,'-B',str(S/'scripts/yammerknit_tool.py'),command,'--help'],capture_output=True)
            self.assertEqual(result.returncode,0)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); path=root/'sources'/'bad';path.mkdir(parents=True);(path/'source-manifest.json').write_text('[]')
            result=subprocess.run([sys.executable,'-B','-X','utf8',str(S/'scripts/yammerknit_tool.py'),'inspect-record','--workspace',str(root),'--record-id','bad'],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,2);self.assertNotIn('Traceback',result.stderr)

class AcquisitionIdentityTests(unittest.TestCase):
    def run_case(self,identity='abcdefghijk',language='en',extra=False,exitcode=0):
        def backend(command,**kwargs):
            template=Path(command[command.index('--output')+1]);stage=template.parent
            (stage/f'{identity}.{language}.vtt').write_text('WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<v A>One cue.\n',encoding='utf-8')
            if extra:(stage/'unexpected.mp4').write_bytes(b'not actual media')
            return SimpleNamespace(returncode=exitcode,stdout=f'YAMMERKNIT_META\t{identity}\tAuthor\tN/A\tTitle\thttps://youtube.com/watch?v={identity}\n',stderr='fictional-secret-do-not-echo')
        with tempfile.TemporaryDirectory() as temp,patch.object(tool.shutil,'which',return_value='yt-dlp'),patch.object(tool.subprocess,'run',side_effect=backend):
            return tool.acquire_youtube(url='https://youtube.com/watch?v=abcdefghijk',rights_basis=None,workspace=Path(temp),languages='en',backend='yt-dlp')
    def test_matching_identity_succeeds(self):self.assertEqual(self.run_case()['status'],'created')
    def test_wrong_identity_language_or_media_rejected(self):
        for kwargs in ({'identity':'different12'},{'language':'fr'},{'extra':True}):
            with self.subTest(kwargs=kwargs),self.assertRaises(tool.YammerknitError):self.run_case(**kwargs)
    def test_failure_does_not_echo_private_backend_text(self):
        with self.assertRaises(tool.YammerknitError) as failure:self.run_case(exitcode=1)
        self.assertNotIn('fictional-secret',str(failure.exception))

if __name__=='__main__':unittest.main()
