# Week6 完了レポート

## 実施内容

- GitHub Actionsから予測更新パイプラインを手動実行できるワークフローを追加しました。
- 手動実行のみを対象とし、cronによる定期実行は追加していません。
- Actions内で構文チェック、pytest、次節予測、全未消化試合予測、過去予測結果JSON生成、生成物検証、commit & pushを実行する構成にしました。
- ローカル確認専用の `outputs/local/model_metrics.json` はActionsで生成せず、コミット対象にも含めない方針にしました。

## 作成・更新ファイル

- `.github/workflows/update_predictions_manual.yml`
- `.gitignore`
- `README.md`
- `tests/test_actions_workflow.py`
- `docs/week6_completion_report.md`

## GitHub Actionsで実行する処理

1. `actions/checkout`
2. Python 3.11 セットアップ
3. `pip install -r requirements.txt`
4. `python -m compileall app src scripts`
5. `pytest`
6. `python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section --use-cache`
7. `python scripts/run_prediction.py --mode all_unplayed`
8. `python scripts/build_past_prediction_results.py`
9. `latest_predictions.json`、`all_unplayed_predictions.json`、`prediction_history` の存在確認
10. 必要な生成物のみをcommit & push

## Actionsに含めない処理

- cron定期実行
- モデル再学習
- `scripts/build_model_metrics.py`
- Streamlitアプリ起動
- `outputs/local/model_metrics.json` の生成・コミット

## ローカル確認結果

- `python -m compileall app src scripts`: 成功
- `pytest`: 19件成功
- `python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section --use-cache`: 成功
- `python scripts/run_prediction.py --mode all_unplayed`: 成功
- `python scripts/build_past_prediction_results.py`: 成功

生成物確認:

- `outputs/latest_predictions.json`: `matches` 1件、`warnings=[]`
- `outputs/all_unplayed_predictions.json`: `matches` 11件、`warnings=[]`
- `outputs/past_prediction_results.json`: `matches` 18件
- `outputs/prediction_history/`: latest / all_unplayed の履歴JSON生成を確認
- `outputs/local/model_metrics.json`: ローカルには残るが、Git管理対象から除外

## GitHub Actions 実行結果

- `Update Predictions Manual` の手動実行がGitHub Actions上で成功しました。
- Actions実行後、更新対象として想定していたファイルがGitHub上で更新されていることを確認しました。
- Actionsが生成した更新コミットをローカルへ `git pull origin main` で取り込み済みです。
- 取り込み後の最新コミットは `531dcc8 Update prediction outputs` です。

更新確認済みファイル:

- `Data/processed/update_2026_report.json`
- `Data/features/match_features_2026.csv`
- `Data/features/upcoming_features_2026.csv`
- `outputs/latest_predictions.json`
- `outputs/latest_predictions.csv`
- `outputs/all_unplayed_predictions.json`
- `outputs/all_unplayed_predictions.csv`
- `outputs/prediction_history/`
- `outputs/past_prediction_results.json`
- `outputs/last_updated.txt`

Actions実行時に発生した問題と対応:

- `src` importエラーに対して、`PYTHONPATH` とpytest設定を追加しました。
- Linux上の大文字小文字区別により `Data/` と `data/` の参照差異が出たため、Actions内で `data -> Data` のシンボリックリンクを作成するようにしました。
- `outputs/local/model_metrics.json` はローカル確認専用のため、Actionsで生成・コミットしない方針に合わせてテストを修正しました。

## 残課題

- Week7以降で必要に応じてcron定期実行化を検討します。
- GitHub Actions上で外部サイト取得に失敗する場合は、キャッシュ運用または取得元ごとのリトライ方針を追加で検討します。
- 中長期的には、`Data/` と `data/` のディレクトリ名をどちらかに統一し、Linux環境でもシンボリックリンクに依存しない構成へ整理する余地があります。
