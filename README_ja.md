# Sunless Sea 日本語再翻訳MOD — K26.3 RC3 導入・復元ガイド

**K26.3 RC3は公開プレリリース（試験用）です。正式安定版ではありません。** 現行の未解決[P0取引・ロード #1](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/1)と[P0 QEffect例外 #2](https://github.com/seitymoe/sunless-sea-ja-retranslation/issues/2)を確認してから利用してください。既公開のK26.2から更新する場合も、まず全バックアップを作成してください。

## 1. 何を日本語化するか

- 対象：原文から**28,073文字列フィールド**を置換する差分。対象は`entities/events.json`など**10個のJSON**。全プレイヤー向け項目数と変更フィールド数は異なります。無理に内部キーやデバッグ項目まで訳しません。
- 保護対象：ゲームが英語名で探す`Quality.Name`の**7件**。通常プレイのUnity QEffectで使われる `Almost Safe` (111067)、`Terror` (102025)、`Hull` (102029) と、**EditorMode=true の時だけ**`NavigationProvider.Dock`が参照する `Memoirs: Your Past` (108651)、`Memoirs: Quality of Lodgings` (108290)、`Addressed as` (102969)、`a stranger` (231) を保持します。後の4件を通常プレイのエラー修復と誤認しないでください。
- 任意のMac向けUI日本語化：**529ルールで552か所**。ゲームの一部ボタン・説明・航海UI等。内部識別子を兼ねる`Stack Item`、`BUY / SELL`、通貨・価格・所持金、装備スロット、Prefab、ホットキー名は英語原文を保持します。すべてのUIが日本語になるわけではありません。
- **現行RC3の実機確認（2026-10-19）**：所有者Macで既存AutosaveをContinueからロードし、ロンドン・キャロウ店の魚雷部品をBUY £5 / SELL £1で操作。所持金は£2171→£2166→£2167、商品数量は0→1→0と即時更新し、今回のセッションではNullReferenceException 0件。セーブ2本のSHAは前後一致しました。**これは1店舗・1商品のスモークテストに限られます。ほかの商店・海域・原本との同一セーブA/Bは未検証です。**


### 現行RC3の実機確認と未検証範囲（2026-10-19）

所有者MacのSunless Sea v3.0.0.31で、以前のAutosaveから「続ける」→入域・ロンドンの商店表示を確認しました。キャロウの魚雷部品のBUY £5、SELL £1を実際に行い、所持金£2171→£2166→£2167、数量0→1→0が各操作の約0.5秒後に表示されました。今回のPlayer.logではNullReferenceException 0件、セーブ2本のSHAは変更されていません。£999999もこの品には表示されませんでした。

**これは1セーブ・1店舗・1品目だけのスモークテストです。** 全店舗・全分岐・他のQEffect・元の英語ゲームとの同一セーブA/B・全文の文学的独立校正は未検証です。BUY / SELL、通貨・価格・入力識別子は意図的に英語のままです。無検証のOSやゲーム版への適用は禁止です。

## 2. 環境と事前バックアップ

- 購入済みのSunless Seaが必要です。検証対象は**Steam macOS版 v3.0.0.31**です。ゲームの原文JSONのSHAが一致しなければ、安全のため生成を拒否します。強制適用は禁止。
- 本文差分を組み立てるには `python3` が必要です。
- Mac UIも生成する場合に限り、`mono`、`mcs`、Mono.Cecilが必要です。Homebrew導入済みなら `brew install mono` で用意できます。
- 事前に**Sunless Sea.app全体**、既存の`addon/japanese_translation/`、**saves/全体**、設定ファイルを別フォルダへバックアップし、SHA256と元の場所を記録してください。Steam Cloud同期中なら完了を待ち、他の日本語化MODと二重配置しないでください。
- ゲームを完全終了し、`pgrep -x 'Sunless Sea'` で実プロセスが残っていないことを確認します。

## 3. 自分で所有する原文から日本語MODを生成する

RC3の配布ZIPを解凍し、そのフォルダでターミナルを開いて次を実行します。例は標準的なMac版です。

```bash
python3 apply_text_patch.py \
  --game-data "$HOME/Library/Application Support/com.failbettergames.sunlesssea" \
  --output "$HOME/Downloads/SunlessSea_JA_K26_3_RC3_stage"
```

生成先は`~/Downloads/SunlessSea_JA_K26_3_RC3_stage/japanese_translation/`です。**この生成コマンドは実際のゲーム・現在のMOD・セーブを変更しません。** 検証が通ったことを確かめてから、ゲームを終了した状態で生成先の `japanese_translation/` を`~/Library/Application Support/com.failbettergames.sunlesssea/addon/` へ切り替えてください。古いフォルダは別ディレクトリに保管しておきます。

## 4. 任意：Mac UIの一部も日本語化する

**ゲーム本体のDLLを書き換えるため、上級者のみ。** 本文翻訳だけなら不要です。アプリが起動していないこと、バックアップのSHAが検証できることを確認してから、配布ZIPを解凍したフォルダで次を実行します。

```bash
python3 build_ui_patch.py \
  --managed "$HOME/Library/Application Support/Steam/steamapps/common/SunlessSea/Sunless Sea.app/Contents/Resources/Data/Managed" \
  --output "$HOME/Downloads/SunlessSea_JA_K26_3_RC3_UI_stage"
```

この操作はゲームアプリの**外にDLL候補を生成**します。既に日本語化したDLLを入力に使わないでください。SHA不一致や対象バージョン違いなら強制適用しません。生成された2個のDLLを実ゲームに入れる場合、Sunless Sea.app全体を保存してから対応場所へ配置し、macOSで署名を再確認します。

```bash
codesign --force --sign - --timestamp=none "$HOME/Library/Application Support/Steam/steamapps/common/SunlessSea/Sunless Sea.app"
codesign --verify --deep --strict "$HOME/Library/Application Support/Steam/steamapps/common/SunlessSea/Sunless Sea.app"
```

署名・起動に失敗したら、元のアプリ全体とMODをバックアップから戻してください。**元ゲームのDLL・原文JSON・画像・セーブのバイナリを再配布していません。**

## 5. プレイテストと復元

安全なセーブのコピーを使い、Continue/Load/Save、航海、港、士官、船倉、装備、戦闘を確認してください。商店では購入/売却前後のエコーと個数が即時一致することを確認します。原文上、ロンドンのCarrowの魚雷部品はBUY £5 / SELL £1です。`£999999`、表示更新遅延、二重売買、`NullReferenceException` があれば購入を繰り返さず、画面・ログ・時刻を記録します。

不具合時はゲームを終了し、試験中のMODやDLLを退避して、バックアップしたゲームアプリ全体と古いMODを復元します。**セーブは無断でバックアップに戻さないこと**（その後のプレイ進行を上書きするため）。セーブ破損時のみ現在版とバックアップのSHAを照合したうえで復元してください。

## 6. 確認範囲と権利

確認済み：静的なID/数値/文字列マクロ、10/10日本語JSONの再構築、ZIP SHA/CRC、30件のユニット/回帰テスト、CI。

未完了：同一セーブでのRC3対原本のA/B、全商店取引、入港/航海のQEffect例外切り分け、全分岐校正、Windows向けUIと別ゲームバージョン。**RC3を実機完全検証済み・正常性保証付きとは表示しません。**

Sunless Sea / Fallen Londonは © / ™ Failbetter Games Limited。これは同社と無関係の**非公式・無償ファン翻訳**です。ゲームは適法に購入してください。独自プログラムに限りMITライセンスで、ゲーム本体や原作テキストの権利は取得しません。

[公式作品](https://www.failbettergames.com/games/sunless-sea) · [公式ファン制作ガイドライン](https://www.failbettergames.com/fan-project-guidelines)
