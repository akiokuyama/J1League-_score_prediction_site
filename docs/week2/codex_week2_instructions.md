# Codex指示書：Week2 単一試合予測関数 `predict_match` 実装

## 目的

この指示書は、J1試合結果予測アプリ開発ロードマップの **Week2「単一試合予測関数の実装」** をCodexに実行してもらうためのものです。

Week2のゴールは、Week1で確認済みの既存モデル読み込み処理と特徴量整形処理を再利用し、指定した1試合に対して、アプリ表示やWeek3以降の一括予測に使える **JSON互換の予測結果** を返す関数を作ることです。

---

## Codexへの重要指示

- すべての説明文、作成ドキュメント、完了レポートは **日本語** で書いてください。
- 既存Notebook、既存CSV、既存モデルpickleは削除・上書きしないでください。
- Week2ではモデル再学習、スクレイピング、Streamlit画面、GitHub Actions、一括次節予測は実装しないでください。
- 予測ロジックは、Week1で作成済みの `src.models.load_model.load_models()` を必ず再利用してください。
- Week1の `scripts/smoke_test_load_models.py` にある特徴量整形・列合わせ処理を、再利用可能な関数として切り出してください。
- `model_features.pkl` の特徴量リストを正とし、推論直前に必ず `reindex(columns=model_features, fill_value=0)` で列を揃えてください。
- 未来試合の特徴量自動生成はWeek3以降の作業です。Week2では、`Data/ML_dataset.csv` に存在する試合行、または外部から渡された特徴量行を使って単一試合予測を行える状態にしてください。

---

## Week1から引き継ぐ前提

Week1では以下が完了済みです。

- 既存モデルファイルを読み込める状態になっている
- `src/models/load_model.py` が作成済み
- `scripts/smoke_test_load_models.py` で1件のサンプル推論が成功済み
- `Models/model_features.pkl` の特徴量数は164
- `Data/ML_dataset.csv` から生成した特徴量と学習時特徴量の差分は0
- 既存のスコア予測モデルは以下の3系統
  - `model_step1_goals.pkl`: ホーム・アウェイ期待得点を予測
  - `model_step2_clf.pkl`: 勝敗クラスを予測
  - `model_step2_diff.pkl`: 得失点差を予測

Week2では、これらをアプリ用の関数として使える形に整理します。


---

## Notebook参照元と再現対象

Week2の推論ロジックは、主に以下の既存Notebookの処理を `src/` 配下へ移植するものです。

### 1. スコア予測ロジック

参照元:

```text
Notebook/04_ML_Model_Training.ipynb
```

再現する処理:

- `Data/ML_dataset.csv` を読み込む
- 以下の列を除外して特徴量 `X` を作る
  - `Season`, `Section`, `Date`, `Score`, `Home`, `Away`, `Stadium`
  - `Home_Goals`, `Away_Goals`, `Goal_Diff`, `Match_Result`
- `Weather`, `Backline_Matchup`, `Home_Formation`, `Away_Formation` を One-Hot Encoding する
- `model_step1_goals.predict(X)` でホーム・アウェイの期待得点を出す
- `model_step2_clf.predict_proba(X)` で勝敗確率を出す
- `model_step2_diff.predict(X)` でホーム視点の得失点差を出す
- `finalize_score()` 相当の処理で、0点〜`max_goals`点のスコア候補を列挙し、以下を掛け合わせた値が最大のスコアを最終予測とする
  - ポアソン確率
  - 勝敗確率
  - 点差整合性のガウス密度

### 2. 得点者予測ロジック

参照元:

```text
Notebook/05_Bayer_Table (Goal Player).ipynb
```

ただし、Week2では得点者予測の本格実装は行いません。`scorer_candidates` はWeek5向けの空配列として返します。

---

---

## Week2で作るもの

### 必須作成・更新ファイル

```text
src/predict/__init__.py
src/predict/feature_preprocess.py
src/predict/score_candidates.py
src/predict/predict_match.py
scripts/smoke_test_predict_match.py
docs/week2_completion_report.md
```

### 可能なら追加するファイル

```text
tests/test_predict_match.py
```

`pytest` が未導入の場合は、テストファイル作成は任意です。ただし、最低限 `scripts/smoke_test_predict_match.py` は必ず作成してください。

---

## Week2でやること

1. Week1の特徴量整形処理を再利用可能な関数へ切り出す
2. 単一試合の特徴量行を選択・受け取りできる仕組みを作る
3. 既存3モデルを使って以下を予測する
   - ホーム期待得点
   - アウェイ期待得点
   - ホーム勝利・引き分け・アウェイ勝利確率
   - 予測得失点差
4. 期待得点、勝敗確率、予測得失点差を統合して、スコア候補Top 5を生成する
5. 最有力スコアを `predicted_score` として返す
6. アプリ表示に使えるJSON互換の辞書を返す
7. スモークテストスクリプトで予測結果JSONを標準出力に表示する
8. Week2完了レポートを作成する

---

## Week2でやらないこと

- モデルの再学習
- Optunaなどによるチューニング
- スクレイピング
- 未来試合用の特徴量生成パイプライン
- 次節全試合の一括予測
- `outputs/latest_predictions.json` の本格生成
- Streamlitアプリの実装
- 得点者予測ロジックの本格実装
- GitHub Actionsの実装
- 既存Notebookの大規模修正

---

## 実装方針

### 1. `src/predict/feature_preprocess.py`

Week1のスモークテストに含まれている特徴量整形処理を、再利用可能な関数として切り出してください。

#### 想定する関数

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def load_reference_dataset(dataset_path: str | Path | None = None) -> pd.DataFrame:
    """Data/ML_dataset.csv を読み込む。候補パスも探索する。"""


def prepare_features_for_model(
    row_or_df: pd.Series | pd.DataFrame | dict[str, Any],
    model_features: list[str],
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """
    目的変数・ID列を除外し、カテゴリ列をOne-Hot Encodingし、
    model_features に列順を揃えたDataFrameを返す。

    戻り値:
      - X: モデル入力DataFrame
      - diagnostics: missing_columns / extra_columns などの診断情報
    """
```

#### 除外列候補

存在する列だけ除外してください。

```python
DROP_COLS = [
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

#### One-Hot Encoding対象候補

存在する列だけ処理してください。

```python
CAT_COLS = [
    "Weather",
    "Backline_Matchup",
    "Home_Formation",
    "Away_Formation",
]
```

#### 必須要件

- `pd.get_dummies()` を使ってカテゴリ列をOne-Hot Encodingする
- `model_features` に存在する列順へ必ず揃える
- 学習時に存在したが入力にない列を `missing_columns` として返す
- 入力に存在するが学習時にない列を `extra_columns` として返す
- `NaN` や無限大が残らないようにする
- 数値列に変換できない値が混入した場合は、エラーまたは明示的な警告を出す
- 関数は1行入力でも複数行入力でも動作するようにする

---

### 2. `src/predict/score_candidates.py`

期待得点、勝敗確率、得失点差予測を統合して、スコア候補を生成する処理を分離してください。

#### 予測スコア統合の考え方

全てのスコア候補、初期値では `0-0` から `5-5` まで、を列挙し、以下の3要素を掛け合わせたスコアを計算してください。

1. 期待得点に基づくポアソン確率
2. 勝敗分類モデルの勝敗確率
3. 得失点差モデルの予測値との整合性

#### 想定する関数

```python
from __future__ import annotations

from typing import Any


def generate_score_candidates(
    expected_home_goals: float,
    expected_away_goals: float,
    result_probabilities: dict[str, float],
    predicted_goal_diff: float,
    max_goals: int = 5,
    top_n: int = 5,
    diff_sigma: float = 1.0,
) -> list[dict[str, Any]]:
    """
    スコア候補Top Nを返す。
    """
```

#### 計算仕様

各候補 `(home_goals, away_goals)` について以下を計算します。

```text
poisson_prob = P(HomeGoals = home_goals) * P(AwayGoals = away_goals)
result_weight = 候補スコアの勝敗に対応する勝敗確率
diff_weight = norm_pdf(candidate_diff, mean=predicted_goal_diff, sigma=diff_sigma)
combined_score = poisson_prob * result_weight * diff_weight
```

`diff_weight` は、参照元Notebookの以下の処理を再現してください。

```python
l_diff = norm.pdf(gh - ga, loc=pred_diff, scale=1.0)
```

`scipy.stats.norm.pdf` を使ってもよいです。依存を避ける場合は、以下の式で同等実装してください。

```python
diff_weight = (
    math.exp(-0.5 * ((candidate_diff - predicted_goal_diff) / diff_sigma) ** 2)
    / (diff_sigma * math.sqrt(2 * math.pi))
)
```

候補の勝敗分類は以下としてください。

```python
if home_goals > away_goals:
    result_key = "home_win"
elif home_goals == away_goals:
    result_key = "draw"
else:
    result_key = "away_win"
```

#### 出力例

```python
[
    {
        "score": "2-1",
        "home_goals": 2,
        "away_goals": 1,
        "probability": 0.084,
        "poisson_probability": 0.072,
        "combined_score": 0.00123,
    },
    ...
]
```

#### 注意点

- `expected_home_goals` と `expected_away_goals` が負になった場合は、0.05などの小さな正値に丸める
- `probability` は、列挙した候補内で `combined_score` を正規化した相対確率としてよい
- この `probability` はアプリ表示用の候補内正規化値であり、参照元Notebookには存在しないWeek2用の拡張である
- `combined_score` の計算式と最上位スコアの選び方は、参照元Notebookの `finalize_score()` と一致させる
- `scipy` を使ってもよいが、依存を増やしたくない場合は `math.exp` と `math.factorial` でポアソンPMFを実装する
- `max_goals` と `top_n` は引数で変更可能にする

---

### 3. `src/predict/predict_match.py`

Week2の中心となる単一試合予測関数を実装してください。

#### 想定インターフェース

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def predict_match(
    home_team: str,
    away_team: str,
    match_date: str | None = None,
    *,
    dataset_path: str | Path | None = None,
    model_dir: str | Path | None = None,
    feature_row: pd.Series | dict[str, Any] | None = None,
    max_goals: int = 5,
    top_n_scores: int = 5,
) -> dict[str, Any]:
    """
    指定された1試合について予測結果をJSON互換dictで返す。
    """
```

#### 入力の扱い

- `feature_row` が渡された場合は、それを最優先で使用する
- `feature_row` が渡されない場合は、`dataset_path` または `Data/ML_dataset.csv` から候補行を探す
- `home_team` と `away_team` は `Home` / `Away` 列と照合する
- `match_date` が指定された場合は `Date` 列と照合する
- 完全一致行が複数ある場合は、日付の新しい行を優先する
- 完全一致行がない場合は、同じホーム・アウェイカードの最新行を使ってよい
- それでも候補行が見つからない場合は、無理に特徴量を捏造せず、分かりやすい例外を出す

#### 未来試合についての扱い

Week2では未来試合の特徴量生成は実装しません。

そのため、未来カードに対して以下のどちらかで動く設計にしてください。

1. Week3以降の特徴量生成処理から `feature_row` が渡される
2. `Data/ML_dataset.csv` に同一カードの参照行が存在する場合のみ、その行を使ってデモ予測する

候補行が過去試合である場合は、出力の `feature_source.warnings` に以下のような注意を入れてください。

```text
Data/ML_dataset.csv の過去試合行を参照しているため、未来試合用の最新特徴量ではありません。
```

---

## 予測処理の詳細

### 1. モデル読み込み

`src.models.load_model.load_models()` を使って、以下を読み込んでください。

```python
bundle = load_models(model_dir=model_dir)
```

利用する属性は以下を想定します。

```python
bundle.step1_goals
bundle.step2_clf
bundle.step2_diff
bundle.feature_names
```

### 2. 期待得点予測

```python
expected_goals = bundle.step1_goals.predict(X)[0]
expected_home_goals = float(expected_goals[0])
expected_away_goals = float(expected_goals[1])
```

### 3. 勝敗確率予測

```python
proba = bundle.step2_clf.predict_proba(X)[0]
classes = bundle.step2_clf.classes_
```

勝敗クラスの想定は以下です。

```text
-1: アウェイ勝利
 0: 引き分け
 1: ホーム勝利
```

ただし、必ず `classes_` を見て対応付けしてください。

出力形式は以下に統一してください。

```python
result_probabilities = {
    "home_win": 0.45,
    "draw": 0.27,
    "away_win": 0.28,
}
```

### 4. 得失点差予測

```python
predicted_goal_diff = float(bundle.step2_diff.predict(X)[0])
```

`Goal_Diff = Home_Goals - Away_Goals` として扱ってください。

### 5. スコア候補生成

`generate_score_candidates()` を使って、Top 5のスコア候補を作ってください。

```python
score_candidates = generate_score_candidates(
    expected_home_goals=expected_home_goals,
    expected_away_goals=expected_away_goals,
    result_probabilities=result_probabilities,
    predicted_goal_diff=predicted_goal_diff,
    max_goals=max_goals,
    top_n=top_n_scores,
)
```

最上位候補を `predicted_score` とします。

---

## 返却JSON仕様

`predict_match()` は、以下のようなJSON互換の `dict` を返してください。

```python
{
    "match_id": "2026-J1-unknown-名古屋グランパス-vs-横浜 F・マリノス",
    "date": "2026-05-10",
    "home_team": "名古屋グランパス",
    "away_team": "横浜 F・マリノス",
    "predicted_score": {
        "home": 2,
        "away": 1,
    },
    "expected_goals": {
        "home": 1.62,
        "away": 1.08,
    },
    "result_probabilities": {
        "home_win": 0.45,
        "draw": 0.27,
        "away_win": 0.28,
    },
    "score_candidates": [
        {
            "score": "2-1",
            "home_goals": 2,
            "away_goals": 1,
            "probability": 0.084,
            "poisson_probability": 0.072,
            "combined_score": 0.00123,
        }
    ],
    "predicted_goal_diff": 0.54,
    "scorer_candidates": {
        "home": [],
        "away": [],
    },
    "feature_source": {
        "type": "dataset_row",
        "dataset_path": "Data/ML_dataset.csv",
        "row_index": 123,
        "warnings": []
    },
    "model_info": {
        "feature_count": 164,
        "max_goals": 5,
        "top_n_scores": 5,
    }
}
```

### 必須条件

- 返却値は `json.dumps(result, ensure_ascii=False)` でシリアライズできること
- `numpy.float64` や `numpy.int64` をそのまま返さないこと
- 確率値は `float` に変換すること
- スコアは `int` に変換すること
- `scorer_candidates` はWeek5で使う予定のため、Week2では空配列でよい

---

## チーム名の扱い

Week2では大規模なチーム名マスタ整備は行いませんが、最低限以下の仕組みを入れてください。

```python
TEAM_NAME_ALIASES = {
    "名古屋": "名古屋グランパス",
    "横浜FM": "横浜 F・マリノス",
    "横浜Ｆ・マリノス": "横浜 F・マリノス",
}
```

`normalize_team_name(name: str) -> str` を作り、入力の前後空白を除去し、エイリアスがある場合は標準名に変換してください。

ただし、既存データセット内のチーム名が上記と異なる可能性があるため、標準名変換で一致しない場合は、元の入力名でも検索してよいです。

---

## `scripts/smoke_test_predict_match.py`

単一試合予測の動作確認スクリプトを作成してください。

### 要件

- コマンドライン引数で `--home`、`--away`、`--date` を受け取れるようにする
- 引数未指定の場合は、`Data/ML_dataset.csv` の末尾または最新行から `Home` / `Away` / `Date` を取り出して実行する
- `predict_match()` を呼び出す
- JSONを見やすく標準出力する
- 成功時は `[OK] 単一試合予測テスト成功` を出力する
- 失敗時は例外内容を表示し、`sys.exit(1)` で終了する

### 実行例

```bash
python scripts/smoke_test_predict_match.py
python scripts/smoke_test_predict_match.py --home "名古屋グランパス" --away "横浜 F・マリノス"
python scripts/smoke_test_predict_match.py --home "名古屋グランパス" --away "横浜 F・マリノス" --date "2026-05-10"
```

---

## `tests/test_predict_match.py` を作る場合

可能であれば、以下のテストを追加してください。

```python
def test_generate_score_candidates_returns_top_n():
    ...


def test_predict_match_returns_json_serializable_dict():
    ...


def test_result_probabilities_keys_are_stable():
    ...
```

ただし、テストのために大きなモデルファイルを毎回読み込むと遅くなる場合は、スモークテストを優先してください。

---

## `docs/week2_completion_report.md`

作業完了後、以下の内容を日本語で記載してください。

```markdown
# Week2 完了レポート

## 概要

## 作成・更新したファイル

## 実装した関数

## 予測JSONの形式

## スモークテスト結果

## 実行したコマンド

## 見つかった課題

## Week3への引き継ぎ
```

### Week3への引き継ぎに必ず書くこと

- Week2では未来試合特徴量の自動生成は未実装であること
- Week3では日程データから未消化試合を抽出し、各試合の特徴量行を作って `predict_match()` に渡すこと
- `outputs/latest_predictions.json` はWeek3で本格生成すること
- `scorer_candidates` はWeek5で本格実装すること

---

## 実行してほしい確認コマンド

作業後に以下を実行してください。

```bash
python -m compileall src scripts
python scripts/smoke_test_load_models.py
python scripts/smoke_test_predict_match.py
```

`pytest` を導入または既に利用している場合のみ、以下も実行してください。

```bash
pytest
```

---

## エラー時の対応方針

### モデル読み込みに失敗した場合

- Week1で作成した `src/models/load_model.py` を確認する
- モデルファイル名や `Models/` / `models/` の大文字小文字を確認する
- 既存モデルを再学習しない
- エラー内容を `docs/week2_completion_report.md` に記載する

### `Data/ML_dataset.csv` が見つからない場合

- `Data/ML_dataset.csv`、`data/ML_dataset.csv`、`data/features/*.csv` など候補パスを探索する
- それでも見つからない場合は、分かりやすい例外を出す
- レポートに必要なファイルとして記載する

### 指定されたカードがデータセットに存在しない場合

- 無理に特徴量を捏造しない
- `feature_row` を渡せば予測できる設計にする
- エラーメッセージには、利用可能なチーム名や候補カードの確認方法を含める

### 勝敗クラスの対応が不明な場合

- `bundle.step2_clf.classes_` を出力して確認する
- `-1, 0, 1` 以外のクラスがある場合は例外にする
- 推測でマッピングしない

### スコア候補の確率がすべて0になる場合

- 期待得点が0以下になっていないか確認する
- 期待得点は最低0.05に丸める
- `combined_score` の合計が0の場合は、ポアソン確率のみでフォールバックする

---

## 完了条件

Week2は、以下を満たしたら完了です。

- [ ] `src/predict/feature_preprocess.py` が作成されている
- [ ] `src/predict/score_candidates.py` が作成されている
- [ ] `src/predict/predict_match.py` が作成されている
- [ ] `scripts/smoke_test_predict_match.py` が作成されている
- [ ] `docs/week2_completion_report.md` が作成されている
- [ ] `predict_match(home_team, away_team, match_date)` がJSON互換dictを返す
- [ ] 期待得点、勝敗確率、予測得失点差、スコア候補Top 5が返る
- [ ] `scorer_candidates` は空配列で返る
- [ ] `python -m compileall src scripts` が成功する
- [ ] `python scripts/smoke_test_load_models.py` が成功する
- [ ] `python scripts/smoke_test_predict_match.py` が成功する
- [ ] 既存Notebook、既存CSV、既存pickleを破壊していない
- [ ] Week3で `predict_upcoming.py` を作りやすい構成になっている

---

## Codexの最終回答に含めてほしい内容

作業完了後、以下の形式で日本語で報告してください。

```markdown
## 実施内容

## 作成・更新したファイル

## 実行したコマンド

## 実行結果

## 見つかった問題

## Week3への引き継ぎ
```

---

## 参考：Week3で作る予定のもの

Week2完了後は、次に以下を作ります。

```text
src/predict/predict_upcoming.py
scripts/run_prediction.py
outputs/latest_predictions.json
```

Week3では、日程データから未消化試合または次節カードを抽出し、各試合に対して `predict_match()` を呼び出して、J1次節全試合分の予測JSONを生成します。

Week2ではここまで作らず、単一試合の予測関数を安定させることを優先してください。
