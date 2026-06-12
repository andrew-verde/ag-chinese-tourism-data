# 福井県観光ロケーション・トレンドレポート

福井県内のオンラインマップやWeb検索のインプレッション回数を集計し、観光ロケーションのトレンドを可視化するインタラクティブなWebアプリケーションです。

**[アプリを開く](https://code4fukui.github.io/fukui-kanko-trend-report/)**

## 概要

本アプリケーションは、福井県内の観光ロケーションにおけるオンラインマップおよびWeb検索ツールのインプレッションデータを集計し、インタラクティブなチャートで可視化します。地域ごとの人気やトレンドを把握するために活用できます。

## 主な機能

- **地域別・全体集計**: 福井県全体、または特定地域のデータを表示
- **時系列分析**: 日次・週次・月次の粒度で分析
- **2期間比較**: 異なる期間のトレンドを並べて比較
- **多様な指標**: 地図検索、Web検索、ルート検索、通話、ウェブサイトクリック、レビュー投稿数、星別レビュー数、平均評点
- **CSVエクスポート**: 表示中のデータをCSV形式でダウンロード

## 対象地域

福井県内の以下13地域のデータを収集しています：

- あわら市
- 池田町
- おおい町
- 永平寺町
- 越前市
- 勝山市
- 南越前町
- 高浜町
- 敦賀市
- 若狭町
- 小浜市
- 美浜町
- 大野市

## 使い方

1. **エリア選択**: 「全域」または特定の地域を選択
2. **時間単位選択**: 日別・週別・月別から表示単位を選択
3. **期間選択**: カレンダーから分析したい期間を選択
4. **2期間比較**: チェックボックスをONにして比較期間を設定
5. **データ確認**: 「回数推移」と「レビュー推移」を確認
6. **CSVダウンロード**: 必要に応じてCSV形式でエクスポート

## データ形式

### CSVファイル構造

各CSVファイルには以下のカラムが含まれます：

| カラム名 | 説明 |
| --- | --- |
| `日付` | 日付（YYYY-MM-DD） |
| `地図検索` | 地図検索回数 |
| `Web検索` | Web検索回数 |
| `ルート検索` | ルート検索回数 |
| `通話` | 通話ボタンクリック数 |
| `ウェブサイトクリック` | ウェブサイトクリック数 |
| `レビュー投稿数` | レビュー投稿数 |
| `星5_レビュー数` | 星5のレビュー数 |
| `星4_レビュー数` | 星4のレビュー数 |
| `星3_レビュー数` | 星3のレビュー数 |
| `星2_レビュー数` | 星2のレビュー数 |
| `星1_レビュー数` | 星1のレビュー数 |
| `平均評点` | 平均評点 |

## 技術スタック

- **フロントエンド**: React 19 + TypeScript
- **ビルドツール**: Vite
- **スタイリング**: Tailwind CSS + shadcn/ui
- **チャート**: Recharts
- **状態管理**: React Context API
- **データ処理**: PapaParse (CSV), Tidy.js
- **日付ユーティリティ**: date-fns, dayjs, react-day-picker
- **パッケージ管理**: pnpm

## 開発

### クイックセットアップ

以下のコマンドをコピーして実行すると、開発サーバーを起動できます。

```bash
# リポジトリをクローン
git clone https://github.com/code4fukui/fukui-kanko-trend-report.git
cd fukui-kanko-trend-report

# Node.js 20.19+ または 22.12+ を用意
# (nvmを使う場合はどちらかを選択)
# nvm install 22.12.0
# nvm use 22.12.0
# --- or ---
# nvm install 20.19.0
# nvm use 20.19.0
# node -v

# pnpm を Corepack で有効化（package.json の packageManager: pnpm@10.11.0 に合わせる）
corepack enable
corepack prepare pnpm@10.11.0 --activate

# サブモジュールを初期化し依存関係をインストール
git submodule update --init --recursive
pnpm install

# 開発サーバーを起動
pnpm dev
```

ブラウザで `http://localhost:5173` にアクセスしてください。

### サブモジュールの更新（最新データ取得）

```bash
git submodule update --remote --recursive
```

### 本番ビルド

```bash
pnpm build
```

生成物は `dist/` に出力されます。

### 本番ビルドのプレビュー

```bash
pnpm preview
```

### Lint

```bash
pnpm lint
```

## プロジェクト構造

```
fukui-kanko-trend-report/
├── public/
│   └── data/                        # CSVデータ（サブモジュール）
├── index.html                       # HTMLエントリーポイント
├── src/
│   ├── components/
│   │   ├── parts/                   # アプリ固有コンポーネント
│   │   │   ├── date-range-picker/   # 期間選択
│   │   │   ├── graph/               # グラフ表示
│   │   │   ├── selector/            # エリア・時間単位選択
│   │   │   ├── download-csv-button.tsx
│   │   │   ├── external-navigation.tsx
│   │   │   └── header.tsx
│   │   └── ui/                      # shadcn/ui コンポーネント
│   ├── context/
│   │   └── ChartSettingsContext.tsx # グローバル状態管理
│   ├── lib/
│   │   └── utils.ts                 # ユーティリティ関数
│   ├── types/
│   │   └── types.ts                 # TypeScript 型定義
│   ├── utils/
│   │   └── csv-export.ts            # CSV出力
│   ├── App.tsx                      # メインアプリケーション
│   ├── main.tsx                     # エントリーポイント
│   └── index.css                    # グローバルスタイル
├── tools/
│   ├── upload.sh                    # デプロイスクリプト
│   └── utils.sh                     # 補助スクリプト
├── .github/
│   ├── copilot-instructions.md
│   ├── pull_request_template.md
│   └── workflows/
│       ├── pages.yml                # GitHub Pages デプロイ
│       └── submodule.yml            # データ自動更新
├── components.json
├── tsconfig.json
├── vite.config.ts
├── eslint.config.js
└── package.json
```

## 設定

### コンポーネントライブラリ

本プロジェクトは [shadcn/ui](https://ui.shadcn.com/) を利用しています。設定は `components.json` を参照してください。

### TypeScript

厳格なTypeScript設定を採用しています。詳細は `tsconfig.json` を参照してください。

### スタイリング

Tailwind CSS v4 を使用しています。グローバルスタイルは `index.css` にあります。

## デプロイ

main ブランチへの変更は GitHub Pages に自動デプロイされます。設定は `.github/workflows/pages.yml` を参照してください。

### データ更新

データは GitHub Actions により自動更新されます。スケジュールは `.github/workflows/submodule.yml` で管理されています。

## スクリプト

| コマンド | 説明 |
| --- | --- |
| `pnpm dev` | 開発サーバーを起動 |
| `pnpm build` | 本番ビルド |
| `pnpm preview` | 本番ビルドのプレビュー |
| `pnpm lint` | ESLint 実行 |
| `pnpm upload` | AWS S3/CloudFront へアップロード（`tools/upload.sh` 経由、ステージ名 `-n` 指定 & AWS 設定が必要） |

## コントリビューション

貢献は歓迎です。PR を送る前に [pull request template](.github/pull_request_template.md) を参照し、既存のコーディング規約に従ってください。

## トラブルシューティング

### ポートが使用中の場合

5173番ポートが使用中の場合、Vite が自動的に別ポートを使用します。ターミナルに表示されるURLを確認してください。

### Node.js のバージョンが古い場合

Vite は Node.js 20.19+ または 22.12+ が必要です。エラーが出た場合は更新してください。nvm の例:

```bash
nvm install 22.12.0
nvm use 22.12.0
node -v
```

### データが表示されない場合

サブモジュールが初期化されているか確認してください。

```bash
git submodule update --init --recursive
```

### ビルドエラーが出る場合

1. キャッシュを削除: `rm -rf node_modules pnpm-lock.yaml`
2. 依存関係を再インストール: `pnpm install`
3. ビルド再実行: `pnpm build`

## ライセンス

本プロジェクトは MIT ライセンスです。詳細は [LICENSE](LICENSE) を参照してください。

## About

本プロジェクトは、地域課題をオープンソースで解決する civic tech 組織 [Code for FUKUI](https://github.com/code4fukui) によって運用されています。

---

**Last Updated**: February 2026  
**Version**: 0.0.0
