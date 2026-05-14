import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

SUB_KEY = "c13c3a8e2f6b46da9c5c425cf61fab3e"

headers_web = {"User-Agent": "Mozilla/5.0"}
headers_api = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

# ====================== LẤY DANH SÁCH CLB ======================
def get_team_slugs_from_web():
    print("Đang lấy danh sách CLB từ LaLiga.com...")
    url = "https://www.laliga.com/en-GB/laliga-easports/clubs"
    response = requests.get(url, headers=headers_web)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    slugs = []
    for a in soup.find_all('a', href=re.compile(r'/clubs/[^/]+')):
        href = a['href']
        if '/clubs/' in href:
            slug = href.split('/clubs/')[1].split('/')[0]
            if slug and slug not in slugs and len(slug) > 3:
                slugs.append(slug)
    print(f"✅ Tìm thấy {len(slugs)} đội.")
    return slugs


# ====================== LẤY SQUAD ======================
def get_squad(slug):
    url = f"https://apim.laliga.com/public-service/api/v1/teams/{slug}/squad-manager"
    params = {
        "limit": 50,
        "offset": 0,
        "seasonYear": 2025,
        "contentLanguage": "en",
        "subscription-key": SUB_KEY
    }
    
    try:
        resp = requests.get(url, headers=headers_api, params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("squads", [])
        else:
            print(f"   ❌ {slug} - Status: {resp.status_code}")
            return []
    except Exception as e:
        print(f"   ❌ Lỗi {slug}: {e}")
        return []


# ====================== CHẠY CHÍNH ======================
team_slugs = get_team_slugs_from_web()
all_players = []

print("\nĐang thu thập cầu thủ từ tất cả đội...")

for slug in team_slugs:
    print(f"→ Đang lấy: {slug}")
    squad = get_squad(slug)
    
    for p in squad:
        person = p.get("person", {})
        position = p.get("position", {})
        team_info = p.get("team", {})
        
        jersey = p.get("shirt_number")
        # Đảm bảo là integer (an toàn)
        if jersey is not None:
            jersey = int(jersey) if str(jersey).replace('.','').isdigit() else None
        
        all_players.append({
            "Player_Name": person.get("name"),
            "Jersey_Number": jersey,
            "Team": team_info.get("name") or slug.replace("-", " ").title(),
            "Position": position.get("name"),
            "Nationality": person.get("country", {}).get("id")
        })
    
    time.sleep(1.3)  # Nghỉ tránh rate limit

# ====================== XUẤT FILE CSV ======================
df = pd.DataFrame(all_players)
df = df[['Team', 'Jersey_Number', 'Player_Name', 'Position', 'Nationality']]
df = df.sort_values(by=['Team', 'Jersey_Number']).reset_index(drop=True)

# Đảm bảo Jersey_Number là kiểu số nguyên
df['Jersey_Number'] = pd.to_numeric(df['Jersey_Number'], errors='coerce').astype('Int64')

df.to_csv("laliga_2025_2026_full_squad.csv", index=False, encoding='utf-8-sig')

print(f"\n🎉 HOÀN THÀNH!")
print(f"Tổng số cầu thủ: {len(df)}")
print(f"File đã lưu: laliga_2025_2026_full_squad.csv")

print("\nPreview:")
print(df.head(20))