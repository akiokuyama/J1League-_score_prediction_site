# Soccer Score App

J1リーグの試合結果・スコア予測に向けたデータ分析、特徴量作成、学習済みモデル読み込みを管理するプロジェクトです。

## セットアップ

このプロジェクトは `uv` で管理しています。

```bash
cd /Users/akihirookuyama/Soccer_Score_App
uv venv .venv
source .venv/bin/activate
uv sync
```

`requirements.txt` を使う場合:

```bash
pip install -r requirements.txt
```

## 現在のディレクトリ構成

```text
Soccer_Score_App/
├── Data/                  # 学習・推論用CSVとRawデータ
│   ├── ML_dataset.csv
│   └── RawData/
├── Models/                # 学習済みモデルと特徴量リスト
├── Notebook/              # 既存の分析・学習Notebook
├── docs/                  # 指示書、棚卸し、完了レポート
├── logs/                  # 実行ログ用ディレクトリ
├── outputs/               # 予測結果などの出力先
├── scripts/               # 確認・運用用スクリプト
├── src/                   # 今後アプリ化するための再利用可能コード
│   ├── models/
│   └── predict/
├── 資料/                  # 既存の日本語メモ・設計資料
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

## Week1確認コマンド

```bash
python -m compileall src scripts
python scripts/smoke_test_load_models.py
```

## メモ

- `Models/model_features.pkl` を推論時の特徴量スキーマとして扱います。
- `Notebook/` は既存資産として残し、Week2以降の実装は `src/` 配下に切り出して進めます。
- `.DS_Store`、Pythonキャッシュ、生成ログはGit管理対象外です。
