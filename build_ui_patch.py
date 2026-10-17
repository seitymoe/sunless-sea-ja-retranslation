#!/usr/bin/env python3
"""Build (not install) verified Mac game-owned UI DLL patches using Mono.Cecil.
Does not redistribute or edit any copyrighted game binary.
"""
from pathlib import Path
import argparse,json,hashlib,subprocess,shutil,sys
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser()
 a.add_argument('--managed',type=Path,required=True,help='Original game app/Contents/Resources/Data/Managed')
 a.add_argument('--output',type=Path,required=True,help='New output folder, never the game folder')
 args=a.parse_args()
 root=Path(__file__).resolve().parent
 data=json.loads((root/'manifest.json').read_text())['ui']
 managed=args.managed.expanduser().resolve()
 output=args.output.expanduser().resolve()
 if output.exists():raise RuntimeError('Output already exists; refusing overwrite')
 if output==managed or managed in output.parents or output in managed.parents:
  raise RuntimeError('Output must be separate from game directory')
 for name,digest in data['original_assembly_sha256'].items():
  p=managed/name
  if not p.exists() or sha(p)!=digest:raise RuntimeError('Unknown, newer or already modified game DLL: '+name)
 for command in ('mcs','mono'):
  if shutil.which(command) is None:raise RuntimeError('Missing '+command+'; install Mono via brew install mono')
 roots=[Path('/opt/homebrew/lib/mono/gac/Mono.Cecil'),Path('/usr/local/lib/mono/gac/Mono.Cecil')]
 cecil=next((p for root in roots if root.exists() for p in sorted(root.glob('*/Mono.Cecil.dll'))),None)
 if cecil is None:raise RuntimeError('Mono.Cecil.dll unavailable in the installed Mono GAC')
 output.mkdir(parents=True)
 exe=output/'SunlessUiILPatcher.exe'
 build=['mcs','-optimize+','-r:'+str(cecil),'-r:System.Web.Extensions',
        '-out:'+str(exe),str(root/'ui/SunlessUiILPatcher.cs')]
 p=subprocess.run(build,capture_output=True,text=True,timeout=90)
 if p.returncode:raise RuntimeError('Compile error: '+p.stderr[-950:])
 audit=output/'UI_STATIC_AUDIT.json'
 run=['mono',str(exe),'--patch',str(managed),str(root/'ui/ui_rules.json'),str(output/'Managed'),str(audit)]
 p=subprocess.run(run,capture_output=True,text=True,timeout=200)
 if p.returncode:raise RuntimeError('IL patch error: '+p.stdout[-600:]+' '+p.stderr[-950:])
 result=json.loads(audit.read_text(encoding='utf-8-sig'))
 if len(result['changes'])!=data['translated_managed_string_instructions']:
  raise RuntimeError('Unexpected number of patched strings')
 for file,digest in data['expected_patched_assembly_sha256'].items():
  target=output/'Managed'/file
  if sha(target)!=digest:raise RuntimeError('Patched binary SHA changed: '+file)
 print(json.dumps({'status':'PASS','built_only_not_installed':True,
  'ui_strings_changed':len(result['changes']),'output':str(output/'Managed'),
  'unmodified_game_originals':True},ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception as e:
  print('UI_BUILD_FAILED: '+str(e),file=sys.stderr)
  raise SystemExit(1)
