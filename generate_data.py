#!/usr/bin/env python3
"""
Generate compact data.js for the frontend.
Uses enriched data + area cache for geocoding.
"""
import json
import zipfile
import os
import sys

ZIP_PATH = "tabelog.zip"
AREA_CACHE = "data/area_cache.json"
GEOCODED_OUTPUT = "data/hyakumeiten-geocoded.json"
FRONTEND_DIR = "../hyakumeiten-nearby-finder"
OUTPUT_JS = os.path.join(FRONTEND_DIR, "data.js")
OUTPUT_JSON = os.path.join(FRONTEND_DIR, "data.json")

def main():
    # Try loading geocoded output first
    if os.path.exists(GEOCODED_OUTPUT):
        with open(GEOCODED_OUTPUT) as f:
            data = json.load(f)
        print(f"Loaded {len(data)} restaurants from geocoded output")
    else:
        with zipfile.ZipFile(ZIP_PATH, "r") as z:
            with z.open("hyakumeiten-restaurants-enriched.json") as f:
                data = json.load(f)
        print(f"Loaded {len(data)} restaurants from zip (no geocoded output yet)")

    # Load area cache for fallback coordinates
    area_cache = {}
    if os.path.exists(AREA_CACHE):
        with open(AREA_CACHE) as f:
            raw_cache = json.load(f)
        # Build lookup: area -> coords
        for key, val in raw_cache.items():
            area = key.split("|")[0]  # area|station
            if val.get("lat") and area:
                area_cache[area] = val

    # Create compact format
    compact = []
    geocoded = 0
    area_filled = 0
    no_coords = 0

    for r in data:
        entry = {
            "id": r["id"],
            "n": r["name"],           # name
            "a": r.get("area", ""),   # area
            "g": r.get("genre", ""),  # genre
            "u": r.get("tabelog_url", ""),
            "i": r.get("image_url", ""),
            "r": r.get("rating"),
            "c": r.get("review_count"),
            "h": r.get("holiday", ""),
            "bl": r.get("budget_lunch", ""),
            "bd": r.get("budget_dinner", ""),
            "p": r.get("phone", ""),
            "s": r.get("seats"),
            "addr": r.get("address", ""),
            "st": r.get("station_name", ""),
            "nw": r.get("is_new", False),
        }

        # Coordinates
        lat, lng = r.get("lat"), r.get("lng")
        if lat and lng:
            entry["la"] = round(lat, 6)
            entry["lo"] = round(lng, 6)
            geocoded += 1
        elif r["area"] in area_cache:
            c = area_cache[r["area"]]
            entry["la"] = round(c["lat"], 6)
            entry["lo"] = round(c["lng"], 6)
            entry["_af"] = True  # area_filled flag
            area_filled += 1
        else:
            no_coords += 1

        compact.append(entry)

    os.makedirs(FRONTEND_DIR, exist_ok=True)

    # Write data.js (for direct script loading)
    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write("const HYAKUMEITEN_DATA = ")
        json.dump(compact, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";")

    # Write data.json (for fetch fallback)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(compact, f, ensure_ascii=False, indent=2)

    js_size = os.path.getsize(OUTPUT_JS)
    json_size = os.path.getsize(OUTPUT_JSON)

    print(f"\n=== Data Generation Complete ===")
    print(f"Total restaurants: {len(compact)}")
    print(f"  Geocoded (exact):  {geocoded} ({geocoded/len(compact)*100:.1f}%)")
    print(f"  Area-filled:       {area_filled} ({area_filled/len(compact)*100:.1f}%)")
    print(f"  No coordinates:    {no_coords} ({no_coords/len(compact)*100:.1f}%)")
    print(f"data.js size:  {js_size/1024/1024:.1f} MB")
    print(f"data.json size: {json_size/1024/1024:.1f} MB")
    print(f"Output: {OUTPUT_JS}")

if __name__ == "__main__":
    main()
