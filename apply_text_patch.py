#!/usr/bin/env python3
"""Rebuild Japanese translation addon using original installed Sunless Sea JSON files.
Does not edit the game or saves; output directory must not yet exist.
"""
from pathlib import Path
import json,hashlib,argparse,shutil,sys,os
def digest(data):return hashlib.sha256(data).hexdigest()
def fail(reason):raise RuntimeError(reason)

def checked_relative_json(name):
 """Reject path traversal, absolute paths, and platform-specific separators."""
 if not isinstance(name,str) or '\\' in name or '\x00' in name or ':' in name:
  fail('Unsafe manifest file path')
 parts=name.split('/')
 if (len(parts)<2 or parts[0] not in ('entities','encyclopaedia','geography')
     or any(part in ('','.','..') for part in parts) or not name.endswith('.json')):
  fail('Unsafe manifest file path: '+repr(name))
 return Path(*parts)

def checked_child(root,path,description):
 """Do not read a JSON symlink that escapes the approved original/delta root."""
 if root not in path.resolve().parents:
  fail(description+' escapes allowed directory')
 return path

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--game-data',type=Path,required=True,help='Original English Sunless Sea user-data root containing entities/ and encyclopaedia/')
 ap.add_argument('--output',type=Path,required=True,help='Fresh build directory (not live game directory)')
 ap.add_argument('--manifest',type=Path,default=Path(__file__).with_name('manifest.json'))
 args=ap.parse_args()
 root=Path(__file__).resolve().parent
 manifest=json.loads(args.manifest.read_text())
 if manifest.get('format')!='sunless-sea-ja-patch-only-v1':fail('Unknown patch format')
 if not isinstance(manifest.get('files'),dict) or not manifest['files']:
  fail('Invalid patch manifest file list')
 original=args.game_data.expanduser().resolve()
 if args.output.expanduser().is_symlink():fail('Output cannot be a symlink')
 dest=args.output.expanduser().resolve()
 if dest.exists():fail('Output exists; refusing to overwrite: '+str(dest))
 if dest==original or original in dest.parents or dest in original.parents:
  fail('Output may not be inside or contain the game original data root')
 # Even if --game-data is a separate English copy, do not write into a
 # live installation. On Windows Unity stores saves/addons under LocalLow,
 # not LOCALAPPDATA (which normally points to the sibling "Local" folder).
 # These guards do NOT imply Windows UI or game-version compatibility.
 protected_roots=[
   Path.home()/'Library/Application Support/com.failbettergames.sunlesssea',
   Path.home()/'Library/Application Support/Steam/steamapps/common/SunlessSea/Sunless Sea.app',
   Path.home()/'AppData/LocalLow/Failbetter Games/Sunless Sea',
 ]
 if os.environ.get('USERPROFILE'):
  protected_roots.append(Path(os.environ['USERPROFILE'])/'AppData/LocalLow/Failbetter Games/Sunless Sea')
 if os.environ.get('LOCALAPPDATA'):
  protected_roots.append(Path(os.environ['LOCALAPPDATA']).parent/'LocalLow/Failbetter Games/Sunless Sea')
 for live in protected_roots:
  protected=live.expanduser().resolve()
  if dest==protected or protected in dest.parents:
   fail('Output may not be inside the live Sunless Sea installation')
 delta_root=(root/'delta').resolve()
 if root not in delta_root.parents:fail('Patch source directory escapes release')
 validated=[]
 for rel,record in manifest['files'].items():
  relative=checked_relative_json(rel)
  src=checked_child(original,original/relative,'Original game JSON')
  patch_file=checked_child(delta_root,delta_root/relative,'Patch JSON')
  if not src.is_file():fail('Missing original game data: '+str(src))
  if not patch_file.is_file():fail('Missing patch JSON: '+str(patch_file))
  b=src.read_bytes()
  if digest(b)!=record['source_sha256']:
   fail('Wrong game version or already localized base file: '+rel+'; do not force patch')
  patches=json.loads(patch_file.read_text())
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
  validated.append((relative,target,record['target_canonical_json_sha256']))
 # Validate all ten source/target hashes before creating any partial output.
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.mkdir(exist_ok=False)
 try:
  for relative,target,expected_sha in validated:
   out=dest/'japanese_translation'/relative
   out.parent.mkdir(parents=True,exist_ok=True)
   out.write_bytes(target)
   if digest(out.read_bytes())!=expected_sha:fail('Build readback failed: '+str(relative))
 except BaseException:
  # Only clean the newly created stage, never originals/addon/saves.
  shutil.rmtree(dest)
  raise
 print(json.dumps({'status':'PASS','addon':str(dest/'japanese_translation'),'files':len(manifest['files']),
  'changed_text_fields':sum(x['changed_text_fields'] for x in manifest['files'].values()),
  'installed':False,'game_and_saves_unchanged':True},ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception as error:
  print('PATCH_FAILED: '+str(error),file=sys.stderr)
  raise SystemExit(1)
