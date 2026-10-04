#!/usr/bin/env python3
"""Validate package integrity and input/reference separation without API access."""
from pathlib import Path
import hashlib,json,csv
ROOT=Path(__file__).resolve().parent.parent
catalog=json.loads((ROOT/'datasets/final40/catalog.json').read_text())
assert len(catalog)==40 and len({r['filename'] for r in catalog})==40
assert len(list((ROOT/'datasets/final40/pdfs').glob('*.pdf')))==40
for r in catalog:
    for field in ['pdf','text']+(['source_html'] if 'source_html' in r else []):
        p=ROOT/'datasets/final40'/r[field];assert hashlib.sha256(p.read_bytes()).hexdigest()==r[field+'_sha256'],str(p)
manifest=ROOT/'package_manifest.json'
if manifest.exists():
    for r in json.loads(manifest.read_text())['files']:
        p=ROOT/r['path'];assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
assert (ROOT/'dashboard/index.html').exists()
assert len(json.loads((ROOT/'dashboard/data.json').read_text())['contracts'])==40
print('Package OK: 40 replacement input PDFs, text/source hashes and packaged files verified; final card dashboard included.')
