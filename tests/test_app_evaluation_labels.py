from app.utils.evaluation import get_match_insight_label


def test_match_insight_label_for_home_away_and_draw() -> None:
    assert get_match_insight_label({"home_win": 0.5, "draw": 0.3, "away_win": 0.2}) == "ホーム優勢"
    assert get_match_insight_label({"home_win": 0.2, "draw": 0.3, "away_win": 0.5}) == "アウェイ優勢"
    assert get_match_insight_label({"home_win": 0.2, "draw": 0.5, "away_win": 0.3}) == "引き分け濃厚"
