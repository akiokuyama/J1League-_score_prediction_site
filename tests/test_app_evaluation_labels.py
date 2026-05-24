from app.utils.evaluation import build_score_probability_explanation, get_confidence_label, get_match_insight_label


def test_match_insight_label_for_home_away_and_draw() -> None:
    assert get_match_insight_label({"home_win": 0.5, "draw": 0.3, "away_win": 0.2}) == "ホーム優勢"
    assert get_match_insight_label({"home_win": 0.2, "draw": 0.3, "away_win": 0.5}) == "アウェイ優勢"
    assert get_match_insight_label({"home_win": 0.2, "draw": 0.5, "away_win": 0.3}) == "引き分け濃厚"


def test_confidence_label_thresholds() -> None:
    assert get_confidence_label(0.60)["label"] == "確度高め"
    assert get_confidence_label(0.45)["label"] == "やや優勢"
    assert get_confidence_label(0.44)["label"] == "拮抗"


def test_score_probability_explanation() -> None:
    same = build_score_probability_explanation({"home": 2, "away": 1}, {"home_win": 0.6, "draw": 0.2, "away_win": 0.2})
    assert same == "予測スコアと勝敗確率トップは同じ方向を示しています。"

    mismatch = build_score_probability_explanation({"home": 1, "away": 1}, {"home_win": 0.3, "draw": 0.2, "away_win": 0.5})
    assert mismatch == "スコア候補では引き分けが最有力ですが、勝敗カテゴリ全体ではアウェイ勝利が最も高くなっています。"
