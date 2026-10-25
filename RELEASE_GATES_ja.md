> **K26.3 RC3公開テスト版：所有者MacでContinue／ロンドンのBUY £5・SELL £1がスモーク合格。P0 #1/#2の全体回帰と同一セーブ英語原本A/Bは未完了。安定版昇格は禁止。**

> **現行公開版（2026-10-25確認）：[K26.3 RC3](https://github.com/seitymoe/sunless-sea-ja-retranslation/releases/tag/v2026.10.19-k26.3-rc3) は2026-10-19公開の `prerelease=true`。PR #9はDraft・未マージ。差分28,073件、内部名保護7件、静的テスト30件合格。ただしP0実機A/Bと原因確定は未完了で、安定版ではありません。**

# Sunless Sea JA — PM公開ゲート

## 現状
- 最新公開テスト版: [v2026.10.19-k26.3-rc3](https://github.com/seitymoe/sunless-sea-ja-retranslation/releases/tag/v2026.10.19-k26.3-rc3)（2026-10-19公開・prerelease）。K26.2とK26.1は前版であり、PR #9は未マージDraft。
- 差分方式: 所有ゲームの英語データから日本語ファイルを再構築し、元ゲームデータやDLLを再配布しない
- RC3の翻訳差分28,073フィールド / 10 JSON。任意Mac UIは529ルール・552命令。
- 既知問題: 航海中のQEffectOnEnterでNullReferenceExceptionが稀に発生。原因・MODとの因果は未確定
- 開発者のゲームが起動中はゲーム本体、MOD、セーブを書き換えない

## ゲートA: CI・供給物の安全
- [x] JSON差分のパス・件数・型・SHAを検証
- [x] ゲームの版が違うとき生成を拒否し、元データを上書きしない
- [x] BUY/SELL、Stack Item、入力キー、通貨と商店の処理をUIパッチで変更しない
- [x] ゲームDLL・セーブ・ゲーム本体JSONの再配布をしない
- [x] 開発者Macで英語ゲーム原本から10/10翻訳JSONのSHAが一致
- [x] 開発者Macで元DLLから任意UI552箇所の出力SHAが一致
- [x] mainの最新GitHub Actionsは2026-10-19に成功（SHA `c8c31d8d11de6a759efd99c2918c03636f9f291d`、[run 39171629998](https://github.com/seitymoe/sunless-sea-ja-retranslation/actions/runs/39171629998)）。**mainはK26.2相当**。RC3 PR #9の最新CIも2026-10-19成功（[run 39180293151](https://github.com/seitymoe/sunless-sea-ja-retranslation/actions/runs/39180293151)）。PR #11の合成ログテストCIは2026-10-24成功（[run 40044092872](https://github.com/seitymoe/sunless-sea-ja-retranslation/actions/runs/40044092872)）。いずれも実機の全操作を証明するものではない。

## ゲートB: 実機プレイ・ロールバック
- [ ] 元のSteamアプリ、addon、全セーブが別ディレクトリでハッシュ付きバックアップ済み
- [ ] 商店でBUY 5・SELL 1、所持金・所持数をクリック直後に照合
- [ ] £999999の初期文字列が残らない。再現時はログと画面を確保
- [ ] 新規/オートセーブ/ロード、港、航海、戦闘、装備、士官が操作できる
- [ ] 署名とDLL版、内部キー保護が正常
- [ ] QEffectOnEnterの例外の原本ゲームとの比較検証
- [ ] 異常時はセーブを上書きせず復元できる

## ゲートC: 文学的品質と配布
- [ ] 人物口調・固有名詞・敬語・地名の横断校正
- [ ] UI文字切れ・改行・翻訳不要の内部識別子を確認
- [ ] READMEのOS、バージョン、SHA、必要なツール、復元手順を照合
- [ ] Windowsなど未検証プラットフォームを明示
- [ ] 公開Asset SHAと再現ビルドが一致
- [x] 全重大問題はGitHub Issueで追跡（[売買・ロード #1](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/1)、[QEffectOnEnter #2](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/2)、[文学的校正 #3](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/3)、[互換性 #4](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/4)）

## PM優先順位
1. セーブ破損、進行不能、誤った取引金額
2. 操作識別子とPrefab名への翻訳による副作用
3. リリース再現性、テスト自動化、実機回帰
4. 誤訳・訳語・画面の改善
5. 安定版判定。全ルート未テストなら「完全検証済み」とは称さない

内部識別子を壊してまで全UIの英語を除去しない。

## 最新の運用状況（2026-10-25 09:09 JST読み取り専用確認）

- **GitHub公開状態:** K26.3 RC3は公開済みプレリリース。公開AssetのSHA-256は `6054ac2cffe6ef5bd77c0b69f2fc56282016c51a3d6289032561aecdbe56510a`。公開ZIPは変更せず、正式安定版タグも作らない。
- **所有者Macの現用パッチ:** `entities/qualities.json` SHA-256は `e514c01cf815f0dbccf5f408f1c2d85d3a208a7672cde1f91d09f7865990b3fa`（旧K25相当）。RC3の `3fb9f6c9ae98784ec671246811697414fd6b7669c1f6b0b791eee36211002f43` と異なり、**RC3が現在稼働中と扱わない**。ゲームは稼働中であり終了・MOD切替・セーブ・Steam Cloud・元DLLの変更は禁止。
- **未解決P0の追加証拠:** 2026-10-25 02:31 JST更新の私有 `Player.log` に `QEffectOnEnter`（南方群島）1件、`QEffectOverTime`（鉄の共和国）1件のNullReference例外が含まれる。旧K25相当での観測であり、**RC3が失敗した証拠ではない**。生ログや個人セーブは公開しない。
- **限定された成功:** 2026-10-19のRC3実機スモークはContinueとキャロウ店1商品・1セーブだけ。原本英語・旧K25・RC3の独立A/B/C、売買の反復・ロード・他海域の再現試験は未完了。
- **次の作業:** #1/#2はユーザーの明示許可、ゲーム正常終了、Steam Cloud同期確認、別フォルダのアプリ・MOD・セーブ全量SHAバックアップ後、隔離セーブで比較。#3はTeaser↔Description候補106件の先頭20件の二重査読。#4はWindows互換性と復元手順の実機検証。PR #9/#11はDraft継続。
- **文書管理:** `RELEASE_STATUS.json` の `checked_at_utc=2026-10-18T22:17:14.485637+00:00` と `previous_public_release_tag` は**公開前の歴史的スナップショット**。最新の公開状態・現用Macを表す欄と誤認しない。更新する場合は依存する `CHECKSUMS.json` も再生成してCIを通す。

**以下の2026-10-19以前の各節は、その時点の履歴・当時の判断であり、上記の最新状態に優先しません。**

## 2026-10-19 K26.2参照名保護の追加確認（公開テスト版）

- 所有者の`resources.assets`内にあるMonoBehaviourと`globalgamemanagers.assets`のMonoScriptを照合。QEffectOnEnter/Exit/OverTimeの6参照すべてで、内部英語名と日本語Nameの不一致があった。
- そのうち`Almost Safe`（111067）・`Terror`（102025）・`Hull`（102029）の`Name`だけ英語原文を保持する修正候補を用意。差分28,077件。
- **ゲームは起動中のため、実セーブ/元アプリ/稼働中のaddonは未変更。** まだ同一セーブによる原本とのA/B試験がないので #2の根本原因確定・完全解決とはしない。
- 今回の作業は既存のK26.1公開Asset SHAや過去のリリースに影響しない。新たなバージョンは独立リリース候補として審査する。

## 2026-10-19 PM検証済みの証拠と残作業

- 公開テスト版: [v2026.10.17-k26.1](https://github.com/seitymoe/sunless-sea-ja-retranslation/releases/tag/v2026.10.17-k26.1)。GitHub Releaseは `prerelease=true`。
- GitHubによる公開AssetのSHA-256: `652996c05b0c2a24993a9fe483717a04b43e127751973259b4c7d84540f6d651`（`SunlessSea_Japanese_Retranslation_PatchOnly_K26_1_20261017.zip`、1,371,990 bytes）。
- mainのActionsはgreen（2026-10-19 05:58 JST頃）。ただし**これは静的CIであり、ゲームでの価格・ロード・航海操作の正常性の保証ではない**。
- 原文SHAを必要とする差分方式を保持。実ゲーム原文JSON・ゲームDLL・ゲームバイナリ・セーブデータは公開ZIPに同梱しない。
- **公開Assetと手元の再現ビルドのSHA-256の直接照合**は、同一資産を独立に取得・ハッシュ検証するまで未完了。GitHub表示digestを記録したこと自体は照合完了ではない。
- 優先順位: #1（単発BUY/SELLと即時残高、Continue/Load） → #2（QEffectOnEnter の原本比較） → #3（全訳の文体校正） → #4（Windows/導入互換性）。
- 再現テストでは **商品名・価格表示・エコー残高・所持数をクリック前後で記録**。データ不一致や進行不能が1件でもあれば安定版への昇格を停止。
- **ゲーム起動中のDLL・MOD・セーブの書換え禁止**。ロールバックは完全バックアップとSHA検証を確保してから、元のセーブを上書きしない形で行う。

### 安定版昇格の判定

**現在: 公開テスト版を維持し、安定版への昇格は保留。**

オフラインテストが通ったことだけで Issue #1/#2 の完了や「全場面テスト済み」を宣言しない。各Issueに再現手順、スクリーンショット/ゲームログ、テスト開始・終了時のセーブSHA、変更差分、原本との差分を保存してから個別に閉じる。

## K26.3 RC3 最新PMゲート（2026-10-19）
- 6つのName保護に加え、エディタ専用の入港処理で参照される \`a stranger\` 品質ID231も保護（合計7つ）。
- RC2の自動適用監視は見落とし発見時点で停止済み。RC3の実機A/Bを行うまでは再開しない。
- 『Addressed As』(コード側) と『Addressed as』(原作Quality.Name)は不一致。原作由来の問題かゲーム内で再現するか、同一セーブでテストが必要。
- ほか9JSON/数値/ゲームDLL/売買処理・セーブは不変。
