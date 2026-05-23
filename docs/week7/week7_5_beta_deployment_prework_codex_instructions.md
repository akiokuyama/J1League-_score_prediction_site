# Week7.5 Codex指示書：Week8前のStreamlit β公開・事前準備

## 0. この作業の目的

Week7.5では、来週のWeek8本作業に入る前の事前処理として、Jリーグ予測アプリを **正式公開ではなく「β公開・自分用確認公開」** として、Streamlit Community Cloud等で動作確認できる状態に整える。

今回の主目的は、SNS等で広く共有することではなく、以下を確認できる公開環境を作ることである。

- Streamlitアプリがクラウド上で起動するか
- `outputs/latest_predictions.json` をクラウド上で読めるか
- GitHub Actionsで予測ファイルが更新された後、アプリ表示も更新されるか
- 依存関係、ファイルパス、大文字小文字、JSON読み込みでエラーが出ないか
- READMEとアプリ内に、予測アプリとしての注意書きがあるか

重要: この作業は **Week8の正式タスクを完了した扱いにはしない**。Week8で実施するREADME最終整備、定期実行後の表示確認、必要なUI微修正をスムーズに進めるための前倒し確認として扱う。

---

## 1. Codexに必ず守ってほしいこと

### 1.1 言語

作成・更新するドキュメント、コメント、完了報告は **日本語** で書くこと。

### 1.2 今回の位置づけ

今回の作業は **Week8本番作業ではなく、Week8前のβ公開事前準備** として扱うこと。

そのため、以下のような表現は避ける。

- 「正式リリース完了」
- 「一般公開完了」
- 「本番公開完了」
- 「SNS共有準備完了」
- 「Week8完了」
- 「公開準備完了」だけでWeek8全体が終わったように見える表現

代わりに、以下の表現を使う。

- 「β公開準備」
- 「自分用確認公開」
- 「クラウド動作確認環境」
- 「正式公開前の確認環境」
- 「Week8前の事前処理」
- 「Week7.5作業」

### 1.3 Codexができないことを勝手に完了扱いしない

Codexは、ブラウザでStreamlit Community Cloudにログインして、GitHub連携やデプロイボタン操作を実行することはできない。

そのため、Codex側でできない作業については、作業完了報告の中で必ず **「ユーザーが実施する作業」** として、具体的な手順を返すこと。

特に、以下はCodexが完了したと主張してはいけない。

- Streamlit Community Cloudへのログイン
- GitHubアカウント連携
- Streamlit Community Cloud上でのCreate app操作
- デプロイボタンのクリック
- 発行された公開URLの確認
- スマホ実機での表示確認
- GitHub Actionsの定期実行後の実表示確認

---

## 2. 現在の前提

これまでの作業で、以下は実装済みの前提で確認する。

- Streamlitアプリ本体: `app/streamlit_app.py`
- 予測表示用JSON: `outputs/latest_predictions.json`
- 全未消化試合予測: `outputs/all_unplayed_predictions.json`
- 過去予測結果: `outputs/past_prediction_results.json`
- GitHub Actions手動実行: `Update Predictions Manual`
- GitHub Actions定期実行: Week7で追加済み、またはWeek7成果物として存在する想定
- Streamlitアプリは、スクレイピングや重い推論をアプリ起動時に実行せず、生成済みJSONを読み込む構成

ただし、実際のリポジトリ状態を必ず確認し、存在しないファイルやスクリプトがある場合は、実装済みコードに合わせて調整すること。

---

## 3. 今回Codexに実施してほしいこと

## Phase 0: 現状確認

まず、以下を確認する。

```bash
git status --short
ls -la
ls -la app src scripts outputs .github/workflows || true
```

確認観点:

- `app/streamlit_app.py` が存在するか
- `requirements.txt` が存在するか
- `outputs/latest_predictions.json` が存在するか
- `outputs/all_unplayed_predictions.json` が存在するか
- `outputs/past_prediction_results.json` が存在するか
- GitHub Actionsのworkflowファイルが存在するか
- `Data/` と `data/` の大文字小文字問題が残っていないか
- Streamlitアプリが、クラウド起動時にローカル専用ファイルへ強く依存していないか

---

## Phase 1: ローカル検証コマンドの実行

以下を実行する。

```bash
python -m compileall app src scripts
pytest
```

次に、以下の検証スクリプトが存在するか確認する。

```bash
ls scripts/validate_prediction_outputs.py scripts/validate_past_prediction_results.py
```

存在する場合は実行する。

```bash
python scripts/validate_prediction_outputs.py
python scripts/validate_past_prediction_results.py
```

存在しない場合は、軽量な検証スクリプトを作成してから実行する。

### `scripts/validate_prediction_outputs.py` の最低要件

以下を検証すること。

- `outputs/latest_predictions.json` が存在する
- JSONとして読み込める
- トップレベルに `matches` が存在する
- `matches` がlistである
- 各試合に最低限以下のキーが存在する
  - `match_id`
  - `home_team`
  - `away_team`
  - `predicted_score`
  - `result_probabilities`
- `outputs/all_unplayed_predictions.json` も同様に検証する

### `scripts/validate_past_prediction_results.py` の最低要件

以下を検証すること。

- `outputs/past_prediction_results.json` が存在する場合、JSONとして読み込める
- `matches` が存在する場合、listである
- ファイルが存在しない場合でも、β公開を止めるべきか警告で済ませるべきかを明示する
  - 過去予測表示が任意機能なら警告でよい
  - アプリがそのファイル必須ならエラーにする

---

## Phase 2: Streamlit Community Cloud向けのリポジトリ確認

### 2.1 エントリーポイント確認

Streamlit Community Cloudで指定するメインファイルは、原則として以下にする。

```text
app/streamlit_app.py
```

Codexは、このファイルをクラウド上のエントリーポイントとして指定する前提で、READMEやチェックリストにも明記すること。

### 2.2 依存関係確認

`requirements.txt` を確認し、Streamlitアプリ起動に必要な依存関係が不足していないか確認する。

確認対象の例:

- streamlit
- pandas
- numpy
- scikit-learn
- lightgbm
- joblib
- plotly など、実際にimportしているライブラリ

注意:

- 標準ライブラリは `requirements.txt` に追加しない
- 不要な学習用ライブラリを増やしすぎない
- ただし、既存のモデル読み込みやアプリimportで必要なものは不足させない

### 2.3 `.streamlit/config.toml` の確認

必要であれば、最小限の `.streamlit/config.toml` を追加してよい。

ただし、過度なデザイン調整や本格的なUI改修は今回の主目的ではない。

### 2.4 secretsの確認

今回のアプリがGitHub上のJSONを読むだけであれば、基本的にStreamlit secretsは不要のはずである。

ただし、コード上で `st.secrets`、APIキー、外部DB、Google Sheets等を参照している場合は、以下を行う。

- secretsが必要な箇所を特定する
- secretsファイルをGitにコミットしない
- READMEまたはチェックリストに、ユーザーがStreamlit Community CloudのAdvanced settingsで設定すべき内容を説明する
- 実際の秘密情報は絶対に書かない

---

## Phase 3: アプリ内の注意書き確認・追加

`app/streamlit_app.py` を確認し、予測アプリとしての注意書きが十分でない場合は、画面上に短い注意書きを追加する。

例:

```text
このアプリの予測は、過去データと機械学習モデルに基づく参考情報です。実際の試合結果を保証するものではありません。
```

追加場所の候補:

- トップ画面上部
- About/説明セクション
- サイドバー下部

注意:

- 長すぎる免責文は避ける
- ユーザーが見落とさない位置に置く
- 既存UIを大きく壊さない

---

## Phase 4: README更新

`README.md` に、β公開向けの情報を追記する。

最低限、以下を含めること。

### 4.1 アプリ概要

- J1の試合結果予測アプリであること
- 予測スコア、勝敗確率、得点者候補を表示すること
- 予測は参考情報であり、確定情報ではないこと

### 4.2 ローカル起動方法

例:

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

### 4.3 事前検証コマンド

例:

```bash
python -m compileall app src scripts
pytest
python scripts/validate_prediction_outputs.py
python scripts/validate_past_prediction_results.py
```

### 4.4 Streamlit Community Cloudでのβ公開手順

Codexは実際のWeb操作はできないため、READMEにはユーザー向け手順を書く。

以下の内容を含めること。

1. Streamlit Community Cloudにログインする
2. GitHubアカウントを連携する
3. `Create app` を選択する
4. 対象リポジトリとブランチを選択する
5. Main file path に以下を指定する

```text
app/streamlit_app.py
```

6. Advanced settingsでPythonバージョンを選べる場合は、GitHub Actionsと合わせて `3.11` を選ぶ
7. secretsが必要な場合のみ、Advanced settingsに設定する
8. Deployを実行する
9. 発行されたURLでアプリが起動するか確認する

### 4.5 β公開後の確認項目

- アプリが起動する
- `latest_predictions.json` が読めている
- これからの試合一覧が表示される
- 試合詳細に遷移できる
- 過去予測画面が落ちない
- スマホ表示で大きく崩れない
- GitHub Actions実行後に表示が更新される

---

## Phase 5: β公開チェックリストの作成

以下のようなドキュメントを作成する。

```text
docs/week7_5_beta_deployment_checklist.md
```

内容には、以下を含める。

- ローカル検証チェック
- GitHub push前チェック
- Streamlit Community Cloudでユーザーが実施する作業
- デプロイ後の画面確認
- GitHub Actions実行後の表示更新確認
- 正式公開前に残すべき確認項目

正式公開前に残すべき確認項目の例:

- 月曜朝の定期実行が成功するか
- 木曜夜の定期実行が成功するか
- 定期実行後にアプリ表示が更新されるか
- READMEが第三者にも分かる内容になっているか
- 注意書きが十分か
- 表示崩れがないか

---

## Phase 6: 必要なら軽微なUI/パス修正

クラウド公開に影響する範囲に限り、軽微な修正をしてよい。

修正してよい例:

- `outputs/latest_predictions.json` が存在しない場合のエラーメッセージ改善
- パス解決をリポジトリルート基準にする
- `Data/` と `data/` の混在による読み込み失敗回避
- `outputs/past_prediction_results.json` がない場合に画面が落ちないようにする
- Streamlit Cloud上で不要なローカル専用処理を避ける

修正してはいけない例:

- 予測ロジックの大幅変更
- モデル再学習
- スクレイピング処理の大幅変更
- JSONスキーマの破壊的変更
- 得点者候補ロジックの大幅変更
- 正式公開用の大規模UI改修

---

## Phase 7: 最終確認

最後に以下を実行する。

```bash
python -m compileall app src scripts
pytest
python scripts/validate_prediction_outputs.py
python scripts/validate_past_prediction_results.py
```

可能であれば、ローカルでStreamlit起動確認も行う。

```bash
streamlit run app/streamlit_app.py
```

Codex環境でブラウザ確認ができない場合は、無理に完了扱いせず、ユーザーに以下を依頼すること。

- ローカルで `streamlit run app/streamlit_app.py` を実行する
- ブラウザで `http://localhost:8501` を開く
- 主要画面が表示されるか確認する

---

## 4. Codexが作成・更新してよいファイル

想定される更新ファイル:

```text
README.md
app/streamlit_app.py
scripts/validate_prediction_outputs.py
scripts/validate_past_prediction_results.py
docs/week7_5_beta_deployment_checklist.md
docs/week7_5_completion_report.md
.streamlit/config.toml  # 必要な場合のみ
requirements.txt       # 不足がある場合のみ
```

既存の予測出力JSONは、検証や表示確認で更新される可能性がある。

ただし、意図しない予測結果の更新を避けるため、作業後に必ず `git diff` で差分を確認し、不要な出力差分をコミット対象にしないこと。

---

## 5. やってはいけないこと

今回の作業では、以下は実施しない。

- 正式公開したと表現する
- SNS共有を前提にした文言へ変更する
- Streamlit CloudへのWeb操作を完了したと主張する
- secretsやAPIキーをGitにコミットする
- モデルを再学習する
- 予測アルゴリズムを変更する
- 大規模なUI刷新を行う
- GitHub Actionsの定期実行時刻を不用意に変更する
- `outputs/local/model_metrics.json` を公開用またはコミット対象にする
- `latest_predictions.json` を壊す可能性がある処理を入れる

---

## 6. ユーザーが実施する必要がある作業を、Codexが必ず返すこと

作業完了時、Codexは以下の形式で **ユーザー実施作業** を必ず返すこと。

```text
## ユーザー側で実施してください

1. Streamlit Community Cloudにログインしてください。
2. GitHubアカウントを連携してください。
3. Create appを選択してください。
4. RepositoryにこのプロジェクトのGitHubリポジトリを指定してください。
5. Branchに main を指定してください。
6. Main file path に app/streamlit_app.py を指定してください。
7. Advanced settingsでPython 3.11を選択してください。
8. secretsが必要な場合のみ設定してください。今回不要なら空で構いません。
9. Deployをクリックしてください。
10. 発行されたURLで以下を確認してください。
    - アプリが起動する
    - これからの試合一覧が表示される
    - 試合詳細画面に遷移できる
    - 過去予測画面が落ちない
    - 注意書きが表示されている
11. 公開URLを控えてください。
12. GitHub Actions実行後に、アプリ表示が更新されるか確認してください。
```

また、Codexは以下も明記すること。

```text
Streamlit Community Cloud上でのデプロイ操作と公開URL確認は、Codexでは実行できません。上記手順はユーザー側で実施してください。
```

---

## 7. 完了条件

以下を満たしたら、Week7.5の「Week8前β公開事前準備」は完了とする。

- `python -m compileall app src scripts` が成功する
- `pytest` が成功する
- `validate_prediction_outputs.py` が成功する
- `validate_past_prediction_results.py` が成功または妥当な警告で終了する
- READMEにβ公開手順が追記されている
- アプリ内に予測である旨の注意書きがある
- `docs/week7_5_beta_deployment_checklist.md` が作成されている
- `docs/week7_5_completion_report.md` が作成されている
- Codexが、ユーザー側で実施すべきStreamlit Community Cloud操作手順を返している

---

## 8. 作業完了時の報告フォーマット

Codexは作業完了後、以下の形式で報告すること。

```text
## 実施内容

- ...

## 作成・更新したファイル

- ...

## 確認結果

- python -m compileall app src scripts: ...
- pytest: ...
- validate_prediction_outputs.py: ...
- validate_past_prediction_results.py: ...
- Streamlitローカル起動確認: 実施 / 未実施 / ユーザー確認が必要

## ユーザー側で実施してください

1. ...

## 注意点・残課題

- 月曜朝の定期実行後の確認は未実施
- 木曜夜の定期実行後の確認は未実施
- Streamlit Community Cloud上の実デプロイはユーザー側で実施が必要
- 正式公開は、上記確認が終わってから判断
```

---

## 9. 補足：β公開と正式公開の違い

今回のWeek7.5 β公開事前準備は、技術的にはURLが発行されるが、目的はあくまで自分用の動作確認である。

正式公開は、少なくとも以下を確認してから行う。

- 月曜朝の試合後更新ワークフローが成功した
- 木曜夜の次節予測更新ワークフローが成功した
- Actions更新後にStreamlit表示も更新された
- READMEが第三者に伝わる内容になっている
- アプリ内の注意書きが十分である
- スマホ表示に大きな崩れがない
- 予測結果が確定情報ではないことが明確である

