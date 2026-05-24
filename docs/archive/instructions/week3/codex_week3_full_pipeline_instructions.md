# Codex指示書：Week3 天候なし再学習・2026年データ取得・次節一括予測パイプライン実装

## 0. 目的

この指示書は、Jリーグ予測アプリの **Week3作業** をCodexに実行してもらうためのものです。

Week3のゴールは、以下を満たすことです。

1. 天候特徴量を使用しない方針でモデルを再学習する
2. 2026年の明治安田J1百年構想リーグのデータを取得する
3. 最新データから未来試合用の特徴量を生成する
4. Week2で実装済みの `predict_match()` を使って、次節または未消化試合を一括予測する
5. `outputs/latest_predictions.json` を安全に生成する

---

## 1. Codexへの最重要指示

- 作成するドキュメント、コメント、完了レポートは **日本語** で書いてください。
- 既存Notebook、既存CSV、既存pickleを削除・破壊しないでください。
- 既存モデルを上書きする前に、必ずバックアップを作成してください。
- `outputs/latest_predictions.json` は直接上書きせず、必ず一時ファイルへ書き出し、検証成功後に置換してください。
- スクレイピングは `requests + BeautifulSoup` を優先してください。
- Selenium / Playwright は最終手段です。
- 高頻度アクセスを避け、HTMLキャッシュ、待機時間、リトライを実装してください。
- 未来試合予測では、試合後にしか分からない情報を使わないでください。
- 天候データは取得・使用しないでください。

---

## 2. 今回の前提

### 2.1 既存実装

Week1・Week2で以下が実装済みの前提です。

```text
src/models/load_model.py
src/predict/feature_preprocess.py
src/predict/score_candidates.py
src/predict/predict_match.py
scripts/smoke_test_load_models.py
scripts/smoke_test_predict_match.py
Data/ML_dataset.csv
Models/model_step1_goals.pkl
Models/model_step2_clf.pkl
Models/model_step2_diff.pkl
Models/model_features.pkl
```

Week2では未来試合用の特徴量生成は未実装です。Week3では、日程データから未消化試合を抽出し、各試合の特徴量行を作って `predict_match()` に渡してください。

### 2.2 2026年対象大会

```text
season: 2026
league: J1
competition: 明治安田J1百年構想リーグ
category: 100yj1
```

Jリーグ公式の日程URL:

```text
https://www.jleague.jp/match/search/?category%5B%5D=100yj1&year=2026&section=
```

### 2.3 天候特徴量の扱い

天候データは取得難易度に対して予測寄与が小さいため、今後は正式モデルでは使用しません。

今回実施すること:

- `Weather` 列を学習特徴量から除外する
- `Weather_*` のOne-Hot特徴量を生成しない
- 天候なしモデルを再学習する
- `model_features.pkl` を天候なし版に更新する
- `feature_policy.json` に天候除外方針を保存する

### 2.4 ゴールパターン・チームスタイルの扱い

正式モデルでは、ゴールパターン・チームスタイルは **前年シーズン終了時点の `Prev_*` 特徴量のみ使用** してください。

理由:

- 過去データには、各試合前時点のゴールパターン・チームスタイルのスナップショットが存在しない
- 当該シーズン終了時点の値を過去試合に使うと、未来情報リークになる
- そのため、正式モデルの学習・推論では、前年値を固定特徴量として使う

一方で、2026年以降は、今後のモデル改善用に当年のゴールパターン・チームスタイルを毎節スナップショット保存してください。

ただし、保存した当年最新値は、今回の正式モデルの特徴量には使わないでください。

保存先例:

```text
data/raw/football_lab/goal_patterns/goal_patterns_2026_asof_YYYYMMDD.csv
data/raw/football_lab/team_styles/team_styles_2026_asof_YYYYMMDD.csv
```

---

## 3. Week3で作成・更新するファイル

### 3.1 モデル再学習・評価

```text
src/evaluation/__init__.py
src/evaluation/metrics.py
src/evaluation/model_evaluation.py
src/evaluation/weather_ablation.py
src/models/train_score_models.py
scripts/evaluate_weather_feature.py
scripts/retrain_models_no_weather.py
docs/weather_feature_decision.md
docs/model_retraining_report.md
Models/feature_policy.json
Models/model_metadata.json
```

### 3.2 データ取得

```text
src/config.py
src/data/__init__.py
src/data/scraping.py
src/data/team_master.py
src/data/scrape_matches.py
src/data/scrape_standings.py
src/data/scrape_team_stats.py
src/data/scrape_market_values.py
src/data/scrape_football_lab_team.py
src/data/scrape_formations.py
src/data/scrape_player_stats.py
scripts/update_2026_data.py
docs/data_source_report_2026.md
```

### 3.3 特徴量生成

```text
src/features/__init__.py
src/features/build_match_features.py
src/features/build_upcoming_features.py
src/features/elo.py
src/features/rolling.py
src/features/travel.py
src/features/tactical.py
src/features/validation.py
scripts/make_upcoming_features.py
```

### 3.4 一括予測

```text
src/predict/predict_upcoming.py
scripts/run_prediction.py
scripts/full_pipeline.py
docs/week3_completion_report.md
```

---

## 4. Phase 1：天候なしモデル再学習

### 4.1 目的

天候特徴量を完全に除外したモデルを再学習し、既存モデルと比較してください。

### 4.2 除外する特徴量

Raw列:

```text
Weather
```

One-Hot列:

```text
Weather_Bad_Weather
Weather_Cloudy
Weather_Indoor
Weather_Rain
Weather_Sunny
Weather_Unknown
```

### 4.3 カテゴリ変数

天候なしモデルでは、以下のみOne-Hot Encodingしてください。

```python
CAT_COLS_NO_WEATHER = [
    "Backline_Matchup",
    "Home_Formation",
    "Away_Formation",
]
```

### 4.4 目的変数

```text
Home_Goals
Away_Goals
Match_Result
Goal_Diff
```

### 4.5 除外列

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
    "Weather",
]
```

### 4.6 学習・評価分割

既存方針に合わせて、以下で評価してください。

```text
学習データ: 2021〜2024
テストデータ: 2025
```

### 4.7 モデル構成

既存Notebookのロジックを優先してください。

想定モデル:

```text
Step1: MultiOutputRegressor(LGBMRegressor)
Step2A: LGBMClassifier
Step2B: LGBMRegressor
Step3: score_candidates.py の最終スコア統合ロジック
```

### 4.8 評価指標

最低限、以下を比較してください。

```text
Home MAE
Away MAE
平均MAE
勝敗Accuracy
勝敗LogLoss
Goal Diff MAE
最終スコアEMR
最終Home MAE
最終Away MAE
最終勝敗Accuracy
```

### 4.9 採用基準

天候なしモデルが以下を満たす場合、正式採用してください。

```text
平均MAEの悪化が +0.01 未満
勝敗Accuracyの低下が 0.5pt 未満
勝敗LogLossの悪化が +0.01 前後まで
Goal Diff MAEの悪化が +0.01 未満
最終スコアEMRがほぼ同等または改善
```

### 4.10 モデル保存

まず以下に保存してください。

```text
Models/weather_removed_v1/model_step1_goals.pkl
Models/weather_removed_v1/model_step2_clf.pkl
Models/weather_removed_v1/model_step2_diff.pkl
Models/weather_removed_v1/model_features.pkl
Models/weather_removed_v1/model_metadata.json
Models/weather_removed_v1/feature_policy.json
```

採用基準を満たし、`--activate` が指定された場合のみ、既存モデルをバックアップしたうえで以下を更新してください。

```text
Models/model_step1_goals.pkl
Models/model_step2_clf.pkl
Models/model_step2_diff.pkl
Models/model_features.pkl
Models/model_metadata.json
Models/feature_policy.json
```

バックアップ先:

```text
Models/legacy_weather_YYYYMMDD_HHMMSS/
```

### 4.11 `feature_policy.json`

以下の内容を保存してください。

```json
{
  "exclude_weather": true,
  "categorical_columns": [
    "Backline_Matchup",
    "Home_Formation",
    "Away_Formation"
  ],
  "ignored_raw_columns": [
    "Weather"
  ],
  "forbidden_feature_prefixes": [
    "Weather_"
  ],
  "goal_pattern_policy": "use_previous_season_prev_features_only",
  "team_style_policy": "use_previous_season_prev_features_only"
}
```

---

## 5. Phase 2：データ取得

### 5.1 共通スクレイピング方針

`src/data/scraping.py` に共通処理を実装してください。

要件:

- `requests + BeautifulSoup` を優先
- User-Agentを設定
- `data/raw/html_cache/` にHTMLキャッシュを保存
- `--use-cache` で再取得せずパース可能にする
- リトライ、指数バックオフ、待機時間を実装
- 取得URL、取得件数、保存先をログ出力
- 失敗時に既存rawを壊さない

---

## 5.2 試合日程・結果

### 取得元

```text
https://www.jleague.jp/match/search/?category%5B%5D=100yj1&year=2026&section=
```

### 作成ファイル

```text
src/data/scrape_matches.py
```

### 取得カラム

```text
season
league
competition
category
section
match_date
kickoff_time
home_team
away_team
home_score
away_score
stadium
attendance
status
match_url
match_id
```

### 保存先

```text
data/raw/matches/schedule_2026_100yj1.csv
data/processed/matches_2026_clean.csv
```

### 注意

- `VS` またはスコア未確定なら未消化
- スコアがある場合は終了済み
- 中止・延期・未定は `status` に残す
- 予測対象から除外するか、注意付きで扱う
- `match_id` は `season + category + section + home + away` をベースに一意化

---

## 5.3 順位表

### 取得元

```text
https://www.jleague.jp/standings/j1/
```

### 作成ファイル

```text
src/data/scrape_standings.py
```

### 保存先

```text
data/raw/standings/standings_2026.csv
data/processed/standings_2026_clean.csv
```

### 注意

- 2026年特別シーズンの大会形式が通常J1と違う場合は、レポートに明記
- 取得が難しい場合は、消化済み試合結果から順位・勝ち点を生成
- `Current_Rank`、`Current_Points` は試合前時点で生成できるようにする

---

## 5.4 チームスタッツ

### 作成ファイル

```text
src/data/scrape_team_stats.py
```

### URL形式

```text
https://www.jleague.jp/stats/j1/club/2026/{stat_type}/
```

### 取得対象

```python
TEAM_STAT_TYPES = {
    "shoot": "Total Shots",
    "shoot_on_target": "Shots on Target",
    "suffer_shoot": "Total Shots Against",
    "score": "Total Goals",
    "lost": "Total Goals Against",
    "clean_sheet": "Clean Sheets",
    "pass_count": "Total Passes",
    "dribble_count": "Total Dribbles",
    "through_pass_count": "Total Through Balls",
    "cross_count": "Total Crosses",
    "clear_count": "Total Clearances",
    "tackle_count": "Total Tackles",
    "block_count": "Total Blocks",
    "foul_count": "Total Fouls",
    "intercept_count": "Total Interceptions",
    "air_battle_win_count": "Aerial Duels Won",
    "yellow_count": "Yellow Cards",
    "red_count": "Red Cards",
    "ball_rate": "Average Possession",
    "chance_create": "Chances Created",
    "one_on_one": "Duels Won",
    "recovery_count": "Recoveries",
    "expected_goals": "Expected Goals",
    "expected_goals_against": "Expected Goals Against",
    "distance_per_game": "Avg Distance Covered",
    "sprint_per_game": "Avg Sprints",
    "possession_distance_per_game": "Distance Covered In Possession",
    "possession_sprint_per_game": "Sprints In Possession",
    "un_possession_distance_per_game": "Distance Covered Out of Possession",
    "un_possession_sprint_per_game": "Sprints Out of Possession"
}
```

### 保存先

```text
data/raw/team_stats/team_stats_2026.csv
data/processed/team_stats_2026_clean.csv
```

### 注意

- 公式スタッツは試合翌日〜2日後に更新される前提
- 欠損がある場合は補完可否を判断
- 補完できない場合は対象試合をスキップし、`skipped_matches` に理由を残す

---

## 5.5 市場価値

### 作成ファイル

```text
src/data/scrape_market_values.py
```

### 取得元

```text
https://www.transfermarkt.com/j1-league/startseite/wettbewerb/JAP1/plus/?saison_id=2025
```

2026年用の市場価値は、Transfermarktの仕様上、`saison_id=2025` を使う可能性があります。既存資料では、2021シーズンは `saison_id=2020`、2022シーズンは `saison_id=2021` のように、対象シーズンの前年IDを使う仕様になっているためです。

### 方針

- 自動取得を試みる
- 取得できない場合は `data/manual/market_values_2026.csv` を読み込む
- 金額表記を数値化する
- 通貨・単位を統一する
- チーム名を標準名へ変換する

### 保存先

```text
data/raw/market_values/market_values_2026.csv
data/processed/market_values_2026_clean.csv
data/manual/market_values_2026.csv
```

---

## 5.6 Football Lab：AGI / KAGI / xG系

### 作成ファイル

```text
src/data/scrape_football_lab_team.py
```

### 取得元例

```text
https://www.football-lab.jp/summary/team_ranking/j1?year=2026&data=expected
https://www.football-lab.jp/summary/team_ranking/j1?year=2026&data=kagi
```

### 取得対象

```text
Rolling_xG 用のxG系データ
AGI
KAGI
```

### 注意

- シーズン中は試合後に更新されるため、予測時点で取得済みの最新値のみ使用
- 過去学習用のスナップショットが存在しない値は、既存仕様に合わせてシーズン値を節数で割った近似値を使う
- 近似を使った特徴量には、必要に応じて補完フラグを持たせる

---

## 5.7 Football Lab：フォーメーション

### 作成ファイル

```text
src/data/scrape_formations.py
```

### URL例

```text
https://www.football-lab.jp/ka-f/formation?year=2026
```

### 方針

未来試合の実フォーメーションは分からないため、予測では以下の順に補完してください。

1. 今季で最も使用しているフォーメーション
2. 直近3試合の最頻フォーメーション
3. 前年最頻フォーメーション
4. `Unknown`

生成対象:

```text
Home_Formation
Away_Formation
is_Mirror_Game
Home_Midfield_Advantage
Backline_Matchup
Defense_Margin_Home
Defense_Margin_Away
DF_count
MF_count
FW_count
```

---

## 5.8 Football Lab：ゴールパターン・チームスタイル

### 作成ファイル

```text
src/data/scrape_football_lab_team.py
```

### URL例

ゴールパターン:

```text
https://www.football-lab.jp/summary/team_ranking/j1?year=2026&data=goal
```

チームスタイル:

```text
https://www.football-lab.jp/summary/team_style/j1?year=2026&data=21
```

### 正式モデルでの扱い

正式モデルでは、当年最新値を特徴量として使わないでください。

正式モデルで使うのは、以下のみです。

```text
Prev_Goal_* 系
Prev_Set-piece Index
Prev_Left Attack Index
Prev_Center Attack Index
Prev_Right Attack Index
Prev_Short Counter
Prev_Long Counter
Prev_Opponent Area Possession
Prev_My Area Possession
```

これらは、前年シーズン終了時点のデータから作成してください。

### 将来改善用の保存

当年のゴールパターン・チームスタイルは、将来の検証用として毎節保存してください。

保存先:

```text
data/raw/football_lab/goal_patterns/goal_patterns_2026_asof_YYYYMMDD.csv
data/raw/football_lab/team_styles/team_styles_2026_asof_YYYYMMDD.csv
```

このデータは、今回の正式予測特徴量には入れないでください。

---

## 5.9 選手スタッツ・得点者予測用データ

### 作成ファイル

```text
src/data/scrape_player_stats.py
```

### URL例

```text
https://www.football-lab.jp/kasm/ranking?year=2026
```

※ 上記は鹿島の例です。各チームのURLコードに対応できるよう、チームマスタを用意してください。

### 取得対象

```text
Player
Team
Position
Played Games
Goals
Assists
CBP
CBP_90
Shoot_Point
Shoot_Point_90
Goal_Point
Goal_Point_90
```

### 今回の扱い

余裕があれば、得点者候補Top5を `scorer_candidates` に入れてください。難しい場合は、`scorer_candidates` は空配列のままで構いません。

---

## 6. Phase 3：特徴量生成

### 6.1 入力

```text
data/processed/matches_2026_clean.csv
data/processed/standings_2026_clean.csv
data/processed/team_stats_2026_clean.csv
data/processed/market_values_2026_clean.csv
Data/ML_dataset.csv
Models/model_features.pkl
Models/feature_policy.json
```

### 6.2 出力

```text
data/features/match_features_2026.csv
data/features/upcoming_features_2026.csv
```

### 6.3 生成する特徴量

最低限、`Models/model_features.pkl` に存在する特徴量を生成してください。

主なカテゴリ:

```text
Team Baseline:
- Current_Rank
- Rank_Delta_3
- Rank_Diff
- Elo_Before
- Elo_Diff
- Market_Value
- Market_Value_Diff
- Manager_Tenure

Team Momentum & H2H:
- Current_Points
- Rolling_Points_5
- Rolling_xG
- AGI
- KAGI
- H2H_Score_Avg
- Stadium_Fill_Rate

Team Stats:
- Jリーグ公式チームスタッツ一式
- Prev_チームスタッツ一式

Conditioning:
- Rest_Days
- Away_Travel_Distance_km

Tactical:
- Formation系
- Backline_Matchup
- is_Mirror_Game
- Midfield_Advantage
- Defense_Margin
- Prev_Goal_* 系
- Prev_Team_Style系

Season Motivation:
- Season_Progress
- Urgency_Score
```

### 6.4 未来試合の補完ルール

未来試合で取得できない値は、以下の順で補完してください。

1. 試合前時点の最新値
2. 直近値
3. 前年値
4. リーグ平均
5. それでも無理なら対象試合をスキップ

ただし、天候は補完しないでください。天候なしモデルでは使いません。

### 6.5 特徴量列合わせ

モデル入力直前で、必ず以下を行ってください。

```python
X = X.reindex(columns=model_features, fill_value=0)
```

ただし、`Weather` / `Weather_*` は生成しないでください。

---

## 7. Phase 4：一括予測

### 7.1 作成ファイル

```text
src/predict/predict_upcoming.py
scripts/run_prediction.py
scripts/full_pipeline.py
```

### 7.2 `predict_upcoming.py`

以下の関数を実装してください。

```python
def load_upcoming_features(path):
    ...

def select_prediction_targets(df, mode="next_section"):
    ...

def predict_upcoming_matches(
    features_df,
    model_dir=None,
    season=2026,
    league="J1",
    competition="明治安田J1百年構想リーグ",
    category="100yj1",
):
    ...
```

### 7.3 予測対象モード

```text
next_section: 次節のみ
all_unplayed: 未消化試合すべて
date_range: 指定期間内の試合
```

### 7.4 出力JSON

```text
outputs/latest_predictions.json
outputs/latest_predictions.csv
outputs/prediction_history/latest_predictions_YYYYMMDD_HHMMSS.json
outputs/last_updated.txt
```

JSON形式:

```json
{
  "last_updated": "2026-05-09T21:00:00+09:00",
  "season": 2026,
  "league": "J1",
  "competition": "明治安田J1百年構想リーグ",
  "category": "100yj1",
  "matchweek": 12,
  "model_version": "weather_removed_v1",
  "feature_policy": {
    "exclude_weather": true
  },
  "matches": [],
  "skipped_matches": [],
  "warnings": [],
  "data_sources": {}
}
```

各matchには、Week2の `predict_match()` の返却項目を維持してください。

---

## 8. Phase 5：安全な保存・バリデーション

### 8.1 latest_predictions.jsonの保存手順

1. `outputs/latest_predictions.tmp.json` に保存
2. JSONとして読み込めるか確認
3. 必須キーを検証
4. `matches` が空でないか確認
5. 各試合に必須項目があるか確認
6. `Weather` / `Weather_*` が含まれていないことを確認
7. 問題なければ `outputs/latest_predictions.json` に置換
8. `outputs/prediction_history/` にコピー
9. `outputs/last_updated.txt` を更新

### 8.2 品質チェック

`src/features/validation.py` に以下を実装してください。

```text
スキーマチェック
件数チェック
チーム名チェック
重複チェック
欠損チェック
未来情報チェック
Weather特徴量禁止チェック
model_featuresとの差分チェック
```

失敗時は `latest_predictions.json` を更新しないでください。

---

## 9. 実行スクリプト

### 9.1 データ更新

```bash
python scripts/update_2026_data.py
python scripts/update_2026_data.py --use-cache
```

### 9.2 天候なしモデル再学習

```bash
python scripts/evaluate_weather_feature.py
python scripts/retrain_models_no_weather.py --dataset Data/ML_dataset.csv --output-dir Models/weather_removed_v1
python scripts/retrain_models_no_weather.py --dataset Data/ML_dataset.csv --output-dir Models/weather_removed_v1 --activate
```

### 9.3 特徴量生成

```bash
python scripts/make_upcoming_features.py --season 2026 --category 100yj1
```

### 9.4 一括予測

```bash
python scripts/run_prediction.py --mode next_section
python scripts/run_prediction.py --mode all_unplayed
```

### 9.5 フルパイプライン

```bash
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode all_unplayed --use-cache
```

---

## 10. 完了レポート

以下を作成してください。

```text
docs/weather_feature_decision.md
docs/model_retraining_report.md
docs/data_source_report_2026.md
docs/week3_completion_report.md
```

### `docs/week3_completion_report.md` の構成

```markdown
# Week3 完了レポート

## 概要

## 実施した作業

## 作成・更新したファイル

## 天候特徴量の扱い

## モデル再学習結果

## 2026年データ取得結果

## ゴールパターン・チームスタイルの扱い

## 特徴量生成結果

## 一括予測結果

## latest_predictions.json の検証結果

## 実行したコマンド

## 見つかった問題

## 次フェーズへの引き継ぎ
```

---

## 11. 実行確認コマンド

作業後、最低限以下を実行してください。

```bash
python -m compileall src scripts
python scripts/smoke_test_load_models.py
python scripts/smoke_test_predict_match.py
python scripts/evaluate_weather_feature.py
python scripts/retrain_models_no_weather.py --dataset Data/ML_dataset.csv --output-dir Models/weather_removed_v1
python scripts/update_2026_data.py --use-cache
python scripts/make_upcoming_features.py --season 2026 --category 100yj1
python scripts/run_prediction.py --mode next_section
python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section --use-cache
```

pytestが利用できる場合:

```bash
pytest
```

---

## 12. 完了条件

以下を満たしたらWeek3完了です。

- [ ] 天候なしモデルの再学習が完了している
- [ ] 既存モデルとの比較レポートがある
- [ ] 採用基準を満たす場合のみ、天候なしモデルが正式反映されている
- [ ] `feature_policy.json` が作成されている
- [ ] `Weather` / `Weather_*` を使わずに推論できる
- [ ] 2026年J1百年構想リーグの日程・結果が取得されている
- [ ] 2026年チームスタッツが取得されている
- [ ] 2026年市場価値が取得または手動CSVから読み込まれている
- [ ] ゴールパターン・チームスタイルは正式特徴量では前年 `Prev_*` のみ使用されている
- [ ] 当年ゴールパターン・チームスタイルは将来改善用rawとして保存されている
- [ ] `data/features/upcoming_features_2026.csv` が生成されている
- [ ] `outputs/latest_predictions.json` が生成されている
- [ ] JSONバリデーションが成功している
- [ ] 失敗時に既存latestを壊さない
- [ ] 完了レポートが日本語で作成されている

---

## 13. Codexの最終回答に含める内容

作業完了後、以下の形式で日本語で報告してください。

```markdown
## 実施内容

## 作成・更新したファイル

## モデル再学習結果

## 2026年データ取得結果

## 一括予測結果

## 実行したコマンド

## 実行結果

## 見つかった問題

## 次にやるべきこと
```
