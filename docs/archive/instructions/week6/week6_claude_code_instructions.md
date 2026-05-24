# Week6 Claude Code 指示書：GitHub Actions 手動実行化

## 0. この作業の目的

Week6では、ローカルで実行している予測更新パイプラインを、GitHub Actions の `workflow_dispatch` から手動実行できるようにしてください。

今回の主目的は **定期実行化ではなく、GitHub上の手動実行ボタンから安全に予測ファイルを更新できる状態を作ること** です。

---

## 1. 背景

これまでの作業で、以下は実装済みです。

- 次節予測の生成
- 全未消化試合予測の生成
- 得点者候補Top5の生成
- 過去予測結果JSONの生成
- Streamlitでの予測表示
- pytestベースのテスト

Week5時点では、以下の方針が決まっています。

- `scripts/build_past_prediction_results.py` は公開用パイプラインに組み込む
- `scripts/build_model_metrics.py` はローカル確認専用のため、GitHub Actionsには組み込まない
- `outputs/local/model_metrics.json` はユーザー向け表示・公開用パイプラインでは使わない
- 失敗時に `outputs/latest_predictions.json` を壊さない

---

## 2. 今回実装してほしいこと

### 2.1 GitHub Actions ワークフローを追加する

以下のような手動実行用ワークフローを作成してください。

```text
.github/workflows/update_predictions_manual.yml
```

ワークフロー名は、たとえば以下にしてください。

```yaml
name: Update Predictions Manual
```

トリガーは `workflow_dispatch` のみです。

```yaml
on:
  workflow_dispatch:
```

今回は cron による定期実行は追加しないでください。定期実行はWeek7以降で扱います。

---

## 3. GitHub Actionsで実行する処理

ワークフロー内では、以下の順番で実行してください。

1. checkout
2. Python 3.11 のセットアップ
3. 依存関係のインストール
4. Python構文チェック
5. pytest
6. 次節予測パイプライン実行
7. 全未消化試合予測の更新
8. 過去予測結果JSONの生成
9. 生成物の存在確認
10. 必要な出力ファイルを commit & push

想定コマンドは以下です。

```bash
python -m compileall app src scripts
pytest
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section --use-cache
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
```

ただし、既存の `full_pipeline.py` の引数仕様が異なる場合は、実装済みコードを確認し、既存仕様に合わせてください。

---

## 4. commit対象

GitHub Actionsで更新・コミットする対象は、原則として以下です。

```text
data/processed/
data/features/
outputs/latest_predictions.json
outputs/latest_predictions.csv
outputs/all_unplayed_predictions.json
outputs/all_unplayed_predictions.csv
outputs/prediction_history/
outputs/past_prediction_results.json
outputs/last_updated.txt
```

存在しないファイルがある場合にワークフローが落ちないよう、`[ -e "$file" ] && git add "$file"` のように安全に扱ってください。

### 重要

以下はコミット対象にしないでください。

```text
outputs/local/
outputs/local/model_metrics.json
```

必要であれば `.gitignore` に以下を追加してください。

```gitignore
outputs/local/
```

---

## 5. GitHub Actions YAMLの注意点

### 5.1 権限

Actionsからcommit & pushできるように、以下を設定してください。

```yaml
permissions:
  contents: write
```

### 5.2 push先

基本的には、ワークフローを実行したブランチにpushする形でよいです。

```bash
git push
```

もし既存のブランチ運用に合わせる必要がある場合は、現在のリポジトリ設定を確認して、自然な実装にしてください。

### 5.3 差分がない場合

差分がない場合に失敗しないようにしてください。

例:

```bash
if git diff --cached --quiet; then
  echo "No changes to commit"
else
  git commit -m "Update prediction outputs"
  git push
fi
```

---

## 6. 生成物の検証

Actions内、またはローカル確認で、最低限以下を検証してください。

- `outputs/latest_predictions.json` が存在する
- `outputs/latest_predictions.json` がJSONとして読み込める
- `outputs/latest_predictions.json` に `matches` が存在する
- `outputs/all_unplayed_predictions.json` が存在する
- `outputs/prediction_history/` に履歴が保存される
- `scripts/build_past_prediction_results.py` が失敗せずに実行できる
- `outputs/local/model_metrics.json` がActionsで生成・コミットされない

既存のテストで十分に検証できている場合は、新規テスト追加は必須ではありません。ただし、Actions用の挙動確認が不足している場合は、軽量なテストを追加してください。

---

## 7. READMEの更新

`README.md` に、GitHub Actionsの手動実行方法を追記してください。

最低限、以下を記載してください。

- GitHubリポジトリの `Actions` タブを開く
- `Update Predictions Manual` を選択する
- `Run workflow` をクリックする
- 実行後に更新される主なファイル
- `model_metrics.json` はローカル確認専用であり、Actionsでは生成しないこと

READMEには、開発者が迷わない程度の短い説明で問題ありません。

---

## 8. やってはいけないこと

今回の作業では、以下は実施しないでください。

- GitHub Actionsのcron定期実行を追加する
- モデル再学習をActionsに組み込む
- `scripts/build_model_metrics.py` をActionsに組み込む
- StreamlitアプリをActions上で起動する
- 予測ロジックや特徴量生成ロジックを大きく変更する
- `outputs/latest_predictions.json` を途中生成物で直接上書きするような危険な変更を入れる
- `outputs/local/model_metrics.json` をコミット対象にする

---

## 9. ローカルでの確認コマンド

実装後、ローカルで以下を実行してください。

```bash
python -m compileall app src scripts
pytest
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section --use-cache
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
```

その後、以下も確認してください。

```bash
git status
git diff -- .github/workflows/update_predictions_manual.yml README.md .gitignore
```

出力ファイルに差分が出る場合は、意図した差分か確認してください。

---

## 10. 期待する最終成果物

最低限、以下が作成・更新されている状態にしてください。

```text
.github/workflows/update_predictions_manual.yml
README.md
.gitignore  # 必要な場合のみ
docs/week6_completion_report.md  # 可能であれば作成
```

`docs/week6_completion_report.md` には、以下を簡潔に記載してください。

- Week6で実施した内容
- 作成・更新したファイル
- GitHub Actionsで実行する処理
- Actionsに含めない処理
- ローカル確認結果
- 残課題

---

## 11. 完了条件

以下を満たしたらWeek6完了とします。

- `workflow_dispatch` で手動実行できるGitHub Actionsワークフローがある
- Actions上で `pytest` が実行される
- Actions上で予測生成処理が実行される
- `latest_predictions.json` が安全に更新される
- `all_unplayed_predictions.json` が更新される
- `prediction_history` に履歴が残る
- `past_prediction_results.json` が生成または既存保持される
- `build_model_metrics.py` はActionsに含まれていない
- `outputs/local/model_metrics.json` はコミットされない
- READMEに手動実行方法が追記されている

---

## 12. 作業完了時の報告フォーマット

作業完了後、以下の形式で報告してください。

```text
## 実施内容

- ...

## 作成・更新したファイル

- ...

## 確認結果

- python -m compileall app src scripts: ...
- pytest: ...
- full_pipeline: ...
- run_prediction --mode all_unplayed: ...
- build_past_prediction_results: ...

## 注意点・残課題

- ...
```
