from pathlib import Path
import json,zipfile,sys
R=Path(r'E:\Github\yammerknit');V=R/'verification/estate-quality-20261007';A=V/'authorship';A.mkdir(exist_ok=True)
def write(p,t):p.write_text(t.rstrip()+'\n',encoding='utf-8',newline='\n')
with zipfile.ZipFile(V/'baseline-source.zip') as z:
 names=set(z.namelist());paths=[]
 candidates=[*R.glob('*.md'),*R.glob('customer-docs/*.md'),*R.glob('docs/*.html'),*R.glob('skills/yammerknit/**/*.md'),R/'skills/yammerknit/examples/pilot-source.txt',*R.glob('delivery-sidecars/estate-quality-20261007-r1/*.md')]
 for p in candidates:
  rel=p.relative_to(R).as_posix()
  current=p.read_text('utf-8-sig').replace('\r\n','\n').strip();old=z.read(rel).decode('utf-8-sig').replace('\r\n','\n').strip() if rel in names else None
  if current!=old:paths.append(rel)
paths=sorted(set(paths));write(A/'documentation-manifest.json',json.dumps({'format':'cd-customer-documentation/v1','product':'Yammerknit','version':'0.1.0','customer_docs':paths,'scope':'New or materially revised active instruction and customer text; original seeds, retained history, artwork and formatting-only changes excluded.'},indent=2))
write(A/'evidence-packet.json',json.dumps({'product':'Yammerknit','version':'0.1.0','audience':'Source owner, unfamiliar reader, source-grounded author, RAG preparer, installer and maintainer','top_tasks':['Create a faithful useful mesh from an available source','Reuse a chunk with its evidence and qualifiers intact','Preserve and revise source-linked artifacts','Return without knowing a record ID','Recover corrupt records without rewriting history','Install and reproduce the customer kit'],'sources':['verification/estate-quality-20261007/product-audit/critique.md','verification/estate-quality-20261007/baseline-probes.json','verification/estate-quality-20261007/browser-r1/browser-review.json','skills/yammerknit/examples/pilot-source.txt','skills/yammerknit/scripts/yammerknit_tool.py'],'external_references':[{'url':'https://support.claude.com/en/articles/12512180-use-skills-in-claude','use':'Current upload labels checked by primary documentation; not live activation.'},{'url':'https://code.claude.com/docs/en/skills','use':'Current skill-folder reference.'},{'url':'https://www.w3.org/TR/webvtt1/','use':'Subtitle timing/voice representation context; helper is not full renderer.'}],'limits':'In-process expert authorship, synthetic native cases and real local browser documentation journey; no model or participant trial, live acquisition or private corpus mutation.'},indent=2))
write(A/'execution.md','''# In-process documentation authorship

The worker read and applied Hesperos entry, preserved persona, integrated practitioner and usability verification guidance, and Promptcraft's complete design reference. It reconstructed product truth from canonical source, retained baseline failure probes, package topology, CLI help and exact native behavior. The new active adapter, complete fictional teaching source/artifact, specific source-to-shard contrasts, entry, browse/return, custody recovery and package reproduction instructions were composed in this execution. The public site was materially revised to carry the same actual journey.

The authored source fixture is explicitly fictional and its digest is computed from the exact shipped bytes. Neither that authored example nor expert continuations represent an executed model trial. Current native runtime and actual browser navigation are separate evidence. The author preserved canonical SOP/persona, original art and historical verification; unchanged and formatting-only documents are excluded. Root's independent review follows the frozen candidate and is not impersonated here.
''')
sys.path.insert(0,r'E:\Github\scribe-hesperos-clearpath\source\working-package\skills\hesperos-documentation\scripts');from hesperos_authorship import documentation_fingerprint
fp=documentation_fingerprint(R,paths);write(A/'authoring-response.md',f'AUTHORING_RUN_ID: yammerknit-estate-20261007\nAUTHORING_CAPABILITY: hesperos-documentation\nAUTHORSHIP_SCOPE: materially-revised\nAUTHORED_FILES_COUNT: {len(paths)}\nAUTHORED_FILES: '+'|'.join(paths)+f'\nDOCUMENTATION_FINGERPRINT: {fp}\nHESPEROS_AUTHORING_COMPLETE')
print(json.dumps({'authored_documents':len(paths),'fingerprint':fp,'files':paths},indent=2))
