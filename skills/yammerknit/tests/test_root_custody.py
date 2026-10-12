import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('root_yammer_tool',ROOT/'scripts/yammerknit_tool.py')
tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)
class RootCustodyRegressions(unittest.TestCase):
    def test_no_bridge_exception_cannot_hide_actual_bridge(self):
        text=(ROOT/'examples/pilot-yammerknit.md').read_text('utf-8')
        one=text.split('### Cluster 2:')[0]+'## Relational Mesh\n\nNo supported bridge: this source warrants one cluster only.\n\n## Prompt Seeding Kit'+text.split('## Prompt Seeding Kit')[1]
        self.assertTrue(tool.validate_text(one)['valid'])
        bad=one.replace('No supported bridge: this source warrants one cluster only.','No supported bridge: this source warrants one cluster only.\n\nMissing A ⇄ Missing B\nBridge Type: comparison\nEffect: no such endpoints\nStrategic Value: invalid')
        self.assertFalse(tool.validate_text(bad)['valid'])
        self.assertTrue(tool.validate_text(text)['valid'])
    def test_missing_vtt_separator_does_not_move_later_words(self):
        text='WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n<v Alice>Yes.\n00:00:03.000 --> 00:00:04.000\n<v Bob>No.\n'
        with self.assertRaisesRegex(tool.YammerknitError,'blank separator'):tool.normalize_vtt_text(text)
        repaired=text.replace('Yes.\n00:00:03','Yes.\n\n00:00:03')
        self.assertEqual(tool.normalize_vtt_text(repaired),'[00:00:01.000 --> 00:00:02.000] [Alice] Yes.\n[00:00:03.000 --> 00:00:04.000] [Bob] No.\n')
if __name__=='__main__':unittest.main()
