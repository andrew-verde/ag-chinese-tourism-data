# 開発者向けドキュメント

このドキュメントでは、プロジェクトの実行手順、データ変換の詳細、データの自動ダウンロード、出力ファイルについて説明します。

## 処理フロー

`merge_survey.py`を実行すると、以下の順序で処理が実行されます：

1. **データの自動ダウンロード**
   - 富山県: Box.comから最新データをダウンロード
   - 石川県: Googleスプレッドシートから最新データをダウンロード
   - 福井県: GitHubリポジトリから2023年以降のCSVファイルをダウンロードしてマージ

2. **出力ディレクトリのクリーンアップ**
   - `output/toyama/`、`output/ishikawa/`、`output/fukui/`内の古いファイルを削除

3. **データ変換**
   - 各県の変換スクリプトを順に実行
   - 統一された形式に変換

4. **CSVファイルのマージ**
   - 変換後のCSVファイルを1つのファイルに統合

5. **年毎のファイル分割**
   - `merged_survey.csv`を年毎に分割（`merged_survey_2023.csv`など）
   - 各変換後CSVファイルも年毎に分割（`toyama_converted_2023.csv`など）
   - サイズが大きいファイルをGitHubにpushしないための対策

## 実行手順

### 1. 環境準備

#### Pythonのインストール確認

まず、Pythonがインストールされているか確認してください：

```bash
python --version
# または
python3 --version
```

バージョン3.6以上が表示されれば、Pythonは既にインストールされています。

#### MacでのPythonインストール

**方法1: Homebrewを使用（推奨）**

1. Homebrewをインストール（未インストールの場合）：
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Pythonをインストール：
```bash
brew install python
```

**方法2: 公式インストーラーを使用**

1. [Python公式サイト](https://www.python.org/downloads/)から最新版をダウンロード
2. ダウンロードした`.pkg`ファイルをダブルクリックしてインストール
3. インストール時に「Add Python to PATH」にチェックを入れる

#### WindowsでのPythonインストール

**方法1: Microsoft Storeを使用（推奨）**

1. Microsoft Storeを開く
2. 検索で「Python」を検索
3. 最新版（Python 3.11など）をインストール

**方法2: 公式インストーラーを使用**

1. [Python公式サイト](https://www.python.org/downloads/)から最新版をダウンロード
2. ダウンロードした`.exe`ファイルを実行
3. インストール時に「Add Python to PATH」にチェックを入れる
4. 「Install Now」をクリック

#### インストール確認

インストール後、以下のコマンドで確認してください：

```bash
# Pythonのバージョン確認
python --version
# または
python3 --version

# pip（パッケージマネージャー）の確認
pip --version
# または
pip3 --version
```

正常にバージョンが表示されれば、インストールは成功です。

### 2. 実行

ターミナルから、以下のコマンドでデータダウンロード、変換、マージを一括実行します：

```bash
python merge_survey.py
```

このコマンドを実行すると、以下の処理が自動的に実行されます：

1. 最新データの自動ダウンロード
2. 出力ディレクトリのクリーンアップ（古いファイルの削除）
3. 各県のデータ変換
4. CSVファイルのマージ
5. 年毎のファイル分割

ZIPファイルでダウンロードした場合は、そのZIPを解凍したディレクトリへ移動し実行します

例）ZIPを解凍したディレクトリが、/Users/自身のユーザ名/Desktop/merged_survey_csv_py-mainの場合

```bash
# ディレクトリ移動
cd /Users/自身のユーザ名/Desktop/merged_survey_csv_py-main
# マージ一括実行
python merge_survey.py
```

### 3. 個別実行

各県のデータを個別に変換したい場合は、以下のコマンドを使用できます：

```bash
# 富山県データの変換
python convert_toyama.py

# 石川県データの変換
python convert_ishikawa.py

# 福井県データの変換
python convert_fukui.py
```

### 入力データを入れ替えたい時の配置

通常は`merge_survey.py`を実行すると最新データが自動的にダウンロードされますが、手動でデータを入れ替えたい場合や列マッピングを変更したい場合は、以下のようにファイルを配置してください：

- `input/toyama/toyama.csv` - 富山県のアンケートデータ（自動ダウンロードされるが、手動で置き換え可能）
- `input/toyama/column_mapping_toyama.json` - 富山県の列マッピング定義
- `input/ishikawa/ishikawa.csv` - 石川県のアンケートデータ（自動ダウンロードされるが、手動で置き換え可能）
- `input/ishikawa/column_mapping_ishikawa.json` - 石川県の列マッピング定義
- `input/fukui/fukui.csv` - 福井県のアンケートデータ（自動生成されるが、手動で置き換え可能）
- `input/fukui/fukui_2023.csv` - 福井県2023年データ（自動ダウンロード）
- `input/fukui/fukui_2024.csv` - 福井県2024年データ（自動ダウンロード）
- `input/fukui/column_mapping_fukui.json` - 福井県の列マッピング定義

**注意**: `merge_survey.py`を実行すると、既存のデータが最新データで上書きされます。手動で配置したデータを保持したい場合は、実行前にバックアップを取ってください。

## データ変換の詳細

### 共通処理

- **対象県の設定**: 各県のデータに「対象県（富山/石川/福井）」列を追加し、該当する県名を設定
- **BOM除去**: 入力CSVファイルのBOM（Byte Order Mark）を自動除去
- **日付形式統一**: 「アンケート回答日」を `yyyy/MM/dd hh:mm:ss` 形式に統一

### 県別処理

#### 富山県（convert_toyama.py）

- **情報源連結**: 「情報源（デジタル）」と「情報源（デジタル以外）」を連結
- **情報源フラグ生成**: 25種類の情報源フラグを自動生成

#### 石川県（convert_ishikawa.py）

- **改行コード正規化**: LFと単独CRを削除し、CRLFを保持
- **情報源フラグ生成**: 「今回   当施設   を訪れる際に参考にした情報源は何ですか？（複数選択可）」からフラグ生成

#### 福井県（convert_fukui.py）

- **会員ID匿名化**: 6桁数字の会員IDを「000000」に置換
- **改行コード処理**: LFを削除し、レコード区切りとしてCRLFを挿入
- **情報源フラグ生成**: 「情報収集ALL」からフラグ生成

### 情報源フラグ

以下の25種類のフラグが自動生成されます：

- Facebook, Google, Googleマップ, Instagram, TikTok
- X（旧Twitter）, YouTube, SNS広告, ブログ, まとめサイト
- インターネット・アプリ, デジタルニュース, 宿泊予約Webサイト, 宿泊施設
- TV・ラジオ番組やCM, ラブライブのスタンプラリー, 新聞・雑誌・ガイドブック
- 旅行会社, 友人・知人, 地元の人, 観光パンフレット・ポスター
- 観光案内所, 観光展・物産展, 観光連盟やDMOのHP, その他

各フラグは、対応するキーワードが情報源に含まれている場合は1、含まれていない場合は0が設定されます。

## データの自動ダウンロード

`merge_survey.py`を実行すると、最新のデータが自動的にダウンロードされます。

### ダウンロード元

- **富山県**: Box.comの共有ファイルからダウンロード
- **石川県**: GoogleスプレッドシートからCSV形式でエクスポート
- **福井県**: GitHubリポジトリ（code4fukui/fukui-kanko-survey）から2023年以降のCSVファイルを取得してマージ

### 福井県データの保存形式

福井県のデータは、年毎のファイルとして`input/fukui/`ディレクトリに保存されます：

- `fukui_2023.csv` - 2023年データ
- `fukui_2024.csv` - 2024年データ
- （他の年も同様）

これらのファイルは、`fukui.csv`（全データをマージしたファイル）とは別に保存されます。

### 手動ダウンロード

データを手動でダウンロードしたい場合は、`download_data.py`を実行できます：

```bash
# すべてのデータをダウンロード
python download_data.py

# 特定の県のデータのみダウンロード
python download_data.py --toyama
python download_data.py --ishikawa
python download_data.py --fukui
```

## 出力ファイル

### 変換後ファイル

各県の変換後CSVファイルは、処理の最後に年毎に分割されます。

- `output/toyama/toyama_converted.csv` - 全データ（GitHubにpushしない）
- `output/toyama/toyama_converted_2023.csv` - 2023年データ
- `output/toyama/toyama_converted_2024.csv` - 2024年データ
- `output/toyama/toyama_converted_2025.csv` - 2025年データ
- （他の年も同様）

- `output/ishikawa/ishikawa_converted.csv` - 全データ（GitHubにpushしない）
- `output/ishikawa/ishikawa_converted_2023.csv` - 2023年データ
- `output/ishikawa/ishikawa_converted_2024.csv` - 2024年データ
- （他の年も同様）

- `output/fukui/fukui_converted.csv` - 全データ（GitHubにpushしない）
- `output/fukui/fukui_converted_2023.csv` - 2023年データ
- `output/fukui/fukui_converted_2024.csv` - 2024年データ
- （他の年も同様）

### マージ後ファイル

マージ後のCSVファイルも、処理の最後に年毎に分割されます。

- `output_merge/merged_survey.csv` - 全県のデータを統合した最終ファイル（GitHubにpushしない）
- `output_merge/merged_survey_2023.csv` - 2023年データ
- `output_merge/merged_survey_2024.csv` - 2024年データ
- `output_merge/merged_survey_2025.csv` - 2025年データ
- （他の年も同様）

### ファイルサイズ制限への対応

GitHubでは50MBを超えるファイルをpushする際に警告が表示されます。このプロジェクトでは以下の対策を実施しています：

- 元のマージファイル（`merged_survey.csv`、`fukui.csv`など）は`.gitignore`に追加し、GitHubにpushしない
- 年毎に分割されたファイルのみをGitHubにpushする
- 各分割ファイルにはCSVヘッダーが含まれるため、個別に使用可能
