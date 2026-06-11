import requests
from bs4 import BeautifulSoup
import csv
import time


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
    "Mozilla/5.0"
}



def log(msg):
    print(f"[DEBUG] {msg}")



def clean_nation(slug):

    return (
        slug
        .replace("-", " ")
        .title()
    )



def get_html(url):

    for i in range(3):

        try:

            r = requests.get(
                url,
                headers=HEADERS,
                timeout=20
            )

            if r.status_code == 200:

                return r.text


            log(
                f"HTTP {r.status_code} {url}"
            )


        except Exception as e:

            log(
                f"Request error {e}"
            )


        time.sleep(2)


    return None



def save_debug(nation, html):

    filename = (
        "debug_"
        + nation.lower()
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



# =====================
# GET TEAM LIST
# =====================


log("Loading teams")


html = get_html(
    START_URL
)


if not html:

    raise Exception(
        "Cannot load WorldCupRanking"
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



# =====================
# PARSE EACH TEAM
# =====================


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


    html = get_html(
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



    team_count = 0



    for table in tables:


        rows = table.find_all(
            "tr"
        )


        if len(rows) < 2:
            continue



        header = None


        # ----------------
        # FIND HEADER
        # ----------------

        for row in rows[:5]:

            cols = [
                c.get_text(
                    " ",
                    strip=True
                )
                for c in row.find_all(
                    ["th","td"]
                )
            ]


            text = (
                " ".join(cols)
                .lower()
            )


            if (
                "pos" in text
                and (
                    "club" in text
                    or "#" in text
                )
            ):

                header = [
                    x.lower()
                    for x in cols
                ]

                break



        if not header:

            continue



        log(
            f"{nation}: header={header}"
        )



        name_idx = None
        pos_idx = None
        number_idx = None
        club_idx = None



        for i, col in enumerate(header):


            if (
                "name" in col
                or "shirt" in col
            ):

                name_idx = i


            elif col == "pos":

                pos_idx = i


            elif col == "#":

                number_idx = i


            elif "club" in col:

                club_idx = i



        log(
            f"{nation}: "
            f"name={name_idx}, "
            f"pos={pos_idx}, "
            f"num={number_idx}, "
            f"club={club_idx}"
        )



        if (
            name_idx is None
            or pos_idx is None
        ):

            continue



        # ----------------
        # PARSE ROWS
        # ----------------


        for row in rows:


            cols = [
                c.get_text(
                    " ",
                    strip=True
                )
                for c in row.find_all(
                    ["td","th"]
                )
            ]



            if len(cols) <= pos_idx:

                continue



            # skip header

            if [
                x.lower()
                for x in cols
            ] == header:

                continue



            pos = cols[pos_idx]


            if pos not in POSITION_MAP:

                continue



            name = cols[name_idx]



            if (
                not name
                or name.isdigit()
            ):

                continue



            number = ""

            club = ""



            if (
                number_idx is not None
                and number_idx < len(cols)
            ):

                number = cols[number_idx]



            if (
                club_idx is not None
                and club_idx < len(cols)
            ):

                club = cols[club_idx]



            players.append(
                {
                    "name": name,

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



    log(
        f"{nation}: added {team_count}"
    )


    time.sleep(
        0.5
    )



# =====================
# EXPORT CSV
# =====================


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



log("====================")

log(
    f"TOTAL PLAYERS: {len(players)}"
)

log(
    f"Saved: {OUTPUT}"
)