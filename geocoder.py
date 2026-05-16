#!/usr/bin/env python3
"""
Hyakumeiten Geocoder
Batch geocodes restaurants using OpenStreetMap Nominatim API.

Usage:
    python geocoder.py                              # Geocode all restaurants in data/restaurants.json
    python geocoder.py --input data/restaurants.json --output data/restaurants_geocoded.json
    python geocoder.py --resume                     # Resume from last checkpoint
    python geocoder.py --dry-run                    # Show what would be geocoded
"""

import argparse
import json
import logging
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import requests

BASE_URL = "https://nominatim.openstreetmap.org/search"
CHECKPOINT_FILE = "data/geocode_checkpoint.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class GeocodeResult:
    lat: Optional[float] = None
    lng: Optional[float] = None
    display_name: Optional[str] = None
    status: str = "pending"  # pending, success, failed, skipped


def load_restaurants(input_path: str) -> list[dict]:
    """Load restaurants from JSON file."""
    path = Path(input_path)
    if not path.exists():
        logger.error(f"Input file not found: {input_path}")
        logger.info("Run scraper.py first to generate restaurant data.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_restaurants(restaurants: list[dict], output_path: str):
    """Save restaurants to JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(restaurants)} restaurants to {output_path}")


def save_checkpoint(processed_ids: set, checkpoint_path: str = CHECKPOINT_FILE):
    """Save checkpoint of processed restaurant IDs."""
    path = Path(checkpoint_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f)


def load_checkpoint(checkpoint_path: str = CHECKPOINT_FILE) -> set:
    """Load checkpoint of processed restaurant IDs."""
    path = Path(checkpoint_path)
    if not path.exists():
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return set(json.load(f))


def build_query(restaurant: dict) -> str:
    """Build a geocoding query from restaurant data."""
    parts = []

    # Restaurant name (most specific)
    name = restaurant.get("name", "")
    if name:
        parts.append(name)

    # Area string (prefecture + station/area)
    area = restaurant.get("area", "")
    if area:
        parts.append(area)

    # Genre context
    genre = restaurant.get("genre", "")
    if genre:
        parts.append(genre)

    return ", ".join(parts)


def geocode(session: requests.Session, query: str, rate_limit_delay: float = 1.1) -> GeocodeResult:
    """Geocode a query using Nominatim API."""
    params = {
        "q": query,
        "format": "json",
        "countrycodes": "jp",  # Japan only
        "limit": 1,
        "addressdetails": 1,
    }

    try:
        resp = session.get(BASE_URL, params=params, timeout=15)

        if resp.status_code == 429:
            # Rate limited — wait longer
            logger.warning("Rate limited. Waiting 5 seconds...")
            time.sleep(5)
            resp = session.get(BASE_URL, params=params, timeout=15)

        resp.raise_for_status()
        data = resp.json()

        time.sleep(rate_limit_delay)  # Nominatim requires 1 req/sec

        if not data:
            return GeocodeResult(status="failed")

        result = data[0]
        return GeocodeResult(
            lat=float(result["lat"]),
            lng=float(result["lon"]),
            display_name=result.get("display_name", ""),
            status="success",
        )
    except requests.RequestException as e:
        logger.error(f"Geocoding error for '{query}': {e}")
        time.sleep(rate_limit_delay)
        return GeocodeResult(status="failed")
    except (ValueError, KeyError) as e:
        logger.error(f"Parse error for '{query}': {e}")
        return GeocodeResult(status="failed")


def geocode_with_fallback(session: requests.Session, restaurant: dict) -> GeocodeResult:
    """Try multiple geocoding strategies with fallback."""
    # Strategy 1: Full query (name + area + genre)
    query = build_query(restaurant)
    result = geocode(session, query)

    if result.status == "success" and result.lat and result.lng:
        return result

    # Strategy 2: Just name + area
    name = restaurant.get("name", "")
    area = restaurant.get("area", "")
    if name and area:
        query2 = f"{name}, {area}"
        result = geocode(session, query2)
        if result.status == "success" and result.lat and result.lng:
            return result

    # Strategy 3: Just area (fallback to area-level geocoding)
    if area:
        query3 = area
        result = geocode(session, query3)
        if result.status == "success" and result.lat and result.lng:
            result.display_name = f"[Area fallback] {result.display_name}"
            return result

    return result


def geocode_all(
    restaurants: list[dict],
    resume: bool = False,
    dry_run: bool = False,
    rate_limit: float = 1.1,
    batch_size: int = 50,
) -> list[dict]:
    """Geocode all restaurants with batching and checkpointing."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "HyakumeitenNearbyFinder/1.0 (educational project; contact: local)",
    })

    checkpoint = load_checkpoint() if resume else set()
    to_process = [
        r for r in restaurants
        if r.get("id") not in checkpoint
        and (not r.get("lat") or not r.get("lng"))
    ]

    if dry_run:
        logger.info(f"DRY RUN — Would geocode {len(to_process)} restaurants:")
        for r in to_process[:10]:
            logger.info(f"  [{r['id']}] {r['name']} — {r.get('area', 'N/A')}")
        if len(to_process) > 10:
            logger.info(f"  ... and {len(to_process) - 10} more")
        return restaurants

    total = len(to_process)
    logger.info(f"Geocoding {total} restaurants (rate: {rate_limit}s between requests)...")

    for i, restaurant in enumerate(to_process):
        rid = restaurant.get("id", "")
        name = restaurant.get("name", "")
        area = restaurant.get("area", "")

        result = geocode_with_fallback(session, restaurant)

        if result.status == "success" and result.lat and result.lng:
            restaurant["lat"] = result.lat
            restaurant["lng"] = result.lng
            logger.info(
                f"  [{i+1}/{total}] ✓ {name} ({area}) "
                f"→ ({result.lat:.6f}, {result.lng:.6f})"
            )
        else:
            restaurant["lat"] = None
            restaurant["lng"] = None
            logger.warning(
                f"  [{i+1}/{total}] ✗ {name} ({area}) — could not geocode"
            )

        checkpoint.add(rid)

        # Save checkpoint periodically
        if (i + 1) % batch_size == 0:
            save_checkpoint(checkpoint)
            logger.info(f"  → Checkpoint saved ({i+1}/{total})")

    # Final save
    save_checkpoint(checkpoint)
    logger.info(f"Geocoding complete: {total} processed")

    # Summary
    geocoded = sum(1 for r in restaurants if r.get("lat") and r.get("lng"))
    failed = total - geocoded + sum(
        1 for r in restaurants
        if r.get("id") in checkpoint and not r.get("lat")
    )
    logger.info(f"Results: {geocoded} geocoded, {len(restaurants) - geocoded} not geocoded")

    return restaurants


def main():
    parser = argparse.ArgumentParser(description="Hyakumeiten Geocoder")
    parser.add_argument(
        "--input", default="data/restaurants.json",
        help="Input JSON file (default: data/restaurants.json)"
    )
    parser.add_argument(
        "--output", default="data/restaurants_geocoded.json",
        help="Output JSON file (default: data/restaurants_geocoded.json)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from last checkpoint"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be geocoded without making requests"
    )
    parser.add_argument(
        "--rate-limit", type=float, default=1.1,
        help="Delay between geocoding requests in seconds (default: 1.1)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=50,
        help="Save checkpoint every N requests (default: 50)"
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing lat/lng values"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    restaurants = load_restaurants(args.input)
    if not restaurants:
        return

    logger.info(f"Loaded {len(restaurants)} restaurants from {args.input}")

    # If not overwriting, skip already-geocoded entries
    if not args.overwrite:
        already_geocoded = sum(1 for r in restaurants if r.get("lat") and r.get("lng"))
        logger.info(f"Already geocoded: {already_geocoded}")

    restaurants = geocode_all(
        restaurants,
        resume=args.resume,
        dry_run=args.dry_run,
        rate_limit=args.rate_limit,
        batch_size=args.batch_size,
    )

    if not args.dry_run:
        save_restaurants(restaurants, args.output)


if __name__ == "__main__":
    main()
