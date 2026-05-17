from src.data.scrape_matches import _parse_data_site_tables


def test_parse_data_site_table_includes_regular_and_playoff_matches() -> None:
    html = """
    <table>
      <thead>
        <tr>
          <th>シーズン</th><th>大会</th><th>節</th><th>試合日</th><th>K/O時刻</th>
          <th>ホーム</th><th>スコア</th><th>アウェイ</th><th>スタジアム</th><th>入場者数</th><th>インターネット中継・TV放送</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>2026特別</td><td>明治安田Ｊ１百年構想 EASTグループ</td><td>第１節第１日</td><td>26/02/06(金)</td><td>19:03</td>
          <td>横浜FM</td><td>2-3</td><td>町田</td><td>日産ス</td><td>30529</td><td>ＤＡＺＮ</td>
        </tr>
        <tr>
          <td>2026特別</td><td>明治安田Ｊ１百年構想 プレーオフラウンド</td><td>第１戦第１日</td><td>26/05/30(土)</td><td>14:00</td>
          <td>名古屋</td><td></td><td>未定</td><td>パロ瑞穂</td><td></td><td>ＤＡＺＮ</td>
        </tr>
      </tbody>
    </table>
    """

    df = _parse_data_site_tables(html, "https://example.test")

    assert len(df) == 2
    regular = df.iloc[0]
    assert regular["section"] == 1
    assert regular["match_date"] == "2026-02-06"
    assert regular["home_team"] == "y-fm"
    assert regular["away_team"] == "mcd"
    assert regular["home_score"] == 2
    assert regular["away_score"] == 3
    assert regular["status"] == "finished"

    playoff = df.iloc[1]
    assert playoff["section"] == 101
    assert playoff["section_label"] == "第１戦第１日"
    assert playoff["home_team"] == "nago"
    assert playoff["away_team"] == "tbd"
    assert playoff["status"] == "postponed_or_tbd"
