# Codex指示書：Week5 得点者候補・過去予測結果・簡易精度指標の整備

## 目的

この指示書は、J1試合結果予測アプリ開発ロードマップの **Week5** 作業をCodexに依頼するためのものです。

Week5では、いきなり実装を追加するのではなく、まず **現状で提案内容が再現できているか** を確認してください。

確認の結果、すでに十分実装済みであれば、不要な実装は行わず、確認結果と不足点だけを報告してください。未実装または再現できない部分がある場合は、勝手に実装を進めず、どの方針で進めるべきかをユーザーに確認してください。

---

## 今回の最重要ルール

1. **最初に現状確認だけを行うこと**
   - 既存コード、既存JSON、既存テスト、既存UIの状態を確認する。
   - この段階では、原則としてファイルを変更しない。

2. **提案内容が再現できているかを判定すること**
   - 得点者候補Top5が生成されているか。
   - 得点者候補がStreamlitで表示されているか。
   - 過去予測結果JSONが存在し、アプリで読めるか。
   - 過去予測結果JSONを自動生成する処理があるか。
   - `model_metrics.json` または同等の簡易精度指標出力があるか。
   - テストでこれらが検証されているか。

3. **未実装・不明点がある場合は、すぐに実装しないこと**
   - 不足点を一覧化する。
   - 実装案を提示する。
   - ユーザーに「この方針で進めてよいか」を確認してから実装する。

4. **既存のデータ取得・特徴量生成・スコア予測モデルは原則変更しないこと**
   - Week5の主目的は、得点者候補・過去予測結果・簡易精度指標の整備である。
   - データ取得ロジックやモデル再学習ロジックを大きく変更しない。

5. **`latest_predictions.json` を壊さないこと**
   - 出力ファイルを更新する場合は、一時ファイルに保存し、検証成功後に置換する。
   - 既存の `outputs/latest_predictions.json` を破損させる変更は禁止。

6. **すべての説明文・レポート・コメントは日本語で書くこと**
   - ただし、Python関数名・変数名・ファイル名は英語でよい。

---

## Week5で確認したい背景

Week4完了時点で、以下は実装済みと報告されています。

- `outputs/latest_predictions.json` を読み込むStreamlit MVP
- 「これからの試合」と「過去の予測結果」の切り替え
- 試合一覧から詳細画面への遷移
- 得点者候補Top5の折りたたみ表示
- `outputs/past_prediction_results.json` が存在する場合の過去予測結果表示
- 過去予測の勝敗的中率・スコア的中率表示
- `pytest` 7 passed

一方で、Week5以降への引き継ぎとして、以下が候補に挙がっています。

- 得点者候補表示の改善
- 過去予測結果JSONの自動生成処理
- モデル精度画面の追加
- GitHub Actionsによる手動実行ワークフロー
- README更新

したがって、Week5では **既にできていることを重複実装しない** ことが重要です。

---

## Phase 0：現状確認のみ実施

まず、以下を実行・確認してください。この段階では、原則としてコード変更をしないでください。

### 0.1 リポジトリ構成確認

```bash
pwd
find . -maxdepth 3 -type f | sort | sed 's#^./##' | head -300
```

確認観点:

- `app/streamlit_app.py` が存在するか
- `app/utils/evaluation.py` が存在するか
- `app/utils/formatters.py` が存在するか
- `app/utils/load_predictions.py` が存在するか
- `src/predict/` 配下に得点者候補関連の処理があるか
- `src/features/` 配下に得点者特徴量関連の処理があるか
- `scripts/` 配下に過去予測結果生成や評価指標生成のスクリプトがあるか
- `tests/` 配下に関連テストがあるか

### 0.2 既存出力ファイル確認

```bash
ls -la outputs || true
find outputs -maxdepth 3 -type f | sort || true
```

確認対象:

- `outputs/latest_predictions.json`
- `outputs/all_unplayed_predictions.json`
- `outputs/past_prediction_results.json`
- `outputs/model_metrics.json`
- `outputs/prediction_history/`

### 0.3 JSON構造確認

以下のPythonワンライナーまたは同等のスクリプトで、既存JSONを確認してください。

```bash
python - <<'PY'
import json
from pathlib import Path

for path in [
    Path('outputs/latest_predictions.json'),
    Path('outputs/all_unplayed_predictions.json'),
    Path('outputs/past_prediction_results.json'),
    Path('outputs/model_metrics.json'),
]:
    print(f'\n=== {path} ===')
    if not path.exists():
        print('MISSING')
        continue
    data = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data, dict):
        print('top_keys:', sorted(data.keys()))
        matches = data.get('matches') or data.get('results') or []
        print('record_count:', len(matches) if isinstance(matches, list) else 'not-list')
        if isinstance(matches, list) and matches:
            first = matches[0]
            print('first_keys:', sorted(first.keys()) if isinstance(first, dict) else type(first))
            if isinstance(first, dict):
                print('scorer_candidates:', first.get('scorer_candidates'))
    elif isinstance(data, list):
        print('list_count:', len(data))
        if data:
            print('first_keys:', sorted(data[0].keys()) if isinstance(data[0], dict) else type(data[0]))
    else:
        print('type:', type(data))
PY
```

確認観点:

- `latest_predictions.json` の各試合に `scorer_candidates.home` / `scorer_candidates.away` があるか
- 各チームの候補がTop5になっているか
- 候補に `player` / `name` / `position` / `score` / `probability` / `rank` 相当の情報があるか
- `past_prediction_results.json` が存在するか
- 予測スコア、実スコア、勝敗的中、スコア的中を判定できる構造か
- `model_metrics.json` が存在するか

### 0.4 既存コードのgrep確認

```bash
grep -R "scorer_candidates\|scorer_score\|Goal Propensity\|GPS\|past_prediction\|model_metrics\|accuracy\|exact" -n app src scripts tests docs 2>/dev/null || true
```

確認観点:

- 得点者候補スコア計算がどこで実装されているか
- 過去予測結果JSON生成処理がどこにあるか
- モデル精度指標生成処理がどこにあるか
- Streamlit表示だけがあり、生成処理がない状態ではないか

### 0.5 既存テスト・コンパイル確認

```bash
python -m compileall app src scripts
pytest
```

`pytest` が未導入の場合は、以下のように状況を報告してください。

```bash
python -m pytest
```

失敗した場合は、以下を報告してください。

- 失敗したコマンド
- エラーメッセージ
- 依存関係不足か、コード不具合か、データ不足か
- 実装前にユーザー確認が必要か

---

## Phase 0の報告フォーマット

Phase 0が終わったら、実装に進む前に、必ず以下の形式でユーザーに報告してください。

```markdown
## Week5 現状確認結果

### 実行したコマンド

### 確認結果サマリー

| 確認項目 | 結果 | 根拠 |
|---|---|---|
| scorer_candidates が latest_predictions.json に存在する | OK / NG / 不明 | ... |
| 得点者候補Top5がhome/awayで出力されている | OK / NG / 不明 | ... |
| 得点者候補の計算ロジックが関数化されている | OK / NG / 不明 | ... |
| Streamlitで得点者候補を表示できる | OK / NG / 不明 | ... |
| past_prediction_results.json が存在する | OK / NG / 不明 | ... |
| past_prediction_results.json を自動生成する処理がある | OK / NG / 不明 | ... |
| model_metrics.json が存在する | OK / NG / 不明 | ... |
| model_metrics.json を自動生成する処理がある | OK / NG / 不明 | ... |
| 関連テストがある | OK / NG / 不明 | ... |

### すでに実装済みと判断したもの

### 不足しているもの

### 実装が必要な場合の提案方針

A案: 最小対応
- ...

B案: しっかり対応
- ...

### ユーザーへの確認

上記のうち、どの方針で進めるべきか確認したいです。
```

この報告を行うまでは、原則としてファイルを変更しないでください。

---

## Phase 1：ユーザー承認後に実装する候補

ユーザーが承認した場合のみ、以下の実装に進んでください。

### 1. 得点者候補スコア計算ロジックの整理

既に実装済みの場合は、重複作成せず、既存関数を整えるだけにしてください。

候補ファイル:

```text
src/predict/predict_scorers.py
src/features/build_scorer_features.py
```

想定関数:

```python
def calculate_goal_propensity_score(row: dict | pd.Series) -> float:
    """Football Lab選手スタッツからGoal Propensity Scoreを計算する。"""


def build_team_scorer_candidates(
    player_stats: pd.DataFrame,
    team: str,
    top_n: int = 5,
) -> list[dict]:
    """指定チームの得点者候補TopNを返す。"""


def attach_scorer_candidates_to_predictions(
    predictions: dict,
    player_stats: pd.DataFrame,
    top_n: int = 5,
) -> dict:
    """予測JSONの各試合にscorer_candidatesを付与する。"""
```

GPS計算の基本方針:

```text
GPS = goal_point_90 * 1.0 + shoot_point_90 * 0.5 + cbp_attack_90 * 0.2
```

補正方針:

- 出場試合数が3試合未満の選手は、GPSに0.1を掛ける
- FWは1.2倍
- DFは0.8倍
- MF/GK/不明ポジションは1.0倍
- 欠損値は0として扱う
- GPSが負になる場合は0に丸める
- チーム内合計が0の場合は、候補を空配列にするか、スコア0として返す。ただし、勝手に確率を捏造しない

候補JSONの推奨形式:

```json
{
  "rank": 1,
  "player": "選手名",
  "team": "team_code_or_name",
  "position": "FW",
  "score": 1.2345,
  "probability": 0.184,
  "source": "football_lab_player_stats"
}
```

互換性のため、既存UIが `name` など別キーを参照している場合は、既存キーを壊さず、新キーを追加する形にしてください。

### 2. 得点者候補表示の改善

既に得点者候補Top5が表示されている場合は、大きなUI変更は避け、以下の改善に留めてください。

- ポジションを表示する
- score または probability を表示する
- 「スタメン・怪我・出場停止は未反映」という注意書きを表示する
- データがない場合は「得点者候補データがありません」と表示し、アプリを落とさない

### 3. 過去予測結果JSONの自動生成

既に生成処理がある場合は、それを再利用してください。

候補ファイル:

```text
src/evaluation/past_predictions.py
scripts/build_past_prediction_results.py
```

入力候補:

```text
outputs/prediction_history/*.json
outputs/latest_predictions.json
outputs/all_unplayed_predictions.json
data/processed/matches_2026_special_clean.csv
data/features/match_features_2026_special.csv
```

出力:

```text
outputs/past_prediction_results.json
```

出力JSONに含めたい項目:

```json
{
  "last_updated": "2026-05-17T00:00:00+09:00",
  "season": "2026_special",
  "results": [
    {
      "match_id": "...",
      "date": "2026-05-10",
      "matchweek": 12,
      "section": 12,
      "home_team": "...",
      "away_team": "...",
      "predicted_score": {"home": 1, "away": 0},
      "actual_score": {"home": 2, "away": 1},
      "predicted_result": "home_win",
      "actual_result": "home_win",
      "is_result_correct": true,
      "is_score_correct": false
    }
  ]
}
```

注意:

- 実スコアが未確定の試合は除外する
- `match_id` が一致しない場合は、日付・ホーム・アウェイでマッチングしてよい
- マッチングできない試合は `warnings` に記録する
- 既存JSONを破壊しないよう、一時ファイルに書いてから検証後に置換する

### 4. model_metrics.json の生成

候補ファイル:

```text
src/evaluation/metrics.py
scripts/build_model_metrics.py
```

入力:

```text
outputs/past_prediction_results.json
```

出力:

```text
outputs/model_metrics.json
```

出力例:

```json
{
  "last_updated": "2026-05-17T00:00:00+09:00",
  "season": "2026_special",
  "sample_size": 4,
  "result_accuracy": 0.5,
  "score_exact_match_rate": 0.25,
  "home_goal_mae": 0.75,
  "away_goal_mae": 0.5,
  "period": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-17"
  }
}
```

注意:

- 対象試合数が0の場合は、0除算せず、指標は `null` にする
- JSONとして読み込めることを検証する
- Streamlit側で読み込めない形式にしない

### 5. Streamlitのモデル精度表示

既に過去予測画面で勝敗的中率・スコア的中率を表示できている場合は、新しいページを増やす必要はありません。

実装する場合は、以下のどちらかにしてください。

- 既存の「過去の予測結果」画面に `model_metrics.json` の概要を追加する
- 既存構成に合う場合のみ、モデル精度セクションを追加する

表示項目:

- 対象試合数
- 勝敗的中率
- スコア完全的中率
- Home MAE
- Away MAE
- 評価期間

---

## テスト追加方針

ユーザー承認後に実装する場合は、可能な範囲で以下のテストを追加してください。

候補:

```text
tests/test_scorer_candidates.py
tests/test_past_prediction_results.py
tests/test_model_metrics.py
```

最低限確認したいこと:

- GPS計算式が期待通りに動く
- 出場試合数補正が効く
- ポジション補正が効く
- scorer_candidates がhome/awayにTop5以内で入る
- 過去予測結果で勝敗的中・スコア的中が正しく判定される
- 対象試合数0でも `model_metrics.json` 生成が落ちない
- 壊れたJSONや欠損キーでもStreamlitが落ちない

---

## 実行してほしい確認コマンド

実装後は以下を実行してください。

```bash
python -m compileall app src scripts
pytest
```

必要なスクリプトを追加した場合は、以下も実行してください。

```bash
python scripts/run_prediction.py --mode next_section
python scripts/build_past_prediction_results.py
python scripts/build_model_metrics.py
```

ただし、該当スクリプトが存在しない場合や、ユーザー承認前の場合は実行しないでください。

---

## 完了条件

Week5は、以下を満たしたら完了とします。

- [ ] Phase 0の現状確認結果をユーザーに報告している
- [ ] 未実装部分について、ユーザー確認後に実装している
- [ ] 得点者候補の計算ロジックまたは既存実装の所在が明確になっている
- [ ] `latest_predictions.json` の `scorer_candidates` 形式が確認または整備されている
- [ ] Streamlit上で得点者候補が安全に表示される
- [ ] `past_prediction_results.json` の自動生成処理が存在する、または未実装理由が明確になっている
- [ ] `model_metrics.json` の生成処理が存在する、または未実装理由が明確になっている
- [ ] 関連テストが追加または確認されている
- [ ] `python -m compileall app src scripts` が成功する
- [ ] `pytest` が成功する、または実行不可の理由が報告されている
- [ ] `docs/week5_completion_report.md` が作成されている

---

## docs/week5_completion_report.md に書く内容

作業完了後、以下の構成で日本語の完了レポートを作成してください。

```markdown
# Week5 完了レポート

## 概要

## Phase 0 現状確認結果

## 実施した作業

## 作成・更新したファイル

## 得点者候補ロジックの確認結果

## past_prediction_results.json の生成結果

## model_metrics.json の生成結果

## Streamlit表示確認結果

## テスト結果

## 実行したコマンド

## 見つかった問題

## Week6への引き継ぎ
```

Week6への引き継ぎには、必要に応じて以下を記載してください。

- GitHub Actionsの手動実行化に進める状態か
- `full_pipeline.py` に過去予測結果生成・metrics生成を組み込むべきか
- Streamlit Community Cloud公開前に必要なREADME更新があるか

---

## Codexの最終回答に含める内容

Codexの最終回答は、以下の形式で日本語で報告してください。

```markdown
## 実施内容

## 作成・更新したファイル

## 実行したコマンド

## 実行結果

## 見つかった問題

## ユーザー確認が必要な事項

## Week6への引き継ぎ
```

---

## 禁止事項

- ユーザー確認前に大きな実装へ進むこと
- 既存Notebookを大きく書き換えること
- 既存CSV、既存pickle、既存JSONを理由なく削除すること
- `latest_predictions.json` を検証なしに直接上書きすること
- モデル再学習を勝手に実行すること
- スクレイピング範囲を勝手に広げること
- 得点者候補に、データに存在しない選手を推測で追加すること
- 怪我・出場停止・スタメン情報を取得していないのに、反映済みのように表示すること
