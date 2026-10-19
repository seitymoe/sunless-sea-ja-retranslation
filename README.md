# Sunless Sea 非公式日本語再翻訳パッチ — K26.3 RC3

**状態：公開前のレビュー候補（draft / 実機QA未完了）。正式安定版ではありません。**

これは購入済みの *Sunless Sea* の原文ゲームデータから日本語MODを生成する、非公式・無償の日本語再翻訳パッチです。ゲーム本体、原作英語JSON一式、フルDLL、音声・画像、セーブデータは配布しません。

**現在一般公開しているバージョン**は [K26.2プレリリース](https://github.com/seitymoe/sunless-sea-ja-retranslation/releases/tag/v2026.10.19-k26.2)。**K26.3 RC3はまだ公開していません。** RC3の変更内容は[PR #9](https://github.com/seitymoe/sunless-sea-ja-retranslation/pull/9)で確認できます。

## RC3の仕様

- 英語原文から日本語へ置換する**28,073フィールド**を、計**10個のJSONファイル**の差分として収録。ゲーム内の数値、ID、商店の価格、取引処理、セーブは変更しません。
- ゲームの英語名参照を壊さないため、7つの `Quality.Name` を英語のまま保持します。通常プレイのUnity `QEffect` が参照する3件：`Almost Safe` / `Terror` / `Hull`。エディターモード（`EditorMode=true`）の `NavigationProvider.Dock` が参照する4件：`Memoirs: Your Past` / `Memoirs: Quality of Lodgings` / `Addressed as` / `a stranger`。
- 任意の **Steam macOS版3.0.0.31向けUIパッチ**：529の限定された原文置換ルール、実DLLの552か所に対応。対応する元ゲームのSHA256が一致した場合のみ生成できます。
- `BUY/SELL`、価格・通貨・所持数・取引処理、ホットキー・Prefab・装備スロットの内部識別子は**日本語化しません**。仕様上意図した英語表示です。

## 導入・復元

**[詳しい日本語の導入手順](README_ja.md)** を参照してください。Python 3と、購入済みの対応ゲームが必要です。ゲームアプリ・現在のMOD・すべてのセーブデータを別の場所にバックアップしたうえで、**ゲームを完全終了してから**変更してください。元データのSHAが違う版への強制適用はしないでください。

## 検証済みと未検証

**PASS：** ZIPチェックサム、英語原本からの日本語10 JSON再生成とSHA比較、ID/数値/文字列マクロの静的テスト、30件の自動回帰テスト、CI。

**未完了：** 同じセーブコピーでのQEffect例外の原因切り分け、全商店のBUY/SELLと即時残高更新、Continue/Load/Saveの操作、全ルートの文学的校閲、Windows版UIの動作検証。RC3を「実機ですべて修復済み」とは表現しません。

[P0取引・ロード #1](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/1) · [P0 QEffect例外 #2](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/2) · [日本語校正 #3](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/3) · [他OSの互換性 #4](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/4)

## 著作権とライセンス

Sunless Sea / Fallen Londonは © / ™ Failbetter Games Limited。本パッチは同社の公式・承認作品ではありません。独自の変換**プログラム**に限りMITライセンスを適用し、原作や二次的著作物を勝手に再ライセンスしません。

[公式ゲーム](https://www.failbettergames.com/games/sunless-sea) · [公式ファン作品ガイドライン](https://www.failbettergames.com/fan-project-guidelines)
