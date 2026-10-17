using System;
using System.IO;
using System.Text;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using Mono.Cecil;
using Mono.Cecil.Cil;
using System.Web.Script.Serialization;

public static class SunlessUiILPatcher {
    public sealed class Rule {
       public string assembly { get; set; }
       public string type { get; set; }
       public string method { get; set; }
       public string english { get; set; }
       public string japanese { get; set; }
       public string category { get; set; }
    }
    public sealed class Rules {
       public List<Rule> entries { get; set; }
    }
    static IEnumerable<TypeDefinition> Walk(IEnumerable<TypeDefinition> xs) {
      foreach(var t in xs){yield return t;foreach(var n in Walk(t.NestedTypes))yield return n;}
    }
    static string Sha(byte[] bytes) {
      using (var sha=SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();
    }
    static string Sha(string f){return Sha(File.ReadAllBytes(f));}
    static void Guard(bool ok,string why){if(!ok)throw new InvalidOperationException(why);}
    static bool Applies(Rule r,string asm,string fullType,string method){
      if(r.assembly!="*" && r.assembly!=asm)return false;
      if(!string.IsNullOrEmpty(r.type) && r.type!="*" && !(fullType==r.type || fullType.EndsWith("."+r.type) || fullType.EndsWith("/"+r.type)))return false;
      if(!string.IsNullOrEmpty(r.method) && r.method!="*" && method!=r.method)return false;
      return true;
    }
    static void ValidateTemplate(string before,string after) {
      // Standard .NET String.Format placeholders must be preserved, including indexed
      // formatting, escaped braces and gameplay substitutions.
      var re=new System.Text.RegularExpressions.Regex(@"(?<!\{)\{\d+(?:[^{}]*)\}(?!\})");
      var a=re.Matches(before).Cast<System.Text.RegularExpressions.Match>().Select(x=>x.Value).OrderBy(x=>x).ToArray();
      var b=re.Matches(after).Cast<System.Text.RegularExpressions.Match>().Select(x=>x.Value).OrderBy(x=>x).ToArray();
      bool isJapaneseDateFormat = before == "{0:MMMM} {1}{2}, {0:yyyy}" && after == "{0:yyyy}年{0:MM}月{1}日";
      Guard(isJapaneseDateFormat || a.SequenceEqual(b),"Format placeholders mismatch: "+before+" -> "+after);
      var tags=new System.Text.RegularExpressions.Regex(@"</?[A-Za-z]+(?:\\s+[^<>]*)?>");
      var beforeTags=tags.Matches(before).Cast<System.Text.RegularExpressions.Match>().Select(x=>x.Value).OrderBy(x=>x).ToArray();
      var afterTags=tags.Matches(after).Cast<System.Text.RegularExpressions.Match>().Select(x=>x.Value).OrderBy(x=>x).ToArray();
      Guard(beforeTags.SequenceEqual(afterTags),"HTML tags changed: "+before+" -> "+after);
      var substitutions=new System.Text.RegularExpressions.Regex(@"\\[(?:q|d|x|v):[^\\]]*\\]|\\[(?:fatelink|sharelink)\\]");
      var bt=substitutions.Matches(before).Cast<System.Text.RegularExpressions.Match>().Select(x=>x.Value).OrderBy(x=>x).ToArray();
      var at=substitutions.Matches(after).Cast<System.Text.RegularExpressions.Match>().Select(x=>x.Value).OrderBy(x=>x).ToArray();
      Guard(bt.SequenceEqual(at),"Story placeholders changed: "+before+" -> "+after);
      Guard(!string.IsNullOrWhiteSpace(after),"Blank Japanese "+before);
      Guard(after!=before,"Same-as-source target "+before);
    }
    public static int Main(string[] args) {
      try{
        Guard(args.Length==5,"usage patcher --scan|--patch dllDir rules.json outputDir audit.json");
        bool write=args[0]=="--patch";
        Guard(write || args[0]=="--scan","only --scan or --patch");
        string indir=args[1],rulespath=args[2],outdir=args[3],auditpath=args[4];
        var js=new JavaScriptSerializer(); js.MaxJsonLength=int.MaxValue; js.RecursionLimit=500;
        var input=js.Deserialize<Rules>(File.ReadAllText(rulespath,Encoding.UTF8));
        Guard(input.entries!=null && input.entries.Count>0,"No rules");
        var index=new Dictionary<string,List<Rule>>();
        foreach(var r in input.entries){
          ValidateTemplate(r.english,r.japanese);
          Guard(new[]{"Failbetter.Core.dll","Sunless.Game.dll","*"}.Contains(r.assembly),"Unrecognized library "+r.assembly);
          string key=r.english;
          if(!index.ContainsKey(key))index[key]=new List<Rule>();
          index[key].Add(r);
        }
        Directory.CreateDirectory(Path.GetDirectoryName(auditpath));
        if(write) Directory.CreateDirectory(outdir);
        var audit=new Dictionary<string,object>();
        var allchanges=new List<Dictionary<string,string>>();
        var files=new List<Dictionary<string,object>>();
        var seen=new HashSet<Rule>();
        foreach(var name in new[]{"Failbetter.Core.dll","Sunless.Game.dll"}){
          string original=Path.Combine(indir,name);
          string beforeSha=Sha(original);
          Guard((name=="Failbetter.Core.dll"&&beforeSha=="38086ba0c8c86be0c9de596048fe64d19d2a3b987a4ed056300225dfa9010a24") ||
                (name=="Sunless.Game.dll"&&beforeSha=="961c443303abec73337589f0a214f286b9bb2c8f4d48e2c734f8a1c2a0b5e535"),
                "Unrecognized game version "+name+" "+beforeSha);
          int patched=0;
          var reader=new ReaderParameters{ReadingMode=ReadingMode.Deferred,ReadSymbols=false,InMemory=true};
          using(var asm=AssemblyDefinition.ReadAssembly(original,reader)){
            foreach(var t in Walk(asm.MainModule.Types)){
              foreach(var m in t.Methods){
                if(!m.HasBody)continue;
                foreach(var inst in m.Body.Instructions){
                  if(inst.OpCode.Code!=Code.Ldstr || !(inst.Operand is string))continue;
                  string old=(string)inst.Operand;
                  List<Rule> candidates;
                  if(!index.TryGetValue(old,out candidates))continue;
                  var valid=candidates.Where(x=>Applies(x,name,t.FullName,m.Name)).ToList();
                  if(valid.Count==0)continue;
                  var translations=valid.Select(x=>x.japanese).Distinct().ToList();
                  Guard(translations.Count==1,"Collision "+name+" "+t.FullName+" "+m.Name+" "+old+" "+string.Join(" // ",translations));
                  var selected=valid[0];
                  if(write)inst.Operand=selected.japanese;
                  patched++;
                  valid.ForEach(x=>seen.Add(x));
                  allchanges.Add(new Dictionary<string,string>{
                    {"assembly",name},{"type",t.FullName},{"method",m.Name},
                    {"english",old},{"japanese",selected.japanese},{"category",selected.category??"UI"}
                  });
                }
              }
            }
            if(write){
              string output=Path.Combine(outdir,name);
              if(File.Exists(output))throw new IOException("Refuse overwrite: "+output);
              asm.Write(output,new WriterParameters{WriteSymbols=false});
            }
          }
          string afterSha=write?Sha(Path.Combine(outdir,name)):"not-written";
          files.Add(new Dictionary<string,object>{
            {"assembly",name},{"input_sha256",beforeSha},{"patched_instruction_count",patched},{"output_sha256",afterSha},
            {"original_bytes",new FileInfo(original).Length},{"patched_bytes",write?new FileInfo(Path.Combine(outdir,name)).Length:0}
          });
          Console.WriteLine(name+" instruction replacements="+patched+" output="+afterSha);
        }
        audit["status"]=write?"PATCHED_ISOLATED_UNINSTALLED":"DRY_RUN_NO_MODIFICATION";
        audit["mode"]=args[0];
        audit["rule_count"]=input.entries.Count;
        audit["matched_rules"]=seen.Count;
        audit["unmatched_rules"]=input.entries.Where(x=>!seen.Contains(x)).Select(x=>new{dll=x.assembly,type=x.type,method=x.method,en=x.english}).ToList();
        audit["changes"]=allchanges;
        audit["files"]=files;
        audit["installed"]=false;
        audit["in_game_tested"]=false;
        File.WriteAllText(auditpath,js.Serialize(audit),Encoding.UTF8);
        Console.WriteLine("SUMMARY rules="+input.entries.Count+" seen="+seen.Count+" changed="+allchanges.Count+" file="+auditpath);
        return 0;
      }catch(Exception e){Console.Error.WriteLine("PATCH_ERROR "+e.GetType().Name+" "+e.Message);return 1;}
    }
}
