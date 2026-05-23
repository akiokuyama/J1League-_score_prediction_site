# Week7.5 β公開チェックリスト

このチェックリストは、Week8本作業前にStreamlit Community Cloud等で自分用確認公開を行うためのものです。正式公開やSNS共有の完了条件ではありません。

## 1. ローカル検証チェック

- [ ] `python -m compileall app src scripts` が成功する
- [ ] `pytest` が成功する
- [ ] `python scripts/validate_prediction_outputs.py` が成功する
- [ ] `python scripts/validate_past_prediction_results.py` が成功する
- [ ] `outputs/latest_predictions.json` が存在する
- [ ] `outputs/all_unplayed_predictions.json` が存在する
- [ ] `outputs/past_prediction_results.json` が存在する
- [ ] `streamlit run app/streamlit_app.py` でローカル起動できる
- [ ] `http://localhost:8501` でアプリを表示できる

## 2. GitHub push前チェック

- [ ] `git status --short` で意図しない差分がない
- [ ] `outputs/local/model_metrics.json` がコミット対象に含まれていない
- [ ] 予測出力JSONを意図せず更新していない
- [ ] READMEにβ公開手順が記載されている
- [ ] アプリ内に予測が参考情報である旨の注意書きが表示される

## 3. Streamlit Community Cloudでユーザーが実施する作業

- [ ] Streamlit Community Cloudにログインする
- [ ] GitHubアカウントを連携する
- [ ] `Create app` を選択する
- [ ] RepositoryにこのプロジェクトのGitHubリポジトリを指定する
- [ ] Branchに `main` を指定する
- [ ] Main file path に `app/streamlit_app.py` を指定する
- [ ] Advanced settingsでPython 3.11を選択する
- [ ] secretsが不要であることを確認する
- [ ] Deployを実行する
- [ ] 発行されたURLを控える

## 4. デプロイ後の画面確認

- [ ] アプリが起動する
- [ ] これからの試合一覧が表示される
- [ ] 試合カードをクリックして詳細画面へ遷移できる
- [ ] 詳細画面から一覧へ戻れる
- [ ] スコア候補Top 5を展開できる
- [ ] 得点者候補Top 5を展開できる
- [ ] 過去の予測結果画面が落ちない
- [ ] 注意書きが表示されている
- [ ] スマホ実機またはスマホ幅のブラウザで大きな表示崩れがない

## 5. GitHub Actions実行後の表示更新確認

- [ ] `Update Results After Matches` が成功する
- [ ] `Update Predictions Scheduled` が成功する
- [ ] 必要に応じて `Manual Prediction Update` が成功する
- [ ] Actions実行後にGitHub上の `outputs/latest_predictions.json` が更新される
- [ ] Streamlit Community Cloud上の表示が更新後のJSONを反映している

## 6. 正式公開前に残すべき確認項目

- [ ] 月曜朝の定期実行が実スケジュールで成功する
- [ ] 木曜夜の定期実行が実スケジュールで成功する
- [ ] 定期実行後にアプリ表示が更新される
- [ ] READMEが第三者にも分かる内容になっている
- [ ] 予測が確定情報ではないことが十分に伝わる
- [ ] スマホ表示に大きな崩れがない
- [ ] 共有範囲をprivate運用にするかpublic運用にするか決める
