# Codex指示書：Week1 既存資産整理・モデル読み込み確認

## 目的

この指示書は、J1試合結果予測アプリ開発ロードマップの **Week1「既存資産の整理」** をCodexに実行してもらうためのものです。

Week1のゴールは、アプリ実装やスクレイピングに入る前に、既存Notebook・データセット・学習済みモデルを整理し、**ローカル環境で既存モデルを読み込める状態** にすることです。

---

## Codexに依頼する作業の全体像

あなたは、既存のJリーグ試合結果予測プロジェクトを、今後アプリ化できる形に整理してください。

Week1では、以下を実施してください。

1. 既存ファイルの棚卸し
2. 学習済みモデル・特徴量・データセットの所在確認
3. 最小限のディレクトリ整備
4. モデル読み込み用モジュールの作成
5. モデル読み込み確認スクリプトの作成
6. 依存ライブラリの整理
7. Week1完了レポートの作成

---

## 重要な前提

このプロジェクトでは、既にスコア予測モデルと得点者予測ロジックは作成済みです。Week1では **モデルの再学習は行わないでください**。

また、Streamlitアプリ実装、スクレイピング、GitHub Actions化、次節全試合予測はWeek2以降の作業です。Week1では実装しないでください。

### Week1でやること

- 既存資産を把握する
- モデルファイルを読み込めるようにする
- 学習時特徴量と現在データの列を安全に揃える
- 1件のサンプルデータに対して推論が実行できることを確認する
- Week2で `predict_match.py` を作れる状態にする

### Week1でやらないこと

- 新しいモデル学習
- スクレイピング実装
- Streamlit画面実装
- GitHub Actions実装
- `latest_predictions.json` の本格生成
- 得点者予測ロジックの画面表示
- 大規模なリファクタリング
- 既存Notebookの破壊的変更

---

## 想定プロジェクト名

```text
Soccer_Score_App
```

ただし、実際のルートディレクトリ名が異なる場合は、現在のリポジトリ構成に合わせてください。

---

## 想定される既存Notebook

以下のNotebookが存在する可能性があります。存在する場合は、内容を確認し、役割を棚卸ししてください。

```text
01_Data_Preparation.ipynb
02_ML_Table.ipynb
03_EDA_score_prediction.ipynb
04_ML_Model_Training.ipynb
05_Bayer_Table (Goal Player).ipynb
```

各Notebookについて、以下を整理してください。

- ファイルパス
- 役割
- 入力データ
- 出力データ
- 学習済みモデルを保存しているか
- Week2以降で参照すべき箇所
- そのまま使えるか、整理が必要か

---

## 想定される重要ファイル

まず、以下のファイルが存在するか確認してください。

```text
Data/ML_dataset.csv
Models/model_step1_goals.pkl
Models/model_step2_clf.pkl
Models/model_step2_diff.pkl
Models/model_features.pkl
```

ただし、実際のファイル名・配置が異なる可能性があります。その場合は、リポジトリ内を探索して、対応するファイルを見つけてください。

### モデルファイルの想定役割

| ファイル | 役割 |
|---|---|
| `model_step1_goals.pkl` | ホーム得点・アウェイ得点を予測するモデル |
| `model_step2_clf.pkl` | 勝敗分類モデル |
| `model_step2_diff.pkl` | 得点差予測モデル |
| `model_features.pkl` | 学習時に使用した特徴量リスト |

---

## 作成・更新してほしいディレクトリ

存在しない場合は作成してください。

```text
docs/
scripts/
src/
src/models/
src/predict/
outputs/
logs/
```

この段階では、空ディレクトリをGit管理するために `.gitkeep` を置いても構いません。

---

## 作成してほしいファイル

### 1. `docs/asset_inventory.md`

既存資産の棚卸しドキュメントを作成してください。

最低限、以下のセクションを含めてください。

```markdown
# Week1 Asset Inventory

## 1. Project Summary

## 2. Existing Notebooks

| Path | Role | Main Inputs | Main Outputs | Notes |
|---|---|---|---|---|

## 3. Existing Data Files

| Path | Rows/Shape | Role | Notes |
|---|---:|---|---|

## 4. Existing Model Files

| Path | Loaded Successfully | Type/Class | Role | Notes |
|---|---|---|---|---|

## 5. Feature Files / Feature Columns

## 6. Current Issues / Risks

## 7. Week2 Readiness

## 8. Commands Verified
```

### 2. `src/models/load_model.py`

学習済みモデルを読み込むモジュールを作成してください。

要件：

- `joblib.load` を使用する
- モデルディレクトリを引数で指定できる
- デフォルトでは `Models/` または `models/` を探索する
- 必須モデルが存在しない場合は、分かりやすい例外を出す
- 返り値は `ModelBundle` のようなdataclassにする
- `model_features` は `list[str]` として扱えるようにする
- 既存ファイル名が異なる場合に備えて、コード内で候補探索できるようにする

想定インターフェース：

```python
from src.models.load_model import load_models

bundle = load_models()
print(bundle.feature_names)
```

想定構造：

```python
@dataclass
class ModelBundle:
    step1_goals: Any
    step2_clf: Any
    step2_diff: Any
    feature_names: list[str]
    model_dir: Path
```

### 3. `scripts/smoke_test_load_models.py`

モデル読み込みと簡易推論確認を行うスクリプトを作成してください。

要件：

- `Data/ML_dataset.csv` または候補データセットを読み込む
- モデルを `src/models/load_model.py` 経由で読み込む
- 学習時特徴量に合わせて列を揃える
- データ末尾1件を使って簡易推論する
- 結果を標準出力に分かりやすく表示する
- 失敗時は `sys.exit(1)` で終了する
- 成功時は `[OK] 予測テスト成功` を出力する

### 4. `docs/week1_completion_report.md`

Week1完了レポートを作成してください。

最低限、以下を含めてください。

```markdown
# Week1 Completion Report

## Summary

## Files Created / Updated

## Model Loading Result

## Smoke Test Result

## Issues Found

## Recommended Next Steps for Week2
```

### 5. `requirements.txt`

既に存在する場合は、破壊的に上書きせず、必要なものが含まれているか確認・追記してください。

最低限、以下が必要です。

```text
pandas
numpy
scikit-learn
lightgbm
joblib
scipy
```

既存Notebookやモデル読み込みに必要な追加ライブラリがあれば追記してください。

---

## 特徴量整形の要件

モデル推論前に、データセットから目的変数やID列を除外してください。

除外候補：

```python
drop_cols = [
    "Season",
    "Section",
    "Date",
    "Score",
    "Home",
    "Away",
    "Stadium",
    "Home_Goals",
    "Away_Goals",
    "Goal_Diff",
    "Match_Result",
]
```

One-Hot Encoding対象候補：

```python
cat_cols = [
    "Weather",
    "Backline_Matchup",
    "Home_Formation",
    "Away_Formation",
]
```

ただし、実際に存在する列だけを処理してください。

学習時特徴量との整合は以下のように行ってください。

```python
X = X.reindex(columns=model_features, fill_value=0)
```

### 重要

- 学習時に存在したが現在のデータにない列は警告として表示してください
- 現在のデータにあるが学習時にない列も警告として表示してください
- ただし、Week1ではこの差分を無理に修正しないでください
- まずは安全にモデルが読み込めて、1件推論できる状態を優先してください

---

## 期待されるスモークテスト出力例

以下のような出力を目指してください。

```text
[OK] model_dir: /path/to/Soccer_Score_App/Models
[OK] dataset: /path/to/Soccer_Score_App/Data/ML_dataset.csv
[OK] モデル読み込み成功
[INFO] feature count: 221
[OK] ML_dataset 読み込み成功: shape=(1752, 215)

[INFO] sample match:
{'Season': 2025, 'Section': 38, 'Home': '...', 'Away': '...', 'Score': '...'}

[OK] 予測テスト成功
  expected_goals_home: 1.234
  expected_goals_away: 0.987
  result_classes: [...]
  result_probabilities: [...]
  predicted_goal_diff: 0.456
```

実際の数値は異なって構いません。

---

## 実行してほしい確認コマンド

作業後に以下を実行してください。

```bash
python -m compileall src scripts
python scripts/smoke_test_load_models.py
```

`pytest` を導入する場合のみ、以下も実行してください。

```bash
pytest
```

---

## エラー時の対応方針

### モデルファイルが見つからない場合

- エラーで終了してよい
- ただし、どのファイルが不足しているか明示する
- `04_ML_Model_Training.ipynb` のモデル保存セルを再実行すべき旨を `docs/week1_completion_report.md` に記載する

### `ML_dataset.csv` が見つからない場合

- 候補パスを探索する
- `.csv` ファイル一覧を確認する
- それでも見つからない場合は、どのデータセットが必要かレポートに記載する

### 特徴量数が合わない場合

- `model_features.pkl` を正とする
- `reindex(columns=model_features, fill_value=0)` で揃える
- 差分列を警告として表示する
- Week1では深追いしない

### LightGBMやscikit-learnのバージョン差異で読み込みに失敗する場合

- 例外内容をレポートに記載する
- 可能であれば、現在環境のバージョンを出力する
- 依存関係の修正案を `requirements.txt` またはレポートに書く
- 既存モデルファイルの再学習は実施しない

---

## 実装時の注意

- 既存Notebookは原則変更しない
- 既存データや既存モデルを削除・上書きしない
- ディレクトリ名の大文字小文字に注意する
- `Models/` と `models/` の両方を探索できるようにする
- `Data/` と `data/` の両方を探索できるようにする
- 絶対パス固定にしない
- プロジェクトルートからの相対パスで動くようにする
- 失敗時のメッセージは、日本語または英語で分かりやすくする
- Week2で `predict_match.py` を作りやすいように、モデル読み込み処理を再利用可能にする

---

## 完了条件

Week1は、以下を満たしたら完了です。

- [ ] `docs/asset_inventory.md` が作成されている
- [ ] `src/models/load_model.py` が作成されている
- [ ] `scripts/smoke_test_load_models.py` が作成されている
- [ ] `docs/week1_completion_report.md` が作成されている
- [ ] `requirements.txt` に必要な依存関係が整理されている
- [ ] `python -m compileall src scripts` が成功する
- [ ] `python scripts/smoke_test_load_models.py` が成功する
- [ ] 既存モデルをローカルで読み込める
- [ ] 1件のサンプルに対して予測結果を出力できる
- [ ] Week2で `predict_match.py` に進める状態になっている

---

## Codexの最終回答に含めてほしい内容

作業完了後、以下を報告してください。

```markdown
## 実施内容

## 作成・更新したファイル

## 実行したコマンド

## 実行結果

## 見つかった問題

## Week2への引き継ぎ
```

---

## 参考：Week2で作る予定のもの

Week1が完了したら、次は以下を作ります。

```text
src/predict/predict_match.py
```

Week2では、以下のようなインターフェースを目指します。

```python
predict_match(
    home_team="名古屋グランパス",
    away_team="横浜 F・マリノス",
    match_date="2026-05-10",
)
```

返り値は、将来的に `latest_predictions.json` に入れられるJSON形式を想定します。

Week1ではここまで作らず、モデル読み込みと1件推論確認までで止めてください。
