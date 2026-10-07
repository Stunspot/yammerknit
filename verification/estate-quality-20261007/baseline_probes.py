from pathlib import Path
import json,sys,importlib.util,copy
R=Path(r'E:\Github\yammerknit');V=R/'verification/estate-quality-20261007';sys.path.insert(0,str(R/'skills/yammerknit/scripts'));import yammerknit_tool as t
spec=importlib.util.spec_from_file_location('fixture',R/'skills/yammerknit/tests/test_yammerknit_tool.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
base=V/'baseline-fixtures';base.mkdir(exist_ok=False);results=[]
def record(name):
 w=base/name;w.mkdir();src=t.create_source_record(workspace=w,original=b'An explicitly fictional source.\n',normalized='An explicitly fictional source.\n',post_date='2026-10-07',channel='Fixture',title=name,source_kind='text',origin='isolated test',url=None,acquisition_method='supplied',rights_basis=None,original_filename='source.txt',transformations=[]);a=base/(name+'.md');a.write_text(f.complete_yammerknit(),encoding='utf-8');saved=t.store_artifact(a,w,src['record_id'],False);return w,src,a,saved
def probe(name,fn):
 try:results.append({'case':name,'result':fn()})
 except Exception as e:results.append({'case':name,'error':type(e).__name__+': '+str(e)})
w,s,a,b=record('source-tamper');p=Path(s['source_directory'])/'source.original.txt';p.write_bytes(b'Altered source bytes.\n');probe('changed_source_inspection',lambda:t.inspect_record(w,s['record_id']))
w,s,a,b=record('missing-revision');a.write_text(f.complete_yammerknit().replace('Gravity Not Filing Cabinets','Modified heading'),encoding='utf-8');rev=t.store_artifact(a,w,s['record_id'],True);Path(rev['artifact']).unlink();probe('missing_latest_artifact',lambda:t.inspect_record(w,s['record_id']))
w,s,a,b=record('wrong-parent');a.write_text(f.complete_yammerknit().replace('Gravity Not Filing Cabinets','Another heading'),encoding='utf-8');rev=t.store_artifact(a,w,s['record_id'],True);p=Path(rev['manifest']);m=json.loads(p.read_text());m['parent']={'kind':'revision','revision_id':'never-existed','artifact_sha256':'0'*64};p.write_text(json.dumps(m));probe('unknown_revision_parent',lambda:t.inspect_record(w,s['record_id']))
root=base/'path-scope';root.mkdir();outside=root/'outside';outside.mkdir();(outside/'source-manifest.json').write_text('{}');(outside/'yammerknit.md').write_text('Outside scope');(outside/'artifact-manifest.json').write_text('{}');workspace=root/'workspace';(workspace/'sources').mkdir(parents=True);(workspace/'artifacts').mkdir();probe('record_id_traversal',lambda:t.inspect_record(workspace,'../../outside'))
w,s,a,b=record('validation-race');real=t.validate_path
def alter_after_validation(p):
 receipt=real(p);p.write_text('UNVALIDATED REPLACEMENT',encoding='utf-8');return receipt
t.validate_path=alter_after_validation
probe('different_bytes_stored_after_validation',lambda:t.store_artifact(a,w,s['record_id'],True));t.validate_path=real
vtt='WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<v Alice>Keep the exception.</v>\n\n00:00:20.000 --> 00:00:22.000\n<v Bob>Keep the exception.</v>\n';probe('separate_speaker_cues_collapsed',lambda:t.normalize_vtt_text(vtt))
probe('impossible_vtt_time',lambda:t.normalize_vtt_text('WEBVTT\n\n00:99:01.000 --> 00:00:02.000\nImpossible cue.\n'))
for url in ['https://www.youtube.com/playlist?list=PL123','https://www.youtube.com/@channel','https://secret:token@youtube.com/watch?v=abcdefghijk']:
 probe('out_of_scope_url_'+url,lambda u=url:({'accepted':True} if t.validate_youtube_url(u) is None else {}))
wrong=f.complete_yammerknit().replace('Semantic Gravity ⇄ Custody Before Derivation','NONEXISTENT A ⇄ NONEXISTENT B').replace('Effect: Retrieval power remains accountable.\n','');probe('dangling_bridge_and_missing_effect',lambda:t.validate_text(wrong))
p=V/'baseline-probes.json';p.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n');print(json.dumps([{'case':x['case'],'status':'accepted' if 'result' in x else x.get('error'),'valid':x.get('result',{}).get('valid') if isinstance(x.get('result'),dict) else x.get('result')} for x in results],indent=2))
