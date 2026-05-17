import React, { useState } from "react";

const predictionData = {
  last_updated: "2026-05-10T14:55:32+09:00",
  season: 2026,
  league: "J1 百年構想リーグ",
  matchweek: 12,
  warnings: [],
  skipped_matches: [],
  matches: [
    {
      match_id: "2026-J1YV-012-001",
      date: "2026-05-16",
      kickoff: "14:00",
      venue: "町田GIONスタジアム",
      home_team: "町田ゼルビア",
      away_team: "東京ヴェルディ",
      predicted_score: { home: 1, away: 1 },
      expected_goals: { home: 1.18, away: 1.35 },
      result_probabilities: { home_win: 0.2211, draw: 0.2668, away_win: 0.5121 },
      score_candidates: [
        { score: "1-1", probability: 0.116 },
        { score: "1-2", probability: 0.104 },
        { score: "0-1", probability: 0.092 },
        { score: "2-1", probability: 0.076 },
        { score: "0-0", probability: 0.071 }
      ],
      scorer_candidates: {
        home: [
          { player: "ホーム選手A", probability: 0.21, position: "FW" },
          { player: "ホーム選手B", probability: 0.17, position: "MF" },
          { player: "ホーム選手C", probability: 0.13, position: "FW" },
          { player: "ホーム選手D", probability: 0.1, position: "MF" },
          { player: "ホーム選手E", probability: 0.08, position: "DF" }
        ],
        away: [
          { player: "アウェイ選手A", probability: 0.24, position: "FW" },
          { player: "アウェイ選手B", probability: 0.18, position: "FW" },
          { player: "アウェイ選手C", probability: 0.14, position: "MF" },
          { player: "アウェイ選手D", probability: 0.11, position: "MF" },
          { player: "アウェイ選手E", probability: 0.09, position: "DF" }
        ]
      }
    },
    {
      match_id: "2026-J1YV-012-002",
      date: "2026-05-16",
      kickoff: "15:00",
      venue: "ノエビアスタジアム神戸",
      home_team: "ヴィッセル神戸",
      away_team: "京都サンガF.C.",
      predicted_score: { home: 1, away: 0 },
      expected_goals: { home: 1.41, away: 0.74 },
      result_probabilities: { home_win: 0.4816, draw: 0.4211, away_win: 0.0973 },
      score_candidates: [
        { score: "1-0", probability: 0.132 },
        { score: "0-0", probability: 0.118 },
        { score: "1-1", probability: 0.109 },
        { score: "2-0", probability: 0.087 },
        { score: "2-1", probability: 0.071 }
      ],
      scorer_candidates: {
        home: [
          { player: "神戸選手A", probability: 0.23, position: "FW" },
          { player: "神戸選手B", probability: 0.19, position: "MF" },
          { player: "神戸選手C", probability: 0.15, position: "FW" },
          { player: "神戸選手D", probability: 0.12, position: "MF" },
          { player: "神戸選手E", probability: 0.08, position: "DF" }
        ],
        away: [
          { player: "京都選手A", probability: 0.22, position: "FW" },
          { player: "京都選手B", probability: 0.16, position: "MF" },
          { player: "京都選手C", probability: 0.13, position: "FW" },
          { player: "京都選手D", probability: 0.1, position: "MF" },
          { player: "京都選手E", probability: 0.07, position: "DF" }
        ]
      }
    }
  ]
};

const pastPredictionData = {
  season: 2026,
  league: "J1 百年構想リーグ",
  matches: [
    {
      match_id: "2026-J1YV-011-001",
      date: "2026-05-06",
      kickoff: "19:00",
      matchweek: 11,
      venue: "豊田スタジアム",
      home_team: "名古屋グランパス",
      away_team: "浦和レッズ",
      predicted_score: { home: 1, away: 0 },
      actual_score: { home: 2, away: 1 },
      result_probabilities: { home_win: 0.46, draw: 0.31, away_win: 0.23 },
      score_candidates: [
        { score: "1-0", probability: 0.128 },
        { score: "1-1", probability: 0.116 },
        { score: "2-1", probability: 0.094 }
      ]
    },
    {
      match_id: "2026-J1YV-011-002",
      date: "2026-05-06",
      kickoff: "19:30",
      matchweek: 11,
      venue: "国立競技場",
      home_team: "FC東京",
      away_team: "川崎フロンターレ",
      predicted_score: { home: 1, away: 1 },
      actual_score: { home: 0, away: 1 },
      result_probabilities: { home_win: 0.28, draw: 0.34, away_win: 0.38 },
      score_candidates: [
        { score: "1-1", probability: 0.121 },
        { score: "0-1", probability: 0.101 },
        { score: "1-2", probability: 0.086 }
      ]
    },
    {
      match_id: "2026-J1YV-010-001",
      date: "2026-04-29",
      kickoff: "15:00",
      matchweek: 10,
      venue: "パナソニックスタジアム吹田",
      home_team: "ガンバ大阪",
      away_team: "セレッソ大阪",
      predicted_score: { home: 2, away: 1 },
      actual_score: { home: 1, away: 1 },
      result_probabilities: { home_win: 0.49, draw: 0.27, away_win: 0.24 },
      score_candidates: [
        { score: "2-1", probability: 0.109 },
        { score: "1-1", probability: 0.103 },
        { score: "1-0", probability: 0.091 }
      ]
    }
  ]
};

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f1f5f9",
    color: "#0f172a",
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    padding: 20
  },
  container: { maxWidth: 760, margin: "0 auto" },
  header: {
    background: "white",
    borderRadius: 24,
    padding: 20,
    boxShadow: "0 1px 4px rgba(15, 23, 42, 0.08)",
    marginBottom: 16
  },
  badge: {
    display: "inline-block",
    background: "#f1f5f9",
    color: "#475569",
    borderRadius: 999,
    padding: "6px 12px",
    fontSize: 12,
    fontWeight: 700
  },
  title: { fontSize: 28, margin: "12px 0 6px", fontWeight: 900, letterSpacing: "-0.04em" },
  subtitle: { margin: 0, color: "#64748b", fontSize: 14, lineHeight: 1.6 },
  metaGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 16 },
  metaBox: { background: "#f8fafc", borderRadius: 16, padding: 12 },
  metaLabel: { fontSize: 12, color: "#64748b" },
  metaValue: { fontWeight: 800, marginTop: 4 },
  panel: {
    background: "white",
    borderRadius: 22,
    padding: 16,
    boxShadow: "0 1px 4px rgba(15, 23, 42, 0.08)",
    marginBottom: 14
  },
  stepBar: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 8,
    marginBottom: 14,
    position: "sticky",
    top: 0,
    zIndex: 5,
    background: "#f1f5f9",
    padding: "8px 0"
  },
  stepActive: {
    border: "1px solid #0f172a",
    background: "#0f172a",
    color: "white",
    borderRadius: 999,
    padding: "10px 12px",
    fontWeight: 800,
    cursor: "pointer"
  },
  stepInactive: {
    border: "1px solid #cbd5e1",
    background: "white",
    color: "#475569",
    borderRadius: 999,
    padding: "10px 12px",
    fontWeight: 800,
    cursor: "pointer"
  },
  buttonRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 10 },
  button: {
    border: "1px solid #cbd5e1",
    background: "white",
    color: "#334155",
    borderRadius: 12,
    padding: "10px 12px",
    cursor: "pointer",
    fontWeight: 700
  },
  buttonActive: {
    border: "1px solid #0f172a",
    background: "#0f172a",
    color: "white",
    borderRadius: 12,
    padding: "10px 12px",
    cursor: "pointer",
    fontWeight: 700
  },
  select: {
    width: "100%",
    marginTop: 10,
    border: "1px solid #cbd5e1",
    borderRadius: 12,
    padding: 10,
    background: "white"
  },
  matchCard: {
    width: "100%",
    border: "1px solid transparent",
    borderRadius: 20,
    background: "white",
    padding: 16,
    boxShadow: "0 1px 4px rgba(15, 23, 42, 0.08)",
    textAlign: "left",
    cursor: "pointer",
    marginBottom: 12
  },
  matchCardSelected: {
    width: "100%",
    border: "2px solid #0f172a",
    borderRadius: 20,
    background: "white",
    padding: 15,
    boxShadow: "0 1px 4px rgba(15, 23, 42, 0.08)",
    textAlign: "left",
    cursor: "pointer",
    marginBottom: 12
  },
  smallText: { fontSize: 12, color: "#64748b" },
  scoreBox: {
    display: "grid",
    gridTemplateColumns: "1fr auto 1fr",
    alignItems: "center",
    gap: 8,
    marginTop: 14,
    padding: 14,
    background: "#f8fafc",
    borderRadius: 16
  },
  teamCell: { textAlign: "center", fontSize: 13, fontWeight: 700, lineHeight: 1.4 },
  scoreText: { fontSize: 30, fontWeight: 900, padding: "0 10px", whiteSpace: "nowrap" },
  outcomeBadge: {
    display: "inline-block",
    background: "#e0f2fe",
    color: "#075985",
    borderRadius: 999,
    padding: "5px 10px",
    fontSize: 12,
    fontWeight: 800,
    marginTop: 10
  },
  backButton: {
    border: "1px solid #cbd5e1",
    background: "white",
    color: "#334155",
    borderRadius: 999,
    padding: "9px 13px",
    cursor: "pointer",
    fontWeight: 800,
    marginBottom: 12
  },
  detailHeader: { display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" },
  bigScore: {
    background: "#0f172a",
    color: "white",
    borderRadius: 20,
    padding: "16px 24px",
    textAlign: "center",
    minWidth: 140
  },
  bigScoreValue: { fontSize: 40, fontWeight: 900, lineHeight: 1.1 },
  statGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 16 },
  statBox: { background: "#f8fafc", borderRadius: 16, padding: 16 },
  statValue: { fontSize: 24, fontWeight: 900, marginTop: 4 },
  borderedBox: { border: "1px solid #e2e8f0", borderRadius: 18, padding: 16, background: "white", marginTop: 14 },
  barBack: { height: 8, background: "#e2e8f0", borderRadius: 999, overflow: "hidden", marginTop: 5 },
  barFill: { height: "100%", background: "#0f172a", borderRadius: 999 },
  row: { display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" },
  candidateRow: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: 10,
    border: "1px solid #e2e8f0",
    borderRadius: 14,
    background: "white",
    marginTop: 8
  },
  rank: {
    width: 28,
    height: 28,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f1f5f9",
    borderRadius: 999,
    fontWeight: 800,
    fontSize: 12,
    flexShrink: 0
  },
  note: {
    background: "#f8fafc",
    border: "1px solid #cbd5e1",
    borderRadius: 18,
    padding: 14,
    fontSize: 14,
    color: "#475569",
    lineHeight: 1.7,
    marginTop: 14
  },
  explanation: {
    background: "#fff7ed",
    border: "1px solid #fed7aa",
    borderRadius: 18,
    padding: 14,
    fontSize: 14,
    color: "#9a3412",
    lineHeight: 1.7,
    marginTop: 14
  },
  toggle: {
    width: "100%",
    border: "1px solid #cbd5e1",
    background: "#f8fafc",
    color: "#0f172a",
    borderRadius: 14,
    padding: "12px 14px",
    cursor: "pointer",
    fontWeight: 800,
    marginTop: 10
  },
  insightBadge: {
    display: "inline-block",
    background: "#ecfdf5",
    color: "#166534",
    borderRadius: 999,
    padding: "5px 10px",
    fontSize: 12,
    fontWeight: 800,
    marginTop: 10,
    marginRight: 6
  },
  conclusion: {
    background: "#eef2ff",
    border: "1px solid #c7d2fe",
    borderRadius: 18,
    padding: 14,
    fontSize: 14,
    color: "#3730a3",
    lineHeight: 1.7,
    marginTop: 14
  }
};

function pct(value) {
  return `${Math.round(Number(value || 0) * 1000) / 10}%`;
}

function fmtDateTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value || "");

  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}時${String(date.getMinutes()).padStart(2, "0")}分`;
}

function getStrongestOutcome(probabilities) {
  const items = [
    { key: "home", label: "ホーム勝利", value: probabilities.home_win || 0 },
    { key: "draw", label: "引き分け", value: probabilities.draw || 0 },
    { key: "away", label: "アウェイ勝利", value: probabilities.away_win || 0 }
  ];
  return items.sort((a, b) => b.value - a.value)[0];
}

function getScoreOutcome(score) {
  if (score.home > score.away) return { key: "home", label: "ホーム勝利" };
  if (score.home < score.away) return { key: "away", label: "アウェイ勝利" };
  return { key: "draw", label: "引き分け" };
}

function formatScore(score) {
  return `${score.home}-${score.away}`;
}

function getResultEvaluation(match) {
  const predictedOutcome = getScoreOutcome(match.predicted_score);
  const actualOutcome = getScoreOutcome(match.actual_score);
  const resultHit = predictedOutcome.key === actualOutcome.key;

  return resultHit
    ? { label: "勝敗的中", color: "#075985", background: "#e0f2fe" }
    : { label: "勝敗外れ", color: "#991b1b", background: "#fee2e2" };
}

function getScoreEvaluation(match) {
  const scoreHit = formatScore(match.predicted_score) === formatScore(match.actual_score);

  return scoreHit
    ? { key: "score_hit", label: "スコア的中", color: "#166534", background: "#dcfce7" }
    : { key: "score_miss", label: "スコア外れ", color: "#92400e", background: "#fef3c7" };
}

function getMatchInsightLabels(match) {
  const strongest = getStrongestOutcome(match.result_probabilities || {});

  if (strongest.key === "home") return ["ホーム優勢"];
  if (strongest.key === "away") return ["アウェイ優勢"];
  return [];
}

function formatAccuracy(hits, total) {
  if (!total) return "0.0%（0/0）";
  return `${Math.round((hits / total) * 1000) / 10}%（${hits}/${total}）`;
}

function getConclusionText(match) {
  const strongest = getStrongestOutcome(match.result_probabilities || {});
  const scoreOutcome = getScoreOutcome(match.predicted_score || { home: 0, away: 0 });
  const labels = getMatchInsightLabels(match);
  const trendText = labels.length ? ` 試合傾向は「${labels.join("・")}」です。` : "";
  const scoreText = formatScore(match.predicted_score);

  if (strongest.key !== scoreOutcome.key) {
    return `この試合の見立て：単一スコアでは ${scoreText} が最有力です。ただし勝敗確率では ${strongest.label} が最も高くなっています。${trendText}`;
  }

  return `この試合の見立て：予測スコアは ${scoreText}、勝敗確率トップは ${strongest.label} です。${trendText}`;
}

function getPastSummary(matches) {
  const total = matches.length;
  const resultHits = matches.filter((match) => getResultEvaluation(match).label === "勝敗的中").length;
  const scoreHits = matches.filter((match) => getScoreEvaluation(match).label === "スコア的中").length;
  return { total, resultHits, scoreHits };
}

function ProbabilityBar({ label, value }) {
  const numericValue = Number(value || 0);
  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ ...styles.row, fontSize: 13, color: "#475569" }}>
        <span>{label}</span>
        <strong style={{ color: "#0f172a" }}>{pct(numericValue)}</strong>
      </div>
      <div style={styles.barBack}>
        <div style={{ ...styles.barFill, width: `${Math.max(3, numericValue * 100)}%` }} />
      </div>
    </div>
  );
}

function MatchCard({ match, selected, onClick }) {
  const probabilities = match.result_probabilities || {};
  const strongest = getStrongestOutcome(probabilities);
  const scoreOutcome = getScoreOutcome(match.predicted_score);

  return (
    <button type="button" onClick={onClick} style={selected ? styles.matchCardSelected : styles.matchCard}>
      <div style={styles.smallText}>{match.date} {match.kickoff} / {match.venue}</div>
      <div style={{ fontWeight: 900, marginTop: 6, fontSize: 17 }}>{match.home_team} vs {match.away_team}</div>
      <span style={styles.outcomeBadge}>勝敗確率トップ: {strongest.label} {pct(strongest.value)}</span>
      <div>
        {getMatchInsightLabels(match).map((label) => (
          <span key={label} style={styles.insightBadge}>{label}</span>
        ))}
      </div>
      <div style={styles.scoreBox}>
        <div style={styles.teamCell}>{match.home_team}</div>
        <div style={styles.scoreText}>{match.predicted_score.home} - {match.predicted_score.away}</div>
        <div style={styles.teamCell}>{match.away_team}</div>
      </div>
      {strongest.key !== scoreOutcome.key && (
        <div style={{ marginTop: 8, fontSize: 12, color: "#64748b", lineHeight: 1.5 }}>
          ※ 単一スコアと、勝敗確率トップが異なる試合です。
        </div>
      )}
      <div style={{ marginTop: 12, fontSize: 13, fontWeight: 800, color: "#0f172a" }}>詳細を見る →</div>
    </button>
  );
}

function PastPredictionCard({ match }) {
  const resultEvaluation = getResultEvaluation(match);
  const scoreEvaluation = getScoreEvaluation(match);
  const predictedOutcome = getScoreOutcome(match.predicted_score);
  const actualOutcome = getScoreOutcome(match.actual_score);

  return (
    <section style={styles.matchCard}>
      <div style={styles.smallText}>{match.date} {match.kickoff} / {match.venue}</div>
      <div style={{ fontWeight: 900, marginTop: 6, fontSize: 17 }}>{match.home_team} vs {match.away_team}</div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
        <span style={{ ...styles.outcomeBadge, marginTop: 0, color: resultEvaluation.color, background: resultEvaluation.background }}>{resultEvaluation.label}</span>
        <span style={{ ...styles.outcomeBadge, marginTop: 0, color: scoreEvaluation.color, background: scoreEvaluation.background }}>{scoreEvaluation.label}</span>
      </div>

      <div style={styles.scoreBox}>
        <div style={styles.teamCell}>予測</div>
        <div style={styles.scoreText}>{formatScore(match.predicted_score)}</div>
        <div style={styles.teamCell}>{predictedOutcome.label}</div>
      </div>

      <div style={{ ...styles.scoreBox, background: "#fff" }}>
        <div style={styles.teamCell}>実際</div>
        <div style={styles.scoreText}>{formatScore(match.actual_score)}</div>
        <div style={styles.teamCell}>{actualOutcome.label}</div>
      </div>
    </section>
  );
}

function ScoreCandidateList({ candidates }) {
  return (
    <div>
      {(candidates || []).map((item, index) => (
        <div key={`${item.score}-${index}`} style={styles.candidateRow}>
          <div style={styles.rank}>{index + 1}</div>
          <strong>{item.score}</strong>
          <div style={{ marginLeft: "auto", width: 120 }}>
            <ProbabilityBar label="" value={item.probability} />
          </div>
        </div>
      ))}
    </div>
  );
}

function ScorerList({ title, players }) {
  return (
    <div style={styles.borderedBox}>
      <h3 style={{ margin: 0, fontSize: 16 }}>{title}</h3>
      {(players || []).map((player, index) => (
        <div key={`${player.player}-${index}`} style={styles.candidateRow}>
          <div style={styles.rank}>{index + 1}</div>
          <div>
            <strong>{player.player}</strong>
            <div style={styles.smallText}>{player.position}</div>
          </div>
          <strong style={{ marginLeft: "auto" }}>{pct(player.probability)}</strong>
        </div>
      ))}
    </div>
  );
}

export default function Week4StreamlitMvpPreview() {
  const [selectedId, setSelectedId] = useState(predictionData.matches[0].match_id);
  const [view, setView] = useState("list");
  const [mainTab, setMainTab] = useState("upcoming");
  const [mode, setMode] = useState("next");
  const [teamFilter, setTeamFilter] = useState("all");
  const [showScorers, setShowScorers] = useState(false);
  const [pastWeekFilter, setPastWeekFilter] = useState("all");
  const [pastTeamFilter, setPastTeamFilter] = useState("all");
  const [pastResultFilter, setPastResultFilter] = useState("all");

  const teams = ["all"];
  predictionData.matches.forEach((match) => {
    if (!teams.includes(match.home_team)) teams.push(match.home_team);
    if (!teams.includes(match.away_team)) teams.push(match.away_team);
  });

  const pastTeams = ["all"];
  pastPredictionData.matches.forEach((match) => {
    if (!pastTeams.includes(match.home_team)) pastTeams.push(match.home_team);
    if (!pastTeams.includes(match.away_team)) pastTeams.push(match.away_team);
  });

  const pastWeeks = ["all"];
  pastPredictionData.matches.forEach((match) => {
    const week = String(match.matchweek);
    if (!pastWeeks.includes(week)) pastWeeks.push(week);
  });

  const filteredMatches = predictionData.matches.filter((match) => {
    return teamFilter === "all" || match.home_team === teamFilter || match.away_team === teamFilter;
  });

  const selectedMatch = filteredMatches.find((match) => match.match_id === selectedId) || filteredMatches[0] || predictionData.matches[0];
  const selectedStrongestOutcome = getStrongestOutcome(selectedMatch.result_probabilities || {});
  const selectedScoreOutcome = getScoreOutcome(selectedMatch.predicted_score || { home: 0, away: 0 });

  const filteredPastMatches = pastPredictionData.matches.filter((match) => {
    const weekMatch = pastWeekFilter === "all" || String(match.matchweek) === pastWeekFilter;
    const teamMatch = pastTeamFilter === "all" || match.home_team === pastTeamFilter || match.away_team === pastTeamFilter;
    const resultEvaluation = getResultEvaluation(match);
    const scoreEvaluation = getScoreEvaluation(match);
    const resultMatch = pastResultFilter === "all" || resultEvaluation.label === pastResultFilter || scoreEvaluation.label === pastResultFilter;
    return weekMatch && teamMatch && resultMatch;
  });

  const pastSummary = getPastSummary(filteredPastMatches);

  function handleTeamFilterChange(event) {
    const nextTeam = event.target.value;
    setTeamFilter(nextTeam);
    const firstMatch = predictionData.matches.find((match) => {
      return nextTeam === "all" || match.home_team === nextTeam || match.away_team === nextTeam;
    });
    setSelectedId(firstMatch ? firstMatch.match_id : predictionData.matches[0].match_id);
    setView("list");
  }

  function selectMatch(matchId) {
    setSelectedId(matchId);
    setShowScorers(false);
    setView("detail");
  }

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <header style={styles.header}>
          <span style={styles.badge}>Week4 MVP Preview</span>
          <h1 style={styles.title}>J1 試合結果予測アプリ</h1>
          <p style={styles.subtitle}>モバイルで見やすいように、「一覧 → 詳細」の流れを強調したMVPモックです。</p>
          <div style={styles.metaGrid}>
            <div style={styles.metaBox}>
              <div style={styles.metaLabel}>Season</div>
              <div style={styles.metaValue}>{predictionData.season}</div>
            </div>
            <div style={styles.metaBox}>
              <div style={styles.metaLabel}>Matchweek</div>
              <div style={styles.metaValue}>第{predictionData.matchweek}節</div>
            </div>
            <div style={{ ...styles.metaBox, gridColumn: "1 / -1" }}>
              <div style={styles.metaLabel}>最終更新</div>
              <div style={styles.metaValue}>{fmtDateTime(predictionData.last_updated)}</div>
            </div>
          </div>
        </header>

        <section style={styles.panel}>
          <strong>表示切替</strong>
          <div style={styles.buttonRow}>
            <button
              type="button"
              style={mainTab === "upcoming" ? styles.buttonActive : styles.button}
              onClick={() => {
                setMainTab("upcoming");
                setView("list");
              }}
            >
              これからの試合
            </button>
            <button
              type="button"
              style={mainTab === "past" ? styles.buttonActive : styles.button}
              onClick={() => {
                setMainTab("past");
                setView("list");
              }}
            >
              過去の予測結果
            </button>
          </div>
        </section>

        {mainTab === "upcoming" && view === "list" && (
          <>
            <section style={styles.panel}>
              <strong>表示モード</strong>
              <div style={styles.buttonRow}>
                <button type="button" style={mode === "next" ? styles.buttonActive : styles.button} onClick={() => setMode("next")}>次節のみ</button>
                <button type="button" style={mode === "all" ? styles.buttonActive : styles.button} onClick={() => setMode("all")}>未消化すべて</button>
              </div>
              <p style={{ ...styles.smallText, marginBottom: 0 }}>MVPでは次節表示を主対象にします。</p>
            </section>

            <section style={styles.panel}>
              <strong>チームで絞り込み</strong>
              <select value={teamFilter} onChange={handleTeamFilterChange} style={styles.select}>
                {teams.map((team) => (
                  <option key={team} value={team}>{team === "all" ? "すべて" : team}</option>
                ))}
              </select>
            </section>

            {filteredMatches.map((match) => (
              <MatchCard
                key={match.match_id}
                match={match}
                selected={selectedMatch.match_id === match.match_id}
                onClick={() => selectMatch(match.match_id)}
              />
            ))}
          </>
        )}

        {mainTab === "past" && (
          <main>
            <section style={styles.panel}>
              <h2 style={{ margin: 0 }}>過去の予測結果</h2>
              <p style={styles.subtitle}>
                過去に出した予測と、実際の試合結果を並べて確認できます。モデルの当たり具合を直感的に見るための画面です。
              </p>

              <div style={styles.statGrid}>
                <div style={styles.statBox}>
                  <div style={styles.metaLabel}>勝敗的中率</div>
                  <div style={styles.statValue}>{formatAccuracy(pastSummary.resultHits, pastSummary.total)}</div>
                </div>
                <div style={styles.statBox}>
                  <div style={styles.metaLabel}>スコア的中率</div>
                  <div style={styles.statValue}>{formatAccuracy(pastSummary.scoreHits, pastSummary.total)}</div>
                </div>
                <div style={{ ...styles.statBox, gridColumn: "1 / -1" }}>
                  <div style={styles.metaLabel}>直近表示試合数</div>
                  <div style={styles.statValue}>{pastSummary.total}</div>
                </div>
              </div>

              <div style={styles.note}>
                <strong>判定の見方:</strong> 「勝敗」は勝ち・引き分け・負けの方向性で判定し、「スコア」は点数まで完全一致したかで判定します。
              </div>
            </section>

            <section style={styles.panel}>
              <strong>絞り込み</strong>
              <div style={{ display: "grid", gap: 10, marginTop: 10 }}>
                <select value={pastWeekFilter} onChange={(event) => setPastWeekFilter(event.target.value)} style={styles.select}>
                  {pastWeeks.map((week) => (
                    <option key={week} value={week}>{week === "all" ? "すべての節" : `第${week}節`}</option>
                  ))}
                </select>
                <select value={pastTeamFilter} onChange={(event) => setPastTeamFilter(event.target.value)} style={styles.select}>
                  {pastTeams.map((team) => (
                    <option key={team} value={team}>{team === "all" ? "すべてのチーム" : team}</option>
                  ))}
                </select>
                <select value={pastResultFilter} onChange={(event) => setPastResultFilter(event.target.value)} style={styles.select}>
                  <option value="all">すべての判定</option>
                  <option value="勝敗的中">勝敗的中</option>
                  <option value="勝敗外れ">勝敗外れ</option>
                  <option value="スコア的中">スコア的中</option>
                  <option value="スコア外れ">スコア外れ</option>
                </select>
              </div>
            </section>

            {filteredPastMatches.length === 0 && (
              <section style={styles.panel}>
                <p style={styles.subtitle}>条件に一致する過去予測はありません。</p>
              </section>
            )}

            {filteredPastMatches.map((match) => (
              <PastPredictionCard key={match.match_id} match={match} />
            ))}
          </main>
        )}

        {mainTab === "upcoming" && view === "detail" && (
          <main>
            <button type="button" style={styles.backButton} onClick={() => setView("list")}>← 試合一覧に戻る</button>

            <section style={styles.panel}>
              <div style={styles.detailHeader}>
                <div>
                  <div style={styles.smallText}>{selectedMatch.date} {selectedMatch.kickoff} / {selectedMatch.venue}</div>
                  <h2 style={{ fontSize: 26, margin: "8px 0 0", fontWeight: 900 }}>{selectedMatch.home_team} vs {selectedMatch.away_team}</h2>
                  <span style={styles.outcomeBadge}>勝敗確率トップ: {selectedStrongestOutcome.label} {pct(selectedStrongestOutcome.value)}</span>
                  <div>
                    {getMatchInsightLabels(selectedMatch).map((label) => (
                      <span key={label} style={styles.insightBadge}>{label}</span>
                    ))}
                  </div>
                </div>
                <div style={styles.bigScore}>
                  <div style={{ fontSize: 12, opacity: 0.75 }}>予測スコア</div>
                  <div style={styles.bigScoreValue}>{selectedMatch.predicted_score.home} - {selectedMatch.predicted_score.away}</div>
                </div>
              </div>

              <div style={styles.conclusion}>
                <strong>結論:</strong> {getConclusionText(selectedMatch)}
              </div>

              {selectedStrongestOutcome.key !== selectedScoreOutcome.key && (
                <div style={styles.explanation}>
                  <strong>なぜ「1-1」なのにアウェイ勝利が高いのか？</strong><br />
                  予測スコアは、個別のスコア候補の中で最も選ばれやすい1つを表示しています。一方、勝敗確率は「0-1」「1-2」「0-2」など、アウェイが勝つ複数のスコア候補を合算した確率です。<br />
                  そのため、単一スコアでは {selectedMatch.predicted_score.home}-{selectedMatch.predicted_score.away} が最上位でも、勝敗全体では {selectedStrongestOutcome.label} が最も高くなる場合があります。
                </div>
              )}

              <div style={styles.statGrid}>
                <div style={styles.statBox}>
                  <div style={styles.metaLabel}>ホーム期待得点</div>
                  <div style={styles.statValue}>{selectedMatch.expected_goals.home.toFixed(2)}</div>
                </div>
                <div style={styles.statBox}>
                  <div style={styles.metaLabel}>アウェイ期待得点</div>
                  <div style={styles.statValue}>{selectedMatch.expected_goals.away.toFixed(2)}</div>
                </div>
                <div style={{ ...styles.statBox, gridColumn: "1 / -1" }}>
                  <div style={styles.metaLabel}>最有力スコア候補</div>
                  <div style={styles.statValue}>{selectedMatch.score_candidates[0].score}</div>
                </div>
              </div>

              <div style={styles.borderedBox}>
                <h3 style={{ marginTop: 0 }}>勝敗確率</h3>
                <ProbabilityBar label={`${selectedMatch.home_team} 勝利`} value={selectedMatch.result_probabilities.home_win} />
                <ProbabilityBar label="引き分け" value={selectedMatch.result_probabilities.draw} />
                <ProbabilityBar label={`${selectedMatch.away_team} 勝利`} value={selectedMatch.result_probabilities.away_win} />
                <div style={styles.note}>
                  <strong>見方:</strong> 勝敗確率は「勝ち・引き分け・負け」という結果カテゴリごとの合算値です。予測スコアとは計算単位が異なるため、必ずしも同じ結論に見えるとは限りません。
                </div>
              </div>

              <div style={{ ...styles.borderedBox, background: "#f8fafc" }}>
                <h3 style={{ marginTop: 0 }}>スコア候補 Top 5</h3>
                <ScoreCandidateList candidates={selectedMatch.score_candidates} />
              </div>
            </section>

            <section style={styles.panel}>
              <h2 style={{ margin: 0 }}>得点者候補 Top 5</h2>
              <p style={styles.subtitle}>情報量が多いため、初期表示では折りたたみます。</p>
              <button type="button" style={styles.toggle} onClick={() => setShowScorers(!showScorers)}>
                {showScorers ? "得点者候補を閉じる" : "得点者候補を表示する"}
              </button>
              {showScorers && (
                <div>
                  <ScorerList title={selectedMatch.home_team} players={selectedMatch.scorer_candidates.home} />
                  <ScorerList title={selectedMatch.away_team} players={selectedMatch.scorer_candidates.away} />
                </div>
              )}
            </section>

            <div style={styles.note}>
              <strong>注意:</strong> この画面はUI確認用のMVPモックです。実装時は Streamlit が outputs/latest_predictions.json を読み込み、同じ情報構造を表示します。
            </div>
          </main>
        )}
      </div>
    </div>
  );
}
