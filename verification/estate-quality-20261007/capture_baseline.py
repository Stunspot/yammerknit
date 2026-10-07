from pathlib import Path
import json,hashlib,subprocess,zipfile,shutil
R=Path(r'E:\Github\yammerknit');V=R/'verification/estate-quality-20261007';audit=V/'product-audit';audit.mkdir(exist_ok=True)
if (V/'baseline.json').exists():raise SystemExit('Baseline already exists; do not rerun')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0');paths=[p for p in paths if p and not p.startswith('release/')]
files={p:sha(R/p) for p in paths}
with zipfile.ZipFile(V/'baseline-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(R/p,p)
shelf=Path(r'E:\Indranet\Augments\0 Free\Yammerknit v0.1.0.zip');shutil.copyfile(shelf,V/'accepted-shelf.zip')
scope=json.loads(Path(r'E:\Indranet\Nova\projects\project-records\projects\augment-estate-quality-repair\records\scope-inventory.json').read_text(encoding='utf-8-sig'));owner=next(p for p in scope['products'] if p['id']=='yammerknit')
manifest=json.loads(Path(r'E:\Indranet\Augment-Custody\Active Shelf Control\SHELF-MANIFEST.json').read_text(encoding='utf-8-sig'))
def find(v):
 if isinstance(v,dict):
  if v.get('id')=='yammerknit':return v
  for x in v.values():
   got=find(x)
   if got:return got
 elif isinstance(v,list):
  for x in v:
   got=find(x)
   if got:return got
baseline={'product':'yammerknit','version':'0.1.0','head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'git_status':subprocess.check_output(['git','status','--short'],cwd=R,text=True),'source_inventory':files,'baseline_snapshot_sha256':sha(V/'baseline-source.zip'),'accepted_shelf':str(shelf),'accepted_shelf_sha256':sha(shelf),'repo_release_sha256':sha(R/'release/0.1.0/Yammerknit-v0.1.0.zip'),'ownership':owner,'shelf_manifest_record':find(manifest),'preserve':'Source canonical SOP/persona and artwork exact; frozen release/ and all history immutable; no live corpus or user workspace read or written.'}
(V/'baseline.json').write_text(json.dumps(baseline,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'source_files':len(files),'head':baseline['head'],'shelf_sha256':baseline['accepted_shelf_sha256'],'repo_sha256':baseline['repo_release_sha256'],'shelf_record':baseline['shelf_manifest_record']},indent=2))
