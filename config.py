"""
Configuration constants for VCT Display Demo
"""
import os

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "font", "FoundryGridnikW03-ExtraBold.ttf")
CN_FONT_PATH = os.path.join(ASSETS_DIR, "font", "HarmonyOS_Sans_SC_Bold.ttf")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# Table headers
HEADERS = ["日期", "时间", "赛事", "对阵信息", "备注"]
HEADERS_EXTENDED = ["日期", "时间", "赛事", "Team A", "vs", "Team B", "备注"]

# Teams by region - names match asset filenames (without .png)
TEAMS_BY_REGION = {
    "pacific": ["dfm", "drx", "fs", "ge", "geng", "nongshim", "prx", "rrq", "t1", "ts", "vl", "zeta"], 
    "emea": ["bbl", "fnc", "fut", "gx", "kc", "m8", "navi", "pcf", "th", "tl", "ulf", "vit"], 
    "amer": ["100t", "cloud9", "eg", "envy", "furia", "g2", "kru", "lev", "loud", "mibr", "nrg", "sen"],
    "cn": ["ag", "blg", "drg", "edg", "fpx", "jdg", "nova", "te", "tec", "tyl", "wol", "xlg"],
    "others": ["5fw", "aq", "ra", "待定", "手动输入"]
}

# Tournaments - names match vct folder filenames (without .png)
TOURNAMENTS = ["pacific", "emea", "americas", "cn", "masters", "champions", "ascensions", "others", "national tournament"]

# Region colors mapping
REGION_COLORS = {
    "pacific": "#00B5E2",
    "emea": "#004667",
    "americas": "#DE4500",
    "amer": "#DE4500",
    "cn": "#E04F4F",
    "masters": "#9B59B6",
    "champions": "#C6B275",
    "ascensions": "#0DB397",
    "others": "#6b7280",
    "national tournament": "#D6B200"
}

# Full team name to abbreviation mapping (for VLR.gg API)
TEAM_NAME_MAPPING = {
    # Pacific
    "detonation focusme": "dfm",
    "dfm": "dfm",
    "drx": "drx",
    "funplus phoenix": "fpx",
    "gen.g": "geng",
    "gen.g esports": "geng",
    "geng": "geng",
    "global esports": "ge",
    "nongshim redforce": "nongshim",
    "paper rex": "prx",
    "prx": "prx",
    "rex regum qeon": "rrq",
    "rrq": "rrq",
    "t1": "t1",
    "talon esports": "ts",
    "team secret": "ts",
    "ts": "ts",
    "zeta division": "zeta",
    "zeta": "zeta",
    "team vitality": "vit",
    "vitality": "vit",
    "vit": "vit",
    "bleed esports": "bleed",
    "full sense": "fs",
    "fs": "fs",
    
    # EMEA
    "bbls esports": "bbl",
    "bbl esports": "bbl",
    "bbl": "bbl",
    "fnatic": "fnc",
    "fnc": "fnc",
    "fut esports": "fut",
    "fut": "fut",
    "giants gaming": "gx",
    "giants": "gx",
    "gx": "gx",
    "karmine corp": "kc",
    "kc": "kc",
    "team heretics": "th",
    "heretics": "th",
    "th": "th",
    "team liquid": "tl",
    "liquid": "tl",
    "tl": "tl",
    "natus vincere": "navi",
    "navi": "navi",
    "movistar koi": "m8",
    "m8": "m8",
    "apeks": "apeks",
    "team vitality": "vit",
    "vitality": "vit",
    "vit": "vit",
    
    # Americas
    "100 thieves": "100t",
    "100t": "100t",
    "cloud9": "cloud9",
    "c9": "cloud9",
    "evil geniuses": "eg",
    "eg": "eg",
    "furia": "furia",
    "furia esports": "furia",
    "g2 esports": "g2",
    "g2": "g2",
    "kru esports": "kru",
    "krü esports": "kru",
    "kru": "kru",
    "krü": "kru",
    "leviatán": "lev",
    "leviatan": "lev",
    "lev": "lev",
    "loud": "loud",
    "mibr": "mibr",
    "nrg esports": "nrg",
    "nrg": "nrg",
    "sentinels": "sen",
    "sen": "sen",
    "envy": "envy",
    "optic gaming": "envy",
    "optic": "envy",
    "2game esports": "2g",
    
    # China
    "all gamers": "ag",
    "ag": "ag",
    "bilibili gaming": "blg",
    "blg": "blg",
    "dragon ranger gaming": "drg",
    "drg": "drg",
    "edward gaming": "edg",
    "edg": "edg",
    "funplus phoenix": "fpx",
    "fpx": "fpx",
    "jd gaming": "jdg",
    "jdg": "jdg",
    "nova esports": "nova",
    "nova": "nova",
    "trace esports": "te",
    "te": "te",
    "titan esports club": "tec",
    "tec": "tec",
    "tyloo": "tyl",
    "tyl": "tyl",
    "wolves esports": "wol",
    "wol": "wol",
    "xiao long gaming": "xlg",
    "xlg": "xlg",
    
    # Others
    "5fw": "5fw",
    "rare atoms": "ra",
    "aq": "aq",
    "tbd": "待定",
    "待定": "待定",
}
