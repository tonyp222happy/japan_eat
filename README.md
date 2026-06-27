# 🍣 Japan Eat - Tabelog Hyakumeiten (百名店)

A curated collection of Japan's best restaurants from [Tabelog Hyakumeiten](https://award.tabelog.com/hyakumeiten/), featuring 3,000+ award-winning establishments across 30+ cuisine genres.

## 🌐 Live Website

**[View Interactive Map →](https://tonyp222happy.github.io/japan_eat/)**

Explore restaurants by:
- 📍 Location (interactive map)
- 🍱 Cuisine type (sushi, ramen, tempura, etc.)
- 🏆 Award category

## 📊 Data Coverage

- **3,000+ restaurants** from Tabelog's prestigious Hyakumeiten list
- **30+ cuisine genres** including sushi, ramen, kaiseki, tempura, yakitori, and more
- **All major regions** - Tokyo, Osaka, Kyoto, Hokkaido, Kyushu, and beyond
- **Geocoded locations** for precise mapping
- **Regular updates** - Data refreshed when Tabelog announces new award winners

## 🗂️ Data Format

The restaurant data (`data.json`) includes:
```json
{
  "id": "13016622",
  "name": "炭焼き かどた",
  "area": "東京都 恵比寿駅",
  "genre": "食堂",
  "tabelog_url": "https://tabelog.com/tokyo/A1303/A130302/13016622/",
  "image_url": "...",
  "holiday": "日曜日",
  "lat": 35.6421,
  "lng": 139.7119
}
```

## 📝 About

This project showcases Japan's culinary excellence by visualizing the Tabelog Hyakumeiten award winners. The data is sourced from Tabelog's official awards page and geocoded for interactive exploration.

**Note:** The scraping and data processing scripts are private. This repository contains only the public-facing website and aggregated data.

## 🙏 Credits

- Data source: [Tabelog Hyakumeiten](https://award.tabelog.com/hyakumeiten/)
- Geocoding: OpenStreetMap Nominatim
- Visualization: Custom interactive map

## 📄 License

Data is for personal reference only. Please respect Tabelog's terms of service.
