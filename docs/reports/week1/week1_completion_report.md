# Week1 完了レポート

## 概要

Week1の既存資産棚卸しとモデル読み込み準備は完了しました。既存Notebook、データセット、学習済みモデルファイルを確認し、再利用可能なモデル読み込みモジュールとスモークテスト用スクリプトを追加しました。スモークテストでは、現在のモデルを正常に読み込み、1件のサンプルデータに対して予測を実行できることを確認しました。

## 作成・更新したファイル

- `docs/asset_inventory.md` を作成
- `docs/week1_completion_report.md` を作成
- `src/models/load_model.py` を作成
- `scripts/smoke_test_load_models.py` を作成
- `src/` 配下にPythonパッケージ用の `__init__.py` を追加
- `src/predict/`、`outputs/`、`logs/` に `.gitkeep` を追加
- `requirements.txt` を作成
- Pythonキャッシュと生成ログを除外するため `.gitignore` を更新

## モデル読み込み結果

- `Models/model_step1_goals.pkl`: `sklearn.multioutput.MultiOutputRegressor` として正常に読み込み
- `Models/model_step2_clf.pkl`: `lightgbm.sklearn.LGBMClassifier` として正常に読み込み
- `Models/model_step2_diff.pkl`: `lightgbm.sklearn.LGBMRegressor` として正常に読み込み
- `Models/model_features.pkl`: 164個の特徴量名を持つ `list` として正常に読み込み

## スモークテスト結果

確認したコマンド:

```bash
python scripts/smoke_test_load_models.py
```

実行結果:

```text
[OK] model_dir: /Users/akihirookuyama/Soccer_Score_App/Models
[OK] モデル読み込み成功
[INFO] feature count: 164
[OK] dataset: /Users/akihirookuyama/Soccer_Score_App/Data/ML_dataset.csv
[OK] ML_dataset 読み込み成功: shape=(1752, 155)
[OK] 予測テスト成功
  expected_goals_home: 1.2966655818840997
  expected_goals_away: 0.9613211031878056
  result_classes: [-1, 0, 1]
  result_probabilities: [0.06446506323211247, 0.027206731535693453, 0.908328205232194]
  predicted_goal_diff: 0.30078430871275325
```

## 見つかった問題

- 現在のデータセットと学習時特徴量リストは、前処理後に完全に一致しており、特徴量の不一致はありませんでした。
- 既存Notebookには絶対パスが含まれているため、自動化で直接利用する前にパス整理が必要です。
- 得点者予測ロジックはまだNotebook内にあり、Week1の対象外です。

## Week2への推奨次ステップ

- `load_models()` とスモークテストの特徴量整形処理を使って `src/predict/predict_match.py` を作成する。
- アプリ用ロジックを追加する前に、特徴量準備処理をスモークテストから再利用可能なソースコードへ切り出す。
- 推論時の列定義は引き続き `model_features.pkl` を正とする。
- モデル予測関数が安定してから、アプリ表示用の出力形式を整える。
