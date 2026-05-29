# J1 League Score Prediction App

J1リーグ 2026年特別シーズン（J1百年構想リーグ）の試合結果・スコアを予測し、Streamlitで確認するためのアプリです。

予測は過去データ、チーム成績、選手スタッツ、フォーメーション、移動距離、Eloなどの特徴量と機械学習モデルに基づく参考情報です。実際の試合結果を保証するものではありません。

## 主な機能

- 今後行われる未消化試合すべての予測結果を表示
- 予測スコア、勝敗確率、スコア候補Top5を表示
- 得点者候補Top5とゴール期待値を表示
- チーム・節による絞り込み
- 試合詳細ページの表示
- 過去予測結果と実際の結果の照合
- 絞り込み条件に連動した精度サマリー
- Light/Darkモード対応
- GitHub Actionsによる定期データ更新

## アプリの表示データ

Streamlitアプリは主に以下の出力ファイルを読み込みます。

```text
outputs/all_unplayed_predictions.json   # 今後行われる未消化試合すべての予測
outputs/latest_predictions.json         # 次節予測
outputs/past_prediction_results.json    # 過去予測と実際の結果の照合
outputs/last_updated.txt                # 更新時刻
```

現在の「これからの試合」画面では、`outputs/all_unplayed_predictions.json` を優先して表示します。ファイルがない場合のみ `outputs/latest_predictions.json` にフォールバックします。

## ローカルセットアップ

このプロジェクトは `uv` で管理しています。

```bash
cd /Users/akihirookuyama/Soccer_Score_App
uv venv .venv
source .venv/bin/activate
uv sync
```

`requirements.txt` を使う場合:

```bash
pip install -r requirements.txt
```

## Streamlitアプリの起動

```bash
streamlit run app/streamlit_app.py
```

ブラウザで以下を開きます。

```text
http://localhost:8501
```

スマートフォンで確認する場合は、PCとスマートフォンを同じWi-Fiに接続し、Streamlit起動時に表示される `Network URL` をスマートフォンのブラウザで開きます。

## 検証コマンド

変更後やデプロイ前は、以下を実行します。

```bash
python -m compileall app src scripts
pytest
python scripts/validate_prediction_outputs.py
python scripts/validate_past_prediction_results.py
```

モデル指標をローカルで確認する場合:

```bash
python scripts/build_model_metrics.py
```

生成される `outputs/local/model_metrics.json` はローカル確認専用です。GitHub Actionsでは生成せず、コミット対象にも含めません。

## GitHub Actions

データ更新と予測更新はGitHub Actionsで運用します。

### Update Results After Matches

- 実行タイミング: 月曜 07:00 JST
- 目的: 週末試合の結果取得と、過去予測結果の更新
- 主な処理:

```bash
python scripts/update_2026_special_data.py --season 2026_special --category 100yj1 --scope results
python scripts/build_past_prediction_results.py
python scripts/validate_past_prediction_results.py
```

主な更新対象:

```text
Data/processed/matches_2026_special_clean.csv
Data/processed/update_2026_special_report.json
outputs/past_prediction_results.json
```

このワークフローでは、予測ファイル本体は更新しません。

### Update Predictions Scheduled

- 実行タイミング: 水曜 07:00 JST
- 目的: 週末前のデータ更新、特徴量作成、予測更新
- 主な処理:

```bash
python scripts/full_pipeline.py --season 2026_special --category 100yj1 --mode next_section
python scripts/run_prediction.py --mode all_unplayed
python scripts/build_past_prediction_results.py
python scripts/validate_prediction_outputs.py
python scripts/validate_past_prediction_results.py
```

主な更新対象:

```text
Data/processed/
Data/features/
outputs/latest_predictions.json
outputs/latest_predictions.csv
outputs/all_unplayed_predictions.json
outputs/all_unplayed_predictions.csv
outputs/prediction_history/
outputs/past_prediction_results.json
outputs/last_updated.txt
```

### Manual Prediction Update

GitHubの `Actions` タブから手動実行できます。

用途:

- スクレイピング修正後の再実行
- 試合日程・結果の急な変更への対応
- 定期実行失敗後の再実行
- Streamlit表示データの手動更新

## 主要ディレクトリ

```text
Soccer_Score_App/
├── app/                   # Streamlitアプリ
│   └── utils/             # 表示用フォーマッタ、JSON読み込み
├── Data/                  # 学習・推論用データ
│   ├── processed/         # 整形済み試合日程・順位など
│   ├── features/          # 学習・推論用特徴量
│   ├── raw/               # スクレイピング取得データ
│   └── manual/            # 手動管理データ
├── Models/                # 学習済みモデルと特徴量リスト
├── outputs/               # アプリ表示用の予測結果
│   ├── prediction_history/
│   └── local/             # ローカル確認専用出力
├── scripts/               # パイプライン、検証、運用スクリプト
├── src/                   # データ取得、特徴量作成、推論、評価ロジック
├── tests/                 # 回帰テスト
├── docs/                  # レポート、作業記録、指示書アーカイブ
└── archive/               # 旧Notebook、旧RawData
```

## 2026年特別シーズンの扱い

このプロジェクトでは、現在対象としているJ1百年構想リーグを通常の2026シーズンと区別するため、保存名・識別子に `2026_special` を使用します。

例:

```text
Data/processed/matches_2026_special_clean.csv
Data/features/upcoming_features_2026_special.csv
Data/manual/market_values_2026_special.csv
```

## 予測データの考え方

- `latest_predictions.json` は次節予測です。
- `all_unplayed_predictions.json` は未消化試合すべての予測です。
- Streamlitの一覧画面では `all_unplayed_predictions.json` を表示します。
- `prediction_history/` は過去予測の照合に使います。
- 対戦相手が未定の試合は、対戦カードが確定し、特徴量が作成できる状態になってから予測対象になります。

## 運用メモ

- 定期実行では原則として最新データ取得を試します。
- `--use-cache` はデバッグ、再現確認、外部サイト障害時の手動実行向けです。
- `Models/model_features.pkl` を推論時の特徴量スキーマとして扱います。
- 天候特徴量は現在使用していません。
- 旧Notebookは `archive/notebooks/`、旧RawDataは `archive/legacy_rawdata/` に保存しています。
- 作業指示書は `docs/archive/instructions/`、完了レポートや判断メモは `docs/reports/` に整理しています。
