# モデル再学習レポート

## 概要

天候特徴量を除外した方針でモデルを再学習し、`weather_removed_v1` として保存・有効化しました。既存モデルは上書き前にバックアップ済みです。

## 学習条件

| 項目 | 内容 |
|---|---|
| データセット | `Data/ML_dataset.csv` |
| 学習データ | `Season < 2025`、1372行 |
| テストデータ | `Season == 2025`、380行 |
| 特徴量数 | 158 |
| 天候特徴量 | 不使用 |
| モデルバージョン | `weather_removed_v1` |
| 学習日時 | `2026-05-09T17:33:00+09:00` |

## モデル構成

| レイヤー | 目的変数 | アルゴリズム |
|---|---|---|
| Step1 | `Home_Goals`, `Away_Goals` | `MultiOutputRegressor(LGBMRegressor)` |
| Step2A | `Match_Result` | `LGBMClassifier` |
| Step2B | `Goal_Diff` | `LGBMRegressor` |
| Step3 | 最終スコア | `score_candidates.py` の候補統合ロジック |

## 評価結果

| レイヤー | 目的変数 | 評価指標 | 結果 |
|---|---|---|---:|
| 1 | 得点（Home/Away） | Home MAE | 0.8992 |
| 1 | 得点（Home/Away） | Away MAE | 0.8038 |
| 1 | 得点（Home/Away） | 平均MAE | 0.8515 |
| 2 | 勝敗（Match_Result） | Accuracy | 0.5079 |
| 2 | 勝敗（Match_Result） | LogLoss | 1.0589 |
| 2 | 得点差（Goal_Diff） | MAE | 1.0893 |
| 3 | 最終予測 | 最終スコア完全的中率（EMR） | 0.1737 |
| 3 | 最終予測 | 最終Home MAE | 0.9132 |
| 3 | 最終予測 | 最終Away MAE | 0.8447 |
| 3 | 最終予測 | 最終勝敗Accuracy | 0.4974 |

## 保存先

再学習モデルは以下に保存しました。

- `Models/weather_removed_v1/model_step1_goals.pkl`
- `Models/weather_removed_v1/model_step2_clf.pkl`
- `Models/weather_removed_v1/model_step2_diff.pkl`
- `Models/weather_removed_v1/model_features.pkl`
- `Models/weather_removed_v1/model_metadata.json`
- `Models/weather_removed_v1/feature_policy.json`

有効化後のモデルは以下に反映済みです。

- `Models/model_step1_goals.pkl`
- `Models/model_step2_clf.pkl`
- `Models/model_step2_diff.pkl`
- `Models/model_features.pkl`
- `Models/model_metadata.json`
- `Models/feature_policy.json`

## バックアップ

有効化前の既存モデルは以下に退避しました。

- `Models/legacy_weather_20260509_173300/`

## feature_policy

`Models/feature_policy.json` の主な内容は以下です。

- `exclude_weather: true`
- カテゴリ列: `Backline_Matchup`, `Home_Formation`, `Away_Formation`
- 除外Raw列: `Weather`
- 禁止特徴量prefix: `Weather_`
- ゴールパターン: 前年 `Prev_*` 特徴量のみ使用
- チームスタイル: 前年 `Prev_*` 特徴量のみ使用

## 実行コマンド

```bash
python scripts/evaluate_weather_feature.py
python scripts/retrain_models_no_weather.py --dataset Data/ML_dataset.csv --output-dir Models/weather_removed_v1
python scripts/retrain_models_no_weather.py --dataset Data/ML_dataset.csv --output-dir Models/weather_removed_v1 --activate
```
