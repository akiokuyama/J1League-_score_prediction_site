# Week1 既存資産棚卸し

## 1. プロジェクト概要

このリポジトリには、J1の試合スコア予測に関する既存Notebook、CSVデータセット、学習済みモデルのpickleファイルが含まれています。Week1では、アプリ実装やスクレイピングには入らず、既存資産の棚卸し、ローカルでのモデル読み込み、特徴量列の整合、1件のサンプル推論確認までを対象にしました。

## 2. 既存Notebook

| パス | 役割 | 主な入力 | 主な出力 | メモ |
|---|---|---|---|---|
| `archive/notebooks/01_Data_Preparation.ipynb` | チーム基礎力、勢い、個人稼働状況、チームスタッツ、コンディション、戦術相性などの元データ収集・整形。 | Web上のJリーグ関連データ、Football Lab、Transfermarkt相当のデータなど。 | `archive/legacy_rawdata/` 配下のRaw CSV。 | セル内に絶対パスが含まれる。Rawデータ作成の参照元として有用だが、自動化前にパスの整理が必要。 |
| `archive/notebooks/02_ML_Table.ipynb` | Rawデータを結合して機械学習用テーブルを作成。 | `archive/legacy_rawdata/*.csv` | `Data/ML_dataset.csv` | 複数セルで `ML_dataset.csv` を保存している。Week2ではNotebookを再実行するより、生成済みCSVを参照するのが安全。 |
| `archive/notebooks/03_EDA_score_prediction.ipynb` | スコア予測向けの探索的データ分析。 | `Data/ML_dataset.csv` | グラフ、分析結果。 | 学習済みモデルの保存処理は確認されていない。 |
| `archive/notebooks/04_ML_Model_Training.ipynb` | 得点予測、勝敗分類、得失点差予測モデルを学習。 | `Data/ML_dataset.csv` | `Models/` 配下のモデルpickleファイル。 | モデル学習・保存ロジックを含む。既存モデルが欠損または互換性エラーになる場合のみ再実行候補。 |
| `archive/notebooks/05_Bayer_Table (Goal Player).ipynb` | 得点者予測用のスコアリングとシミュレーター。 | `archive/legacy_rawdata/df_player_stats.csv` | Notebook内の `predict_goalscorers` 関数。 | Week1のスコアモデル読み込みとは別系統。Week2以降で得点者予測を扱う場合は `src/` への抽出候補。 |

## 3. 既存データファイル

| パス | 行数/形状 | 役割 | メモ |
|---|---:|---|---|
| `Data/ML_dataset.csv` | `(1752, 155)` | モデル推論・学習用のメインデータセット。 | スモークテストで使用。 |
| `archive/legacy_rawdata/df_agi_kagi.csv` | `(96, 4)` | Football LabのAGI/KAGIデータ。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_fixtures.csv` | `(1752, 18)` | 試合日程・結果データ。 | Raw試合データ。 |
| `archive/legacy_rawdata/df_goal_patterns.csv` | `(242, 13)` | ゴールパターン特徴量。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_manager_changes.csv` | `(26, 8)` | 監督交代データ。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_managers.csv` | `(96, 3)` | チーム監督データ。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_market_values.csv` | `(96, 3)` | チーム市場価値データ。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_player_stats.csv` | `(2172, 13)` | 選手スタッツ。 | 得点者予測Notebookで使用。 |
| `archive/legacy_rawdata/df_ranks.csv` | `(101, 40)` | 節ごとの順位データ。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_season_stats.csv` | `(3504, 7)` | シーズン内順位、勝ち点、緊急度など。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_team_stats.csv` | `(114, 32)` | チームスタッツ。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_team_styles.csv` | `(242, 11)` | チーム戦術・スタイル指標。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/df_xg.csv` | `(96, 6)` | 期待得点データ。 | Raw特徴量ソース。 |
| `archive/legacy_rawdata/stadium_df.csv` | `(58, 6)` | スタジアム情報。 | Raw特徴量ソース。 |

## 4. 既存モデルファイル

| パス | 読み込み結果 | 型/クラス | 役割 | メモ |
|---|---|---|---|---|
| `Models/model_step1_goals.pkl` | 成功 | `sklearn.multioutput.MultiOutputRegressor` | ホーム・アウェイの期待得点を予測。 | 2つの推定器を含む。 |
| `Models/model_step2_clf.pkl` | 成功 | `lightgbm.sklearn.LGBMClassifier` | 勝敗クラスを予測。 | クラスは `[-1, 0, 1]`。 |
| `Models/model_step2_diff.pkl` | 成功 | `lightgbm.sklearn.LGBMRegressor` | 得失点差を予測。 | 正常に読み込み済み。 |
| `Models/model_features.pkl` | 成功 | `list` | 学習時の特徴量列リスト。 | 特徴量数は164。 |

## 5. 特徴量ファイル / 特徴量列

推論時の列定義は `Models/model_features.pkl` を正とします。現在のスモークテストでは、目的変数やID列を除外し、存在するカテゴリ列だけOne-Hot Encodingしたうえで、以下の形で学習時特徴量に合わせています。

```python
X = X.reindex(columns=model_features, fill_value=0)
```

現在の確認結果:

- 学習時特徴量数: 164
- `ML_dataset.csv` から生成した特徴量数: 164
- 学習時特徴量にあるが現在データにない列: 0
- 現在データにあるが学習時特徴量にない列: 0

## 6. 現在の課題 / リスク

- 複数のNotebookに絶対パスが含まれているため、自動実行や別環境での再利用前にパスの整理が必要。
- `archive/notebooks/04_ML_Model_Training.ipynb` には `optuna` など学習時のみ必要なライブラリが含まれる。`requirements.txt` には追記済みだが、Week1では再学習は実施していない。
- pickle形式の学習済みモデルは、`scikit-learn`、`lightgbm`、`numpy`、`joblib` などのバージョン差異で読み込み互換性の影響を受ける可能性がある。
- 得点者予測ロジックはまだNotebook内にあり、再利用可能な `src/` 配下のコードにはなっていない。

## 7. Week2準備状況

Week2では、以下を土台にして `src/predict/predict_match.py` を作成できます。

- `src.models.load_model.load_models()`
- `scripts/smoke_test_load_models.py` の特徴量整形・列合わせ処理
- 現時点で正常に推論できる入力形式としての `Data/ML_dataset.csv`

スコア予測モデルはローカルで読み込みでき、特徴量を揃えた1件のサンプル行に対して推論できる状態です。

## 8. 確認済みコマンド

```bash
python -m compileall src scripts
python scripts/smoke_test_load_models.py
```
