#!/usr/bin/env python3
"""Rebuild Japanese translation addon using original installed Sunless Sea JSON files.
Does not edit the game or saves; output directory must not yet exist.
"""
from pathlib import Path
import json,hashlib,argparse,copy,sys
def digest(data):return hashlib.sha256(data).hexdigest()
def fail(reason):raise RuntimeError(reason)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--game-data',type=Path,required=True,help='Original English Sunless Sea user-data root containing entities/ and encyclopaedia/')
 ap.add_argument('--output',type=Path,required=True,help='Fresh build directory (not live game directory)')
 ap.add_argument('--manifest',type=Path,default=Path(__file__).with_name('manifest.json'))
 args=ap.parse_args()
 root=Path(__file__).resolve().parent
 manifest=json.loads(args.manifest.read_text())
 if manifest.get('format')!='sunless-sea-ja-patch-only-v1':fail('Unknown patch format')
 original=args.game_data.expanduser().resolve()
 dest=args.output.expanduser().resolve()
 if dest.exists():fail('Output exists; refusing to overwrite: '+str(dest))
 if dest==original or original in dest.parents or dest in original.parents:
  fail('Output may not be inside or contain the game original data root')
 for rel,record in manifest['files'].items():
  src=original/rel
  if not src.is_file():fail('Missing original game data: '+str(src))
  b=src.read_bytes()
  if digest(b)!=record['source_sha256']:
   fail('Wrong game version or already localized base file: '+rel+'; do not force patch')
  patches=json.loads((root/'delta'/rel).read_text())
  if len(patches)!=record['changed_text_fields']:fail('Patch count changed: '+rel)
  obj=json.loads(b)
  for parts,value in patches:
   if not isinstance(parts,list) or not parts or not isinstance(value,str):fail('Invalid patch content: '+rel)
   cur=obj
   for key in parts[:-1]:cur=cur[key]
   if not isinstance(cur[parts[-1]],str):fail('Patch targets non-text game field: '+rel)
   cur[parts[-1]]=value
  target=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
  if digest(target)!=record['target_canonical_json_sha256']:
   fail('Built JSON differs from reviewed reference: '+rel)
  out=dest/'japanese_translation'/rel
  out.parent.mkdir(parents=True,exist_ok=True)
  out.write_bytes(target)
  if digest(out.read_bytes())!=record['target_canonical_json_sha256']:fail('Build readback failed: '+rel)
 print(json.dumps({'status':'PASS','addon':str(dest/'japanese_translation'),'files':len(manifest['files']),
  'changed_text_fields':sum(x['changed_text_fields'] for x in manifest['files'].values()),
  'installed':False,'game_and_saves_unchanged':True},ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('PATCH_FAILED: '+str(error),file=sys.stderr)
  raise SystemExit(1)
