#!/usr/bin/env python3
"""
Scrape scenic spots from OpenStreetMap Overpass API for Japan.
Single query for all of Japan, split into fewer regions for reliability.
"""
import json
import time
import urllib.request
import urllib.parse

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Split into 6 wider regions (east-west strips)
REGIONS = [
    (24.0, 122.0, 30.0, 146.0),  # Kyushu, Okinawa
    (30.0, 129.0, 34.5, 136.5),  # Chugoku, Shikoku, Kansai
    (30.0, 136.5, 34.5, 146.0),  # Chubu, Kanto (south)
    (34.5, 122.0, 39.0, 141.0),  # Tohoku (west), Hokuriku, Kanto (north)
    (34.5, 141.0, 39.0, 146.0),  # Tohoku (east)
    (39.0, 122.0, 46.0, 146.0),  # Hokkaido
]

def query_region(s, w, n, e):
    query = f"""
    [out:json][timeout:180];
    (
      node["tourism"="attraction"]({s},{w},{n},{e});
      node["tourism"="viewpoint"]({s},{w},{n},{e});
      node["tourism"="museum"]({s},{w},{n},{e});
      node["tourism"="gallery"]({s},{w},{n},{e});
      node["tourism"="theme_park"]({s},{w},{n},{e});
      node["tourism"="zoo"]({s},{w},{n},{e});
      node["tourism"="aquarium"]({s},{w},{n},{e});
      node["historic"="castle"]({s},{w},{n},{e});
      node["historic"="monument"]({s},{w},{n},{e});
      node["historic"="shrine"]({s},{w},{n},{e});
      node["amenity"="place_of_worship"]["religion"="shinto"]({s},{w},{n},{e});
      node["amenity"="place_of_worship"]["religion"="buddhist"]({s},{w},{n},{e});
      node["leisure"="garden"]["name"]({s},{w},{n},{e});
      node["natural"="peak"]["name"]({s},{w},{n},{e});
      node["natural"="beach"]["name"]({s},{w},{n},{e});
      node["natural"="hot_spring"]({s},{w},{n},{e});
    );
    out body;
    """
    
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(OVERPASS_URL, data=data, headers={
        "User-Agent": "Hyakumeiten Nearby Finder (https://github.com/tonyp222happy/japan_eat)"
    })
    
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_category(tags):
    t = tags
    if t.get("natural") == "hot_spring" or t.get("attraction") == "hot_spring":
        return "onsen"
    if t.get("religion") == "shinto" or t.get("historic") == "shrine":
        return "shrine"
    if t.get("religion") == "buddhist":
        return "temple"
    if t.get("tourism") == "museum" or t.get("tourism") == "gallery":
        return "museum"
    if t.get("historic") == "castle":
        return "castle"
    if t.get("leisure") == "garden":
        return "garden"
    if t.get("natural") == "peak":
        return "nature"
    if t.get("natural") == "beach":
        return "beach"
    if t.get("tourism") == "viewpoint":
        return "viewpoint"
    if t.get("tourism") in ("theme_park", "zoo", "aquarium"):
        return "attraction"
    if t.get("historic") in ("monument",):
        return "historic"
    if t.get("tourism") == "attraction":
        return "attraction"
    return "other"

def get_name(tags):
    return (tags.get("name:en") or tags.get("name") or tags.get("name:ja") or 
            tags.get("alt_name") or tags.get("short_name") or "Unnamed")

def main():
    spots = []
    seen_ids = set()
    
    for idx, (s, w, n, e) in enumerate(REGIONS):
        print(f"[{idx+1}/{len(REGIONS)}] Querying [{s},{w},{n},{e}]...")
        try:
            result = query_region(s, w, n, e)
            for element in result.get("elements", []):
                elem_id = element.get("id")
                if elem_id in seen_ids:
                    continue
                seen_ids.add(elem_id)
                
                tags = element.get("tags", {})
                name = get_name(tags)
                if name == "Unnamed":
                    continue
                
                category = get_category(tags)
                spot = {
                    "id": f"osm_{elem_id}",
                    "name": name,
                    "name_ja": tags.get("name:ja") or tags.get("name") or name,
                    "lat": round(element.get("lat"), 6),
                    "lng": round(element.get("lon"), 6),
                    "category": category,
                }
                spots.append(spot)
            
            print(f"  → {len([e for e in result.get('elements', [])])} new spots, total: {len(spots)}")
        except Exception as e:
            print(f"  → Error: {e}")
        
        if idx < len(REGIONS) - 1:
            time.sleep(3)
    
    # Save
    with open("data/scenic_spots.json", "w", encoding="utf-8") as f:
        json.dump(spots, f, ensure_ascii=False, indent=2)
    
    # Category counts
    cats = {}
    for s in spots:
        cats[s["category"]] = cats.get(s["category"], 0) + 1
    
    print(f"\n=== Scenic Spots Summary ===")
    print(f"Total: {len(spots)}")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()
