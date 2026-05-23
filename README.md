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

## GitHub Actionsで予測を手動更新する

GitHub上で予測ファイルを更新する場合は、リポジトリの `Actions` タブを開き、`Update Predictions Manual` を選択して `Run workflow` をクリックします。

この手動ワークフローでは、構文チェック、`pytest`、次節予測、全未消化試合予測、過去予測結果JSONの生成を実行します。デバッグ、試合延期対応、スクレイピング修正後の再実行に使います。主に以下のファイルが更新対象です。

```text
Data/processed/
Data/features/
outputs/latest_predictions.json
outputs/latest_predictions.csv
outputs/all_unplayed_predictions.json
outputs/all_unplayed_predictions.csv
outputs/prediction_history/
outputs/past_prediction_results.json
outputs/last_updated.txt
```

`outputs/local/model_metrics.json` はローカル確認専用です。GitHub Actionsでは生成せず、コミット対象にも含めません。

## GitHub Actionsの定期実行

Week7以降は、手動実行に加えて月曜朝と木曜夜の定期実行を分けて運用します。

### 月曜朝: 試合後の結果評価

- ワークフロー名: `Update Results After Matches`
- 実行タイミング: 月曜 07:00 JST
- 目的: 週末試合の結果取得と、過去予測との照合
- 実行コマンド:

```bash
python scripts/update_2026_data.py --season 2026 --category 100yj1 --scope results
python scripts/build_past_prediction_results.py
```

更新対象:

```text
Data/processed/matches_2026_clean.csv
Data/processed/update_2026_report.json
outputs/past_prediction_results.json
```

月曜朝には以下を更新しません。

```text
Data/features/
outputs/latest_predictions.json
outputs/latest_predictions.csv
outputs/all_unplayed_predictions.json
outputs/all_unplayed_predictions.csv
outputs/prediction_history/
```

### 木曜夜: 次節予測更新

- ワークフロー名: `Update Predictions Scheduled`
- 実行タイミング: 木曜 21:00 JST
- 目的: 週末前の特徴量更新と次節予測更新
- 実行コマンド:

```bash
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
```

更新対象:

```text
Data/processed/
Data/features/
outputs/latest_predictions.json
outputs/latest_predictions.csv
outputs/all_unplayed_predictions.json
outputs/all_unplayed_predictions.csv
outputs/prediction_history/
outputs/past_prediction_results.json
outputs/last_updated.txt
```

### `--use-cache` の扱い

定期実行では原則として最新データ取得を試します。`--use-cache` は、デバッグ、再現確認、外部サイト障害時の手動実行向けです。

古いキャッシュを使ったまま最新予測を更新すると、実際の試合日程・結果と出力JSONの整合性が崩れる可能性があります。そのため、定期実行では `--use-cache` を使わない方針です。

## メモ

- `Models/model_features.pkl` を推論時の特徴量スキーマとして扱います。
- `Notebook/` は既存資産として残し、Week2以降の実装は `src/` 配下に切り出して進めます。
- `.DS_Store`、Pythonキャッシュ、生成ログはGit管理対象外です。
