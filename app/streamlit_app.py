"""Streamlit MVP for viewing generated J1 prediction outputs."""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import quote

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.evaluation import (  # noqa: E402
    evaluate_prediction,
    get_match_insight_label,
    get_score_outcome,
    get_strongest_outcome,
    outcome_label,
)
from app.utils.formatters import (  # noqa: E402
    format_accuracy,
    format_date,
    format_datetime_jp,
    format_optional_parts,
    format_percent,
    format_score,
)
from app.utils.load_predictions import (  # noqa: E402
    load_all_unplayed_predictions,
    load_latest_predictions,
    load_past_prediction_results,
)
from src.data.team_master import to_display_name  # noqa: E402


st.set_page_config(
    page_title="J1 AI試合結果予測",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def main() -> None:
    inject_css()
    latest = load_latest_predictions()
    all_unplayed = load_all_unplayed_predictions()
    past = load_past_prediction_results()

    initialize_state()
    render_header(latest)

    tab = "これからの試合"
    if st.session_state.view != "detail":
        tab = st.radio(
            "表示切替",
            ["これからの試合", "過去の予測結果"],
            horizontal=True,
            label_visibility="collapsed",
        )

    if tab == "これからの試合":
        if st.session_state.view != "detail":
            render_prediction_logic_summary(latest)
        render_future_matches(latest, all_unplayed)
    else:
        render_past_predictions(past)


def initialize_state() -> None:
    if "view" not in st.session_state:
        st.session_state.view = "list"
    if "selected_match_id" not in st.session_state:
        st.session_state.selected_match_id = None
    query_params = st.query_params
    if query_params.get("view") == "detail" and query_params.get("match_id"):
        st.session_state.view = "detail"
        st.session_state.selected_match_id = query_params.get("match_id")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: #f6f8fb;
        }
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", "Noto Sans JP", "Segoe UI", sans-serif;
            color: #0f172a;
        }
        .block-container { max-width: 760px; padding-top: 2rem; padding-bottom: 2rem; }
        div[data-testid="stRadio"] > div { gap: .45rem; }
        .app-header, .summary-card {
            border: 1px solid #dbe3ef;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
            margin-bottom: 14px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }
        .app-header {
            border-left: 6px solid #2563eb;
        }
        .app-title {
            margin: 0 0 .45rem 0;
            font-size: 1.9rem;
            line-height: 1.2;
            letter-spacing: 0;
            font-weight: 850;
        }
        .muted { color: #64748b; font-size: .88rem; }
        .small { color: #64748b; font-size: .8rem; }
        .section-title {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 18px 0 10px;
            font-size: 1.08rem;
            font-weight: 800;
        }
        .section-title::before {
            content: "";
            width: 4px;
            height: 20px;
            border-radius: 99px;
            background: #2563eb;
        }
        .header-meta {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin-top: 12px;
        }
        .meta-chip {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 9px 10px;
            background: #f8fafc;
            color: #334155;
            font-size: .86rem;
            font-weight: 700;
        }
        .match-card-link {
            text-decoration: none !important;
            color: inherit !important;
            display: block;
        }
        .match-card {
            border: 1px solid #dbe3ef;
            border-left: 5px solid #0f766e;
            border-radius: 8px;
            padding: 18px 18px 16px;
            background: #ffffff;
            margin-bottom: 14px;
            box-shadow: 0 7px 18px rgba(15, 23, 42, 0.055);
            cursor: pointer;
            transition: border-color .12s ease, background .12s ease, box-shadow .12s ease, transform .12s ease;
        }
        .match-card:hover {
            border-color: #94a3b8;
            background: #f8fafc;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.085);
            transform: translateY(-1px);
        }
        .teams { font-size: 1.06rem; font-weight: 800; margin: .45rem 0 .65rem; }
        .score-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            border-top: 1px solid #eef2f7;
            padding-top: 12px;
            margin-top: 10px;
        }
        .score, .score-pill {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
            letter-spacing: 0;
        }
        .score { font-size: 1.65rem; font-weight: 850; color: #0f172a; }
        .score-pill {
            display: inline-block;
            border-radius: 8px;
            padding: 7px 10px;
            background: #eff6ff;
            color: #1d4ed8;
            font-size: 1.35rem;
            font-weight: 850;
            line-height: 1;
        }
        .prob-line {
            color: #475569;
            font-size: .88rem;
            font-weight: 650;
            text-align: right;
        }
        .label {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: .78rem;
            font-weight: 700;
            background: #f1f5f9;
            color: #334155;
            margin-right: 4px;
            margin-top: 6px;
        }
        .home-advantage { background: #dbeafe; color: #1d4ed8; }
        .away-advantage { background: #fee2e2; color: #b91c1c; }
        .hit { background: #dcfce7; color: #166534; }
        .miss { background: #fee2e2; color: #991b1b; }
        .metric-line { display: flex; justify-content: space-between; gap: 10px; }
        .summary-card {
            border-left: 5px solid #f59e0b;
        }
        .logic-card {
            border: 1px solid #dbe3ef;
            border-left: 5px solid #2563eb;
            border-radius: 8px;
            padding: 16px;
            background: #ffffff;
            margin-bottom: 16px;
            box-shadow: 0 7px 18px rgba(15, 23, 42, 0.055);
        }
        .logic-card-title {
            font-weight: 850;
            font-size: 1.02rem;
            margin-bottom: 8px;
        }
        .logic-card ul {
            margin: 8px 0 0 1.1rem;
            padding: 0;
            color: #475569;
            font-size: .9rem;
            line-height: 1.65;
        }
        .beta-note {
            border: 1px solid #fde68a;
            border-left: 5px solid #f59e0b;
            border-radius: 8px;
            background: #fffbeb;
            color: #92400e;
            padding: 12px 14px;
            margin: 0 0 16px 0;
            font-size: .9rem;
            line-height: 1.55;
            font-weight: 650;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
        }
        .summary-item {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background: #f8fafc;
            padding: 10px;
        }
        .summary-label {
            color: #64748b;
            font-size: .78rem;
            margin-bottom: 4px;
        }
        .summary-value {
            color: #0f172a;
            font-size: 1.05rem;
            font-weight: 850;
        }
        @media (max-width: 640px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .score { font-size: 1.45rem; }
            .app-header { padding: 18px 16px; }
            .app-title { font-size: 1.55rem; }
            .header-meta, .summary-grid { grid-template-columns: 1fr; }
            .score-row { align-items: flex-start; flex-direction: column; }
            .prob-line { text-align: left; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_prediction_logic_summary(data: dict[str, Any]) -> None:
    feature_count = resolve_feature_count(data)
    feature_text = f"{feature_count}個" if feature_count is not None else "複数"
    st.markdown(
        f"""
        <div class="beta-note">
          このアプリの予測は、過去データと機械学習モデルに基づく参考情報です。実際の試合結果を保証するものではありません。
        </div>
        <div class="logic-card">
          <div class="logic-card-title">このアプリの予測について</div>
          <ul>
            <li>試合ごとのチーム状態・直近成績・戦術情報など、{feature_text}の特徴量を使って機械学習モデルが試合結果を予測しています。</li>
            <li>予測スコアは、AIモデルが算出した期待得点と勝敗確率をもとに、最も有力なスコア候補として表示しています。</li>
            <li>得点者候補は、チームのゴール期待値を選手の得点実績・アシスト・攻撃指標に応じて配分した参考予測です。</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(data: dict[str, Any]) -> None:
    season = data.get("season", "-")
    matchweek = data.get("matchweek", "-")
    updated = format_datetime_jp(data.get("last_updated"))
    matchweek_text = f"第{matchweek}節" if matchweek not in (None, "-") else "-"
    st.markdown(
        f"""
        <div class="app-header">
          <h1 class="app-title">J1 試合結果予測アプリ</h1>
          <div class="muted">次節の試合予測と過去の予測結果を確認できます。</div>
          <div class="header-meta">
            <div class="meta-chip">シーズン：{escape(str(season))}</div>
            <div class="meta-chip">対象節：{escape(str(matchweek_text))}</div>
            <div class="meta-chip">最終更新：{escape(str(updated))}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_future_matches(latest: dict[str, Any], all_unplayed: dict[str, Any]) -> None:
    matches = safe_matches(latest)
    if st.session_state.view == "detail":
        selected = find_match(matches, st.session_state.selected_match_id)
        if selected:
            render_match_detail(selected)
            return
        st.session_state.view = "list"
        st.session_state.selected_match_id = None

    st.markdown('<div class="section-title">試合一覧</div>', unsafe_allow_html=True)
    if all_unplayed.get("matches"):
        st.caption(f"管理用の未消化試合全件データ: {len(all_unplayed['matches'])}試合")
    if not matches:
        st.info("予測データが見つかりません。")
        return
    filtered_matches = filter_future_matches(matches)
    st.caption(f"表示中：{len(filtered_matches)} / {len(matches)} 試合")
    if not filtered_matches:
        st.info("条件に一致する試合はありません。")
        return
    for match in filtered_matches:
        render_match_card(match)


def filter_future_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    st.markdown('<div class="section-title">絞り込み</div>', unsafe_allow_html=True)
    teams = sorted({display_team(team) for match in matches for team in [match.get("home_team"), match.get("away_team")] if team})
    sections = sorted({int(match_section(match)) for match in matches if _is_int_like(match_section(match))})

    team = st.selectbox("チーム", ["すべてのチーム", *teams], key="future_team_filter")
    section = st.selectbox("試合が行われる節", ["すべての節", *sections], key="future_section_filter")

    filtered: list[dict[str, Any]] = []
    for match in matches:
        names = {display_team(match.get("home_team")), display_team(match.get("away_team"))}

        if team != "すべてのチーム" and team not in names:
            continue
        if section != "すべての節" and safe_int(match_section(match)) != int(section):
            continue
        filtered.append(match)
    return filtered


def render_match_card(match: dict[str, Any]) -> None:
    probabilities = match.get("result_probabilities")
    strongest = get_strongest_outcome(probabilities)
    insight = get_match_insight_label(probabilities)
    match_id = str(match.get("match_id") or id(match))
    home = display_team(match.get("home_team"))
    away = display_team(match.get("away_team"))
    matchup = format_matchup(home, away)
    score = format_score(match.get("predicted_score"))
    meta = format_match_meta(match)
    href = f"?view=detail&match_id={quote(match_id)}"
    insight_class = "home-advantage" if insight == "ホーム優勢" else "away-advantage" if insight == "アウェイ優勢" else ""
    insight_html = f'<span class="label {insight_class}">{escape(insight)}</span>' if insight else ""

    st.markdown(
        f"""
        <a href="{href}" target="_self" class="match-card-link">
          <div class="match-card">
            <div class="small">{escape(meta)}</div>
            <div class="teams">{escape(matchup)}</div>
            <div class="score-row">
              <div class="score-pill">{escape(score)}</div>
              <div class="prob-line">勝敗確率トップ：{escape(str(strongest["label"]))}<br>{escape(format_percent(strongest["value"]))}</div>
            </div>
            {insight_html}
          </div>
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_match_detail(match: dict[str, Any]) -> None:
    if st.button("← 試合一覧に戻る", use_container_width=True):
        st.session_state.view = "list"
        st.session_state.selected_match_id = None
        st.query_params.clear()
        st.rerun()

    home = display_team(match.get("home_team"))
    away = display_team(match.get("away_team"))
    matchup = format_matchup(home, away)
    probabilities = match.get("result_probabilities")
    strongest = get_strongest_outcome(probabilities)
    insight = get_match_insight_label(probabilities)
    predicted_score = match.get("predicted_score")
    score_text = format_score(predicted_score)

    st.markdown(f'<div class="section-title">{escape(matchup)}</div>', unsafe_allow_html=True)
    st.caption(format_match_meta(match))
    st.markdown(f"<div class='score'>{score_text}</div>", unsafe_allow_html=True)

    render_conclusion(match, strongest, insight)
    render_expected_goals(match)
    render_probability_bars(probabilities)
    render_probability_note(match, strongest)
    render_score_candidates(match.get("score_candidates"))
    render_scorer_candidates(match, home, away)


def render_conclusion(match: dict[str, Any], strongest: dict[str, Any], insight: str | None) -> None:
    score_text = format_score(match.get("predicted_score"))
    predicted_outcome = get_score_outcome(match.get("predicted_score"))
    strongest_key = strongest.get("key")
    trend = f'試合傾向は「{insight}」です。' if insight else ""

    if strongest_key == "draw":
        message = f"この試合の見立て：予測スコアは {score_text}、勝敗確率トップは 引き分け です。"
    elif predicted_outcome == strongest_key:
        message = f"この試合の見立て：予測スコアは {score_text}、勝敗確率トップは {strongest['label']} です。{trend}"
    else:
        message = f"この試合の見立て：単一スコアでは {score_text} が最有力です。ただし勝敗確率では {strongest['label']} が最も高くなっています。{trend}"

    st.markdown(f"<div class='summary-card'><strong>{message}</strong></div>", unsafe_allow_html=True)


def render_expected_goals(match: dict[str, Any]) -> None:
    expected = match.get("expected_goals") if isinstance(match.get("expected_goals"), dict) else {}
    home_xg = safe_float(expected.get("home"))
    away_xg = safe_float(expected.get("away"))
    st.markdown('<div class="section-title">期待得点</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("ホーム期待得点", f"{home_xg:.2f}" if home_xg is not None else "-")
    col2.metric("アウェイ期待得点", f"{away_xg:.2f}" if away_xg is not None else "-")

    candidates = match.get("score_candidates") or []
    if candidates:
        st.caption(f"最有力スコア候補：{candidates[0].get('score', '-')}（{format_percent(candidates[0].get('probability'))}）")


def render_probability_bars(probabilities: dict | None) -> None:
    st.markdown('<div class="section-title">勝敗確率</div>', unsafe_allow_html=True)
    values = [
        ("ホーム勝利", _probability_value(probabilities, "home_win")),
        ("引き分け", _probability_value(probabilities, "draw")),
        ("アウェイ勝利", _probability_value(probabilities, "away_win")),
    ]
    for label, value in values:
        st.markdown(f"<div class='metric-line'><span>{label}</span><strong>{format_percent(value)}</strong></div>", unsafe_allow_html=True)
        st.progress(max(0.0, min(float(value or 0), 1.0)))


def render_probability_note(match: dict[str, Any], strongest: dict[str, Any]) -> None:
    score_text = format_score(match.get("predicted_score"))
    st.caption("勝敗確率は「勝ち・引き分け・負け」という結果カテゴリごとの合算値です。予測スコアとは計算単位が異なります。")
    predicted_outcome = get_score_outcome(match.get("predicted_score"))
    if strongest.get("key") in {"home", "away"} and predicted_outcome != strongest.get("key"):
        st.info(
            f"なぜ「{score_text}」なのに{strongest['label']}が高いのか？\n\n"
            f"予測スコアは、個別のスコア候補の中で最も選ばれやすい1つを表示しています。"
            f"一方、勝敗確率は複数のスコア候補を合算した確率です。"
            f"そのため、単一スコアでは {score_text} が最上位でも、勝敗全体では{strongest['label']}が最も高くなる場合があります。"
        )


def render_score_candidates(candidates: Any) -> None:
    with st.expander("スコア候補 Top 5", expanded=False):
        if not isinstance(candidates, list) or not candidates:
            st.write("スコア候補はありません。")
            return
        st.caption("各行は「その試合が該当スコアで終わる確率」を表します。%はスコア候補内での相対的な起こりやすさです。")
        for index, candidate in enumerate(candidates[:5], start=1):
            score = candidate.get("score", "-") if isinstance(candidate, dict) else "-"
            probability = candidate.get("probability") if isinstance(candidate, dict) else None
            st.write(f"{index}. 予測スコア {score} ({format_percent(probability)})")


def render_scorer_candidates(match: dict[str, Any], home: str, away: str) -> None:
    candidates = match.get("scorer_candidates") if isinstance(match.get("scorer_candidates"), dict) else {}
    expected = match.get("expected_goals") if isinstance(match.get("expected_goals"), dict) else {}
    with st.expander("得点者候補 Top 5", expanded=False):
        render_team_scorers(home, candidates.get("home"), safe_float(expected.get("home")))
        st.divider()
        render_team_scorers(away, candidates.get("away"), safe_float(expected.get("away")))


def render_team_scorers(team: str, scorers: Any, team_expected_goals: float | None) -> None:
    st.markdown(f"**{team}**")
    if not isinstance(scorers, list) or not scorers:
        st.write("得点者候補はまだありません。")
        return
    total_weight = sum(max(safe_float(scorer.get("scorer_score")) or 0.0, 0.0) for scorer in scorers if isinstance(scorer, dict))
    for index, scorer in enumerate(scorers[:5], start=1):
        if not isinstance(scorer, dict):
            continue
        parts = [scorer.get("player", "-")]
        if scorer.get("position"):
            parts.append(str(scorer["position"]))
        if scorer.get("probability") is not None:
            parts.append(format_percent(scorer.get("probability")))
        goals = safe_float(scorer.get("goals"))
        if goals is not None:
            parts.append(f"今季{int(goals)}得点")
        scorer_expected_goals = estimate_scorer_expected_goals(scorer, total_weight, team_expected_goals)
        if scorer_expected_goals is not None:
            parts.append(f"ゴール期待値 {scorer_expected_goals:.2f}")
        st.write(f"{index}. " + " / ".join(parts))


def render_past_predictions(data: dict[str, Any]) -> None:
    st.markdown('<div class="section-title">過去の予測結果</div>', unsafe_allow_html=True)
    matches = safe_matches(data)
    if not matches:
        st.info("過去の予測結果はまだありません。")
        return

    st.caption("判定の見方：「勝敗」は勝ち・引き分け・負けの方向性で判定し、「スコア」は点数まで完全一致したかで判定します。")
    filtered = filter_past_matches(matches)
    render_past_summary(filtered)
    if not filtered:
        st.info("条件に一致する過去予測はありません。")
        return
    for match in filtered:
        render_past_card(match)


def filter_past_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections = sorted({int(m.get("matchweek") or m.get("section")) for m in matches if _is_int_like(m.get("matchweek") or m.get("section"))})
    teams = sorted({display_team(team) for m in matches for team in [m.get("home_team"), m.get("away_team")] if team})
    result_options = ["すべての判定", "勝敗的中", "勝敗外れ", "スコア的中", "スコア外れ"]

    st.markdown('<div class="section-title">絞り込み</div>', unsafe_allow_html=True)
    team = st.selectbox("チーム", ["すべてのチーム", *teams], key="past_team_filter")
    section = st.selectbox("試合が行われた節", ["すべての節", *sections], key="past_section_filter")
    judgment = st.selectbox("予測結果に対する判定", result_options, key="past_judgment_filter")

    filtered: list[dict[str, Any]] = []
    for match in matches:
        evaluation = evaluate_prediction(match.get("predicted_score"), match.get("actual_score"))
        match_section = match.get("matchweek") or match.get("section")
        names = {display_team(match.get("home_team")), display_team(match.get("away_team"))}
        if section != "すべての節" and safe_int(match_section) != int(section):
            continue
        if team != "すべてのチーム" and team not in names:
            continue
        if judgment != "すべての判定" and judgment not in {evaluation["result_label"], evaluation["score_label"]}:
            continue
        filtered.append(match)
    return filtered


def render_past_summary(matches: list[dict[str, Any]]) -> None:
    evaluations = [evaluate_prediction(m.get("predicted_score"), m.get("actual_score")) for m in matches]
    total = len(evaluations)
    result_hits = sum(1 for item in evaluations if item["result_hit"])
    score_hits = sum(1 for item in evaluations if item["score_hit"])

    st.markdown(
        f"""
        <div class="summary-card">
          <div class="summary-grid">
            <div class="summary-item">
              <div class="summary-label">勝敗的中率</div>
              <div class="summary-value">{format_accuracy(result_hits, total)}</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">スコア的中率</div>
              <div class="summary-value">{format_accuracy(score_hits, total)}</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">今シーズン予測試合数</div>
              <div class="summary-value">{total}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_past_card(match: dict[str, Any]) -> None:
    evaluation = evaluate_prediction(match.get("predicted_score"), match.get("actual_score"))
    result_class = "hit" if evaluation["result_hit"] else "miss"
    score_class = "hit" if evaluation["score_hit"] else "miss"
    home = display_team(match.get("home_team"))
    away = display_team(match.get("away_team"))
    matchup = format_matchup(home, away)

    st.markdown(
        f"""
        <div class="match-card">
          <div class="small">{escape(format_match_meta(match))}</div>
          <div class="teams">{escape(matchup)}</div>
          <span class="label {result_class}">{evaluation["result_label"]}</span>
          <span class="label {score_class}">{evaluation["score_label"]}</span>
          <div class="score-row">
            <div>予測スコア：<strong class="score">{format_score(match.get("predicted_score"))}</strong></div>
            <div>実際のスコア：<strong class="score">{format_score(match.get("actual_score"))}</strong></div>
          </div>
          <div class="small">予測の勝敗方向：{outcome_label(evaluation["predicted_outcome"])}</div>
          <div class="small">実際の勝敗方向：{outcome_label(evaluation["actual_outcome"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_match_meta(match: dict[str, Any]) -> str:
    date = format_date(match.get("date") or match.get("match_date"))
    kickoff = match.get("kickoff")
    venue = match.get("venue")
    return format_optional_parts(date, kickoff, venue)


def format_matchup(home: str, away: str) -> str:
    return f"{home}（H） vs {away}（A）"


def match_section(match: dict[str, Any]) -> Any:
    return match.get("matchweek") or match.get("section")


def resolve_feature_count(data: dict[str, Any]) -> int | None:
    for match in safe_matches(data):
        model_info = match.get("model_info")
        if isinstance(model_info, dict) and _is_int_like(model_info.get("feature_count")):
            return int(model_info["feature_count"])
    return None


def find_match(matches: list[dict[str, Any]], match_id: str | None) -> dict[str, Any] | None:
    for match in matches:
        if str(match.get("match_id") or id(match)) == str(match_id):
            return match
    return None


def safe_matches(data: dict[str, Any]) -> list[dict[str, Any]]:
    matches = data.get("matches")
    if not isinstance(matches, list):
        return []
    return [match for match in matches if isinstance(match, dict)]


def display_team(value: Any) -> str:
    if value is None or value == "":
        return "-"
    return to_display_name(str(value))


def safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def estimate_scorer_expected_goals(
    scorer: dict[str, Any],
    total_weight: float,
    team_expected_goals: float | None,
) -> float | None:
    if team_expected_goals is None or team_expected_goals < 0 or total_weight <= 0:
        return None
    scorer_weight = max(safe_float(scorer.get("scorer_score")) or 0.0, 0.0)
    if scorer_weight <= 0:
        return None
    return team_expected_goals * scorer_weight / total_weight


def _probability_value(probabilities: dict | None, key: str) -> float:
    if not isinstance(probabilities, dict):
        return 0.0
    value = safe_float(probabilities.get(key))
    return value if value is not None else 0.0


def _is_int_like(value: Any) -> bool:
    try:
        int(value)
    except (TypeError, ValueError):
        return False
    return True


if __name__ == "__main__":
    main()
