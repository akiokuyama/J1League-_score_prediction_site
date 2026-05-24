# 2026_specialデータ取得レポート

## 概要

2026年特別シーズンの明治安田J1百年構想リーグ向けに、日程・順位表・市場価値・Football Lab系データ・選手スタッツの取得処理を実装しました。取得できたHTMLは `data/raw/html_cache/` に保存し、`--use-cache` で再パースできるようにしています。

2026-05-10に追加調査を行い、前回未取得だった市場価値、Jリーグ公式チームスタッツ、Football Lab summary系は取得できる状態まで復旧しました。推測で値を作らず、取得できたHTMLキャッシュとパーサ修正に基づいてCSVを更新しています。

## 取得結果

| データ | 取得件数 | 状態 | 保存先 |
|---|---:|---|---|
| 試合日程・結果 | 180行 | 取得成功 | `data/processed/matches_2026_special_clean.csv` |
| 順位表 | 20行 | EAST/WEST各10行を取得。`division` 列を追加し、処理済みCSVでは英字列名・チームコードへ正規化済み | `data/processed/standings_2026_special_clean.csv` |
| チームスタッツ | 520行 | 取得成功。HTMLカード形式をパース | `data/processed/team_stats_2026_special_clean.csv` |
| 市場価値 | 20行 | 取得成功。Transfermarkt正規URLから取得し、手動CSVにも保存 | `data/processed/market_values_2026_special_clean.csv` |
| Football Lab expected | 40行 | 取得成功 | `data/raw/football_lab/expected_2026_special.csv` |
| Football Lab AGI/KAGI | 40行 | 取得成功 | `data/raw/football_lab/kagi_2026_special.csv` |
| Football Lab ゴールパターン | 20行 | 取得成功 | `data/raw/football_lab/goal_patterns/goal_patterns_2026_special_asof_20260510.csv` |
| Football Lab チームスタイル | 60行 | 取得成功 | `data/raw/football_lab/team_styles/team_styles_2026_special_asof_20260510.csv` |
| フォーメーション | 20行 | 取得成功。実フォーメーション抽出済み、Unknown 0件 | `data/processed/formations_2026_special_clean.csv` |
| 選手スタッツ | 200行 | `?year=2026` 付きURLが2025年ページを返すため、現行2026年特別シーズンページの `/ranking` から再取得。英字列正規化と `scorer_score` 作成済み | `data/processed/player_stats_2026_special_clean.csv` |

試合日程は180試合中151試合が終了済み、29試合が未消化として抽出されています。

## 取得できたHTML

代表的なHTMLキャッシュは以下です。

- 試合日程: `data/raw/html_cache/ad943ca5b09cfc2f236e.html`
- 順位表: `data/raw/html_cache/836fd36e66a723a2c84c.html`
- Transfermarkt: `data/raw/html_cache/0ca37779893876f4fbc6.html`
- Football Lab expected: `data/raw/html_cache/c96428150c18b33720de.html`
- Football Lab AGI/KAGI: `data/raw/html_cache/7355adbabf3470f0e06e.html`
- Football Lab ゴールパターン: `data/raw/html_cache/2b95089cde730e517a47.html`
- Football Lab チームスタイル: `data/raw/html_cache/a75273ed6ddfbdc86006.html`
- Football Labのチーム別フォーメーション・ランキングページ: `data/raw/html_cache/*.html`
- Jリーグ公式チームスタッツ各ページ: `data/raw/html_cache/*.html`

詳細な取得URL・件数・警告は `data/processed/update_2026_special_report.json` に保存しています。

## 解消済みの失敗ログ

前回の失敗内容と解消内容は以下です。

- Jリーグ公式チームスタッツ: `pd.read_html` では `No tables found` だったが、HTML内の `ul.ranking_list` をBeautifulSoupで読むことで解消
- Transfermarkt: URLが旧J1リーグ向けだったため、`https://www.transfermarkt.com/j1-100-year-vision-league/startseite/wettbewerb/J1YV` に修正して解消
- Football Lab summary系: `year=2026` のURLでは500エラーだったため、百年構想リーグ用の `j1001` / `year=100` URLに修正して解消

## 残っている問題

- フォーメーションは `?year=2026` では2025ページを返すため、現行2026年特別シーズンページの `/formation/` に修正して解消
- 選手スタッツは `?year=2026` では2025ページを返すため、現行2026年特別シーズンページの `/ranking` を取得するよう修正し、2026_special現行データとして再取得済み
- 特徴量生成ではセル単位の実取得由来/補完由来フラグを `data/features/upcoming_features_2026_special_sources.csv` に出力済み

## 未完了タスク

- 順位表のEAST/WEST取得、列名正規化、チーム名重複表記の除去は対応済み
- アプリ側で `scorer_candidates` を表示するUI確認
- `next_section` と `all_unplayed` の出力ファイル分離方針の決定
- pytestベースの回帰テスト追加

## 代替案

- 市場価値は自動取得結果を `data/manual/market_values_2026_special.csv` に保存済み。今後Transfermarkt取得が失敗した場合は手動CSVを優先する
- チームスタッツ・xG・AGI・KAGIは取得済み。今後取得失敗した場合は既存キャッシュを `--use-cache` で使用する
- Football Lab summary系は、接続可能な環境でHTMLキャッシュを作成済み。以後は `--use-cache` でパース可能
- フォーメーションは現行2026年特別シーズンページから抽出済み。今後取得に失敗した場合は既存キャッシュを `--use-cache` で使用する

## 実行コマンド

```bash
python scripts/update_2026_special_data.py --use-cache
```
