# Codex 指示書：Week5追加対応（過去予測評価・モデル指標の扱い修正）

## 目的

Week5で追加した過去予測結果生成・モデル指標生成まわりについて、以下を修正してください。

1. `match_id` 不一致と、実スコア未確定による評価対象外を明確に切り分ける。
2. `build_past_prediction_results.py` のログ・診断情報を改善する。
3. 正常系・評価対象外・不一致ケースのテストを追加する。
4. `model_metrics.json` はローカル確認専用とし、Streamlitなどユーザーが見る画面には表示しない。
5. Week5完了レポートの不正確な記述を修正する。

重要：今回は大きな機能追加ではなく、Week5実装の検証性・安全性・表現の正確性を高めるための追加対応です。

---

## 最初に必ず実施すること：Phase 0 現状確認

いきなり実装に入らず、まず以下を確認してください。

### 0.1 予測履歴と試合結果データの状態確認

以下を確認してください。

- `outputs/prediction_history/*.json` に含まれる予測件数
- 代表的な `match_id`
- `data/processed/matches_2026_clean.csv` または `Data/processed/matches_2026_clean.csv` の存在有無
- 試合結果CSV側の同一 `match_id` の有無
- 一致した試合の `status`
- 一致した試合の `home_score` / `away_score`

現時点で想定している状態は以下です。

```text
match_id は一致している。
ただし、該当試合は status=unplayed かつ home_score/away_score が NaN のため、過去予測評価の対象外である。
```

もしこの想定と異なる場合は、実装に入らず、以下を報告して停止してください。

```text
- prediction_history 側の match_id 例
- 試合結果CSV側の match_id 例
- match_id一致件数
- status=finished の件数
- home_score/away_score が両方存在する件数
- 想定と異なる点
- 推奨対応案
```

### 0.2 Streamlit上のモデル指標表示確認

以下を確認してください。

- `app/streamlit_app.py` で `model_metrics.json` を読み込んでいるか
- `app/utils/load_predictions.py` に `load_model_metrics()` があるか
- Streamlitの「過去の予測結果」画面などで、勝敗Accuracy、スコア的中率、MAEなどのモデル指標を表示しているか

ユーザー向け画面にモデル指標が表示されている場合は、今回の対応で非表示にしてください。

---

## 対応方針

## 1. 過去予測結果生成スクリプトのログ改善

対象候補：

- `scripts/build_past_prediction_results.py`
- `src/evaluation/past_predictions.py`

`past_prediction_results.json` の生成時に、単に「結合0件」と出すのではなく、以下の段階別件数を出力してください。

```text
prediction_history_files: N
prediction_history_matches: N
matches_rows: N
match_id_matched: N
finished_matched: N
score_complete_matched: N
evaluation_target_matches: N
unmatched_prediction_matches: N
matched_but_unplayed: N
matched_but_missing_score: N
```

定義は以下を想定します。

- `match_id_matched`: prediction_history の match_id が試合結果CSVにも存在する件数
- `finished_matched`: match_id が一致し、かつ `status == "finished"` の件数
- `score_complete_matched`: match_id が一致し、かつ `home_score` / `away_score` が両方存在する件数
- `evaluation_target_matches`: match_id が一致し、`status == "finished"` かつ `home_score` / `away_score` が両方存在する件数
- `matched_but_unplayed`: match_id は一致したが `status != "finished"` の件数
- `matched_but_missing_score`: match_id は一致したがスコアが欠損している件数

標準出力で読める形にしてください。可能であれば、関数の戻り値にも診断情報を含めて、テストしやすくしてください。

### 重要な挙動

現状どおり、評価対象が0件の場合は、デフォルトでは既存の `outputs/past_prediction_results.json` を空で上書きしないでください。

`--allow-empty` が指定された場合のみ、空の結果で上書きしてよいです。

---

## 2. `match_id` に関するレポート文言修正

対象候補：

- `docs/week5_completion_report.md`
- もし `docs/` ではなく別パスにある場合は、実際の Week5 完了レポート

現在の記述に、以下のような不正確な表現がある場合は修正してください。

```text
過去予測履歴と実スコア付き試合の match_id が一致するデータがありませんでした。
```

正しい表現は以下です。

```text
予測履歴と試合結果データの match_id は一致していましたが、該当試合は status=unplayed かつ home_score/away_score が未確定だったため、過去予測評価の対象外でした。
そのため、実データ由来の past_prediction_results.json はまだ生成できていません。
```

補足として、今回の挙動は異常ではなく、試合結果データを5/13以降に再取得していないために起きた正常な状態であることも明記してください。

---

## 3. モデル指標はユーザー向け画面に表示しない

ユーザー方針：

```text
model_metrics.json はユーザー向けに表示しない。
あくまで開発者がローカルで確認するためのファイルとして扱う。
```

### 3.1 Streamlitからモデル指標表示を削除

以下を確認し、必要に応じて削除または無効化してください。

- `app/streamlit_app.py` から `model_metrics.json` を読み込む処理を削除
- 過去予測結果画面から以下のような表示を削除
  - 勝敗Accuracy
  - スコア完全的中率
  - Home MAE
  - Away MAE
  - 評価対象試合数
  - `model_metrics.json` 由来の概要表示

注意：過去予測結果そのものの表示は残してください。削除するのは `model_metrics.json` 由来の集計指標表示だけです。

### 3.2 `load_model_metrics()` の扱い

`app/utils/load_predictions.py` に `load_model_metrics()` がある場合、以下のどちらかで対応してください。

推奨：

```text
アプリから使わないので削除する。
```

ただし、他のテストやローカル確認スクリプトが利用している場合は、削除せず残しても構いません。その場合でも、Streamlitからは呼ばないでください。

### 3.3 ローカル確認専用であることを明示

`scripts/build_model_metrics.py` は残して構いません。
ただし、ヘルプ文、コメント、README相当の説明、またはレポートで以下を明記してください。

```text
このスクリプトはローカル確認用です。Streamlit画面やユーザー向け表示には使用しません。
```

可能であれば、出力先を以下のどちらかに変更してください。

```text
outputs/local/model_metrics.json
```

または

```text
outputs/model_metrics.local.json
```

出力先を変更する場合は、既存テストも合わせて更新してください。
ただし、影響が大きい場合は、出力先は現状維持でも構いません。その場合も、Streamlitで表示しないことを優先してください。

### 3.4 GitHub Actions / full_pipeline への組み込み禁止

`build_model_metrics.py` はローカル確認専用なので、以下には組み込まないでください。

- `scripts/full_pipeline.py`
- GitHub Actions workflow
- Streamlit起動時処理

---

## 4. テスト追加・修正

対象候補：

- `tests/test_past_prediction_results.py`
- `tests/test_model_metrics.py`
- 必要に応じて新規テストファイル

以下のテストを追加してください。

### 4.1 過去予測結果生成：正常系

条件：

```text
prediction_history 側に match_id=A が存在
matches CSV 側にも match_id=A が存在
status=finished
home_score/away_score が両方存在
```

期待結果：

- 評価対象として採用される
- `past_prediction_results.json` が生成できる
- 予測スコアと実スコアから以下が正しく計算される
  - 勝敗的中
  - スコア完全的中
  - 予測勝敗方向
  - 実勝敗方向

### 4.2 過去予測結果生成：未消化試合

条件：

```text
match_id は一致
status=unplayed
home_score/away_score は欠損
```

期待結果：

- 評価対象にしない
- `matched_but_unplayed` または相当の診断件数が増える
- デフォルトでは既存の `past_prediction_results.json` を空で上書きしない

### 4.3 過去予測結果生成：スコア欠損

条件：

```text
match_id は一致
status=finished
home_score または away_score が欠損
```

期待結果：

- 評価対象にしない
- `matched_but_missing_score` または相当の診断件数が増える

### 4.4 過去予測結果生成：match_id不一致

条件：

```text
prediction_history 側の match_id が matches CSV 側に存在しない
```

期待結果：

- 評価対象にしない
- `unmatched_prediction_matches` または相当の診断件数が増える

### 4.5 Streamlitでモデル指標を表示しないテスト

可能であれば、以下を確認するテストを追加してください。

- `app/streamlit_app.py` が `load_model_metrics` を呼んでいない
- Streamlit画面生成ロジックに `model_metrics.json` 由来の表示がない

難しい場合は、最低限 `grep` ベースで以下を確認できるようにしてください。

```bash
rg "load_model_metrics|model_metrics|勝敗Accuracy|Home MAE|Away MAE|スコア完全的中率" app
```

この検索で、ユーザー画面表示に関係する該当箇所が残っていないことを確認してください。

---

## 5. 実行してほしい確認コマンド

作業後、以下を実行してください。

```bash
python -m compileall app src scripts
pytest
python scripts/build_past_prediction_results.py
python scripts/build_model_metrics.py
```

さらに、Streamlit側にモデル指標表示が残っていないか確認してください。

```bash
rg "load_model_metrics|model_metrics|勝敗Accuracy|Home MAE|Away MAE|スコア完全的中率" app
```

`model_metrics` に関する記述が `scripts/` や `src/evaluation/` に残るのは問題ありません。  
ただし、`app/` 配下、特に `app/streamlit_app.py` でユーザー向けに表示される状態は不可です。

---

## 完了条件

以下をすべて満たしたら完了です。

- `match_id` 一致件数と実スコア確定件数を分けてログ出力できる
- `match_id` は一致しているが `unplayed` / スコア欠損のため評価対象外、という状態を正しく説明できる
- 評価対象0件の場合でも、デフォルトでは既存 `past_prediction_results.json` を空上書きしない
- finished + scoreありの正常系テストがある
- unplayed / score欠損 / match_id不一致のテストがある
- Streamlit画面に `model_metrics.json` 由来のモデル指標が表示されない
- `build_model_metrics.py` はローカル確認用として残っている
- Week5完了レポートの不正確な文言が修正されている
- `python -m compileall app src scripts` が成功
- `pytest` が成功

---

## 作業報告テンプレート

作業後、以下の形式で報告してください。

```markdown
## 実施内容

- ...

## Phase 0 確認結果

- prediction_history 件数:
- matches CSV 件数:
- match_id一致件数:
- finished件数:
- scoreあり件数:
- 評価対象件数:

## 修正したファイル

- ...

## モデル指標表示の扱い

- Streamlit上の表示: 削除済み / 元からなし
- `build_model_metrics.py`: ローカル確認用として維持
- full_pipeline / GitHub Actions への組み込み: なし

## テスト結果

- `python -m compileall app src scripts`: 成功/失敗
- `pytest`: 成功/失敗
- `python scripts/build_past_prediction_results.py`: 成功/失敗
- `python scripts/build_model_metrics.py`: 成功/失敗
- `rg "load_model_metrics|model_metrics|勝敗Accuracy|Home MAE|Away MAE|スコア完全的中率" app`: 結果

## 残課題

- ...
```

