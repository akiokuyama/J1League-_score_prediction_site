# Week5 完了レポート

## 概要

Week5では、得点者候補ロジック、過去予測結果JSON、簡易モデル評価指標を整備しました。既存のStreamlit表示と予測JSONスキーマを壊さないようにしつつ、得点者候補の計算を専用モジュール化し、過去予測結果とモデル指標を生成するスクリプトを追加しました。

## Phase 0 現状確認結果

- `latest_predictions.json` / `all_unplayed_predictions.json` には `scorer_candidates.home` / `away` が存在していました。
- Streamlitでは得点者候補Top5と過去予測結果の表示が実装済みでした。
- 過去予測結果の表示用JSONは存在していましたが、自動生成スクリプトは未実装でした。
- `model_metrics.json` と生成スクリプトは未実装でした。
- Week5専用の得点者候補、過去予測結果、モデル指標テストは未実装でした。

## 実施した作業

- 得点者候補スコア計算を `src/predict/scorer_candidates.py` に分離しました。
- Goal Propensity Scoreを計算し、チーム別Top5候補に `rank` / `score` / `probability` / `source` を追加しました。
- 既存の `scorer_score` / `goals` / `assists` / `cbp_90` / `played_games` は互換性維持のため残しました。
- `outputs/prediction_history/*.json` と `data/processed/matches_2026_clean.csv` を照合して `past_prediction_results.json` を生成するスクリプトを追加しました。
- `past_prediction_results.json` から `model_metrics.json` を生成するスクリプトを追加しました。
- `model_metrics.json` はローカル確認専用として扱い、Streamlitなどユーザー向け画面には表示しない方針にしました。
- Week5向けテストを追加しました。

## 作成・更新したファイル

- `src/predict/scorer_candidates.py`
- `src/evaluation/past_predictions.py`
- `src/evaluation/model_metrics.py`
- `scripts/build_past_prediction_results.py`
- `scripts/build_model_metrics.py`
- `app/utils/load_predictions.py`
- `app/streamlit_app.py`
- `src/data/scrape_player_stats.py`
- `src/predict/predict_upcoming.py`
- `tests/test_scorer_candidates.py`
- `tests/test_past_prediction_results.py`
- `tests/test_model_metrics.py`
- `outputs/local/model_metrics.json`
- `outputs/latest_predictions.json`
- `outputs/all_unplayed_predictions.json`

## 得点者候補ロジックの確認結果

`calculate_goal_propensity_score()` で以下の考え方を実装しました。

- `goal_point_90` / `shoot_point_90` / `cbp_attack_90` がある場合はそれを使用
- 現在のCSVには上記列がないため、`goals` / `assists` / `cbp_90` からフォールバック計算
- 出場試合数3未満は0.1倍
- FWは1.2倍、DFは0.8倍、その他は1.0倍
- 負値は0に丸める
- チーム内Top5の合計スコアから候補内の `probability` を算出

`latest_predictions.json` と `all_unplayed_predictions.json` では、home / away ともデータのあるチームでTop5候補が出力されています。

## past_prediction_results.json の生成結果

`scripts/build_past_prediction_results.py` を追加しました。

現時点では、`outputs/prediction_history/*.json` と `data/processed/matches_2026_clean.csv` の `match_id` は一致しています。ただし、該当試合は `status=unplayed` かつ `home_score` / `away_score` が未確定だったため、過去予測評価の対象外でした。

そのため、実データ由来の `past_prediction_results.json` はまだ生成できていません。これは異常ではなく、試合結果データを5/13以降に再取得していないために起きている正常な状態です。

0件のときに既存ファイルを空で上書きしないよう、デフォルトでは既存ファイルを保持する挙動にしています。空出力で上書きしたい場合は `--allow-empty` を使います。

## model_metrics.json の生成結果

`scripts/build_model_metrics.py` を追加し、ローカル確認用の `outputs/local/model_metrics.json` を生成できるようにしました。

このファイルは開発者がローカルで確認するためのもので、Streamlit画面やユーザー向け表示には使用しません。現在の指標は、保持されている確認用 `past_prediction_results.json` 4件をもとに算出しています。

- 評価対象試合数: 4
- スコア完全的中率: 0.25
- Home MAE: 0.75
- Away MAE: 0.25
- 勝敗Accuracy: 0.5

## Streamlit表示確認結果

Streamlitでは `model_metrics.json` 由来のモデル指標を表示しない方針に修正しました。

過去予測結果そのものの表示、勝敗的中・スコア的中のフィルタ、過去予測カードの表示は維持しています。

## テスト結果

以下の確認を実施しました。

- `python -m compileall app src scripts`: 成功
- `pytest`: 17 passed
- `python scripts/run_prediction.py --mode next_section`: 成功
- `python scripts/run_prediction.py --mode all_unplayed`: 成功
- `python scripts/build_past_prediction_results.py`: 成功。ただし評価対象0件のため既存ファイル保持
- `python scripts/build_model_metrics.py`: 成功

## 実行したコマンド

```bash
python -m compileall app src scripts
pytest
python scripts/run_prediction.py --mode next_section
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
python scripts/build_model_metrics.py
```

## 見つかった問題

予測履歴と試合結果データの `match_id` は一致していましたが、該当試合は `status=unplayed` かつ `home_score` / `away_score` が未確定だったため、過去予測評価の対象外でした。そのため、実データ由来の `past_prediction_results.json` はまだ生成できていません。

また、現在の選手スタッツCSVには `goal_point_90` / `shoot_point_90` / `cbp_attack_90` が存在しないため、GPSは `goals` / `assists` / `cbp_90` からのフォールバックで算出しています。

## Week6への引き継ぎ

- `full_pipeline.py` 相当の処理がある場合は、予測実行後に `build_past_prediction_results.py` を組み込むとよいです。
- `build_model_metrics.py` はローカル確認専用のため、Streamlit起動処理、GitHub Actions、公開用パイプラインには組み込まない方針です。
- 試合結果データを再取得し、`status=finished` かつ `home_score` / `away_score` が入った状態になれば、過去予測結果を自動生成できます。
- Streamlit Community Cloud公開前に、READMEへ実行手順と出力ファイルの説明を追記するとよいです。
- GitHub Actionsの手動実行では、予測生成と過去結果生成までを公開用の対象にし、モデル指標生成はローカル確認に留めるのが適しています。
