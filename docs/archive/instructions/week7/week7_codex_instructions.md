# Week7 Codex指示書：GitHub Actions 定期運用化（月曜結果評価・木曜予測更新）

## 0. この作業の目的

Week7では、Week6で作成済みのGitHub Actions手動実行ワークフローを土台に、定期実行ワークフローを追加・整理してください。

今回の目的は、単にcronを追加することではありません。以下の2種類の定期処理を明確に分離し、安全に運用できる状態にすることです。

1. **月曜朝：試合後の結果取得・過去予測との照合のみ**
2. **木曜夜：特徴量更新・次節予測更新**

重要な方針として、月曜朝の処理では特徴量更新や次節予測更新は行わないでください。月曜朝は、あくまで週末試合の結果を取得し、過去に出した予測との差分・的中判定を更新するための処理です。

---

## 1. 背景

これまでの作業で、以下は実装済みです。

- 単一試合予測
- 次節予測の生成
- 全未消化試合予測の生成
- 得点者候補Top5の生成
- 過去予測結果JSONの生成
- Streamlitでの予測表示
- GitHub Actionsによる手動実行
- pytestベースのテスト

Week6では、`.github/workflows/update_predictions_manual.yml` により、`workflow_dispatch` から手動で予測更新できる状態になっています。

Week7では、既存の手動実行は残したまま、定期運用を追加します。

---

## 2. 今回の基本方針

### 2.1 月曜朝は「結果評価だけ」

月曜朝の処理では、週末に終わった試合結果を取得し、過去の予測履歴と照合して `outputs/past_prediction_results.json` を更新してください。

月曜朝にやること:

- 試合結果データを最新化する
- 予測履歴と試合結果を照合する
- `outputs/past_prediction_results.json` を更新する
- 必要に応じて `Data/processed/update_2026_special_report.json` を更新する

月曜朝にやらないこと:

- 特徴量CSVを更新しない
- 次節予測を生成しない
- 全未消化試合予測を生成しない
- `outputs/latest_predictions.json` を更新しない
- `outputs/latest_predictions.csv` を更新しない
- `outputs/all_unplayed_predictions.json` を更新しない
- `outputs/all_unplayed_predictions.csv` を更新しない
- `outputs/prediction_history/` に新しい予測履歴を追加しない
- モデル再学習をしない
- `scripts/build_model_metrics.py` を実行しない
- `outputs/local/model_metrics.json` を生成・コミットしない

理由:

- 月曜時点では、特徴量として更新されていないデータが残っている可能性があります。
- 中途半端なデータ状態で予測を再生成すると、`latest_predictions.json` の整合性が崩れる可能性があります。
- 月曜朝の目的は「予測を更新すること」ではなく「実際の結果と予測を比較すること」です。

### 2.2 木曜夜は「特徴量更新 + 次節予測」

木曜夜の処理では、週末前に次節予測を公開するために、データ取得・特徴量生成・予測生成を実行してください。

木曜夜にやること:

- 最新データ取得
- processedデータ更新
- featuresデータ更新
- 次節予測生成
- 全未消化試合予測生成
- 過去予測結果JSON生成
- 生成物検証
- 必要な出力ファイルのcommit & push

木曜夜にやらないこと:

- モデル再学習をしない
- `scripts/build_model_metrics.py` を実行しない
- `outputs/local/model_metrics.json` を生成・コミットしない
- StreamlitアプリをActions上で起動しない

---

## 3. 作成・更新してほしいワークフロー

既存の手動実行ワークフローは残してください。

追加または更新するワークフロー構成は、以下のどちらかで実装してください。

### 推奨案：用途ごとにYAMLを分ける

```text
.github/workflows/update_predictions_manual.yml
.github/workflows/update_results_after_matches.yml
.github/workflows/update_predictions_scheduled.yml
```

- `update_predictions_manual.yml`: 既存の手動実行。必要に応じて最小修正のみ。
- `update_results_after_matches.yml`: 月曜朝の結果評価専用。
- `update_predictions_scheduled.yml`: 木曜夜の次節予測更新専用。

この構成を推奨します。月曜と木曜で更新対象が異なるため、YAMLを分けた方が事故を防ぎやすいです。

### 代替案：1つのYAML内でscheduleを分岐する

1つのYAML内に複数cronを設定し、`${{ github.event.schedule }}` で分岐しても構いません。

ただし、この場合でも月曜処理と木曜処理のcommit対象・実行コマンドは必ず分離してください。

---

## 4. 月曜朝ワークフロー仕様

### 4.1 ファイル名

```text
.github/workflows/update_results_after_matches.yml
```

### 4.2 ワークフロー名

```yaml
name: Update Results After Matches
```

### 4.3 トリガー

月曜朝 7:00 JST を想定します。GitHub Actionsのcronは基本的にUTC基準のため、JSTから9時間引いて日曜22:00 UTCとします。

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: "0 22 * * 0"  # Mon 07:00 JST
```

`workflow_dispatch` も残してください。試合延期、取得失敗、手動再実行のために必要です。

### 4.4 実行内容

基本ステップ:

1. checkout
2. Python 3.11 セットアップ
3. 依存関係インストール
4. `PYTHONPATH` 設定
5. `Data/` と `data/` の互換対応が必要なら、Week6と同様にシンボリックリンクを作成
6. 構文チェック
7. pytest
8. 試合結果のみ取得
9. 過去予測結果JSON生成
10. 生成物検証
11. 月曜朝用の対象ファイルのみcommit & push

### 4.5 試合結果のみ取得モード

現状の `scripts/update_2026_special_data.py` に試合結果のみ取得するモードが存在しない場合は、追加してください。

推奨引数:

```bash
python scripts/update_2026_special_data.py --season 2026_special --category 100yj1 --scope results
```

または既存設計に合わせて、以下のような名前でも構いません。

```bash
python scripts/update_2026_special_data.py --season 2026_special --category 100yj1 --results-only
```

重要:

- 新しい引数名は、既存コードの設計に自然に合わせてください。
- 月曜ワークフローでは、チームスタッツ、選手スタッツ、Football Lab系、特徴量生成、予測生成は実行しないでください。
- ただし、既存の取得関数の都合で完全分離が難しい場合は、最低限 `outputs/latest_predictions.json`、`data/features/`、`outputs/prediction_history/` を更新しないことを保証してください。

### 4.6 月曜朝の想定コマンド

最終的には、以下に近い形にしてください。

```bash
python -m compileall app src scripts
pytest
python scripts/update_2026_special_data.py --season 2026_special --category 100yj1 --scope results
python scripts/build_past_prediction_results.py
```

既存の引数仕様と異なる場合は、既存コードを優先して自然に調整してください。

### 4.7 月曜朝のcommit対象

月曜朝にcommitしてよい対象は、原則として以下のみです。

```text
Data/processed/matches_2026_special_clean.csv
Data/processed/update_2026_special_report.json
outputs/past_prediction_results.json
```

実際のリポジトリで `Data/` ではなく `data/` が正なら、既存構成に合わせてください。

### 4.8 月曜朝にcommitしてはいけない対象

以下は月曜朝にcommitしないでください。

```text
Data/features/
data/features/
outputs/latest_predictions.json
outputs/latest_predictions.csv
outputs/all_unplayed_predictions.json
outputs/all_unplayed_predictions.csv
outputs/prediction_history/
outputs/last_updated.txt
outputs/local/
outputs/local/model_metrics.json
```

特に、`latest_predictions.json` と `prediction_history/` が月曜朝に更新されないことをテストで保証してください。

### 4.9 月曜朝の検証

最低限、以下を検証してください。

- `outputs/past_prediction_results.json` が存在する
- JSONとして読み込める
- トップレベルに `matches` がある
- 評価対象が0件でもスクリプトが異常終了しない
- 評価対象0件の場合、既存ファイルを意図せず空で上書きしない
- 月曜処理後に `outputs/latest_predictions.json` が変更されていない
- 月曜処理後に `outputs/prediction_history/` が増えていない

---

## 5. 木曜夜ワークフロー仕様

### 5.1 ファイル名

```text
.github/workflows/update_predictions_scheduled.yml
```

### 5.2 ワークフロー名

```yaml
name: Update Predictions Scheduled
```

### 5.3 トリガー

木曜 21:00 JST を想定します。JSTから9時間引いて木曜12:00 UTCです。

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: "0 12 * * 4"  # Thu 21:00 JST
```

`workflow_dispatch` も残してください。スクレイピング修正後の再実行や、試合延期対応で必要です。

### 5.4 実行内容

基本ステップ:

1. checkout
2. Python 3.11 セットアップ
3. 依存関係インストール
4. `PYTHONPATH` 設定
5. `Data/` と `data/` の互換対応が必要なら、Week6と同様にシンボリックリンクを作成
6. 構文チェック
7. pytest
8. 次節予測パイプライン実行
9. 全未消化試合予測更新
10. 過去予測結果JSON生成
11. 生成物検証
12. 必要な出力ファイルのみcommit & push

### 5.5 木曜夜の想定コマンド

```bash
python -m compileall app src scripts
pytest
python scripts/full_pipeline.py --season 2026_special --category 100yj1 --mode next_section
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
```

既存の `full_pipeline.py` の引数仕様が異なる場合は、既存コードを確認して自然に合わせてください。

---

## 6. `--use-cache` の扱いを見直す

### 6.1 現状の問題意識

Week6の手動実行では、安定性のために以下のように `--use-cache` を使っていました。

```bash
python scripts/full_pipeline.py --season 2026_special --category 100yj1 --mode next_section --use-cache
```

これは手動検証では有効ですが、定期実行で常に `--use-cache` を使うと、最新データを取得せず、古いキャッシュから再生成してしまう可能性があります。

### 6.2 月曜朝の扱い

月曜朝は試合結果の最新化が目的なので、原則として `--use-cache` を使わないでください。

推奨:

```bash
python scripts/update_2026_special_data.py --season 2026_special --category 100yj1 --scope results
```

取得失敗時に既存データを使うfallbackを実装する場合でも、以下を守ってください。

- 古いキャッシュだけで「結果更新できた」ように見せない
- 取得失敗時はActionsログに明確に出す
- 取得できなかった場合でも、既存の `latest_predictions.json` は更新しない
- 評価対象が増えない場合は、差分なしとしてcommitしない

### 6.3 木曜夜の扱い

木曜夜は、まず最新データ取得を試してください。

推奨:

```bash
python scripts/full_pipeline.py --season 2026_special --category 100yj1 --mode next_section
```

ただし、外部サイト取得が不安定な場合に備えて、以下のいずれかの対応を実装しても構いません。

#### 案A：明示的なfallbackオプションを追加

```bash
python scripts/full_pipeline.py --season 2026_special --category 100yj1 --mode next_section --fallback-to-cache
```

動作:

1. まず最新データ取得を試す
2. 失敗した取得元だけ既存キャッシュまたは既存processedを使う
3. 警告を `warnings` またはログに残す
4. 品質チェックに合格した場合のみ `latest_predictions.json` を更新する

#### 案B：既存の `--use-cache` は手動・デバッグ専用として残す

定期実行では `--use-cache` を使わず、手動実行時のみ必要に応じて `--use-cache` を使う設計でも構いません。

READMEに以下を明記してください。

- 定期実行では原則として最新取得を試す
- `--use-cache` はデバッグ・再現確認・外部サイト障害時の手動実行向け

### 6.4 どちらを選ぶべきか

まずは案Bで十分です。

ただし、既存コードに小さな修正で案Aを入れられるなら、案Aも可です。

重要なのは、定期実行で古いキャッシュを無自覚に使わないことです。

---

## 7. 失敗時のログと安全停止を強化する

### 7.1 基本方針

失敗時に壊れた出力をcommitしないようにしてください。

特に、以下は絶対に避けてください。

- 空の `latest_predictions.json` をcommitする
- 壊れたJSONをcommitする
- 月曜朝に予測ファイルを更新する
- 途中失敗した状態で `outputs/prediction_history/` に履歴を追加する
- `outputs/local/model_metrics.json` をcommitする

### 7.2 Actionsログで見えるようにすること

最低限、以下をログ出力してください。

- 実行モード（月曜結果評価 / 木曜予測更新 / 手動）
- 実行日時
- 実行コマンド
- 取得対象シーズン
- 取得対象カテゴリ
- 更新したファイル
- スキップしたファイル
- `latest_predictions.json` のmatches件数
- `all_unplayed_predictions.json` のmatches件数
- `past_prediction_results.json` のmatches件数
- warningsの内容
- 取得失敗があった場合のURLまたはデータ種別

可能であれば、GitHub Actionsのロググループを使ってください。

例:

```bash
echo "::group::Validate outputs"
python scripts/validate_prediction_outputs.py
python scripts/validate_past_prediction_results.py
echo "::endgroup::"
```

### 7.3 生成物検証スクリプト

既存に検証処理がある場合は再利用してください。足りない場合は、軽量な検証スクリプトまたはテストを追加してください。

候補:

```text
scripts/validate_prediction_outputs.py
scripts/validate_past_prediction_results.py
```

最低限の検証内容:

#### latest_predictions.json

- ファイルが存在する
- JSONとして読み込める
- `matches` が存在する
- `matches` が空でない
- 各試合に `match_id`, `home_team`, `away_team`, `predicted_score`, `result_probabilities` がある
- Weather関連列・キーが混入していない

#### all_unplayed_predictions.json

- ファイルが存在する
- JSONとして読み込める
- `matches` が存在する

#### past_prediction_results.json

- ファイルが存在する
- JSONとして読み込める
- `matches` が存在する
- 0件でも異常終了しない

### 7.4 commit & pushの安全化

差分がない場合は失敗しないようにしてください。

例:

```bash
if git diff --cached --quiet; then
  echo "No changes to commit"
else
  git commit -m "Update prediction outputs"
  git push
fi
```

月曜朝と木曜夜でcommitメッセージを分けてください。

例:

```text
Update past prediction results
Update scheduled prediction outputs
```

---

## 8. 定期実行用のテストを追加する

既存の `tests/test_actions_workflow.py` を拡張するか、新しいテストファイルを追加してください。

推奨:

```text
tests/test_scheduled_workflows.py
```

### 8.1 月曜朝ワークフローのテスト

以下を検証してください。

- `update_results_after_matches.yml` が存在する
- `workflow_dispatch` がある
- schedule cron がある
- 月曜朝 7:00 JST 相当のcronになっている
  - UTCなら `0 22 * * 0`
- `python -m compileall app src scripts` が含まれている
- `pytest` が含まれている
- `build_past_prediction_results.py` が含まれている
- `full_pipeline.py --mode next_section` が含まれていない
- `run_prediction.py --mode all_unplayed` が含まれていない
- `outputs/latest_predictions.json` をgit addしていない
- `outputs/all_unplayed_predictions.json` をgit addしていない
- `outputs/prediction_history/` をgit addしていない
- `Data/features/` または `data/features/` をgit addしていない
- `build_model_metrics.py` が含まれていない
- `outputs/local/` をgit addしていない

### 8.2 木曜夜ワークフローのテスト

以下を検証してください。

- `update_predictions_scheduled.yml` が存在する
- `workflow_dispatch` がある
- schedule cron がある
- 木曜 21:00 JST 相当のcronになっている
  - UTCなら `0 12 * * 4`
- `python -m compileall app src scripts` が含まれている
- `pytest` が含まれている
- `full_pipeline.py` が含まれている
- `--mode next_section` が含まれている
- `run_prediction.py --mode all_unplayed` が含まれている
- `build_past_prediction_results.py` が含まれている
- `build_model_metrics.py` が含まれていない
- `outputs/local/` をgit addしていない
- 生成物検証ステップが含まれている

### 8.3 手動実行ワークフローのテスト

既存の手動ワークフローについて、以下を引き続き検証してください。

- `workflow_dispatch` がある
- cronがない、または手動専用として維持されている
- `build_model_metrics.py` が含まれていない
- `outputs/local/` をgit addしていない
- commit対象が公開用ファイルに限定されている

---

## 9. README更新

`README.md` にWeek7の定期実行方針を追記してください。

最低限、以下を記載してください。

### 9.1 手動実行

- GitHub Actionsの `Update Predictions Manual` から実行できる
- デバッグ、試合延期対応、スクレイピング修正後の再実行に使う

### 9.2 月曜朝の試合後更新

- ワークフロー名: `Update Results After Matches`
- 実行タイミング: 月曜 07:00 JST
- 目的: 週末試合の結果取得と過去予測との照合
- 更新対象:
  - `Data/processed/matches_2026_special_clean.csv`
  - `Data/processed/update_2026_special_report.json`
  - `outputs/past_prediction_results.json`
- 更新しないもの:
  - `outputs/latest_predictions.json`
  - `outputs/all_unplayed_predictions.json`
  - `Data/features/`
  - `outputs/prediction_history/`

### 9.3 木曜夜の次節予測更新

- ワークフロー名: `Update Predictions Scheduled`
- 実行タイミング: 木曜 21:00 JST
- 目的: 特徴量更新と次節予測更新
- 更新対象:
  - `Data/processed/`
  - `Data/features/`
  - `outputs/latest_predictions.json`
  - `outputs/latest_predictions.csv`
  - `outputs/all_unplayed_predictions.json`
  - `outputs/all_unplayed_predictions.csv`
  - `outputs/prediction_history/`
  - `outputs/past_prediction_results.json`
  - `outputs/last_updated.txt`

### 9.4 `--use-cache` の説明

READMEに以下を明記してください。

- 定期実行では原則として最新データ取得を試す
- `--use-cache` はデバッグ、再現確認、外部サイト障害時の手動実行向け
- 古いキャッシュを使って最新予測を更新しないよう注意する

---

## 10. `.gitignore` の確認

以下が `.gitignore` に含まれていることを確認してください。

```gitignore
outputs/local/
```

`outputs/local/model_metrics.json` はローカル確認専用です。Actionsで生成・コミットしないでください。

---

## 11. 作成・更新する主なファイル

想定される主な作成・更新ファイルは以下です。

```text
.github/workflows/update_results_after_matches.yml
.github/workflows/update_predictions_scheduled.yml
.github/workflows/update_predictions_manual.yml  # 必要に応じて最小修正
scripts/update_2026_special_data.py                      # results-only/scope追加が必要な場合
scripts/validate_prediction_outputs.py            # 必要な場合
scripts/validate_past_prediction_results.py       # 必要な場合
tests/test_scheduled_workflows.py                 # または tests/test_actions_workflow.py の拡張
README.md
.gitignore
docs/week7_completion_report.md
```

既存コードに同等機能がある場合は、新規ファイルを増やしすぎず、既存の実装を活用してください。

---

## 12. やってはいけないこと

以下は実施しないでください。

- 月曜朝に `latest_predictions.json` を更新する
- 月曜朝に `all_unplayed_predictions.json` を更新する
- 月曜朝に `data/features/` または `Data/features/` を更新・commitする
- 月曜朝に `outputs/prediction_history/` を更新・commitする
- 月曜朝に次節予測を実行する
- モデル再学習をActionsに組み込む
- `scripts/build_model_metrics.py` をActionsに組み込む
- `outputs/local/model_metrics.json` を生成・commitする
- StreamlitアプリをActions上で起動する
- 壊れたJSON、空の予測JSON、検証失敗した生成物をcommitする
- 予測ロジックや特徴量生成ロジックを大きく変更する

---

## 13. ローカル確認コマンド

実装後、最低限以下を実行してください。

```bash
python -m compileall app src scripts
pytest
```

月曜朝処理相当:

```bash
python scripts/update_2026_special_data.py --season 2026_special --category 100yj1 --scope results
python scripts/build_past_prediction_results.py
```

木曜夜処理相当:

```bash
python scripts/full_pipeline.py --season 2026_special --category 100yj1 --mode next_section
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
```

`--scope results` ではなく別名を採用した場合は、実装した引数に読み替えてください。

差分確認:

```bash
git status
git diff -- .github/workflows README.md .gitignore tests scripts docs
```

月曜処理の確認では、以下に差分が出ていないことを確認してください。

```bash
git diff -- outputs/latest_predictions.json outputs/all_unplayed_predictions.json outputs/prediction_history Data/features data/features
```

---

## 14. 完了条件

以下を満たしたらWeek7完了とします。

- 月曜朝の試合後結果評価ワークフローがある
- 木曜夜の次節予測更新ワークフローがある
- 既存の手動実行ワークフローが残っている
- 月曜朝ワークフローでは予測ファイルと特徴量ファイルを更新しない
- 木曜夜ワークフローでは特徴量更新と予測更新を実行する
- `--use-cache` の扱いが整理されている
- 定期実行では原則として最新データ取得を試す
- 失敗時に壊れた出力をcommitしない
- 生成物検証がある
- 定期実行用テストが追加されている
- `build_model_metrics.py` がActionsに含まれていない
- `outputs/local/model_metrics.json` がcommit対象外である
- READMEに月曜・木曜・手動実行の違いが記載されている
- `python -m compileall app src scripts` が成功する
- `pytest` が成功する
- `docs/week7_completion_report.md` が作成されている

---

## 15. Week7完了レポートの作成

作業完了後、以下のファイルを作成してください。

```text
docs/week7_completion_report.md
```

内容は簡潔でよいですが、以下を含めてください。

```text
# Week7 完了レポート

## 概要

## 実施内容

## 作成・更新したファイル

## 月曜朝ワークフロー
- 目的
- 実行タイミング
- 実行コマンド
- 更新対象
- 更新しない対象

## 木曜夜ワークフロー
- 目的
- 実行タイミング
- 実行コマンド
- 更新対象

## --use-cache の扱い

## 失敗時の安全対策

## テスト結果

## ローカル確認結果

## 残課題
```

---

## 16. 作業完了時の報告フォーマット

作業完了後、以下の形式で報告してください。

```text
## 実施内容

- ...

## 作成・更新したファイル

- ...

## 確認結果

- python -m compileall app src scripts: ...
- pytest: ...
- 月曜朝処理相当: ...
- 木曜夜処理相当: ...

## 重要な仕様

- 月曜朝は latest_predictions.json を更新しない
- 木曜夜は特徴量更新と次節予測を実行する
- build_model_metrics.py はActionsに含めない

## 注意点・残課題

- ...
```
