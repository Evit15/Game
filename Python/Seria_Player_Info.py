import requests
import pandas as pd
import time
from lxml import html

headers = {
    "User-Agent": "Mozilla/5.0"
}

base_url = "https://bongda24h.vn/cau-thu-serie-a-g3.html?page={}"

players = []
page = 1

while True:
    url = base_url.format(page)

    print(f"Scraping page {page}: {url}")

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("No more pages.")
        break
    # Force UTF-8
    response.encoding = "utf-8"
    tree = html.fromstring(response.text)

    # XPath table user cung cấp
    rows = tree.xpath(
        "/html/body/main/div[2]/section/div/section[1]/div/div[1]/div/div/table/tbody/tr"
    )

    if not rows:
        print("No rows found.")
        break

    page_count = 0

    for row in rows:
        cols = row.xpath("./td")

        # Skip image column
        if len(cols) >= 5:
            try:
                player_name = cols[0].text_content().strip()
                position = cols[1].text_content().strip()
                nationality = cols[2].text_content().strip()
                club = cols[3].text_content().strip()
                squad_number = cols[4].text_content().strip()

                players.append({
                    "player_name": player_name,
                    "club": club,
                    "position": position,
                    "nationality": nationality,
                    "squad_number": squad_number
                })

                page_count += 1

            except Exception as e:
                print("Error:", e)

    print(f" -> Collected {page_count} players")

    if page_count == 0:
        break

    page += 1

    time.sleep(1)

# Create dataframe
df = pd.DataFrame(players)

# Remove duplicates
df = df.drop_duplicates()

# Export CSV
csv_file = "serie_a_players.csv"

df.to_csv(csv_file, index=False, encoding="utf-8-sig")

print(f"\nSaved {len(df)} players to {csv_file}")
print(df.head())