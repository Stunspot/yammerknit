#!/usr/bin/env python3
"""Verify an explicitly selected extracted customer kit; never changes its bytes."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import zipfile
from build_release import files_beneath, safe_path, sha256, PRODUCT_ROOT, VERSION, load_json


def audit(root):
    root = safe_path(root)
    if not root.is_dir():
        raise ValueError('Customer root does not exist')
    manifest_path = root/'release-manifest.json'
    manifest = load_json(manifest_path)
    if not isinstance(manifest,dict) or manifest.get('schema') != 'yammerknit.customer-release.v1' or manifest.get('version') != VERSION:
        raise ValueError('Unexpected customer manifest identity')
    rows=manifest.get('files'); declared={}; issues=[]
    if not isinstance(rows,list) or not rows:
        raise ValueError('Manifest file inventory is empty or malformed')
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('path'),str):
            raise ValueError('Malformed file entry')
        name=row['path']; parts=name.split('/')
        if not name or '\\' in name or any(p in ('','.','..') for p in parts) or name.startswith('/') or ':' in name or name.casefold() in {k.casefold() for k in declared}:
            raise ValueError('Unsafe or duplicate manifest path')
        declared[name]=row
    actual={p.relative_to(root).as_posix():p for p in files_beneath(root) if p != manifest_path}
    if set(actual)!=set(declared): issues.append('Manifest inventory does not match actual files')
    for name,row in declared.items():
        path=actual.get(name)
        if path is None or type(row.get('bytes')) is not int or row['bytes']!=path.stat().st_size or row.get('sha256')!=sha256(path):
            issues.append('Missing or changed file: '+name)
    required={'START-HERE.md','docs/INSTALLATION.md','docs/USE-YAMMERKNIT.md','codex-plugin/yammerknit/skills/yammerknit/SKILL.md','source/verification/build_release.py','claude/yammerknit-v0.1.0.zip','.agents/plugins/marketplace.json'}
    if not required <= set(actual): issues.append('Required customer surfaces missing')
    nested=root/'claude/yammerknit-v0.1.0.zip'
    if nested.is_file():
        with zipfile.ZipFile(nested) as archive:
            names=archive.namelist()
            if len(names)!=len(set(n.casefold() for n in names)) or archive.testzip(): issues.append('Invalid Claude archive')
            plugin=root/'codex-plugin/yammerknit/skills/yammerknit'
            expected={f'yammerknit/{p.relative_to(plugin).as_posix()}':p for p in files_beneath(plugin) if p.relative_to(plugin).parts[0]!='agents'}
            if set(names)!=set(expected): issues.append('Claude runtime inventory differs')
            for name,path in expected.items():
                if name not in names or archive.read(name)!=path.read_bytes(): issues.append('Claude runtime differs: '+name)
    return {'schema':'yammerknit.current-package-audit.v1','root':str(root),'file_count':len(actual)+1,'issues':issues,'summary':{'errors':len(issues)},'scope':'Physical inventory, hashes, required surfaces and nested runtime parity; no model trial or host activation.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',required=True,type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        result=audit(args.root)
        payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output:
            target=safe_path(args.output)
            if target==safe_path(args.root) or safe_path(args.root) in target.parents: raise ValueError('Audit output must stay outside the customer tree')
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('x',encoding='utf-8',newline='\n') as handle:handle.write(payload)
        print(payload,end='');return bool(result['issues'])
    except (OSError,ValueError,RuntimeError,KeyError,TypeError,zipfile.BadZipFile) as exc:
        parser.exit(2,f'Audit failed: {exc}\n')
if __name__=='__main__':raise SystemExit(main())
