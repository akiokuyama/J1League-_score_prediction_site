# Week4 Streamlit MVP 実装指示書

## 0. この指示書の目的

J1試合結果予測アプリの **Week4: Streamlit MVP** を実装してください。

今回のゴールは、データ取得・特徴量生成・モデル推論を追加することではなく、Week3までに生成できるようになった予測結果JSONを、ユーザーが見やすいWebアプリとして確認できる状態にすることです。

この指示書に従って実装すれば、Week4タスクが完了する状態を目指してください。

---

## 1. 最重要方針

以下は必ず守ってください。

- Streamlitアプリ内でスクレイピングを実行しない
- Streamlitアプリ内で特徴量生成を実行しない
- Streamlitアプリ内でモデル推論を実行しない
- アプリは **既に生成済みのJSON/CSVを読み込んで表示するだけ** にする
- モバイル表示を優先する
- 横並び前提のダッシュボードではなく、スマホで自然に見られる **「一覧 → 詳細」形式** にする
- 既存の推論・データ取得・特徴量生成ロジックを壊さない
- JSONが存在しない、空、キー不足の場合でもアプリが落ちないようにする

---

## 2. 実装対象ファイル

以下を新規作成または更新してください。

```text
app/
  streamlit_app.py
  utils/
    __init__.py
    load_predictions.py
    formatters.py
    evaluation.py
```

必要に応じて以下も更新してください。

```text
requirements.txt
```

`requirements.txt` に `streamlit` がなければ追加してください。

---

## 3. 使用する入力ファイル

### 3.1 これからの試合

基本は以下を読み込んでください。

```text
outputs/latest_predictions.json
```

存在する場合は、将来拡張用として以下も読み込める構造にしてください。

```text
outputs/all_unplayed_predictions.json
```

ただし、MVPでは `outputs/latest_predictions.json` の表示を最優先してください。

### 3.2 過去の予測結果

優先順位は以下です。

1. `outputs/past_prediction_results.json` が存在すればそれを読む
2. 存在しなければ、`outputs/prediction_history/` と `data/processed/matches_2026_special_clean.csv` から作成できる範囲で表示する
3. 難しければ、アプリ上で `過去の予測結果はまだありません。` と表示する

MVPでは、過去予測画面が壊れないことを優先してください。

---

## 4. 期待するJSON構造

### 4.1 latest_predictions.json

以下のような構造を想定してください。

```json
{
  "last_updated": "2026-05-10T14:55:32+09:00",
  "season": "2026_special",
  "league": "J1",
  "matchweek": 12,
  "warnings": [],
  "skipped_matches": [],
  "matches": [
    {
      "match_id": "2026-J1YV-012-001",
      "date": "2026-05-16",
      "kickoff": "14:00",
      "venue": "町田GIONスタジアム",
      "home_team": "町田ゼルビア",
      "away_team": "東京ヴェルディ",
      "predicted_score": {"home": 1, "away": 1},
      "expected_goals": {"home": 1.18, "away": 1.35},
      "result_probabilities": {
        "home_win": 0.2211,
        "draw": 0.2668,
        "away_win": 0.5121
      },
      "score_candidates": [
        {"score": "1-1", "probability": 0.116},
        {"score": "1-2", "probability": 0.104}
      ],
      "scorer_candidates": {
        "home": [
          {"player": "選手A", "probability": 0.21, "position": "FW"}
        ],
        "away": [
          {"player": "選手B", "probability": 0.24, "position": "FW"}
        ]
      }
    }
  ]
}
```

実際のJSONに一部キーがなくても落ちないように、防御的に実装してください。

### 4.2 past_prediction_results.json

過去予測ファイルを新規に扱う場合は、以下の形式を推奨します。

```json
{
  "season": "2026_special",
  "league": "J1",
  "matches": [
    {
      "match_id": "2026-J1YV-011-001",
      "matchweek": 11,
      "date": "2026-05-06",
      "kickoff": "19:00",
      "venue": "豊田スタジアム",
      "home_team": "名古屋グランパス",
      "away_team": "浦和レッズ",
      "predicted_score": {"home": 1, "away": 0},
      "actual_score": {"home": 2, "away": 1},
      "result_probabilities": {
        "home_win": 0.46,
        "draw": 0.31,
        "away_win": 0.23
      },
      "score_candidates": [
        {"score": "1-0", "probability": 0.128}
      ]
    }
  ]
}
```

---

## 5. 画面全体の構成

Streamlitアプリの上部に以下を表示してください。

### 5.1 ヘッダー

表示項目：

- アプリ名：`J1 試合結果予測アプリ`
- 説明文：`次節の試合予測と過去の予測結果を確認できます。`
- Season
- Matchweek
- 最終更新

`last_updated` は以下の形式に変換して表示してください。

```text
2026年5月10日 14時55分
```

例：

```python
"2026-05-10T14:55:32+09:00" -> "2026年5月10日 14時55分"
```

### 5.2 メイン切替

上部に以下2つの切替を作ってください。

```text
これからの試合
過去の予測結果
```

Streamlitの実装方法は任意です。

推奨：

```python
tab = st.radio(
    "表示切替",
    ["これからの試合", "過去の予測結果"],
    horizontal=True,
)
```

`st.tabs()` でも構いませんが、モバイルでは `radio(horizontal=True)` の方が扱いやすい場合があります。

---

# 6. 「これからの試合」画面

## 6.1 一覧画面

`latest_predictions.json` の `matches` をカード形式で一覧表示してください。

各カードに以下を表示してください。

- 試合日
- キックオフ時刻があれば表示
- 会場があれば表示
- ホームチーム vs アウェイチーム
- 勝敗確率トップ
- 見立てラベル
- 予測スコア
- `詳細を見る` ボタン

### 6.1.1 一覧から詳細への動線

モバイルで見やすいように、一覧と詳細は横並びにしないでください。

以下の導線にしてください。

```text
試合一覧
  ↓
詳細を見る
  ↓
試合詳細
  ↓
← 試合一覧に戻る
```

Streamlitでは `st.session_state` を使って以下を管理してください。

- 現在の表示状態：`list` / `detail`
- 選択中の `match_id`

例：

```python
if "view" not in st.session_state:
    st.session_state.view = "list"

if "selected_match_id" not in st.session_state:
    st.session_state.selected_match_id = None
```

### 6.1.2 見立てラベル

表示するラベルは以下の2種類のみです。

- `ホーム優勢`
- `アウェイ優勢`

判定ルール：

```python
home_win, draw, away_win のうち最大が home_win の場合 -> ホーム優勢
home_win, draw, away_win のうち最大が away_win の場合 -> アウェイ優勢
draw が最大の場合 -> ラベルなし
```

以下のラベルは表示しないでください。

- 接戦
- 引き分け注意
- 波乱含み
- 拮抗

## 6.2 詳細画面

一覧で `詳細を見る` を押した試合について、詳細画面を表示してください。

詳細画面の最上部に、以下の戻るボタンを表示してください。

```text
← 試合一覧に戻る
```

詳細画面に表示する内容：

- 試合日・キックオフ・会場
- ホームチーム vs アウェイチーム
- 予測スコア
- 勝敗確率トップ
- 見立てラベル
- 結論カード
- ホーム期待得点
- アウェイ期待得点
- 最有力スコア候補
- 勝敗確率バー
- スコア候補Top5
- 得点者候補Top5

---

## 6.3 結論カード

詳細画面の上部に、ユーザーが一目で見立てを理解できる結論カードを表示してください。

### 6.3.1 予測スコアと勝敗確率トップが一致する場合

例：

```text
この試合の見立て：予測スコアは 1-0、勝敗確率トップは ホーム勝利 です。試合傾向は「ホーム優勢」です。
```

### 6.3.2 予測スコアと勝敗確率トップがズレる場合

例：

```text
この試合の見立て：単一スコアでは 1-1 が最有力です。ただし勝敗確率では アウェイ勝利 が最も高くなっています。試合傾向は「アウェイ優勢」です。
```

### 6.3.3 引き分けが勝敗確率トップの場合

引き分けがトップの場合、見立てラベルは表示しなくて構いません。

例：

```text
この試合の見立て：予測スコアは 1-1、勝敗確率トップは 引き分け です。
```

---

## 6.4 勝敗確率の表示

勝敗確率は以下3つを表示してください。

- ホーム勝利
- 引き分け
- アウェイ勝利

可能であれば `st.progress()` または横棒の簡易表示を使ってください。

表示例：

```text
ホーム勝利 22.1%
引き分け 26.7%
アウェイ勝利 51.2%
```

確率は以下の形式で表示してください。

```text
51.2%
```

---

## 6.5 勝敗確率の注意書き

### 6.5.1 常に表示する短い注記

勝敗確率の下に、以下の注記を表示してください。

```text
勝敗確率は「勝ち・引き分け・負け」という結果カテゴリごとの合算値です。予測スコアとは計算単位が異なります。
```

### 6.5.2 予測スコアと勝敗確率トップがズレる場合の説明

予測スコアと勝敗確率トップがズレる場合、以下のような説明を表示してください。

```text
なぜ「1-1」なのにアウェイ勝利が高いのか？

予測スコアは、個別のスコア候補の中で最も選ばれやすい1つを表示しています。
一方、勝敗確率は「0-1」「1-2」「0-2」など、アウェイが勝つ複数のスコア候補を合算した確率です。
そのため、単一スコアでは 1-1 が最上位でも、勝敗全体ではアウェイ勝利が最も高くなる場合があります。
```

スコアやチームは実データに合わせて置換できるようにしてください。

---

## 6.6 スコア候補Top5

`score_candidates` を最大5件表示してください。

表示項目：

- 順位
- スコア
- 確率

`score_candidates` がない場合は、以下を表示してください。

```text
スコア候補はありません。
```

---

## 6.7 得点者候補Top5

得点者候補は情報量が多いため、初期表示では折りたたんでください。

Streamlitでは以下のように実装してください。

```python
with st.expander("得点者候補 Top 5", expanded=False):
    ...
```

表示内容：

- ホームチームの得点者候補Top5
- アウェイチームの得点者候補Top5
- 選手名
- ポジションがあれば表示
- 確率があれば表示

`scorer_candidates` が存在しない場合や空の場合は、エラーにせず以下を表示してください。

```text
得点者候補はまだありません。
```

---

# 7. 「過去の予測結果」画面

## 7.1 目的

過去に出した予測と実際の試合結果を並べて表示し、ユーザーがモデルの当たり具合を確認できるようにしてください。

---

## 7.2 表示内容

過去予測画面には以下を表示してください。

1. 成績サマリー
2. 絞り込み
3. 過去予測カード一覧

---

## 7.3 成績サマリー

画面上部に以下を表示してください。

- 勝敗的中率
- スコア的中率
- 直近表示試合数

表示形式は、パーセントをメインにし、括弧で件数を表示してください。

例：

```text
勝敗的中率：66.7%（2/3）
スコア的中率：0.0%（0/3）
直近表示試合数：3
```

ここでの件数は、絞り込み後に表示されている試合を対象にしてください。

---

## 7.4 絞り込み

以下の絞り込みを追加してください。

- 節
- チーム
- 判定結果

判定結果の選択肢：

```text
すべての判定
勝敗的中
勝敗外れ
スコア的中
スコア外れ
```

絞り込み後、成績サマリーも絞り込み後の件数で再計算してください。

---

## 7.5 過去予測カード

各カードに以下を表示してください。

- 試合日
- キックオフ時刻があれば表示
- 会場があれば表示
- ホームチーム vs アウェイチーム
- 勝敗的中 / 勝敗外れ
- スコア的中 / スコア外れ
- 予測スコア
- 実際のスコア
- 予測の勝敗方向
- 実際の勝敗方向

### 7.5.1 ラベルは2系統に分ける

ラベルは必ず以下の2系統を別々に表示してください。

#### 勝敗判定

- 勝敗的中
- 勝敗外れ

判定ルール：

```python
予測スコアから home / draw / away を判定
実際のスコアから home / draw / away を判定
一致すれば 勝敗的中
一致しなければ 勝敗外れ
```

#### スコア判定

- スコア的中
- スコア外れ

判定ルール：

```python
予測スコアの home / away が実際のスコアと完全一致すれば スコア的中
そうでなければ スコア外れ
```

### 7.5.2 判定説明

カードごとに長い説明文は表示しないでください。

説明は過去予測画面の上部に1回だけ表示してください。

```text
判定の見方：「勝敗」は勝ち・引き分け・負けの方向性で判定し、「スコア」は点数まで完全一致したかで判定します。
```

---

# 8. 実装する関数

以下のような関数を作成してください。

## 8.1 app/utils/load_predictions.py

```python
from pathlib import Path
from typing import Any

def load_json_file(path: str | Path) -> dict[str, Any]:
    """JSONを安全に読み込む。存在しない、壊れている場合は空dictを返す。"""
    ...

def load_latest_predictions(path: str | Path = "outputs/latest_predictions.json") -> dict[str, Any]:
    ...

def load_all_unplayed_predictions(path: str | Path = "outputs/all_unplayed_predictions.json") -> dict[str, Any]:
    ...

def load_past_prediction_results(path: str | Path = "outputs/past_prediction_results.json") -> dict[str, Any]:
    """過去予測結果を読み込む。存在しなければ空のmatchesを返す。"""
    ...
```

`load_json_file()` は例外でアプリを落とさないでください。

---

## 8.2 app/utils/formatters.py

```python
from datetime import datetime

def format_datetime_jp(value: str | None) -> str:
    """ISO datetimeを '2026年5月10日 14時55分' 形式に変換する。"""
    ...

def format_percent(value: float | int | None, digits: int = 1) -> str:
    """0.5121 -> '51.2%' に変換する。"""
    ...

def format_score(score: dict | None) -> str:
    """{'home': 1, 'away': 0} -> '1-0' に変換する。"""
    ...

def format_accuracy(hits: int, total: int) -> str:
    """2, 3 -> '66.7%（2/3）' に変換する。"""
    ...
```

---

## 8.3 app/utils/evaluation.py

```python
from typing import Literal

Outcome = Literal["home", "draw", "away", "unknown"]

def get_score_outcome(score: dict | None) -> Outcome:
    ...

def get_strongest_outcome(probabilities: dict | None) -> dict:
    """
    戻り値例:
    {
        "key": "away",
        "label": "アウェイ勝利",
        "value": 0.5121
    }
    """
    ...

def get_match_insight_label(probabilities: dict | None) -> str | None:
    """
    home_win が最大 -> 'ホーム優勢'
    away_win が最大 -> 'アウェイ優勢'
    draw が最大 -> None
    """
    ...

def evaluate_prediction(predicted_score: dict | None, actual_score: dict | None) -> dict:
    """
    戻り値例:
    {
        "result_hit": True,
        "score_hit": False,
        "result_label": "勝敗的中",
        "score_label": "スコア外れ",
        "predicted_outcome": "home",
        "actual_outcome": "home",
    }
    """
    ...
```

---

# 9. Streamlit実装の注意

## 9.1 モバイル優先

- 横幅が狭くても読みやすい縦積みレイアウトにする
- `st.columns()` を多用しすぎない
- 大きなテーブルだけに頼らず、カード形式で表示する
- 詳細は一覧から遷移する形にする

## 9.2 CSS

CSSを使う場合は最小限にしてください。

使用してよい例：

- カード風の枠
- ラベルの背景色
- 余白調整
- 小さな注記の文字色

ただし、CSSがなくても最低限見られる構成にしてください。

## 9.3 エラー・空データ対応

以下のケースでもアプリを落とさないでください。

- `outputs/latest_predictions.json` が存在しない
- JSONが壊れている
- `matches` が空
- `score_candidates` が存在しない
- `scorer_candidates` が存在しない
- `expected_goals` が存在しない
- `result_probabilities` が存在しない
- 過去予測データが存在しない

表示例：

```text
予測データが見つかりません。
```

```text
過去の予測結果はまだありません。
```

---

# 10. やらないこと

今回の実装では以下は行わないでください。

- スクレイピング追加
- 特徴量生成ロジックの修正
- モデル再学習
- 予測ロジックの変更
- GitHub Actions化
- DB導入
- 認証機能追加
- PWA化
- Notebookの大幅修正

---

# 11. 動作確認

以下で起動できることを確認してください。

```bash
streamlit run app/streamlit_app.py
```

最低限、以下も確認してください。

```bash
python -m compileall app
```

可能であれば既存テストも実行してください。

```bash
pytest
```

ただし、pytestが環境にない場合は、実行不能であることを報告してください。

---

# 12. 確認項目

実装後、以下を確認してください。

## これからの試合

- `latest_predictions.json` が読み込まれる
- これからの試合一覧が表示される
- 試合カードに予測スコアが表示される
- 勝敗確率トップが表示される
- ホーム優勢 / アウェイ優勢 のみ表示される
- 試合カードの `詳細を見る` から詳細へ進める
- 詳細から `← 試合一覧に戻る` で戻れる
- 結論カードが表示される
- 勝敗確率の説明が表示される
- 予測スコアと勝敗確率トップがズレる場合、追加説明が表示される
- スコア候補Top5が表示される
- 得点者候補が折りたたみ表示される

## 過去の予測結果

- 過去の予測結果画面に切り替えられる
- 過去予測がない場合もアプリが落ちない
- 過去予測がある場合、予測スコアと実際のスコアが並んで表示される
- 勝敗的中 / 勝敗外れ が表示される
- スコア的中 / スコア外れ が表示される
- 勝敗的中率が `66.7%（2/3）` 形式で表示される
- スコア的中率が `0.0%（0/3）` 形式で表示される
- 節・チーム・判定結果で絞り込みできる
- 絞り込み後に成績サマリーが再計算される

---

# 13. 完了条件

以下を満たしたらWeek4完了とします。

- `streamlit run app/streamlit_app.py` でローカル起動できる
- モバイル幅でも見やすい
- 「これからの試合」と「過去の予測結果」を切り替えられる
- これからの試合では、一覧から詳細に進める
- 詳細では、予測スコア、勝敗確率、期待得点、スコア候補、得点者候補を確認できる
- 得点者候補は折りたたみ表示になっている
- 過去予測では、勝敗判定とスコア判定が別々に表示される
- 的中率はパーセント + 件数形式で表示される
- JSON不足や空データでもアプリが落ちない
- 既存のデータ取得・特徴量生成・推論処理に影響を与えていない

---

# 14. 実装完了後に報告してほしい内容

作業完了後、以下を報告してください。

- 作成・更新したファイル一覧
- Streamlit起動確認結果
- `python -m compileall app` の結果
- pytestを実行した場合は結果
- pytestを実行できなかった場合は理由
- 既知の制約や今後の改善候補

---

# 15. 参考資料
/Users/akihirookuyama/Soccer_Score_App/docs/week4/week_4_streamlit_mock.jsxのTypeScript/Reactコードは、UIの見た目・文言・画面遷移を確認するためのモックです。
実装対象はReactではなく、Streamlitです。
このコードをそのまま移植するのではなく、同じ表示仕様をStreamlitで再現してください。

以上。
