# Sunless Sea 日本語再翻訳MOD — K26.3候補（まだ未公開・要実機検証）

**K26.3で追加保護する内部品質名**: \`Addressed as\`（102969）、\`Memoirs: Quality of Lodgings\`（108290）、\`Memoirs: Your Past\`（108651）。
ゲームの \`NavigationProvider.Dock\` が品質を英語名で検索するため、\`Name\` の原文を保護し、日本語の \`Description\` は維持します。

**重要**: ゲーム内のコードにある \`Addressed As\` と、原文品質名 \`Addressed as\` は大文字・小文字が異なります。原作側でも完全一致しない可能性があり、今回の保護だけで正常動作を保証するものではありません。元のセーブを用いた実機検証が完了するまで正式版にしません。

# Sunless Sea 日本語再翻訳MOD — K26.2 公開テスト版（非公式）（非公式）

**2026年10月19日／無償のファン制作・実機動作検証中**

> Sunless Sea / Fallen London は © / ™ Failbetter Games Limited の作品です。
> 本プロジェクトは **非公式のファン翻訳** であり、Failbetter Gamesの制作・販売・承認を受けていません。
> 公式作品: https://www.failbettergames.com/games/sunless-sea

K26.2ではゲーム内Unityスクリプトが英語品質名で検索する参照の保護を追加しました。従来のK26/K26.1と同様、2026年10月16日にMacへ導入した「表示・内部識別子分離版（K25）」を購入済みゲームへの**差分適用パッチ**として配布します。旧版に含まれた**ゲームの元JSONファイル、ゲームDLLの全体、セーブデータは入っていません**。

**重要な仕様**
- 物語・港・地名・商店など、実際に表示される文章を日本語化。英語原文と異なるテキスト差分は28,080箇所。
- Mac専用UI（任意）：529種類の置換ルールでゲーム内552箇所の表示文字列を日本語化。元の実行ファイルは同梱しません。
- **BUY / SELL、売値・買値、通貨の内部名、所持金、取引・数量・売買ボタンの処理、重要な操作名・ホットキーの識別子は英語原文のまま**にします。
- 一部の船装備スロット等は内部の名前解決に使われるため英語のままです。意図的な例外です。
- 英語ゲーム原本からK25の本文10ファイルを**完全再現**する検査に通過。2026年10月17日には、現在使用中のMac実機版との本文10ファイル・UI 2ファイルの一致も照合しました。
- すべての港・ルート・ゲーム内イベント・取引分岐・ゲームの更新に対応する保証はありません。
- 旧版で発生した異常な価格表示（`9999` / `999999`）は、**2026年10月17日に現在のMac実機版で解消しているとの確認を受領**しました。公開パッチの生成物も、その実機版と一致しています。全商店・全取引分岐のテストは継続中です。

## 必要な環境

- 本文の生成には **Python 3** が必要です。ターミナルで `python3 --version` が実行できることを確認してください。
- 任意のMac UI生成には **Mono（`mono` / `mcs`）とMono.Cecil** が必要です。本文だけを使う場合、Monoは不要です。
- UI手順の `brew install mono` は、Homebrewが導入済みのMacを前提としています。

## 1. 日本語本文を生成する（ゲーム本体は変更しません）

Sunless Seaを合法的に所有し、ゲームを一度起動して英語のJSONデータが生成されている必要があります。

1. このZIPを解凍します。
2. ターミナルで解凍先に移動します。
3. Mac版の場合、次を実行してください（`<解凍先>` は実際の場所に置換）。

```bash
cd "<解凍先>"
python3 apply_text_patch.py \
  --game-data "$HOME/Library/Application Support/com.failbettergames.sunlesssea" \
  --output "$HOME/Downloads/SunlessSea_JA_K26_2_build"
```

`~/Downloads/SunlessSea_JA_K26_2_build/japanese_translation/` が生成されます。この工程では、ゲーム・元のMOD・セーブファイルを変更しません。

元のJSONのSHA256が一致しない場合、**インストール済みのゲームが対象バージョンではありません**。エラーを無視して強制適用しないでください。

## 2. 日本語本文をインストールする

**必ずゲームを完全終了**してください。Steam Cloudが同期中の場合は完了を待ち、現在のセーブを上書きさせないでください。

`~/Library/Application Support/com.failbettergames.sunlesssea/` 内の `saves/` と `addon/japanese_translation/` を、それぞれゲームフォルダー外へ完全バックアップしてください。現在の日本語MODがある場合はフォルダを置き換え、複数の翻訳MODが同時に読み込まれないようにします。

生成された `japanese_translation` フォルダを `~/Library/Application Support/com.failbettergames.sunlesssea/addon/` にコピーします。

**既存MOD・セーブを削除しないこと。** 不具合時はゲームを終了し、インストールしたフォルダを退避したうえで旧MODフォルダを復元してください。

## 3. Mac版UIも日本語にする（任意・上級者向け）

**すでに日本語化済みのDLLに重ねてパッチを適用しないでください。** ゲームの元のDLLを使います。標準のUIだけで遊ぶならこの工程は不要です。

```bash
brew install mono

python3 build_ui_patch.py \
  --managed "$HOME/Library/Application Support/Steam/steamapps/common/SunlessSea/Sunless Sea.app/Contents/Resources/Data/Managed" \
  --output "$HOME/Downloads/SunlessSea_JA_K26_2_UI_stage"
```

このコマンドはゲームアプリとは**別の場所**に検証済みDLL候補を生成します。実行中のゲームは一切変更しません。元のSteam版とDLLのSHA256が違えば、破損やバージョン不一致を防ぐため処理を拒否します。

実際にDLLを導入する場合は、**Sunless Seaアプリ全体**とユーザーデータ全体をバックアップし、ゲームを終了してから同名の2 DLLのみを `Contents/Resources/Data/Managed/` にコピーした後、macOS版では必要に応じて、所有するアプリについて次のようにアドホック署名を再検証してください。

```bash
codesign --force --sign - --timestamp=none "<Sunless Sea.appの正しい絶対パス>"
codesign --verify --deep --strict "<Sunless Sea.appの正しい絶対パス>"
```

もし失敗したら**アプリ全体**と元のMODをバックアップから戻してください。ファイルの署名を破壊しないよう、ゲームに直接当てる自動パッチは配布していません。

Windows版のUI DLLパッチ、別のゲームバージョン、Steam以外の配布版、Mac以外での動作は未確認です。

## 4. 内容・復元手順

- `delta/**.json` : 日本語の文字列差分のみ。原作の英語ストーリーやJSON構造全体は含みません。
- `manifest.json` : ゲーム原本/再生成先の照合ハッシュ。
- `apply_text_patch.py` : 英語原本に文字列差分を適用するスクリプト。
- `ui/ui_rules.json` : UI置換のためのルールと日本語文。
- `ui/SunlessUiILPatcher.cs` / `build_ui_patch.py` : 所有ゲームの元DLLから修正版をビルドするソース。
- `CHECKSUMS.json` : 配布ファイル各自のSHA256。
- `RELEASE_STATUS.json` : 現在のMac実機版との照合結果と、価格表示について確認できた範囲。
- `CHANGELOG.md` : 配布版の変更履歴。

問題があれば、ゲームを終了し、旧MOD・Steamゲームアプリ全体をバックアップから戻します。**セーブデータは原則として復元しません**（プレイ進行を上書きしないため）。セーブが破損した場合だけ、実際の状態とバックアップを比較してから手動復元してください。

## 5. 著作権と利用

- 本作の原作世界観、物語、ゲーム内設定、原作テキストその他の既存資産に関する権利は**Failbetter Games Limited**に帰属します。
- このファンパッチは無償です。開発元とは無関係であり、ゲーム本体を購入する必要があります。
- この配布物に含まれる独自の変換プログラムのコードについてのみ `LICENSE-CODE.txt`（MIT）を適用します。原作、翻訳された原作テキスト、第三者の資産の権利を許諾するものではありません。
- 元のゲームJSON、フルゲームDLL、画像や音源を含めた再配布は禁止です。
- ファン制作に関する説明: https://www.failbettergames.com/fan-project-guidelines

実プレイで誤訳や日本語の不自然さを見つけた場合は、港・イベント名・再現手順・スクリーンショットを添えて報告してください。

## K26.2 — Unity QEffect の参照名保護（2026-10-19）

所有者MacのUnity `globalgamemanagers.assets` と `resources.assets` を読み取り専用で照合し、`QEffectOnEnter`／`QEffectOnExit`／`QEffectOverTime` が次の英語品質名を内部的に参照することを確認しました。

- 品質ID **111067**: `Almost Safe`（安全海域）
- 品質ID **102025**: `Terror`（恐怖）
- 品質ID **102029**: `Hull`（船体）

日本語差分から、これら3件の **`Name` の翻訳だけ** を取り除いて英語原文の内部参照名を維持します。`Description` などの日本語説明、原文のID／金額／所持品／取引処理には触れません。

**この診断は静的証拠です。** 元DLL・新MODによる同一セーブでの比較・再発防止の実機確認は未完了のため、原因と修復を断定せず、引き続きテスト版として扱います。MacのSteamゲームが起動中の間、ゲーム本体・セーブ・既存MODを変更してはいけません。Windows版のUIパッチも未検証です。

前のK26.1に代わり、この [K26.2公開テスト版](https://github.com/seitymoe/sunless-sea-ja-retranslation/releases/tag/v2026.10.19-k26.2) を配布します。ただしゲーム内の全経路・全商店の実機確認は未完了です。
