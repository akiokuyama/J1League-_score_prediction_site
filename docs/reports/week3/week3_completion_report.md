# Week3 完了レポート

## 概要

Week3の目的である、天候なしモデルへの移行、2026年データ取得、未来試合特徴量生成、次節一括予測、`latest_predictions.json` の安全保存まで実施しました。

2026-05-10に追加対応を行い、前回失敗していた市場価値、Jリーグ公式チームスタッツ、Football Lab summary系データは取得できる状態まで復旧しました。さらに、選手スタッツ正規化、得点者候補連携、フォーメーション実値抽出、補完由来フラグ出力まで対応しました。

## 実施した作業

- 天候特徴量のA/B評価
- 天候なしモデルの再学習と有効化
- 既存モデルのバックアップ作成
- 2026年J1百年構想リーグの日程・結果取得
- 未来試合用特徴量CSVの生成
- 次節一括予測の実行
- `latest_predictions.json` の一時ファイル経由の安全保存
- 日本語レポート作成
- 2026-05-10: Transfermarkt URL修正と市場価値20クラブ分の取得
- 2026-05-10: Jリーグ公式チームスタッツHTMLカードのパース対応
- 2026-05-10: Football Lab百年構想リーグ用URLへの修正とsummary系データ取得
- 2026-05-10: 市場価値、AGI/KAGI、ゴール期待値を未来特徴量へ反映
- 2026-05-10: 選手スタッツを現行2026ページの `/ranking` から再取得し、英字列へ正規化、`scorer_score` を作成
- 2026-05-10: チーム別得点者候補Top5を `latest_predictions.json` の `scorer_candidates` へ連携
- 2026-05-10: Football Labフォーメーションから20クラブ分の実値を抽出
- 2026-05-10: `upcoming_features_2026_sources.csv` と列別補完率レポートを作成

## 作成・更新したファイル

主な作成・更新ファイルは以下です。

- `src/evaluation/`
- `src/models/train_score_models.py`
- `scripts/evaluate_weather_feature.py`
- `scripts/retrain_models_no_weather.py`
- `src/data/`
- `scripts/update_2026_data.py`
- `src/features/`
- `scripts/make_upcoming_features.py`
- `src/predict/predict_upcoming.py`
- `scripts/run_prediction.py`
- `scripts/full_pipeline.py`
- `Models/weather_removed_v1/`
- `Models/legacy_weather_20260509_173300/`
- `Models/model_metadata.json`
- `Models/feature_policy.json`
- `data/processed/update_2026_report.json`
- `data/features/match_features_2026.csv`
- `data/features/upcoming_features_2026.csv`
- `outputs/latest_predictions.json`
- `outputs/latest_predictions.csv`
- `outputs/prediction_history/`
- `data/manual/market_values_2026.csv`
- `data/features/upcoming_features_2026_sources.csv`
- `data/features/upcoming_features_2026_source_report.csv`

## 天候特徴量の扱い

正式モデルでは天候特徴量を使用しません。

- `Weather` は学習・推論から除外
- `Weather_*` のOne-Hot特徴量は生成しない
- `feature_policy.json` に除外方針を保存
- `model_features.pkl` は天候なし158特徴量で更新

詳細は `docs/weather_feature_decision.md` に記載しました。

## モデル再学習結果

| 指標 | 天候なしモデル |
|---|---:|
| Home MAE | 0.8992 |
| Away MAE | 0.8038 |
| 平均MAE | 0.8515 |
| 勝敗Accuracy | 0.5079 |
| 勝敗LogLoss | 1.0589 |
| Goal Diff MAE | 1.0893 |
| 最終スコアEMR | 0.1737 |
| 最終Home MAE | 0.9132 |
| 最終Away MAE | 0.8447 |
| 最終勝敗Accuracy | 0.4974 |

モデルは `weather_removed_v1` として保存し、既存モデルは `Models/legacy_weather_20260509_173300/` にバックアップしました。

## 2026年データ取得結果

| データ | 件数 | 状態 |
|---|---:|---|
| 試合日程・結果 | 180 | 成功 |
| 未消化試合 | 29 | 成功 |
| 順位表 | 20 | EAST/WEST各10行を取得。`division` 列を追加し、処理済みCSVでは英字列名・チームコードへ正規化済み |
| チームスタッツ | 520 | 取得成功。26種類×20クラブ |
| 市場価値 | 20 | 取得成功。手動CSVにも保存済み |
| Football Lab expected | 40 | 取得成功 |
| Football Lab kagi | 40 | 取得成功 |
| Football Lab ゴールパターン | 20 | 取得成功 |
| Football Lab チームスタイル | 60 | 取得成功 |
| フォーメーション | 20 | 取得成功。実値抽出済み、Unknown 0件 |
| 選手スタッツ | 200 | `?year=2026` が2025ページを返す仕様だったため、現行2026ページの `/ranking` から再取得。英字列正規化と `scorer_score` 作成済み |

詳細は `data/processed/update_2026_report.json` と `docs/data_source_report_2026.md` に保存しました。

## ゴールパターン・チームスタイルの扱い

正式モデルでは、当年最新値は使わず、前年シーズン終了時点の `Prev_*` 特徴量のみ使う方針にしました。

2026年のFootball Labゴールパターン・チームスタイルは将来検証用スナップショットとして保存しています。2026-05-10時点で、ゴールパターン20行、チームスタイル60行を取得済みです。ただし、正式予測特徴量には当年のゴールパターン・チームスタイルを混ぜていません。

## 特徴量生成結果

- `data/features/match_features_2026.csv`: 180行
- `data/features/upcoming_features_2026.csv`: 29行
- Weather関連列: 0列
- モデル必須特徴量の欠損: 0列
- 重複行: 0行
- 欠損セル率: 0.0%
- `Unknown` 値: 0件
- 2026年取得値の反映: `Home/Away_Market_Value`, `Home/Away_AGI`, `Home/Away_KAGI`, `Home/Away_Rolling_xG`
- 2026年フォーメーション実値の反映: `Home_Formation`, `Away_Formation`, `Backline_Matchup`
- 補完由来ファイル: `data/features/upcoming_features_2026_sources.csv`
- 列別補完率レポート: `data/features/upcoming_features_2026_source_report.csv`
- 全体actual率: 0.1475
- 全体fallback率: 0.7104

未来試合で取得できない値は、既存の過去データからチーム別中央値・最頻値、またはリーグ中央値・最頻値で補完しています。セル単位の由来は `upcoming_features_2026_sources.csv` に保存しています。

## 一括予測結果

`next_section` で第12節の2試合を予測し、`outputs/latest_predictions.json` に保存しました。

| 試合 | 予測スコア | Home勝率 | 引分率 | Away勝率 |
|---|---:|---:|---:|---:|
| mcd vs tk-v | 1-1 | 0.2211 | 0.2668 | 0.5121 |
| kobe vs kyot | 1-0 | 0.4816 | 0.4211 | 0.0973 |

得点者候補は、各チームTop5を `scorer_candidates.home` / `scorer_candidates.away` に出力しています。

`latest_predictions.json` の確認結果:

- `warnings`: 空配列
- `skipped_matches`: 空配列
- `matches`: 2件
- scorer_candidates: 対象2試合ともhome/away各5件
- 最終更新: `2026-05-10T14:55:32+09:00`

## latest_predictions.json の検証結果

保存時に以下を検証しています。

- JSONとして読み込めること
- 必須トップレベルキーが存在すること
- `matches` が空でないこと
- 各試合に必須キーが存在すること
- `Weather` / `Weather_*` が含まれていないこと

検証成功後に `outputs/latest_predictions.tmp.json` から `outputs/latest_predictions.json` へ置換し、`outputs/prediction_history/` に履歴コピーを作成しました。

## 実行したコマンド

```bash
python -m compileall src scripts
python scripts/smoke_test_load_models.py
python scripts/smoke_test_predict_match.py
python scripts/evaluate_weather_feature.py
python scripts/retrain_models_no_weather.py --dataset Data/ML_dataset.csv --output-dir Models/weather_removed_v1
python scripts/retrain_models_no_weather.py --dataset Data/ML_dataset.csv --output-dir Models/weather_removed_v1 --activate
python scripts/update_2026_data.py --use-cache
python scripts/make_upcoming_features.py --season 2026 --category 100yj1
python scripts/run_prediction.py --mode next_section
python scripts/run_prediction.py --mode all_unplayed
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section --use-cache
python scripts/update_2026_data.py --use-cache
python scripts/make_upcoming_features.py --season 2026 --category 100yj1
python scripts/run_prediction.py --mode next_section
python -m compileall src scripts
python scripts/smoke_test_load_models.py
python scripts/smoke_test_predict_match.py
```

`pytest` はこの環境にインストールされていないため未実行です。

## 見つかった問題

- Jリーグ公式チームスタッツはHTMLテーブルではなくカード形式だったため、BeautifulSoupでパースするよう修正済み
- TransfermarktはURL誤りが原因だったため、`J1YV` の正しいURLに修正済み
- Football Lab summary系はURL形式誤りが原因だったため、`j1001` と `year=100` の形式に修正済み
- フォーメーションは `?year=2026` では2025ページを返すため、現行2026ページの `/formation/` に修正済み
- 選手スタッツは2026百年構想リーグ20クラブのFootball Labコードに修正し、`?year=2026` を使わない現行ページURLで再取得済み
- 補完率はセル単位の由来フラグと列別レポートを追加済み

## 次フェーズへの引き継ぎ

2026-05-10時点で、今回失敗していた主要データ取得は以下の通り復旧しました。

| 対象 | 状態 |
|---|---|
| Transfermarkt市場価値 | 復旧済み。正しいURL `J1YV` から20クラブ分を取得し、`data/manual/market_values_2026.csv` に保存 |
| Jリーグ公式チームスタッツ | 復旧済み。HTMLカード形式をパースし、520行を取得 |
| Football Lab expected/kagi | 復旧済み。`j1001` / `year=100` URLで各40行を取得 |
| Football Lab ゴールパターン | 復旧済み。JavaScript配列から20行を取得 |
| Football Lab チームスタイル | 復旧済み。60行を取得 |

残っている作業は、データ取得・特徴量生成ではなく、アプリ表示と運用整備です。

### 1. アプリ表示と運用整備

- `outputs/latest_predictions.json` をアプリ側で表示できるか確認してください。
- `next_section` と `all_unplayed` を別ファイルで運用するか決めてください。
- `pytest` を追加し、Weather混入禁止、特徴量列一致、予測JSON検証、予測モードのテストを整備してください。
