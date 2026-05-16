# Hyakumeiten (百名店) Scraper

Scrape and geocode Tabelog Hyakumeiten restaurant data from [award.tabelog.com/hyakumeiten](https://award.tabelog.com/hyakumeiten/).

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### 1. Scrape all categories

```bash
# Scrape all ~68 genre+region pages
python scraper.py

# Scrape specific genres only
python scraper.py --genre shokudo ramen_tokyo sushi_east

# Custom output path
python scraper.py --output data/my_restaurants.json

# Dry run — show URLs without scraping
python scraper.py --dry-run

# Append to existing data (for incremental updates)
python scraper.py --append

# Verbose output
python scraper.py -v
```

### 2. Geocode restaurants

```bash
# Geocode all restaurants (requires scraped data first)
python geocoder.py

# Custom input/output
python geocoder.py --input data/restaurants.json --output data/geocoded.json

# Resume from checkpoint (if interrupted)
python geocoder.py --resume

# Dry run
python geocoder.py --dry-run

# Faster/slower rate limiting
python geocoder.py --rate-limit 0.5   # faster (risk of rate limiting)
python geocoder.py --rate-limit 2.0   # slower (safer)

# Overwrite existing lat/lng values
python geocoder.py --overwrite
```

## Output Format

`data/restaurants.json`:
```json
{
  "id": "13016622",
  "name": "炭焼き かどた/お料理すゞ㐂",
  "area": "東京都 恵比寿駅",
  "genre": "食堂",
  "region": null,
  "tabelog_url": "https://tabelog.com/tokyo/A1303/A130302/13016622/",
  "image_url": "https://...",
  "holiday": "日曜日",
  "is_new": false,
  "lat": null,
  "lng": null
}
```

After geocoding, `lat` and `lng` fields are populated.

## Data Coverage

- ~68 genre+region category pages
- ~3,000+ restaurants total
- 30+ cuisine genres
- All major Japanese regions

## Rate Limiting

- Scraper: 1 second delay between pages (configurable with `--delay`)
- Geocoder: 1.1 second delay between Nominatim requests (required by Nominatim policy)
- Geocoding ~3,000 restaurants takes ~55 minutes

## Ongoing Maintenance

Re-run periodically when Tabelog updates the Hyakumeiten list (typically annually):

```bash
# Full refresh
python scraper.py --append
python geocoder.py --resume
```
