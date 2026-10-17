# Sunless Sea 日本語再翻訳MOD — K26 差分配布版（非公式）

**2026年10月17日／無償のファン制作・実機動作検証中**

> Sunless Sea / Fallen London は © / ™ Failbetter Games Limited の作品です。
> 本プロジェクトは **非公式のファン翻訳** であり、Failbetter Gamesの制作・販売・承認を受けていません。
> 公式作品: https://www.failbettergames.com/games/sunless-sea

K26は、2026年10月16日にMacで動作確認を始めた「表示・内部識別子分離版（K25）」と**同一の翻訳内容**を、購入済みゲームへの**差分適用パッチ**として配布したものです。旧版に含まれた**ゲームの元JSONファイル、ゲームDLLの全体、セーブデータは入っていません**。

**重要な仕様**
- 物語・港・地名・商店など、実際に表示される文章を日本語化。英語原文と異なるテキスト差分は28,080箇所。
- Mac専用UI（任意）：529種類の置換ルールでゲーム内552箇所の表示文字列を日本語化。元の実行ファイルは同梱しません。
- **BUY / SELL、売値・買値、通貨の内部名、所持金、取引・数量・売買ボタンの処理、重要な操作名・ホットキーの識別子は英語原文のまま**にします。
- 一部の船装備スロット等は内部の名前解決に使われるため英語のままです。意図的な例外です。
- 2026年10月16日に当該Macで、英語ゲーム原本の入力からK25の10ファイルを**完全再現**する検査に通過。
- すべての港・ルート・ゲーム内イベント・取引分岐・ゲームの更新に対応する保証はありません。
- 商店で「£999999」と表示される問題は数値データ上書きではなく、**現在も原因調査中**です。価格・売買ロジックは変更していません。

## 1. 日本語本文を生成する（ゲーム本体は変更しません）

Sunless Seaを合法的に所有し、ゲームを一度起動して英語のJSONデータが生成されている必要があります。

1. このZIPを解凍します。
2. ターミナルで解凍先に移動します。
3. Mac版の場合、次を実行してください（`<解凍先>` は実際の場所に置換）。

```bash
cd "<解凍先>"
python3 apply_text_patch.py \
  --game-data "$HOME/Library/Application Support/com.failbettergames.sunlesssea" \
  --output "$HOME/Downloads/SunlessSea_JA_K26_build"
```

`~/Downloads/SunlessSea_JA_K26_build/japanese_translation/` が生成されます。この工程では、ゲーム・元のMOD・セーブファイルを変更しません。

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
  --output "$HOME/Downloads/SunlessSea_JA_K26_UI_stage"
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

問題があれば、ゲームを終了し、旧MOD・Steamゲームアプリ全体をバックアップから戻します。**セーブデータは原則として復元しません**（プレイ進行を上書きしないため）。セーブが破損した場合だけ、実際の状態とバックアップを比較してから手動復元してください。

## 5. 著作権と利用

- 本作の原作世界観、物語、ゲーム内設定、原作テキストその他の既存資産に関する権利は**Failbetter Games Limited**に帰属します。
- このファンパッチは無償です。開発元とは無関係であり、ゲーム本体を購入する必要があります。
- この配布物に含まれる独自の変換プログラムのコードについてのみ `LICENSE-CODE.txt`（MIT）を適用します。原作、翻訳された原作テキスト、第三者の資産の権利を許諾するものではありません。
- 元のゲームJSON、フルゲームDLL、画像や音源を含めた再配布は禁止です。
- ファン制作に関する説明: https://www.failbettergames.com/fan-project-guidelines

実プレイで誤訳や日本語の不自然さを見つけた場合は、港・イベント名・再現手順・スクリーンショットを添えて報告してください。
