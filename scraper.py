#!/usr/bin/env python3
"""
Hyakumeiten (百名店) Scraper
Scrapes all restaurant data from award.tabelog.com/hyakumeiten/

Usage:
    python scraper.py                          # Scrape all categories
    python scraper.py --genre shokudo ramen    # Scrape specific genres
    python scraper.py --output data/restaurants.json
    python scraper.py --dry-run                # Show URLs without scraping
"""

import argparse
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://award.tabelog.com"
CATEGORY_PATH = "/hyakumeiten/"

# Genre URL slugs discovered from the navigation
ALL_GENRES = [
    "shokudo",
    "spanish",
    "chinese_tokyo", "chinese_east", "chinese_west",
    "hamburger",
    "tonkatsu",
    "ramen_hokkaido", "ramen_tokyo", "ramen_kanagawa",
    "ramen_aichi", "ramen_osaka", "ramen_east", "ramen_west",
    "yakitori_east", "yakitori_west",
    "toriryori",
    "yakiniku_tokyo", "yakiniku_east", "yakiniku_west",
    "izakaya_east", "izakaya_west",
    "bar",
    "creative_innovative",
    "italian_tokyo", "italian_east", "italian_west",
    "pizza",
    "japanese_tokyo", "japanese_east", "japanese_west",
    "tempura",
    "sushi_tokyo", "sushi_east", "sushi_west",
    "sukiyaki_shabushabu",
    "curry_tokyo", "curry_east", "curry_west",
    "asia_ethnic_tokyo", "asia_ethnic_east", "asia_ethnic_west",
    "unagi",
    "gyoza",
    "udon_kagawa", "udon_east", "udon_west",
    "wagashi_tokyo", "wagashi_east", "wagashi_west",
    "sweets_tokyo", "sweets_east", "sweets_west",
    "ice_gelato",
    "tachinomi",
    "kissaten",
    "okonomiyaki",
    "steak_east", "steak_west",
    "yoshoku_east", "yoshoku_west",
    "french_tokyo", "french_east", "french_west",
    "bread_tokyo", "bread_east", "bread_west",
    "cafe_east", "cafe_west",
    "soba_east", "soba_west",
]

# Map URL slug → human-readable genre name (extracted from page titles)
GENRE_NAME_MAP = {
    "shokudo": "食堂",
    "spanish": "スペイン料理",
    "chinese_tokyo": "中国料理",
    "chinese_east": "中国料理",
    "chinese_west": "中国料理",
    "hamburger": "ハンバーガー",
    "tonkatsu": "とんかつ",
    "ramen_hokkaido": "ラーメン",
    "ramen_tokyo": "ラーメン",
    "ramen_kanagawa": "ラーメン",
    "ramen_aichi": "ラーメン",
    "ramen_osaka": "ラーメン",
    "ramen_east": "ラーメン",
    "ramen_west": "ラーメン",
    "yakitori_east": "焼き鳥",
    "yakitori_west": "焼き鳥",
    "toriryori": "鳥料理",
    "yakiniku_tokyo": "焼肉",
    "yakiniku_east": "焼肉",
    "yakiniku_west": "焼肉",
    "izakaya_east": "居酒屋",
    "izakaya_west": "居酒屋",
    "bar": "バー",
    "creative_innovative": "創作料理・イノベーティブ",
    "italian_tokyo": "イタリアン",
    "italian_east": "イタリアン",
    "italian_west": "イタリアン",
    "pizza": "ピザ",
    "japanese_tokyo": "日本料理",
    "japanese_east": "日本料理",
    "japanese_west": "日本料理",
    "tempura": "天ぷら",
    "sushi_tokyo": "寿司",
    "sushi_east": "寿司",
    "sushi_west": "寿司",
    "sukiyaki_shabushabu": "すき焼き・しゃぶしゃぶ",
    "curry_tokyo": "カレー",
    "curry_east": "カレー",
    "curry_west": "カレー",
    "asia_ethnic_tokyo": "アジア・エスニック",
    "asia_ethnic_east": "アジア・エスニック",
    "asia_ethnic_west": "アジア・エスニック",
    "unagi": "うなぎ",
    "gyoza": "餃子",
    "udon_kagawa": "うどん",
    "udon_east": "うどん",
    "udon_west": "うどん",
    "wagashi_tokyo": "和菓子・甘味処",
    "wagashi_east": "和菓子・甘味処",
    "wagashi_west": "和菓子・甘味処",
    "sweets_tokyo": "スイーツ",
    "sweets_east": "スイーツ",
    "sweets_west": "スイーツ",
    "ice_gelato": "アイス・ジェラート",
    "tachinomi": "立ち飲み",
    "kissaten": "喫茶",
    "okonomiyaki": "お好み焼き",
    "steak_east": "ステーキ",
    "steak_west": "ステーキ",
    "yoshoku_east": "洋食",
    "yoshoku_west": "洋食",
    "french_tokyo": "フレンチ",
    "french_east": "フレンチ",
    "french_west": "フレンチ",
    "bread_tokyo": "パン",
    "bread_east": "パン",
    "bread_west": "パン",
    "cafe_east": "カフェ",
    "cafe_west": "カフェ",
    "soba_east": "そば",
    "soba_west": "そば",
}

# Map URL slug → region
REGION_MAP = {
    "shokudo": None,
    "spanish": None,
    "chinese_tokyo": "TOKYO",
    "chinese_east": "EAST",
    "chinese_west": "WEST",
    "hamburger": None,
    "tonkatsu": None,
    "ramen_hokkaido": "HOKKAIDO",
    "ramen_tokyo": "TOKYO",
    "ramen_kanagawa": "KANAGAWA",
    "ramen_aichi": "AICHI",
    "ramen_osaka": "OSAKA",
    "ramen_east": "EAST",
    "ramen_west": "WEST",
    "yakitori_east": "EAST",
    "yakitori_west": "WEST",
    "toriryori": None,
    "yakiniku_tokyo": "TOKYO",
    "yakiniku_east": "EAST",
    "yakiniku_west": "WEST",
    "izakaya_east": "EAST",
    "izakaya_west": "WEST",
    "bar": None,
    "creative_innovative": None,
    "italian_tokyo": "TOKYO",
    "italian_east": "EAST",
    "italian_west": "WEST",
    "pizza": None,
    "japanese_tokyo": "TOKYO",
    "japanese_east": "EAST",
    "japanese_west": "WEST",
    "tempura": None,
    "sushi_tokyo": "TOKYO",
    "sushi_east": "EAST",
    "sushi_west": "WEST",
    "sukiyaki_shabushabu": None,
    "curry_tokyo": "TOKYO",
    "curry_east": "EAST",
    "curry_west": "WEST",
    "asia_ethnic_tokyo": "TOKYO",
    "asia_ethnic_east": "EAST",
    "asia_ethnic_west": "WEST",
    "unagi": None,
    "gyoza": None,
    "udon_kagawa": "KAGAWA",
    "udon_east": "EAST",
    "udon_west": "WEST",
    "wagashi_tokyo": "TOKYO",
    "wagashi_east": "EAST",
    "wagashi_west": "WEST",
    "sweets_tokyo": "TOKYO",
    "sweets_east": "EAST",
    "sweets_west": "WEST",
    "ice_gelato": None,
    "tachinomi": None,
    "kissaten": None,
    "okonomiyaki": None,
    "steak_east": "EAST",
    "steak_west": "WEST",
    "yoshoku_east": "EAST",
    "yoshoku_west": "WEST",
    "french_tokyo": "TOKYO",
    "french_east": "EAST",
    "french_west": "WEST",
    "bread_tokyo": "TOKYO",
    "bread_east": "EAST",
    "bread_west": "WEST",
    "cafe_east": "EAST",
    "cafe_west": "WEST",
    "soba_east": "EAST",
    "soba_west": "WEST",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class Restaurant:
    """Represents a single Hyakumeiten restaurant."""
    id: str
    name: str
    area: str
    genre: str
    region: Optional[str] = None
    tabelog_url: str = ""
    image_url: str = ""
    holiday: Optional[str] = None
    is_new: bool = False
    lat: Optional[float] = None
    lng: Optional[float] = None


def get_session() -> requests.Session:
    """Create a requests session with browser-like headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
    })
    return session


def fetch_page(session: requests.Session, url: str, retries: int = 3) -> Optional[str]:
    """Fetch a page with retries and error handling."""
    for attempt in range(retries):
        try:
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    logger.error(f"Failed to fetch {url} after {retries} attempts")
    return None


def parse_restaurants(html: str, genre_slug: str) -> list[Restaurant]:
    """Parse restaurant cards from a category page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    genre = GENRE_NAME_MAP.get(genre_slug, genre_slug)
    region = REGION_MAP.get(genre_slug)

    restaurants = []
    items = soup.select("div.hyakumeiten-shop__item")

    for item in items:
        # Extract restaurant ID from data-id attribute
        hozon_btn = item.select_one("div.js-hozon-btn")
        restaurant_id = hozon_btn.get("data-id", "") if hozon_btn else ""

        # Extract tabelog URL from the link
        link = item.select_one("a.hyakumeiten-shop__target")
        tabelog_url = link.get("href", "") if link else ""

        # Extract image URL from data-src
        img = item.select_one("div.hyakumeiten-shop__img img")
        image_url = ""
        if img:
            image_url = img.get("data-src", "") or img.get("src", "")
            if image_url.startswith("//"):
                image_url = "https:" + image_url

        # Extract restaurant name
        name_el = item.select_one("div.hyakumeiten-shop__name")
        name = name_el.get_text(strip=True) if name_el else ""

        # Extract area (last span in the area div, skip the SVG icon span)
        area_el = item.select_one("div.hyakumeiten-shop__area")
        area = ""
        if area_el:
            spans = area_el.find_all("span")
            # The last span contains the area text (first span has the SVG icon)
            area_spans = [s.get_text(strip=True) for s in spans if s.get_text(strip=True)]
            area = area_spans[-1] if area_spans else ""

        # Extract holiday/closed days
        holiday_el = item.select_one("div.hyakumeiten-shop__holiday")
        holiday = None
        if holiday_el:
            spans = holiday_el.find_all("span")
            holiday_spans = [s.get_text(strip=True) for s in spans if s.get_text(strip=True)]
            holiday = holiday_spans[-1] if holiday_spans else None

        # Check for "first selection" badge
        new_el = item.select_one("div.hyakumeiten-shop__new")
        is_new = new_el is not None and "初選出" in new_el.get_text()

        if not restaurant_id or not name:
            logger.debug(f"Skipping item with missing id/name: {item}")
            continue

        restaurants.append(Restaurant(
            id=restaurant_id,
            name=name,
            area=area,
            genre=genre,
            region=region,
            tabelog_url=tabelog_url,
            image_url=image_url,
            holiday=holiday,
            is_new=is_new,
        ))

    return restaurants


def scrape_category(session: requests.Session, genre_slug: str) -> list[Restaurant]:
    """Scrape all restaurants from a single category page."""
    url = f"{BASE_URL}{CATEGORY_PATH}{genre_slug}/"
    logger.info(f"Scraping: {url}")

    html = fetch_page(session, url)
    if not html:
        return []

    restaurants = parse_restaurants(html, genre_slug)
    logger.info(f"  → Found {len(restaurants)} restaurants in {genre_slug}")
    return restaurants


def scrape_all(genres: list[str], delay: float = 1.0, dry_run: bool = False) -> list[Restaurant]:
    """Scrape all specified genre categories."""
    session = get_session()
    all_restaurants = []

    if dry_run:
        logger.info("DRY RUN — URLs to scrape:")
        for slug in genres:
            print(f"  {BASE_URL}{CATEGORY_PATH}{slug}/")
        return []

    for i, slug in enumerate(genres):
        restaurants = scrape_category(session, slug)
        all_restaurants.extend(restaurants)

        # Rate limiting — be polite
        if i < len(genres) - 1:
            time.sleep(delay)

    return all_restaurants


def deduplicate(restaurants: list[Restaurant]) -> list[Restaurant]:
    """Remove duplicate restaurants by ID, keeping the most complete record."""
    seen = {}
    for r in restaurants:
        if r.id not in seen:
            seen[r.id] = r
        else:
            existing = seen[r.id]
            # Keep the one with more data
            if sum(1 for v in [r.tabelog_url, r.image_url, r.holiday, r.area] if v) > \
               sum(1 for v in [existing.tabelog_url, existing.image_url, existing.holiday, existing.area] if v):
                seen[r.id] = r
    return list(seen.values())


def save_json(restaurants: list[Restaurant], output_path: str):
    """Save restaurants to JSON file."""
    data = [asdict(r) for r in restaurants]
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(restaurants)} restaurants to {output_path}")


def load_existing(output_path: str) -> list[Restaurant]:
    """Load previously scraped restaurants from JSON."""
    path = Path(output_path)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Restaurant(**r) for r in data]


def main():
    parser = argparse.ArgumentParser(description="Hyakumeiten (百名店) Scraper")
    parser.add_argument(
        "--genre", nargs="+",
        help="Specific genre slugs to scrape (default: all)"
    )
    parser.add_argument(
        "--output", default="data/restaurants.json",
        help="Output JSON file path (default: data/restaurants.json)"
    )
    parser.add_argument(
        "--delay", type=float, default=1.0,
        help="Delay between requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show URLs without scraping"
    )
    parser.add_argument(
        "--append", action="store_true",
        help="Append to existing data instead of replacing"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    genres = args.genre if args.genre else ALL_GENRES
    logger.info(f"Scraping {len(genres)} genre categories...")

    restaurants = scrape_all(genres, delay=args.delay, dry_run=args.dry_run)

    if args.dry_run:
        return

    # Deduplicate
    restaurants = deduplicate(restaurants)
    logger.info(f"Total unique restaurants: {len(restaurants)}")

    # Optionally merge with existing data
    if args.append:
        existing = load_existing(args.output)
        existing_ids = {r.id for r in existing}
        new_restaurants = [r for r in restaurants if r.id not in existing_ids]
        restaurants = existing + new_restaurants
        logger.info(f"Merged with existing: {len(restaurants)} total ({len(new_restaurants)} new)")

    save_json(restaurants, args.output)

    # Print summary
    genre_counts = {}
    for r in restaurants:
        genre_counts[r.genre] = genre_counts.get(r.genre, 0) + 1
    logger.info("\nGenre summary:")
    for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
        logger.info(f"  {genre}: {count}")


if __name__ == "__main__":
    main()
