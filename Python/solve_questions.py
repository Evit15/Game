import re
import json
import time
import requests
import pandas as pd
from rapidfuzz import process

INPUT_CSV = "questions.csv"
OUTPUT_CSV = "questions_with_answers.csv"
CACHE_FILE = "player_cache.json"

POSITIONS = [
    "Goalkeeper",
    "Defence",
    "Midfield",
    "Attack"
]

# =========================
# CACHE
# =========================

try:
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        CACHE = json.load(f)
except:
    CACHE = {}

# =========================
# OCR FIX
# =========================

def normalize_position(text):

    if pd.isna(text):
        return ""

    text = str(text)

    text = text.replace("A ", "")
    text = text.replace("B ", "")
    text = text.strip()

    result = process.extractOne(
        text,
        POSITIONS
    )

    if result and result[1] >= 60:
        return result[0]

    return text

# =========================
# PLAYER NAME
# =========================

def extract_player(question):

    m = re.search(
        r"What position does .*?'s (.*?) play",
        question,
        re.IGNORECASE
    )

    if m:
        return m.group(1).strip()

    return None

# =========================
# MAP POSITION
# =========================

def map_position(pos):

    if not pos:
        return None

    pos = pos.lower()

    if "goalkeeper" in pos:
        return "Goalkeeper"

    if any(x in pos for x in [
        "defender",
        "centre-back",
        "center-back",
        "left-back",
        "right-back",
        "full-back",
        "wing-back"
    ]):
        return "Defence"

    if "midfielder" in pos:
        return "Midfield"

    if any(x in pos for x in [
        "forward",
        "striker",
        "winger"
    ]):
        return "Attack"

    return None

# =========================
# THESPORTSDB
# =========================

def lookup_player(player):

    if player in CACHE:
        return CACHE[player]

    try:

        url = (
            "https://www.thesportsdb.com/api/v1/json/3/"
            f"searchplayers.php?p={player}"
        )

        r = requests.get(
            url,
            timeout=20
        )

        data = r.json()

        players = data.get("player")

        if not players:
            CACHE[player] = None
            return None

        position = players[0].get("strPosition")

        result = map_position(position)

        CACHE[player] = result

        with open(
            CACHE_FILE,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                CACHE,
                f,
                ensure_ascii=False,
                indent=2
            )

        return result

    except Exception as e:

        print(f"ERROR {player}: {e}")

        CACHE[player] = None

        return None

# =========================
# MAIN
# =========================

df = pd.read_csv(INPUT_CSV)

answers = []

for _, row in df.iterrows():

    question = str(row["Question"])

    if "what position" not in question.lower():

        answers.append("SKIP")
        continue

    player = extract_player(question)

    if not player:

        answers.append("UNKNOWN")
        continue

    a = normalize_position(row["A"])
    b = normalize_position(row["B"])

    print()
    print(f"Searching: {player}")

    real_position = lookup_player(player)

    print(f"Real Position: {real_position}")
    print(f"A={a}")
    print(f"B={b}")

    answer = "UNKNOWN"

    if real_position:

        if a.lower() == real_position.lower():
            answer = "A"

        elif b.lower() == real_position.lower():
            answer = "B"

    answers.append(answer)

    time.sleep(0.2)

df["CorrectAnswer"] = answers

df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print()
print(f"Saved -> {OUTPUT_CSV}")