# Sunless Sea JA — PM公開ゲート

## 現状
- 最新公開テスト版: v2026.10.19-k26.2（GitHub Releases・prerelease）。K26.1は前版。
- 差分方式: 所有ゲームの英語データから日本語ファイルを再構築し、元ゲームデータやDLLを再配布しない
- 翻訳変更28,080か所 / 10 JSON、任意Mac UIは529ルール・552命令
- 既知問題: 航海中のQEffectOnEnterでNullReferenceExceptionが稀に発生。原因・MODとの因果は未確定
- 開発者のゲームが起動中はゲーム本体、MOD、セーブを書き換えない

## ゲートA: CI・供給物の安全
- [x] JSON差分のパス・件数・型・SHAを検証
- [x] ゲームの版が違うとき生成を拒否し、元データを上書きしない
- [x] BUY/SELL、Stack Item、入力キー、通貨と商店の処理をUIパッチで変更しない
- [x] ゲームDLL・セーブ・ゲーム本体JSONの再配布をしない
- [x] 開発者Macで英語ゲーム原本から10/10翻訳JSONのSHAが一致
- [x] 開発者Macで元DLLから任意UI552箇所の出力SHAが一致
- [x] GitHub Actionsの実行がgreen（main: 64d90efef20d51cf7fd8f1c1cf521326d12aa43f、[2026-10-19成功実行](https://github.com/seitymoe/sunless-sea-ja-retranslation/actions/runs/39165689052)）

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
- 6つのName保護に加え、入港時 \`a stranger\` 品質ID231も保護（合計7つ）。
- RC2の自動適用監視は見落とし発見時点で停止済み。RC3の実機A/Bを行うまでは再開しない。
- 『Addressed As』(コード側) と『Addressed as』(原作Quality.Name)は不一致。原作由来の問題かゲーム内で再現するか、同一セーブでテストが必要。
- ほか9JSON/数値/ゲームDLL/売買処理・セーブは不変。
