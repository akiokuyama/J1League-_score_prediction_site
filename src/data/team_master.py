"""Team name mappings used by data ingestion and prediction."""

from __future__ import annotations


TEAM_CODE_TO_NAME = {
    "kasm": "鹿島アントラーズ",
    "uraw": "浦和レッズ",
    "kasw": "柏レイソル",
    "tk-v": "東京ヴェルディ",
    "ka-f": "川崎フロンターレ",
    "shim": "清水エスパルス",
    "kyot": "京都サンガF.C.",
    "c-os": "セレッソ大阪",
    "okay": "ファジアーノ岡山",
    "fuku": "アビスパ福岡",
    "mito": "水戸ホーリーホック",
    "chib": "ジェフユナイテッド千葉",
    "FCtk": "FC東京",
    "fctk": "FC東京",
    "mcd": "FC町田ゼルビア",
    "y-fm": "横浜Ｆ・マリノス",
    "nago": "名古屋グランパス",
    "g-os": "ガンバ大阪",
    "kobe": "ヴィッセル神戸",
    "hiro": "サンフレッチェ広島",
    "ngsk": "Ｖ・ファーレン長崎",
    "y-fc": "横浜FC",
    "shon": "湘南ベルマーレ",
    "niig": "アルビレックス新潟",
    "iwat": "ジュビロ磐田",
    "sapp": "北海道コンサドーレ札幌",
    "tosu": "サガン鳥栖",
    "oita": "大分トリニータ",
    "toku": "徳島ヴォルティス",
    "send": "ベガルタ仙台",
}

TEAM_NAME_TO_CODE = {name: code for code, name in TEAM_CODE_TO_NAME.items()}
TEAM_NAME_TO_CODE.update(
    {
        "鹿島": "kasm",
        "浦和": "uraw",
        "柏": "kasw",
        "東京Ｖ": "tk-v",
        "川崎Ｆ": "ka-f",
        "清水": "shim",
        "京都": "kyot",
        "Ｃ大阪": "c-os",
        "福岡": "fuku",
        "水戸": "mito",
        "千葉": "chib",
        "町田": "mcd",
        "Ｇ大阪": "g-os",
        "神戸": "kobe",
        "名古屋": "nago",
        "広島": "hiro",
        "長崎": "ngsk",
        "湘南": "shon",
        "新潟": "niig",
        "横浜FC": "y-fc",
        "横浜 F・マリノス": "y-fm",
        "横浜FM": "y-fm",
        "横浜FM": "y-fm",
        "横浜Ｆ・マリノス": "y-fm",
        "FC東京": "FCtk",
        "ＦＣ東京": "FCtk",
        "FC町田ゼルビア": "mcd",
        "ＦＣ町田ゼルビア": "mcd",
        "岡山": "okay",
        "横浜ＦＣ": "y-fc",
    }
)

FOOTBALL_LAB_CODES = {
    "kasm": "kasm",
    "mito": "mito",
    "uraw": "uraw",
    "chib": "chib",
    "kasw": "kasw",
    "FCtk": "fctk",
    "tk-v": "tk-v",
    "mcd": "mcd",
    "ka-f": "ka-f",
    "y-fm": "y-fm",
    "shim": "shim",
    "nago": "nago",
    "kyot": "kyot",
    "g-os": "g-os",
    "c-os": "c-os",
    "okay": "okay",
    "kobe": "kobe",
    "hiro": "hiro",
    "fuku": "fuku",
    "ngsk": "ngsk",
}


def normalize_team_name(name: str) -> str:
    return str(name).strip().replace("　", " ")


def to_dataset_code(name_or_code: str) -> str:
    value = normalize_team_name(name_or_code)
    return TEAM_NAME_TO_CODE.get(value, value)


def to_display_name(name_or_code: str) -> str:
    value = normalize_team_name(name_or_code)
    return TEAM_CODE_TO_NAME.get(value, value)
