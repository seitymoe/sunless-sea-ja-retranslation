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
