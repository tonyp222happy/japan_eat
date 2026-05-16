#!/usr/bin/env python3
"""
Verifier for J001: Hyakumeiten Nearby Finder Frontend MVP
Checks: file structure, HTML validity, JSON data, basic smoke tests.

Run from repo root: python scripts/verify_frontend.py
"""

import json
import os
import sys
from pathlib import Path

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
DATA_DIR = Path(__file__).parent.parent / "data"

errors = []
warnings = []


def check_file_exists(path, description):
    if not path.exists():
        errors.append(f"MISSING: {description} ({path})")
        return False
    return True


def check_json_valid(path, description):
    if not check_file_exists(path, description):
        return False
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        errors.append(f"INVALID JSON: {description} — {e}")
        return False


def check_html_has_tag(html_path, tag, description):
    if not check_file_exists(html_path, f"HTML file for {description}"):
        return False
    content = html_path.read_text()
    if tag.lower() not in content.lower():
        errors.append(f"MISSING TAG: {description} should contain '{tag}'")
        return False
    return True


print("=" * 60)
print("  J001 Verifier: Hyakumeiten Nearby Finder Frontend MVP")
print("=" * 60)

# 1. Check required files exist
print("\n  [1/5] Checking file structure...")
check_file_exists(FRONTEND_DIR / "index.html", "Main HTML")
check_file_exists(FRONTEND_DIR / "css" / "style.css", "Stylesheet")
check_file_exists(FRONTEND_DIR / "js" / "app.js", "Main JavaScript")

# 2. Check data file
print("  [2/5] Checking restaurant data...")
data = check_json_valid(FRONTEND_DIR / "data" / "restaurants.json", "Restaurant data")
if data:
    if isinstance(data, list):
        count = len(data)
        print(f"    Loaded {count} restaurants")
        if count == 0:
            errors.append("EMPTY: Restaurant data has 0 entries")
        elif count > 1500:
            warnings.append(f"LARGE: {count} restaurants — consider lazy loading")

        # Check record structure
        if count > 0:
            sample = data[0]
            required_keys = ["id", "name", "lat", "lng", "tabelog_url"]
            for key in required_keys:
                if key not in sample:
                    errors.append(f"SCHEMA: Missing '{key}' in restaurant record")

            # Check geocoded entries
            geocoded = sum(1 for r in data if r.get("lat") and r.get("lng"))
            if geocoded < count * 0.5:
                warnings.append(f"Only {geocoded}/{count} restaurants have coordinates")
    else:
        errors.append("SCHEMA: Restaurant data should be a JSON array")

# 3. Check HTML structure
print("  [3/5] Checking HTML structure...")
html_path = FRONTEND_DIR / "index.html"
if check_file_exists(html_path, "index.html"):
    content = html_path.read_text()
    # Basic HTML5 checks
    if "<!DOCTYPE html>" not in content:
        errors.append("HTML: Missing <!DOCTYPE html>")
    if "<html" not in content:
        errors.append("HTML: Missing <html> tag")
    if "</html>" not in content:
        errors.append("HTML: Missing </html> tag")

    # Required elements for the app
    required_elements = [
        ("leaflet", "Leaflet map library"),
        ("geolocation" if "navigator.geolocation" in content else "", "Geolocation API"),
    ]
    for term, desc in required_elements:
        if term and term.lower() not in content.lower():
            errors.append(f"MISSING: {desc} not found in HTML")

# 4. Check JS for required functionality
print("  [4/5] Checking JavaScript...")
js_path = FRONTEND_DIR / "js" / "app.js"
if check_file_exists(js_path, "app.js"):
    content = js_path.read_text()
    required_functions = [
        ("geolocation", "Geolocation handling"),
        ("distance" or "haversine", "Distance calculation"),
        ("sort", "Result sorting"),
    ]
    for term, desc in required_functions:
        if term.lower() not in content.lower():
            errors.append(f"MISSING: {desc} — no '{term}' found in app.js")

    # Check for language toggle
    if "lang" not in content.lower() and "language" not in content.lower():
        warnings.append("No language toggle detected in app.js")

# 5. CSS checks
print("  [5/5] Checking CSS...")
css_path = FRONTEND_DIR / "css" / "style.css"
if check_file_exists(css_path, "style.css"):
    content = css_path.read_text()
    if "map" not in content.lower():
        warnings.append("No map-related styles found in CSS")
    if "@media" not in content:
        warnings.append("No media queries — may not be responsive")

# Summary
print("\n" + "=" * 60)
if errors:
    print(f"  FAILED: {len(errors)} error(s)")
    for e in errors:
        print(f"    ✗ {e}")
    if warnings:
        print(f"\n  {len(warnings)} warning(s)")
        for w in warnings:
            print(f"    ⚠ {w}")
    sys.exit(1)
else:
    print("  PASSED: All checks passed")
    if warnings:
        print(f"\n  {len(warnings)} warning(s)")
        for w in warnings:
            print(f"    ⚠ {w}")
    sys.exit(0)
