import requests
from bs4 import BeautifulSoup
import csv
import time
import os


BASE = "https://worldcupranking.com"

START_URL = (
    BASE + "/world-cup-2026/squads/"
)


OUTPUT = "worldcup2026_players.csv"


POSITION_MAP = {
    "GK": "Goalkeeper",
    "DF": "Defender",
    "MF": "Midfielder",
    "FW": "Attacker"
}


HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}



def log(msg):
    print(f"[DEBUG] {msg}")



def clean_nation(slug):

    return (
        slug
        .replace("-", " ")
        .title()
    )



def request_html(url):

    for attempt in range(3):

        try:

            r = requests.get(
                url,
                headers=HEADERS,
                timeout=20
            )

            if r.status_code == 200:

                return r.text


            log(
                f"HTTP {r.status_code}: {url}"
            )


        except Exception as e:

            log(
                f"Request error {attempt+1}: {e}"
            )


        time.sleep(2)


    return None



def save_debug(name, html):

    filename = (
        "debug_"
        + name.lower()
        .replace(" ", "_")
        + ".html"
    )


    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)


    log(
        f"Saved {filename}"
    )



# ==========================
# Load teams
# ==========================


log(
    "Loading team list"
)


html = request_html(
    START_URL
)


if not html:

    raise Exception(
        "Cannot load start page"
    )


soup = BeautifulSoup(
    html,
    "html.parser"
)



team_links = []


for a in soup.find_all(
    "a",
    href=True
):

    href = a["href"]


    if (
        "/world-cup-2026/squads/"
        in href
        and href != "/world-cup-2026/squads/"
    ):

        if href not in team_links:

            team_links.append(
                href
            )


log(
    f"Found {len(team_links)} teams"
)



players = []



# ==========================
# Parse teams
# ==========================


for idx, team_url in enumerate(
    team_links,
    start=1
):


    slug = (
        team_url
        .rstrip("/")
        .split("/")[-1]
    )


    nation = clean_nation(
        slug
    )


    log(
        f"[{idx}/{len(team_links)}] {nation}"
    )


    html = request_html(
        BASE + team_url
    )


    if not html:

        log(
            f"{nation}: no html"
        )

        continue



    soup = BeautifulSoup(
        html,
        "html.parser"
    )



    tables = soup.find_all(
        "table"
    )


    log(
        f"{nation}: tables={len(tables)}"
    )



    if len(tables) == 0:

        save_debug(
            nation,
            html
        )

        continue



    team_count = 0



    # thử tất cả table
    for table in tables:


        rows = table.find_all(
            "tr"
        )


        for row in rows:


            cols = [
                c.get_text(
                    " ",
                    strip=True
                )
                for c in row.find_all(
                    [
                        "td",
                        "th"
                    ]
                )
            ]


            if not cols:

                continue



            text = (
                " ".join(cols)
                .lower()
            )



            # remove header

            if (
                "name on shirt"
                in text
                or (
                    "pos"
                    in text
                    and "club"
                    in text
                )
                or "#" == cols[0]
            ):

                log(
                    f"{nation}: skip header {cols}"
                )

                continue



            # find position

            pos = None


            for c in cols:

                if c in POSITION_MAP:

                    pos = c

                    break



            if not pos:

                continue



            pos_index = cols.index(
                pos
            )



            # expected:
            #
            # NAME | POS | NATION | # | CLUB
            #

            try:


                name = cols[
                    pos_index - 1
                ]



                number = None

                club = None



                for c in cols:

                    if c.isdigit():

                        number = c



                # club normally last

                club = cols[-1]



                if (
                    not name
                    or not club
                    or club.lower()
                    == "club"
                ):

                    continue



                players.append(
                    {
                        "name":
                            name,

                        "position":
                            POSITION_MAP[pos],

                        "nation":
                            nation,

                        "number":
                            number,

                        "club":
                            club
                    }
                )


                team_count += 1



            except Exception as e:

                log(
                    f"{nation}: parse error {cols} {e}"
                )



    log(
        f"{nation}: added {team_count}"
    )


    time.sleep(
        0.5
    )



# ==========================
# Export CSV
# ==========================


with open(
    OUTPUT,
    "w",
    newline="",
    encoding="utf-8"
) as f:


    writer = csv.DictWriter(
        f,
        fieldnames=[
            "name",
            "position",
            "nation",
            "number",
            "club"
        ]
    )


    writer.writeheader()

    writer.writerows(
        players
    )



log(
    "======================"
)

log(
    f"TOTAL PLAYERS: {len(players)}"
)

log(
    f"Saved: {OUTPUT}"
)