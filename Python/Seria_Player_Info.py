from curl_cffi import requests
import pandas as pd
import time

session = requests.Session()

# Impersonate Chrome mới nhất
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.sofascore.com",
    "Referer": "https://www.sofascore.com/",
})

TOURNAMENT_ID = 23  # Serie A

POSITION_MAP = {
    "G": "Goalkeeper",
    "D": "Defender",
    "M": "Midfielder",
    "F": "Attacker"
}

# ====================================
# GET SEASONS
# ====================================
season_url = f"https://api.sofascore.com/api/v1/unique-tournament/{TOURNAMENT_ID}/seasons"

resp = session.get(season_url, impersonate="chrome")
season_data = resp.json()

if "error" in season_data:
    print("Error:", season_data.get("error"))
    print(resp.text)
    exit(1)

# Lấy season mới nhất
season_id = season_data["seasons"][0]["id"]
print("Season ID:", season_id)

# ====================================
# GET TEAMS
# ====================================
standings_url = f"https://api.sofascore.com/api/v1/unique-tournament/{TOURNAMENT_ID}/season/{season_id}/standings/total"
standings_data = session.get(standings_url, impersonate="chrome").json()

rows = standings_data["standings"][0]["rows"]

teams = [{"team_id": row["team"]["id"], "club": row["team"]["name"]} for row in rows]

# ====================================
# GET PLAYERS
# ====================================
all_players = []

for team in teams:
    team_id = team["team_id"]
    club = team["club"]
    print(f"Getting players from {club}")

    url = f"https://api.sofascore.com/api/v1/team/{team_id}/players"

    try:
        data = session.get(url, impersonate="chrome").json()
        players = data.get("players", [])

        for item in players:
            player = item.get("player", {})
            position_raw = player.get("position")

            all_players.append({
                "player_name": f"{player.get('name')} ({player.get('slug')})",
                "club": club,
                "position": POSITION_MAP.get(position_raw, position_raw),
                "country": player.get("country", {}).get("name"),
                "shirt_number": player.get("shirtNumber")
            })

        time.sleep(1.2)  # Nghỉ lâu hơn một chút

    except Exception as e:
        print("ERROR:", club, e)

# ====================================
# EXPORT
# ====================================
df = pd.DataFrame(all_players).drop_duplicates()
df.to_csv("serie_a_players.csv", index=False, encoding="utf-8-sig")

print(df.head())
print(f"Saved {len(df)} players")