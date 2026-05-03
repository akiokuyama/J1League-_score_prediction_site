# Week2 完了レポート

## 概要

Week2では、Week1で確認済みのモデル読み込み処理を再利用し、単一試合に対してJSON互換の予測結果を返す `predict_match()` を実装しました。特徴量整形処理は共通モジュールへ切り出し、期待得点、勝敗確率、得失点差予測を統合してスコア候補Top 5を生成できるようにしました。

## 作成・更新したファイル

- `src/predict/feature_preprocess.py` を作成
- `src/predict/score_candidates.py` を作成
- `src/predict/predict_match.py` を作成
- `src/predict/__init__.py` を更新
- `scripts/smoke_test_load_models.py` を共通前処理利用へ更新
- `scripts/smoke_test_predict_match.py` を作成
- `docs/week2_completion_report.md` を作成

## 実装した関数

- `load_reference_dataset()`: `Data/ML_dataset.csv` または指定CSVを読み込み
- `prepare_features_for_model()`: 既に特徴量作成済みの行に対して、目的変数・ID列除外、One-Hot Encoding、特徴量列合わせ、診断情報生成を実行
- `generate_score_candidates()`: 期待得点、勝敗確率、得失点差整合性からスコア候補を生成
- `normalize_team_name()`: 最小限のチーム名エイリアスを標準名へ変換
- `predict_match()`: 単一試合の予測JSONを返却

## Notebook確認後の補足

`Notebook/01_Data_Preparation.ipynb` はスクレイピングとRawData保存、`Notebook/02_ML_Table.ipynb` はRawDataを結合・計算して `Data/ML_dataset.csv` を作る特徴量生成処理です。

Week2で作成した `src/predict/feature_preprocess.py` は、このNotebook 01/02相当の特徴量生成を再実装するものではありません。責務は、既に作成済みの `ML_dataset.csv` またはWeek3以降から渡される特徴量行を、学習済みモデルの入力列へ整える推論前処理です。具体的には、目的変数・ID列の除外、カテゴリ列のOne-Hot Encoding、`model_features.pkl` に基づく列順合わせを行います。

## 予測JSONの形式

`predict_match()` は以下を含むJSON互換の `dict` を返します。

- `match_id`
- `date`
- `home_team`
- `away_team`
- `predicted_score`
- `expected_goals`
- `result_probabilities`
- `score_candidates`
- `predicted_goal_diff`
- `scorer_candidates`
- `feature_source`
- `model_info`

`scorer_candidates` はWeek2では空配列で返します。

## スモークテスト結果

`scripts/smoke_test_predict_match.py` で `Data/ML_dataset.csv` の末尾行を使った単一試合予測が成功しています。出力は `json.dumps(..., ensure_ascii=False)` でシリアライズ可能です。

## 実行したコマンド

```bash
python -m compileall src scripts
python scripts/smoke_test_load_models.py
python scripts/smoke_test_predict_match.py
```

## 見つかった課題

- Week2では未来試合特徴量の自動生成は未実装です。
- `Data/ML_dataset.csv` に同一カードが存在しない場合、`feature_row` を渡さない限り予測できません。
- 既存データセット内のチーム名は略称コードです。主要な日本語チーム名からコード検索できる最低限の対応は追加しましたが、本格的なチーム名マスタ整備は今後必要です。
- `scorer_candidates` は空配列で、得点者予測の本格実装は未対応です。

## Week3への引き継ぎ

- Week2では未来試合特徴量の自動生成は未実装です。
- Week3では日程データから未消化試合を抽出し、各試合の特徴量行を作って `predict_match()` に渡してください。
- `outputs/latest_predictions.json` はWeek3で本格生成してください。
- `scorer_candidates` はWeek5で本格実装してください。
