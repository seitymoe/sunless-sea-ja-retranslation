# QEffectOnEnter / Quality.Name 安全性診断（開発者向け）

対象: [Issue #2](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/2) の `FailBetter.Core.Character.internalEnactQEffect` → `QEffectOnEnter.ApplyQEffects` の NullReferenceException。

一部のゲーム内シーンは `QualityRepository.GetByName(QualityName)` で品質を検索します。品質の表示名 `Name` を日本語化すると、原本のシーン参照名と不一致になる可能性があります。**元ゲームのQEffect側参照が実際にどの名称を指しているかが未検証なので、翻訳のせいだと断定しません。**

## 実行順序

1. 本人所有のSteam版ゲーム、英語原本の `entities/qualities.json`、現在使用する日本語版 `entities/qualities.json` を保護。ゲーム本体・セーブ・Steam Cloudへ書き込まない。
2. Unityの `resources.assets` / `sharedassets*.assets` から `QEffectOnEnter` の `QualityName` を抽出。抽出失敗や不足は **unknown / incomplete** として扱う。
3. 出力例（開発者の手元だけに置き、ゲームの原作アセットをGitHubにアップロードしない）:

```json
[
  {"component":"QEffectOnEnter","QualityName":"Some English Quality",
   "asset":"resources.assets","scene":"example","object":"123"}
]
```

4. 読取専用の照合:

```bash
python3 tools/audit_qeffect_names.py \
  --original "<原本>/entities/qualities.json" \
  --localized "<翻訳生成結果>/japanese_translation/entities/qualities.json" \
  --references qeffect_references.json \
  --output qeffect_lookup_report.json
```

UnityPyで直接抽出する場合（**別途インストールが必要**）:

```bash
python3 tools/audit_qeffect_names.py \
  --original "<原本>/entities/qualities.json" \
  --localized "<翻訳生成結果>/japanese_translation/entities/qualities.json" \
  --asset "<ゲームのUnity Data>/resources.assets" \
  --asset "<ゲームのUnity Data>/sharedassets0.assets" \
  --output qeffect_lookup_report.json
```

ゲーム版に必要なTypeTreeがない場合、UnityPyが `MonoBehaviour` を展開できないことがあります。そのときは診断不能と明記して中止。**0件を「問題なし」と判定しないこと。**

## 判定と改善

- `at_risk_reference_count > 0` : シーンの英語 `QualityName` に対応する品質が日本語名へ変更されている。品質IDと原文を記録し、**該当Quality.Nameだけを英語原文に戻す修正案**を別ブランチに作る。説明文など、表示専用フィールドは日本語を維持する。
- `unresolved_reference_count > 0` : 原文品質に見つからない/複数同名など、検証不能。原因を調査するまでPASSにしない。
- どちらも0件でも、**入力したシーン参照の網羅性を別途確認**。未解析のUnity TypeTreeがある場合は未完了。
- このスクリプトは修正を自動適用しません。ゲーム本体・セーブ・日本語MODは変更しません。

## 完了ゲート

1. 問題の南方群島シーンと英語 `QualityName` の正確な文字列・Quality IDを証拠付きで特定。
2. 変更前後のゲーム内部参照が一致するか、検証可能なテストを追加。
3. 元ゲーム版とMOD版を安全な環境で比較し、原因が原作・MOD・両方のどれかを検証。
4. ゲーム起動中の強制終了や実セーブの上書きは禁止。テスト後も元のセーブのSHAを守る。
5. 根本原因不明のまま「FIXED」や「完璧」として安定版リリースしない。

コードとテストは公開パッチZIPに含むゲームファイルではなく、開発用の安全性診断です。


## Unity TypeTreeのない原本での正規抽出（2026-10-19追加）

本ゲームの所有者Macでは`resources.assets`のMonoBehaviour 2,502件のうち2,478件はUnityPy標準の`read_typetree()`で読み取れませんでした。そこでゲームの **`globalgamemanagers.assets`からMonoScriptのクラス名とPathIDを取得し、各MonoBehaviourの`m_Script`ポインタからQEffectクラスを厳密に識別**する読取専用ツールを追加しました。

以下を**所有ゲームのファイルを読み取り専用**で実行します。リポジトリや公開ZIPにゲームアセットを含めないこと。

```bash
python3 -m venv .qeffect-venv
.qeffect-venv/bin/python -m pip install UnityPy
.qeffect-venv/bin/python tools/extract_qeffect_refs.py   --game-data "<Steam版 Sunless Sea.app>/Contents/Resources/Data"   --original "<所有ゲームの英語データ>/entities/qualities.json"   --asset "<Steam版 Sunless Sea.app>/Contents/Resources/Data/resources.assets"   --output /tmp/sunless-qeffect-references.json

python3 tools/audit_qeffect_names.py   --original "<所有ゲームの英語データ>/entities/qualities.json"   --localized "<別フォルダで生成した日本語MOD>/entities/qualities.json"   --references /tmp/sunless-qeffect-references.json   --output /tmp/sunless-qeffect-audit.json
```

- 抽出側は指定されたUnity資産内のQEffectOnEnter / QEffectOnExit / QEffectOverTimeクラスだけに限定し、元の英語品質名と完全に一致する長さ付き文字列を報告する。クラス未特定・名前複数候補・空の参照は未検証として報告する。
- 本人Macの`resources.assets`では、SafeZoneのAlmost Safe（入退出2件）、TerrorCircleLarge/TheEyeのTerror（2件）、Vortex/AdamsWayBurnのHull（2件）が抽出された。対象品質ID 111067 / 102025 / 102029 のName差分のみ削除する最小修正候補を別ブランチに実装。
- この抽出は**資産に含まれるクラスの静的な照合**であり、ゲーム実行時のnull根本原因や全アセット網羅、セーブの再現テストを保証しない。現行ゲームが起動している間のMOD・セーブ・DLL変更は禁止。
