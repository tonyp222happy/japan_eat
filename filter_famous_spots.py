#!/usr/bin/env python3
"""Filter scenic spots to only the most famous/important ones per city area."""
import json
import re
from collections import defaultdict

with open("/home/ubuntu/hyakumeiten-nearby-finder/frontend/data/scenic_spots_filtered.json") as f:
    spots = json.load(f)

# ─── Famous spots by name (manually curated major Japanese attractions) ───
FAMOUS_NAMES = {
    # Castles
    "姫路城", "Himeji", "松本城", "Matsumoto", "名古屋城", "Nagoya", "大阪城", "Osaka",
    "熊本城", "Kumamoto", "金沢城", "Kanazawa", "松江城", "Matsue", "犬山城", "Inuyama",
    "彦根城", "Hikone", "首里城", "Shuri", "広島城", "Hiroshima", "福岡城", "Fukuoka",
    "仙台城", "Sendai", "若松城", "Wakamatsu", "岡山城", "Okayama", "高知城", "Kochi",
    "丸亀城", "Marugame", "宇和島城", "Uwajima", "伊賀上野城", "Iga Ueno",
    # Temples
    "清水寺", "Kiyomizu", "金閣寺", "Kinkaku", "銀閣寺", "Ginkaku", "東大寺", "Todai",
    "浅草寺", "Senso", "浅草", "浅草寺", "法隆寺", "Horyu", "東寺", "Toji",
    "知恩院", "Chion", "南禅寺", "Nanzen", "龍安寺", "Ryoan", "天龍寺", "Tenryu",
    "建仁寺", "Kennin", "高台寺", "Kodai", "仁和寺", "Ninna", "西本願寺", "Nishi Hongan",
    "東本願寺", "Higashi Hongan", "中尊寺", "Chuson", "毛越寺", "Motsu",
    "延暦寺", "Enryaku", "比叡山", "Hiei", "興福寺", "Kofuku", "薬師寺", "Yakushi",
    "唐招提寺", "Toshodai", "長谷寺", "Hasedera", "三室戸寺", "Mimuroto",
    "永平寺", "Eihei", "総持寺", "Soji", "建長寺", "Kencho", "円覚寺", "Engaku",
    "成田山", "Narita", "新勝寺", "Shinsho", "川崎大師", "Kawasaki Daishi",
    "四天王寺", "Shitenno", "住吉大社", "Sumiyoshi", "出雲大社", "Izumo",
    # Shrines
    "伏見稲荷", "Fushimi Inari", "明治神宮", "Meiji", "嚴島神社", "Itsukushima",
    "厳島神社", "春日大社", "Kasuga", "諏訪大社", "Suwa", "出雲", "Izumo Taisha",
    "熱田神宮", "Atsuta", "伊勢神宮", "Ise", "鶴岡八幡宮", "Tsurugaoka",
    "八幡宮", "Hachimangu", "平安神宮", "Heian", "日光東照宮", "Nikko Toshogu",
    "東照宮", "Toshogu", "二荒山神社", "Futarasan", "輪王寺", "Rinno",
    "上野東照宮", "Ueno Toshogu", "久能山東照宮", "Kunozan",
    "熊野本宮大社", "Kumano Hongu", "熊野", "Kumano", "熊野速玉大社",
    "熊野那智大社", "Kumano Nachi", "那智", "Nachi",
    "吉備津神社", "Kibitsu", "津島神社", "Tsushima",
    "鹿島神宮", "Kashima", "香取神宮", "Katori",
    "気比神宮", "Kehi", "白鬚神社", "Shirahige",
    "多賀大社", "Taga", "大神神社", "Omiwa",
    # Gardens
    "兼六園", "Kenrokuen", "後楽園", "Korakuen", "偕楽園", "Kairakuen",
    "桂離宮", "Katsura", "修学院離宮", "Shugakuin",
    "二条城", "Nijo", "御所", "Gosho", "京都御所", "Kyoto Gosho",
    # Museums
    "東京国立博物館", "Tokyo National", "国立博物館", "National Museum",
    "国立西洋美術館", "National Western", "国立新美術館", "National Art Center",
    "森美術館", "Mori Art", "東京都美術館", "Tokyo Metropolitan Art",
    "京都国立博物館", "Kyoto National", "奈良国立博物館", "Nara National",
    "九州国立博物館", "Kyushu National", "広島平和記念資料館", "Hiroshima Peace",
    "平和記念", "Peace Memorial", "原爆ドーム", "Genbaku Dome",
    "美術館", "Art Museum",
    # Nature / Viewpoints
    "富士山", "Fuji", "富士", "Fuji", "阿蘇", "Aso", "桜島", "Sakurajima",
    "草津温泉", "Kusatsu", "箱根", "Hakone", "別府", "Beppu",
    "地獄", "Jigoku", "洞爺湖", "Lake Toya", "支笏湖", "Lake Shikotsu",
    "十和田湖", "Lake Towada", "田沢湖", "Lake Tazawa", "中禅寺湖", "Lake Chuzenji",
    "嵐山", "Arashiyama", "渡月橋", "Togetsukyo", "竹林", "Bamboo",
    "嵯峨野", "Sagano",
    # Historic / Attractions
    "白川郷", "Shirakawa", "五箇山", "Gokayama", "合掌", "Gassho",
    "金閣", "Kinkaku", "銀閣", "Ginkaku",
    "道頓堀", "Dotonbori", "心斎橋", "Shinsaibashi",
    "錦市場", "Nishiki", "祇園", "Gion", "先斗町", "Pontocho",
    "花見小路", "Hanamikoji", "二年坂", "Ninen", "産寧坂", "Sannen",
    "哲学の道", "Philosopher", "疏水", "Canal",
    "奈良公園", "Nara Park", "東大寺", "Todaiji",
    "宮島", "Miyajima", "弥山", "Mount Misen",
    "金沢", "Kanazawa", "ひがし茶屋街", "Higashi Chaya",
    "東茶屋", "Chaya", "近江町市場", "Omicho",
    "小樽", "Otaru", "運河", "Canal",
    "函館", "Hakodate", "五稜郭", "Goryokaku",
    "登別", "Noboribetsu", "洞爺", "Toya",
    "黒部", "Kurobe", "立山", "Tateyama",
    "白浜", "Shirahama", "那智の滝", "Nachi Falls",
    "高野山", "Koyasan", "奥之院", "Okunoin",
    "吉野", "Yoshino", "桜", "Sakura",
    "日光", "Nikko", "華厳の滝", "Kegon",
    "中禅寺", "Chuzenji", "いろは坂", "Irohazaka",
    "鎌倉", "Kamakura", "江ノ島", "Enoshima",
    "江の島", "Enoshima", "鶴岡", "Tsurugaoka",
    "金毘羅", "Konpira", "琴平", "Kotohira",
    "直島", "Naoshima", "豊島", "Teshima",
    "厳島", "Itsukushima", "宮島口", "Miyajimaguchi",
}

# ─── Category importance weights ───
CATEGORY_WEIGHT = {
    "castle": 10,
    "garden": 9,
    "shrine": 7,
    "temple": 6,
    "museum": 5,
    "historic": 8,
    "viewpoint": 7,
    "nature": 4,
    "beach": 3,
    "onsen": 5,
    "attraction": 4,
}

# ─── Score each spot ───
def score_spot(s):
    score = CATEGORY_WEIGHT.get(s["category"], 0)
    name = s.get("name", "") + " " + s.get("name_ja", "")
    
    # Bonus for matching famous names (large bonus)
    for fn in FAMOUS_NAMES:
        if fn.lower() in name.lower():
            score += 25
            break
    
    # Penalize generic/low-quality names
    if re.match(r'^\d+$', name.strip()):
        score -= 10
    if "第0" in name or re.search(r'第\d+番', name):  # pilgrimage numbers
        score -= 5
    if name.strip().startswith("(") and name.strip().endswith(")"):
        score -= 3
    if "ruins" in name.lower() and "castle" not in name.lower():
        score -= 2
    
    # Exclude obvious non-famous entries
    if re.search(r'church|Chapel|Iglesia|教会', name):
        score -= 20
    if re.search(r'cemeter|grave|墓地|墓所', name):
        score -= 20
    if re.search(r'parking|駐車場', name):
        score -= 20
    if re.search(r'toilet|便所|トイレ', name):
        score -= 20
    if re.search(r'コンビニ|convenience store|CVS', name):
        score -= 20
    if re.search(r'gas station|ガソリン|SS', name):
        score -= 20
    
    return score

# Score and sort
scored = [(s, score_spot(s)) for s in spots]
scored.sort(key=lambda x: -x[1])

# ─── Geographic deduplication ───
# Grid-based: only keep top N spots per grid cell (roughly city-sized)
def lat_lng_to_cell(lat, lng, precision=1):
    """Convert to grid cell at ~100km precision (city/region level)."""
    return (round(lat / precision) * precision, round(lng / precision) * precision)

cell_spots = defaultdict(list)
for s, score in scored:
    if score <= 0:
        continue
    cell = lat_lng_to_cell(s["lat"], s["lng"], precision=1.0)
    cell_spots[cell].append((s, score))

# Keep top spots per cell (limit per city area)
MAX_PER_CELL = 10
MIN_SCORE = 15
famous_spots = []
for cell, items in cell_spots.items():
    # Sort by score within cell
    items.sort(key=lambda x: -x[1])
    # Keep top 10 with minimum score
    for s, score in items[:MAX_PER_CELL]:
        if score < MIN_SCORE:
            break
        famous_spots.append({
            "id": s["id"],
            "name": s["name"],
            "name_ja": s["name_ja"],
            "lat": s["lat"],
            "lng": s["lng"],
            "category": s["category"],
            "emoji": s["emoji"],
            "score": score,
        })

# Sort by score globally
famous_spots.sort(key=lambda x: -x["score"])

# ─── Output stats ───
from collections import Counter
cats = Counter(s["category"] for s in famous_spots)
print(f"Total famous spots: {len(famous_spots)}")
print(f"By category: {dict(cats)}")
print(f"\nTop 20 spots:")
for s in famous_spots[:20]:
    print(f"  [{s['score']:3d}] {s['emoji']} {s['name']} ({s['category']})")

# ─── Save ───
out_path = "/home/ubuntu/hyakumeiten-nearby-finder/frontend/data/scenic_spots_famous.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(famous_spots, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {out_path}")
