# Week7 完了レポート

## 概要

Week6で作成した手動実行ワークフローを残したまま、月曜朝の結果評価専用ワークフローと木曜夜の次節予測更新ワークフローを追加しました。

月曜朝は予測ファイルを更新せず、試合結果の取得と過去予測との照合だけを行います。木曜夜は最新データ取得、特徴量更新、次節予測、全未消化試合予測まで実行します。

## 実施内容

- `scripts/update_2026_data.py` に `--scope results` / `--results-only` を追加しました。
- 月曜朝用の `Update Results After Matches` ワークフローを追加しました。
- 木曜夜用の `Update Predictions Scheduled` ワークフローを追加しました。
- 手動実行ワークフローの生成物検証を共通スクリプト利用に寄せました。
- 予測出力と過去予測結果の軽量検証スクリプトを追加しました。
- 定期実行用のテストを追加しました。
- READMEに手動、月曜朝、木曜夜の運用差分を追記しました。

## 作成・更新したファイル

- `.github/workflows/update_results_after_matches.yml`
- `.github/workflows/update_predictions_scheduled.yml`
- `.github/workflows/update_predictions_manual.yml`
- `scripts/update_2026_data.py`
- `scripts/validate_prediction_outputs.py`
- `scripts/validate_past_prediction_results.py`
- `tests/test_scheduled_workflows.py`
- `README.md`
- `docs/week7/week7_completion_report.md`

## 月曜朝ワークフロー

- 目的: 週末試合の結果取得と過去予測結果の更新
- 実行タイミング: 月曜 07:00 JST
- cron: `0 22 * * 0`
- workflow: `Update Results After Matches`

実行コマンド:

```bash
python -m compileall app src scripts
python -m pytest
python scripts/update_2026_data.py --season 2026 --category 100yj1 --scope results
python scripts/build_past_prediction_results.py
python scripts/validate_past_prediction_results.py
```

更新対象:

```text
Data/processed/matches_2026_clean.csv
Data/processed/update_2026_report.json
outputs/past_prediction_results.json
```

更新しない対象:

```text
Data/features/
outputs/latest_predictions.json
outputs/latest_predictions.csv
outputs/all_unplayed_predictions.json
outputs/all_unplayed_predictions.csv
outputs/prediction_history/
outputs/last_updated.txt
outputs/local/
```

月曜処理では、実行前後で `latest_predictions.json`、`all_unplayed_predictions.json`、`prediction_history` の変化がないことを検証します。

## 木曜夜ワークフロー

- 目的: 週末前の特徴量更新と次節予測更新
- 実行タイミング: 木曜 21:00 JST
- cron: `0 12 * * 4`
- workflow: `Update Predictions Scheduled`

実行コマンド:

```bash
python -m compileall app src scripts
python -m pytest
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
python scripts/validate_prediction_outputs.py
python scripts/validate_past_prediction_results.py
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

## --use-cache の扱い

定期実行では原則として最新データ取得を試すため、月曜朝・木曜夜とも `--use-cache` は使いません。

`--use-cache` は手動実行、デバッグ、再現確認、外部サイト障害時の切り分け用途として残します。古いキャッシュだけで最新予測を更新しないよう、READMEにも注意を追記しました。

## 失敗時の安全対策

- 月曜朝は予測生成コマンドを実行しません。
- 月曜朝は予測ファイルと履歴ディレクトリが変更されていないことを検証します。
- 木曜夜と手動実行では `validate_prediction_outputs.py` と `validate_past_prediction_results.py` でJSON構造を検証します。
- 差分がない場合はcommitせず正常終了します。
- `scripts/build_model_metrics.py` と `outputs/local/model_metrics.json` はActionsに含めません。
- ActionsログではGitHub Actionsのロググループを使い、処理モード、対象シーズン、対象カテゴリ、検証結果を見やすくしました。

## テスト結果

- `python -m compileall app src scripts`: 成功
- `pytest`: 22件成功

## ローカル確認結果

月曜朝相当:

```bash
python scripts/update_2026_data.py --season 2026 --category 100yj1 --scope results
python scripts/build_past_prediction_results.py
```

木曜夜相当:

```bash
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
```

生成物検証:

- `python scripts/validate_prediction_outputs.py`: 成功
- `python scripts/validate_past_prediction_results.py`: 成功
- `outputs/latest_predictions.json`: `matches` 9件
- `outputs/all_unplayed_predictions.json`: `matches` 9件
- `outputs/past_prediction_results.json`: `matches` 20件

## 残課題

- GitHub Actions上で初回の月曜・木曜定期実行が成功するか確認します。
- 中長期的には、`Data/` と `data/` のディレクトリ名を統一し、Actions上のシンボリックリンク依存をなくす余地があります。
- 外部サイト取得失敗時のfallback設計は、運用ログを見ながら必要に応じて追加検討します。
