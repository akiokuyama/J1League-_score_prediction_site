# Point-in-Time 学習データ整備レポート

## 目的

2026 Special、つまり2026年のJ1百年構想リーグは、今後始まる通常の2026シーズンと区別して扱う。
前半戦の週次特徴量スナップショットを保存していなかったため、シーズン終了後の再学習では以下の方針を取る。

- 前半戦など、予測時点の特徴量スナップショットが存在しない試合はフォールバック特徴量を使う
- 今後の週次更新以降は、予測時点の特徴量を保存し、シーズン終了後の学習に使えるようにする
- 試合結果は目的変数として後から結合し、特徴量保存時点では結果を使わない
- 保存用のシーズン識別子は `2026_special` とする
- 学習データ上の `Season` 列は `2026_Special` とする

## 追加した仕組み

### 1. 週次特徴量スナップショット

`scripts/make_upcoming_features.py` の実行時に、次節予測用特徴量を以下へ保存する。

- `Data/features/snapshots/upcoming_features_2026_special_asof_YYYYMMDD_HHMMSS.csv`
- `Data/features/snapshots/upcoming_features_2026_special_sources_asof_YYYYMMDD_HHMMSS.csv`
- `Data/features/snapshots/upcoming_features_2026_special_asof_YYYYMMDD_HHMMSS.json`

特徴量CSVには以下の列を追加する。

- `feature_as_of`
- `season_key`
- `feature_snapshot_source`

### 2. シーズン終了後の再学習用データセット

`scripts/build_point_in_time_training_dataset.py` を追加した。

このスクリプトは、終了済み試合に対して以下の優先順位で特徴量を選ぶ。

1. 同じ `match_id` のスナップショットがある場合は、試合日以前に保存された最新スナップショットを使う
2. スナップショットがない場合は、`Data/features/match_features_2026.csv` のフォールバック特徴量を使う
3. 試合結果を目的変数として結合する

出力ファイル:

- `Data/features/training_dataset_2026_special_point_in_time.csv`
- `Data/features/training_dataset_with_2026_special_point_in_time.csv`
- `Data/features/training_dataset_2026_special_point_in_time_sources.csv`
- `Data/features/training_dataset_2026_special_point_in_time_report.json`

### 3. 再学習時の評価シーズン指定

`scripts/retrain_models_no_weather.py` に `--test-season` を追加した。

2026年シーズン終了後は、以下のように実行できる。

```bash
python scripts/build_point_in_time_training_dataset.py
python scripts/retrain_models_no_weather.py \
  --dataset Data/features/training_dataset_with_2026_special_point_in_time.csv \
  --output-dir Models/point_in_time_2026_special \
  --test-season 2026_Special
```

正式反映する場合のみ `--activate` を付ける。

## 現時点の生成結果

2026年5月24日時点で生成した結果:

- finished matches: 171
- season key: `2026_special`
- season label: `2026 Special`
- Season column value: `2026_Special`
- training rows: 171
- snapshot rows: 0
- fallback rows: 171
- skipped rows: 0
- combined rows: 1923
- snapshot files: 1

現時点では、前半戦のスナップショットが存在しないため、終了済み171試合はすべて `fallback_rebuilt` 扱い。
今後の週次更新でスナップショットが増えると、シーズン終了後に同じスクリプトを再実行した際、該当試合は `snapshot` 扱いになる。

## 確認結果

再学習用CSVの読み込み確認:

- `Data/features/training_dataset_2026_special_point_in_time.csv`: 171行、155列
- `Data/features/training_dataset_with_2026_special_point_in_time.csv`: 1923行、155列
- ダミー展開後の特徴量数: 158
- 目的変数欠損: 0
- 特徴量欠損: 0

一時出力先での再学習確認:

```bash
python scripts/retrain_models_no_weather.py \
  --dataset Data/features/training_dataset_with_2026_special_point_in_time.csv \
  --output-dir /private/tmp/soccer_score_app_point_in_time_model_check \
  --test-season 2026_Special
```

結果:

- feature_count: 158
- train_rows: 1752
- test_rows: 171
- home_mae: 0.9086
- away_mae: 0.9018
- result_accuracy: 0.3801
- final_score_emr: 0.1345

## 注意点

現時点の2026年データは前半戦スナップショットがないため、厳密なpoint-in-time学習としては不完全。
ただし、今後の試合分については週次更新時にスナップショットを保存できるため、シーズン終了後には「前半はフォールバック、後半はスナップショット」という再学習データを作成できる。
