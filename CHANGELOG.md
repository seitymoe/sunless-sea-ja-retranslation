# K26.3 RC3: 発見した入港時の7つめの内部品質参照名を保護（2026-10-19）

- 原作Dockの \`GetByName("a stranger")\` を実DLLで確認。原文品質Id 231のNameが日本語化されていたので、K26.3 RC3で原文の英語に復帰。
- 保存すべき内部Nameは合計7つ（RC2比で追加1つ）。訳文の意味や数値・取引・セーブへの影響なし。
- 原作側の \`Addressed As\` / \`Addressed as\` の大文字不一致は依然として残る。実機確認は必須。
- 前版RC2は不要なため適用せずRC3を試験候補とする。正式安定版への昇格なし。

# K26.3候補：港の内部参照名保護（2026-10-19）

- 追加で3つの内部Quality.Nameを英語原文へ復元。Memoirs: Your Past / Memoirs: Quality of Lodgings / Addressed as
- 原作ゲームの \`NavigationProvider.Dock\` にある名前検索と照合。2つの Memoirs の翻訳は参照失敗を起こし得ることを確認。
- \`Addressed As\` は原作側の \`Addressed as\` と大文字小文字が違い、完全一致検索による既存問題の可能性が残る。
- K26.2から変更するのは3つのNameのみ。元ゲームのID、数値、取引、その他の日本語、UIルールは維持。
- 公開前テスト候補。実機でのLoad/Save・港・航海・商店の再検証は未完了。K26.2も所有者の実ゲームには未適用。

# K26.2 QEffect 参照名保護（2026-10-19、公開テスト版）

- ゲーム所有者MacのUnityアセットをMonoScript参照と原文品質名から読み取り専用解析。
- `QEffectOnEnter` / `QEffectOnExit` / `QEffectOverTime` の6参照を検出（`Almost Safe` / `Terror` / `Hull`）。
- 対象品質ID 111067 / 102025 / 102029 の日本語`Name`差分を除外。ほかのDescription/イベント/価格/原文ID/セーブは変更なし。
- 差分は28,080→28,077、品質の差分は2,340→2,337。Mac UIルール529は変更なし。
- 読取専用抽出ツールと合成テストを追加。原作アセット・ゲームDLL・セーブの公開配布はしない。
- **同一セーブを用いた原本/日本語版の実機A/Bは未完了**。重大問題の診断途上であり「実機完全修復済み」や安定版とは称しない。

# K26.1 非公式日本語再翻訳パッチ（公開テスト版）

K26.1は、最新の実機確認に合わせて説明と配布記録を更新した版です。

## 今回の更新

- 旧版で発生していた異常な価格表示（9999 / 999999）は、2026年10月17日に現在のMac実機版で解消しているとの確認を受領しました。
- 公開パッチから生成する本文10ファイルとUI 2ファイルが、そのMac実機版と一致することを照合しました。
- 古い「価格表示は未解決」という記載を修正し、Python 3および任意のUI生成に必要な環境を明記しました。
- 翻訳28,080か所、UI 529ルール・552か所、変換プログラムはK26と同一です。

## 導入方法

配布ZIPの `README_ja.md` を参照してください。購入済みのSunless Seaが必要です。導入前にゲームアプリ・既存MOD・セーブのバックアップを用意してください。

ゲーム本体、元のゲームJSON一式、完成済みゲームDLL、フォント、セーブデータは同梱していません。

## 確認範囲

- 価格表示の解消は現在のMac実機版での確認です。全商店・全取引分岐・全ゲーム分岐の検証は継続中です。
- Windows版UI、別のゲームバージョン、Steam以外の版は未確認です。
- 無償の非公式ファン翻訳です。コードのMITライセンスは独自の変換プログラムだけに適用されます。

Sunless Sea / Fallen London は © / ™ Failbetter Games Limited。公式による制作・承認・後援を受けていません。

公式作品: https://www.failbettergames.com/games/sunless-sea
公式ファン作品ガイドライン: https://www.failbettergames.com/fan-project-guidelines

前版K26: https://github.com/seitymoe/sunless-sea-ja-retranslation/releases/tag/v2026.10.17-k26
