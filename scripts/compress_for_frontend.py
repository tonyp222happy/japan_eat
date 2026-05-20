#!/usr/bin/env python3
"""Compress data for frontend delivery: short keys, strip nulls, compact JSON."""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Full → compressed key mapping
M = {
    'id':'id','name':'n','area':'a','genre':'g','tabelog_url':'u',
    'image_url':'i','holiday':'h','is_new':'nw','lat':'la','lng':'lo',
    'rating':'r','review_count':'c','budget_lunch':'bl','budget_dinner':'bd',
    'phone':'p','reservable':'rv','address':'addr','station_name':'st',
    'hours_raw':'hr','sub_genres':'sg','awards':'aw','walk_minutes':'wm',
}

def compress(records, mapping):
    out = []
    for rec in records:
        c = {}
        for k, v in rec.items():
            mk = mapping.get(k, k)
            if v is None: continue
            if isinstance(v, str) and v == '': continue
            c[mk] = v
        out.append(c)
    return out

# Main data
with open(f'{BASE}/data.json') as f:
    data = json.load(f)
c = compress(data, M)
with open(f'{BASE}/frontend/data.json', 'w') as f:
    json.dump(c, f, ensure_ascii=False, separators=(',',':'))
sz = os.path.getsize(f'{BASE}/frontend/data.json')
print(f"data.json: {sz/1e6:.1f}MB ({len(c)} records)")

# Famous restaurants
FM = {
    'id':'id','name':'n','name_en':'ne','genre':'g','area':'a',
    'lat':'la','lng':'lo','rating':'r','saved_count':'sc',
    'review_count':'c','budget_lunch':'bl','budget_dinner':'bd',
    'address':'addr','station_name':'st','phone':'p',
    'reservable':'rv','hours_raw':'hr','tabelog_url':'u',
    'image_url':'i','emoji':'em','color':'cl',
}
src = f'{BASE}/frontend/data/famous_restaurants.json'
if os.path.exists(src):
    with open(src) as f:
        fam = json.load(f)
    cf = compress(fam, FM)
    with open(f'{BASE}/frontend/data/famous_restaurants.json', 'w') as f:
        json.dump(cf, f, ensure_ascii=False, separators=(',',':'))
    print(f"famous: {os.path.getsize(f'{BASE}/frontend/data/famous_restaurants.json')/1e6:.1f}MB ({len(cf)} records)")

# Scenic spots
SM = {'id':'id','name':'n','name_ja':'nj','lat':'la','lng':'lo','category':'cat','emoji':'em','score':'sc'}
src = f'{BASE}/frontend/data/scenic_spots_famous.json'
if os.path.exists(src):
    with open(src) as f:
        scn = json.load(f)
    cs = compress(scn, SM)
    with open(f'{BASE}/frontend/data/scenic_spots_famous.json', 'w') as f:
        json.dump(cs, f, ensure_ascii=False, separators=(',',':'))
    print(f"scenic: {os.path.getsize(f'{BASE}/frontend/data/scenic_spots_famous.json')/1e6:.1f}MB ({len(cs)} records)")
