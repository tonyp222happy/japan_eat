#!/usr/bin/env python3
"""
Geocode enriched Hyakumeiten restaurants using detailed addresses.
Uses Nominatim with multi-level fallback + area caching for speed.

Strategy:
  1. Exact address lookup (highest priority)
  2. Area-level lookup (cached — if area already resolved, reuse)
  3. Station-level lookup (fallback)

Usage:
    python geocode_enriched.py                     # Geocode all from tabelog.zip
    python geocode_enriched.py --resume            # Resume from checkpoint
    python geocode_enriched.py --overwrite         # Re-geocode all
    python geocode_enriched.py --dry-run           # Preview only
"""

import argparse
import json
import logging
import time
import zipfile
from collections import Counter
from pathlib import Path

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
CHECKPOINT_FILE = "data/geocode_enriched_checkpoint.json"
AREA_CACHE_FILE = "data/area_cache.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_enriched_data(zip_path: str) -> list[dict]:
    """Load enriched restaurant data from tabelog.zip."""
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open("hyakumeiten-restaurants-enriched.json") as f:
            return json.load(f)


def save_output(restaurants: list[dict], output_path: str):
    """Save geocoded restaurants."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(restaurants)} restaurants to {output_path}")


def load_checkpoint(path: str = CHECKPOINT_FILE) -> set:
    if not Path(path).exists():
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_checkpoint(processed: set, path: str = CHECKPOINT_FILE):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(processed), f)


def load_area_cache(path: str = AREA_CACHE_FILE) -> dict:
    """Load previously resolved area coordinates."""
    if not Path(path).exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_area_cache(cache: dict, path: str = AREA_CACHE_FILE):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def geocode(session: requests.Session, query: str) -> tuple[float, float] | None:
    """Single Nominatim request. Returns (lat, lng) or None."""
    params = {
        "q": query,
        "format": "json",
        "countrycodes": "jp",
        "limit": 1,
        "addressdetails": 1,
    }
    try:
        resp = session.get(NOMINATIM_URL, params=params, timeout=15)
        if resp.status_code == 429:
            logger.warning("Rate limited, waiting 10s...")
            time.sleep(10)
            resp = session.get(NOMINATIM_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        logger.error(f"Geocode error for '{query}': {e}")
    time.sleep(1.0)  # Nominatim rate limit: 1 req/sec
    return None


def build_area_key(r: dict) -> str:
    """Build a cache key from area + station."""
    area = r.get("area", "")
    station = r.get("station_name", "")
    return f"{area}|{station}"


def geocode_with_fallback(session, r: dict, area_cache: dict) -> tuple[float | None, float | None, str]:
    """
    Multi-level geocoding with area caching.
    Returns (lat, lng, strategy_used).
    """
    rid = r.get("id", "")

    # If already geocoded, skip
    if r.get("lat") and r.get("lng"):
        return r["lat"], r["lng"], "already_done"

    # Strategy 1: Exact address (most precise)
    address = r.get("address", "")
    if address:
        # Clean up address — remove building names that might confuse Nominatim
        # Keep: 都道府県 + 市区町村 + 丁目/番地
        coords = geocode(session, address)
        if coords:
            return coords[0], coords[1], "address"

    # Strategy 2: Area + station (cached)
    area_key = build_area_key(r)
    if area_key in area_cache:
        cached = area_cache[area_key]
        if cached and cached.get("lat"):
            return cached["lat"], cached["lng"], "area_cached"

    # Strategy 2b: Area-level geocode (prefecture + city)
    area = r.get("area", "")
    if area:
        coords = geocode(session, area)
        if coords:
            area_cache[area_key] = {"lat": coords[0], "lng": coords[1], "display": area}
            return coords[0], coords[1], "area"

    # Strategy 3: Station name
    station = r.get("station_name", "")
    if station and station != "N/A":
        coords = geocode(session, f"{station}駅, 日本")
        if coords:
            area_cache[area_key] = {"lat": coords[0], "lng": coords[1], "display": station}
            return coords[0], coords[1], "station"

    return None, None, "failed"


def main():
    parser = argparse.ArgumentParser(description="Geocode enriched Hyakumeiten restaurants")
    parser.add_argument("--zip", default="tabelog.zip", help="Path to tabelog.zip")
    parser.add_argument("--output", default="data/hyakumeiten-geocoded.json")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--overwrite", action="store_true", help="Re-geocode everything")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--rate-limit", type=float, default=1.0, help="Delay between requests (seconds)")
    args = parser.parse_args()

    # Load data
    logger.info(f"Loading from {args.zip}...")
    restaurants = load_enriched_data(args.zip)
    logger.info(f"Loaded {len(restaurants)} restaurants")

    # Setup session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "HyakumeitenNearbyFinder/1.0 (educational project; contact: local)",
    })

    # Checkpoint & cache
    checkpoint = load_checkpoint() if args.resume else set()
    area_cache = load_area_cache()

    if args.overwrite:
        checkpoint = set()
        for r in restaurants:
            r["lat"] = None
            r["lng"] = None
            r["geocode_strategy"] = None

    # Filter restaurants to process
    to_process = [
        r for r in restaurants
        if r.get("id") not in checkpoint
        and (not r.get("lat") or not r.get("lng"))
    ]

    if args.dry_run:
        logger.info(f"DRY RUN — Would geocode {len(to_process)} restaurants")
        strategies = Counter()
        for r in to_process[:20]:
            if r.get("address"):
                strategies["address"] += 1
            elif r.get("area"):
                strategies["area"] += 1
            elif r.get("station_name"):
                strategies["station"] += 1
            else:
                strategies["none"] += 1
        logger.info(f"Sample strategy breakdown: {strategies}")
        return

    total = len(to_process)
    already = len(restaurants) - total
    logger.info(f"Already done: {already}, To process: {total}")
    logger.info(f"Estimated time: ~{total/60:.0f} minutes at 1 req/sec")

    success_count = 0
    fail_count = 0
    strategy_counter = Counter()
    area_cache_updates = 0

    for i, r in enumerate(to_process):
        rid = r.get("id", "")
        name = r.get("name", "")
        lat, lng, strategy = geocode_with_fallback(session, r, area_cache)

        if lat and lng:
            r["lat"] = lat
            r["lng"] = lng
            r["geocode_strategy"] = strategy
            success_count += 1
            strategy_counter[strategy] += 1
            if i % 50 == 0:
                logger.info(f"  [{i+1}/{total}] ✓ {name} → ({lat:.4f}, {lng:.4f}) [{strategy}]")
        else:
            r["lat"] = None
            r["lng"] = None
            r["geocode_strategy"] = "failed"
            fail_count += 1
            if i % 50 == 0:
                logger.info(f"  [{i+1}/{total}] ✗ {name} — failed")

        checkpoint.add(rid)

        # Periodic saves
        if (i + 1) % 100 == 0:
            save_checkpoint(checkpoint)
            save_area_cache(area_cache)
            elapsed = (i + 1) * 1.0  # approximate
            remaining = (total - i - 1) * 1.0
            logger.info(
                f"  → Checkpoint #{i+1}: {success_count} OK, {fail_count} failed. "
                f"ETA: {remaining/60:.0f} min remaining"
            )

    # Final save
    save_checkpoint(checkpoint)
    save_area_cache(area_cache)
    save_output(restaurants, args.output)

    # Summary
    total_geocoded = sum(1 for r in restaurants if r.get("lat") and r.get("lng"))
    logger.info("=" * 60)
    logger.info("GEOCODING COMPLETE")
    logger.info(f"  Total restaurants:  {len(restaurants)}")
    logger.info(f"  Geocoded:           {total_geocoded} ({total_geocoded/len(restaurants)*100:.1f}%)")
    logger.info(f"  Not geocoded:       {len(restaurants) - total_geocoded}")
    logger.info(f"  Strategies:         {dict(strategy_counter)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
