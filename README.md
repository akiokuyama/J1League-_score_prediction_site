# Soccer Score App

J1リーグの試合結果・スコア予測に向けたデータ分析、特徴量作成、学習済みモデル読み込みを管理するプロジェクトです。

## アプリ概要

このプロジェクトには、J1の試合結果を確認するためのStreamlitアプリが含まれています。

- これから行われる試合の予測スコアを表示します。
- ホーム勝利、引き分け、アウェイ勝利の勝敗確率を表示します。
- 得点者候補Top 5を表示します。
- 過去予測結果と実際の結果を照合して確認できます。

予測は過去データと機械学習モデルに基づく参考情報であり、実際の試合結果を保証するものではありません。

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

## Streamlitアプリのローカル起動

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

ブラウザで `http://localhost:8501` を開き、これからの試合一覧、試合詳細、過去の予測結果が表示されるか確認します。

## 事前検証コマンド

Week7.5のβ公開準備では、デプロイ前に以下を確認します。

```bash
python -m compileall app src scripts
pytest
python scripts/validate_prediction_outputs.py
python scripts/validate_past_prediction_results.py
```

`outputs/latest_predictions.json` はStreamlit表示用の次節予測、`outputs/all_unplayed_predictions.json` は管理確認用の全未消化試合予測です。

## Streamlit Community Cloudでのβ公開手順

この手順は、正式公開ではなく、自分用確認のためのβ公開環境を作るためのものです。

1. Streamlit Community Cloudにログインします。
2. GitHubアカウントを連携します。
3. `Create app` を選択します。
4. RepositoryにこのプロジェクトのGitHubリポジトリを指定します。
5. Branchに `main` を指定します。
6. Main file path に以下を指定します。

```text
app/streamlit_app.py
```

7. Advanced settingsでPythonバージョンを選べる場合は、GitHub Actionsと合わせて `3.11` を選択します。
8. secretsは現状不要です。今後APIキー等を使う場合のみ、Streamlit Community CloudのAdvanced settingsで設定します。
9. Deployを実行します。
10. 発行されたURLでアプリが起動するか確認します。

β公開後の確認項目:

- アプリが起動する
- `outputs/latest_predictions.json` が読めている
- これからの試合一覧が表示される
- 試合詳細に遷移できる
- 過去予測画面が落ちない
- スマホ表示で大きく崩れない
- GitHub Actions実行後に表示が更新される
- 予測が参考情報であり、確定情報ではないことが画面上で分かる

## 現在のディレクトリ構成

```text
Soccer_Score_App/
├── Data/                  # 学習・推論用CSVとRawデータ
│   ├── ML_dataset.csv
│   ├── processed/
│   ├── features/
│   ├── raw/
│   └── manual/
├── Models/                # 学習済みモデルと特徴量リスト
├── archive/               # 旧分析資産
│   ├── notebooks/
│   └── legacy_rawdata/
├── docs/                  # レポート、指示書アーカイブ、UIモック
│   ├── reports/
│   └── archive/
├── logs/                  # 実行ログ用ディレクトリ
├── outputs/               # 予測結果などの出力先
├── scripts/               # 確認・運用用スクリプト
├── src/                   # 今後アプリ化するための再利用可能コード
│   ├── models/
│   └── predict/
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

GitHub上で予測ファイルを更新する場合は、リポジトリの `Actions` タブを開き、`Manual Prediction Update` を選択して `Run workflow` をクリックします。

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
- 旧Notebookは `archive/notebooks/`、旧RawDataは `archive/legacy_rawdata/` に保存しています。
- 作業指示書は `docs/archive/instructions/`、完了レポートや判断メモは `docs/reports/` に整理しています。
- `.DS_Store`、Pythonキャッシュ、生成ログはGit管理対象外です。
