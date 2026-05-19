#!/usr/bin/env python3
"""
Generate a curated list of famous Japanese tourist spots for the Hyakumeiten Nearby Finder.
These are well-known landmarks that tourists would recognize and search for.
"""
import json

SPOTS = [
    # ─── TOKYO ──────────────────────────────────────────────────────────────
    {"name": "Tokyo Skytree", "name_ja": "東京スカイツリー", "lat": 35.7101, "lng": 139.8107, "category": "tower", "emoji": "🗼"},
    {"name": "Tokyo Tower", "name_ja": "東京タワー", "lat": 35.6586, "lng": 139.7454, "category": "tower", "emoji": "🗼"},
    {"name": "Senso-ji Temple", "name_ja": "浅草寺", "lat": 35.7148, "lng": 139.7967, "category": "temple", "emoji": "⛩️"},
    {"name": "Meiji Shrine", "name_ja": "明治神宮", "lat": 35.6764, "lng": 139.6993, "category": "shrine", "emoji": "⛩️"},
    {"name": "Shinjuku Gyoen National Garden", "name_ja": "新宿御苑", "lat": 35.6852, "lng": 139.7100, "category": "garden", "emoji": "🌸"},
    {"name": "Shibuya Crossing", "name_ja": "渋谷スクランブル交差点", "lat": 35.6595, "lng": 139.7004, "category": "street", "emoji": "🛍️"},
    {"name": "Imperial Palace East Gardens", "name_ja": "皇居東御苑", "lat": 35.6852, "lng": 139.7572, "category": "garden", "emoji": "🌸"},
    {"name": "Ueno Park", "name_ja": "上野公園", "lat": 35.7148, "lng": 139.7739, "category": "park", "emoji": "🌳"},
    {"name": "Tsukiji Outer Market", "name_ja": "築地場外市場", "lat": 35.6654, "lng": 139.7707, "category": "market", "emoji": "🏪"},
    {"name": "TeamLab Planets TOKYO", "name_ja": "チームラボプラネッツ", "lat": 35.6471, "lng": 139.7897, "category": "museum", "emoji": "🏛️"},
    {"name": "Yasukuni Shrine", "name_ja": "靖国神社", "lat": 35.6940, "lng": 139.7435, "category": "shrine", "emoji": "⛩️"},
    {"name": "Rikugien Garden", "name_ja": "六義園", "lat": 35.7334, "lng": 139.7465, "category": "garden", "emoji": "🌸"},
    {"name": "Akihabara Electric Town", "name_ja": "秋葉原", "lat": 35.7022, "lng": 139.7744, "category": "street", "emoji": "🛍️"},
    {"name": "Harajuku / Takeshita Street", "name_ja": "竹下通り", "lat": 35.6702, "lng": 139.7027, "category": "street", "emoji": "🛍️"},
    {"name": "Ginza", "name_ja": "銀座", "lat": 35.6717, "lng": 139.7646, "category": "street", "emoji": "🛍️"},
    {"name": "Tokyo National Museum", "name_ja": "東京国立博物館", "lat": 35.7188, "lng": 139.7765, "category": "museum", "emoji": "🏛️"},
    {"name": "National Art Center Tokyo", "name_ja": "国立新美術館", "lat": 35.6657, "lng": 139.7272, "category": "museum", "emoji": "🏛️"},
    {"name": "Sumida Aquarium", "name_ja": "すみだ水族館", "lat": 35.7099, "lng": 139.8124, "category": "attraction", "emoji": "🐟"},
    {"name": "Odaiba / Statue of Liberty", "name_ja": "お台場", "lat": 35.6256, "lng": 139.7756, "category": "park", "emoji": "🌳"},
    {"name": "Tokyo Disneyland", "name_ja": "東京ディズニーランド", "lat": 35.6329, "lng": 139.8804, "category": "attraction", "emoji": "🏰"},
    {"name": "Tokyo DisneySea", "name_ja": "東京ディズニーシー", "lat": 35.6267, "lng": 139.8890, "category": "attraction", "emoji": "🏰"},
    {"name": "Zoji-ji Temple", "name_ja": "増上寺", "lat": 35.6573, "lng": 139.7484, "category": "temple", "emoji": "⛩️"},
    {"name": "Nezu Shrine", "name_ja": "根津神社", "lat": 35.7228, "lng": 139.7621, "category": "shrine", "emoji": "⛩️"},
    {"name": "Kanda Myojin Shrine", "name_ja": "神田明神", "lat": 35.7041, "lng": 139.7673, "category": "shrine", "emoji": "⛩️"},
    {"name": "Kiyosumi Garden", "name_ja": "清澄庭園", "lat": 35.6805, "lng": 139.7975, "category": "garden", "emoji": "🌸"},
    {"name": "Tokyo Metropolitan Government Building", "name_ja": "東京都庁展望室", "lat": 35.6896, "lng": 139.6917, "category": "tower", "emoji": "🗼"},
    {"name": "Rainbow Bridge", "name_ja": "レインボーブリッジ", "lat": 35.6375, "lng": 139.7592, "category": "other", "emoji": "🌉"},
    {"name": "Kototoi Bridge / Sumida River", "name_ja": "言問橋", "lat": 35.7167, "lng": 139.8026, "category": "other", "emoji": "🌉"},
    {"name": "Yanaka Ginza", "name_ja": "谷中銀座商店街", "lat": 35.7219, "lng": 139.7676, "category": "street", "emoji": "🛍️"},
    {"name": "Nakamise-dori (Asakusa)", "name_ja": "仲見世通り", "lat": 35.7125, "lng": 139.7953, "category": "street", "emoji": "🛍️"},
    {"name": "Hama-rikyu Gardens", "name_ja": "浜離宮恩賜庭園", "lat": 35.6596, "lng": 139.7628, "category": "garden", "emoji": "🌸"},

    # ─── KYOTO ──────────────────────────────────────────────────────────────
    {"name": "Fushimi Inari Taisha", "name_ja": "伏見稲荷大社", "lat": 34.9671, "lng": 135.7727, "category": "shrine", "emoji": "⛩️"},
    {"name": "Kinkaku-ji (Golden Pavilion)", "name_ja": "金閣寺", "lat": 35.0394, "lng": 135.7292, "category": "temple", "emoji": "⛩️"},
    {"name": "Ginkaku-ji (Silver Pavilion)", "name_ja": "銀閣寺", "lat": 35.0269, "lng": 135.7983, "category": "temple", "emoji": "⛩️"},
    {"name": "Arashiyama Bamboo Grove", "name_ja": "嵐山竹林の小道", "lat": 35.0170, "lng": 135.6719, "category": "nature", "emoji": "🎋"},
    {"name": "Kiyomizu-dera", "name_ja": "清水寺", "lat": 34.9949, "lng": 135.7850, "category": "temple", "emoji": "⛩️"},
    {"name": "Nijo Castle", "name_ja": "二条城", "lat": 35.0142, "lng": 135.7481, "category": "castle", "emoji": "🏯"},
    {"name": "Philosopher's Path", "name_ja": "哲学の道", "lat": 35.0217, "lng": 135.7947, "category": "street", "emoji": "🛍️"},
    {"name": "Gion District", "name_ja": "祇園", "lat": 35.0036, "lng": 135.7753, "category": "street", "emoji": "🛍️"},
    {"name": "Pontocho Alley", "name_ja": "先斗町", "lat": 35.0051, "lng": 135.7696, "category": "street", "emoji": "🛍️"},
    {"name": "Nishiki Market", "name_ja": "錦市場", "lat": 35.0050, "lng": 135.7648, "category": "market", "emoji": "🏪"},
    {"name": "To-ji Temple", "name_ja": "東寺", "lat": 34.9805, "lng": 135.7467, "category": "temple", "emoji": "⛩️"},
    {"name": "Sanjusangen-do", "name_ja": "三十三間堂", "lat": 34.9881, "lng": 135.7722, "category": "temple", "emoji": "⛩️"},
    {"name": "Kyoto Imperial Palace", "name_ja": "京都御所", "lat": 35.0254, "lng": 135.7621, "category": "castle", "emoji": "🏯"},
    {"name": "Tenryu-ji Temple", "name_ja": "天龍寺", "lat": 35.0158, "lng": 135.6739, "category": "temple", "emoji": "⛩️"},
    {"name": "Ryoan-ji Temple", "name_ja": "龍安寺", "lat": 35.0340, "lng": 135.7186, "category": "temple", "emoji": "⛩️"},

    # ─── OSAKA ──────────────────────────────────────────────────────────────
    {"name": "Osaka Castle", "name_ja": "大阪城", "lat": 34.6873, "lng": 135.5262, "category": "castle", "emoji": "🏯"},
    {"name": "Dotonbori", "name_ja": "道頓堀", "lat": 34.6686, "lng": 135.5023, "category": "street", "emoji": "🛍️"},
    {"name": "Shinsekai", "name_ja": "新世界", "lat": 34.6522, "lng": 135.5061, "category": "street", "emoji": "🛍️"},
    {"name": "Tsutenkaku Tower", "name_ja": "通天閣", "lat": 34.6522, "lng": 135.5063, "category": "tower", "emoji": "🗼"},
    {"name": "Sumiyoshi Taisha", "name_ja": "住吉大社", "lat": 34.6110, "lng": 135.4923, "category": "shrine", "emoji": "⛩️"},
    {"name": "Shitenno-ji Temple", "name_ja": "四天王寺", "lat": 34.6544, "lng": 135.5153, "category": "temple", "emoji": "⛩️"},
    {"name": "Kuromon Ichiba Market", "name_ja": "黒門市場", "lat": 34.6653, "lng": 135.5067, "category": "market", "emoji": "🏪"},
    {"name": "Universal Studios Japan", "name_ja": "ユニバーサル・スタジオ・ジャパン", "lat": 34.6655, "lng": 135.4321, "category": "attraction", "emoji": "🏰"},
    {"name": "Umeda Sky Building", "name_ja": "梅田スカイビル", "lat": 34.7053, "lng": 135.4901, "category": "tower", "emoji": "🗼"},
    {"name": "Osaka Aquarium Kaiyukan", "name_ja": "海遊館", "lat": 34.6550, "lng": 135.4298, "category": "attraction", "emoji": "🐟"},
    {"name": "Tennoji Park", "name_ja": "天王寺公園", "lat": 34.6505, "lng": 135.5136, "category": "park", "emoji": "🌳"},
    {"name": "Shinsaibashi", "name_ja": "心斎橋筋商店街", "lat": 34.6720, "lng": 135.5015, "category": "street", "emoji": "🛍️"},
    {"name": "Hozen-ji Yokocho", "name_ja": "法善寺横丁", "lat": 34.6680, "lng": 135.5035, "category": "street", "emoji": "🛍️"},

    # ─── NARA ───────────────────────────────────────────────────────────────
    {"name": "Nara Park", "name_ja": "奈良公園", "lat": 34.6851, "lng": 135.8431, "category": "park", "emoji": "🌳"},
    {"name": "Todai-ji Temple (Great Buddha)", "name_ja": "東大寺", "lat": 34.6890, "lng": 135.8398, "category": "temple", "emoji": "⛩️"},
    {"name": "Kasuga Taisha", "name_ja": "春日大社", "lat": 34.6814, "lng": 135.8484, "category": "shrine", "emoji": "⛩️"},
    {"name": "Kofuku-ji Temple", "name_ja": "興福寺", "lat": 34.6821, "lng": 135.8322, "category": "temple", "emoji": "⛩️"},

    # ─── HOKKAIDO ───────────────────────────────────────────────────────────
    {"name": "Odori Park", "name_ja": "大通公園", "lat": 43.0600, "lng": 141.3544, "category": "park", "emoji": "🌳"},
    {"name": "Sapporo TV Tower", "name_ja": "さっぽろテレビ塔", "lat": 43.0611, "lng": 141.3578, "category": "tower", "emoji": "🗼"},
    {"name": "Furano Lavender Fields", "name_ja": "富良野ラベンダー畑", "lat": 43.3472, "lng": 142.3968, "category": "nature", "emoji": "🌿"},
    {"name": "Lake Toya", "name_ja": "洞爺湖", "lat": 42.5781, "lng": 140.8115, "category": "nature", "emoji": "🌊"},
    {"name": "Hakodate Morning Market", "name_ja": "函館朝市", "lat": 41.7739, "lng": 140.7311, "category": "market", "emoji": "🏪"},
    {"name": "Mt. Hakodate Observatory", "name_ja": "函館山展望台", "lat": 41.7594, "lng": 140.7041, "category": "viewpoint", "emoji": "🌅"},
    {"name": "Goryokaku Park", "name_ja": "五稜郭公園", "lat": 41.7970, "lng": 140.7582, "category": "park", "emoji": "🌳"},
    {"name": "Blue Pond (Shirogane)", "name_ja": "青い池", "lat": 43.4294, "lng": 142.3673, "category": "nature", "emoji": "🌊"},
    {"name": "Shiroi Koibito Park", "name_ja": "白い恋人パーク", "lat": 43.0310, "lng": 141.2945, "category": "attraction", "emoji": "🏰"},
    {"name": "Sapporo Clock Tower", "name_ja": "札幌市時計台", "lat": 43.0638, "lng": 141.3553, "category": "other", "emoji": "🏛️"},
    {"name": "Nijo Market", "name_ja": "二条市場", "lat": 43.0556, "lng": 141.3321, "category": "market", "emoji": "🏪"},

    # ─── HIROSHIMA ──────────────────────────────────────────────────────────
    {"name": "Itsukushima Shrine (Miyajima)", "name_ja": "厳島神社", "lat": 34.2958, "lng": 132.3196, "category": "shrine", "emoji": "⛩️"},
    {"name": "Hiroshima Peace Memorial", "name_ja": "平和記念公園", "lat": 34.3956, "lng": 132.4536, "category": "park", "emoji": "🌳"},
    {"name": "Itsukushima Torii Gate", "name_ja": "厳島神社大鳥居", "lat": 34.2960, "lng": 132.3191, "category": "other", "emoji": "🌉"},
    {"name": "Hiroshima Castle", "name_ja": "広島城", "lat": 34.4024, "lng": 132.4593, "category": "castle", "emoji": "🏯"},
    {"name": "Mitaki-dera Temple", "name_ja": "三滝寺", "lat": 34.4127, "lng": 132.4328, "category": "temple", "emoji": "⛩️"},

    # ─── OKINAWA ────────────────────────────────────────────────────────────
    {"name": "Shuri Castle", "name_ja": "首里城", "lat": 26.2175, "lng": 127.7192, "category": "castle", "emoji": "🏯"},
    {"name": "Churaumi Aquarium", "name_ja": "美ら海水族館", "lat": 26.6945, "lng": 127.8790, "category": "attraction", "emoji": "🐟"},
    {"name": "Kokonoe Bridge / Kokusai Street", "name_ja": "国際通り", "lat": 26.2141, "lng": 127.6794, "category": "street", "emoji": "🛍️"},
    {"name": "Emerald Beach", "name_ja": "エメラルドビーチ", "lat": 26.6956, "lng": 127.8739, "category": "beach", "emoji": "🏖️"},
    {"name": "Cape Manzamo", "name_ja": "万座毛", "lat": 26.5499, "lng": 127.8264, "category": "nature", "emoji": "🌊"},
    {"name": "Nago Pineapple Park", "name_ja": "ネオパークオキナワ", "lat": 26.5528, "lng": 127.9534, "category": "attraction", "emoji": "🏰"},

    # ─── KANAGAWA ───────────────────────────────────────────────────────────
    {"name": "Great Buddha of Kamakura", "name_ja": "鎌倉大仏", "lat": 35.3167, "lng": 139.5357, "category": "temple", "emoji": "⛩️"},
    {"name": "Tsurugaoka Hachimangu", "name_ja": "鶴岡八幡宮", "lat": 35.3260, "lng": 139.5560, "category": "shrine", "emoji": "⛩️"},
    {"name": "Hakone Shrine", "name_ja": "箱根神社", "lat": 35.2041, "lng": 139.0346, "category": "shrine", "emoji": "⛩️"},
    {"name": "Lake Ashi (Hakone)", "name_ja": "芦ノ湖", "lat": 35.2131, "lng": 139.0268, "category": "nature", "emoji": "🌊"},
    {"name": "Owaku-dani", "name_ja": "大涌谷", "lat": 35.2432, "lng": 139.0177, "category": "nature", "emoji": "🌋"},
    {"name": "Kamakura Komachi Street", "name_ja": "小町通り", "lat": 35.3188, "lng": 139.5517, "category": "street", "emoji": "🛍️"},
    {"name": "Yokohama Chinatown", "name_ja": "横浜中華街", "lat": 35.4435, "lng": 139.6498, "category": "street", "emoji": "🛍️"},
    {"name": "Minato Mirai 21", "name_ja": "みなとみらい", "lat": 35.4548, "lng": 139.6313, "category": "street", "emoji": "🛍️"},
    {"name": "Yokohama Landmark Tower", "name_ja": "ランドマークタワー", "lat": 35.4548, "lng": 139.6317, "category": "tower", "emoji": "🗼"},
    {"name": "Enoshima Island", "name_ja": "江の島", "lat": 35.2999, "lng": 139.4800, "category": "nature", "emoji": "🌊"},
    {"name": "Enoshima Shrine", "name_ja": "江島神社", "lat": 35.2986, "lng": 139.4814, "category": "shrine", "emoji": "⛩️"},
    {"name": "Hase-dera Temple", "name_ja": "長谷寺", "lat": 35.3122, "lng": 139.5327, "category": "temple", "emoji": "⛩️"},
    {"name": "Sankeien Garden", "name_ja": "三溪園", "lat": 35.4260, "lng": 139.6244, "category": "garden", "emoji": "🌸"},
    {"name": "Cupnoodles Museum Yokohama", "name_ja": "カップヌードルミュージアム", "lat": 35.4577, "lng": 139.6318, "category": "museum", "emoji": "🏛️"},

    # ─── NAGOYA / AICHI ─────────────────────────────────────────────────────
    {"name": "Nagoya Castle", "name_ja": "名古屋城", "lat": 35.1856, "lng": 136.8998, "category": "castle", "emoji": "🏯"},
    {"name": "Atsuta Shrine", "name_ja": "熱田神宮", "lat": 35.1288, "lng": 136.9106, "category": "shrine", "emoji": "⛩️"},
    {"name": "SCMAGLEV and Railway Park", "name_ja": "リニア・鉄道館", "lat": 35.0994, "lng": 136.8553, "category": "museum", "emoji": "🏛️"},
    {"name": "Osu Shopping Street", "name_ja": "大須商店街", "lat": 35.1615, "lng": 136.9020, "category": "street", "emoji": "🛍️"},
    {"name": "Toyota Commemorative Museum", "name_ja": "トヨタ産業技術記念館", "lat": 35.1816, "lng": 136.8763, "category": "museum", "emoji": "🏛️"},
    {"name": "Nabana no Sato", "name_ja": "なばなの里", "lat": 35.0800, "lng": 136.7065, "category": "attraction", "emoji": "🌸"},

    # ─── FUKUOKA ────────────────────────────────────────────────────────────
    {"name": "Dazaifu Tenmangu", "name_ja": "太宰府天満宮", "lat": 33.5159, "lng": 130.5317, "category": "shrine", "emoji": "⛩️"},
    {"name": "Canal City Hakata", "name_ja": "キャナルシティ博多", "lat": 33.5902, "lng": 130.4119, "category": "street", "emoji": "🛍️"},
    {"name": "Fukuoka Tower", "name_ja": "福岡タワー", "lat": 33.5936, "lng": 130.3598, "category": "tower", "emoji": "🗼"},
    {"name": "Ohori Park", "name_ja": "大濠公園", "lat": 33.5903, "lng": 130.3772, "category": "park", "emoji": "🌳"},
    {"name": "Kushida Shrine", "name_ja": "櫛田神社", "lat": 33.5910, "lng": 130.4048, "category": "shrine", "emoji": "⛩️"},
    {"name": "Yanagawa River", "name_ja": "柳川", "lat": 33.2190, "lng": 130.4100, "category": "nature", "emoji": "🌊"},
    {"name": "Itoshima Sunset Beach", "name_ja": "糸島", "lat": 33.5080, "lng": 130.1945, "category": "beach", "emoji": "🏖️"},

    # ─── KYUSHU ─────────────────────────────────────────────────────────────
    {"name": "Aso Volcano", "name_ja": "阿蘇山", "lat": 32.8844, "lng": 131.1090, "category": "nature", "emoji": "🌋"},
    {"name": "Kumamoto Castle", "name_ja": "熊本城", "lat": 32.8061, "lng": 130.7076, "category": "castle", "emoji": "🏯"},
    {"name": "Huis Ten Bosch", "name_ja": "ハウステンボス", "lat": 33.0847, "lng": 129.8667, "category": "attraction", "emoji": "🏰"},
    {"name": "Beppu Hot Springs", "name_ja": "別府温泉", "lat": 33.2833, "lng": 131.4908, "category": "nature", "emoji": "♨️"},
    {"name": "Kagoshima Sengan-en", "name_ja": "仙巌園", "lat": 31.6095, "lng": 130.5086, "category": "garden", "emoji": "🌸"},
    {"name": "Sakurajima", "name_ja": "桜島", "lat": 31.5855, "lng": 130.6568, "category": "nature", "emoji": "🌋"},
    {"name": "Yakushima (Jomon Sugi)", "name_ja": "屋久島・縄文杉", "lat": 30.3531, "lng": 130.5069, "category": "nature", "emoji": "🌿"},
    {"name": "Yufuin Onsen", "name_ja": "由布院温泉", "lat": 33.2676, "lng": 131.3689, "category": "nature", "emoji": "♨️"},

    # ─── CHUBU / ALPS ──────────────────────────────────────────────────────
    {"name": "Shirakawa-go", "name_ja": "白川郷", "lat": 36.2567, "lng": 136.9060, "category": "nature", "emoji": "🏘️"},
    {"name": "Takayama Old Town", "name_ja": "高山三町", "lat": 36.1412, "lng": 137.2522, "category": "street", "emoji": "🛍️"},
    {"name": "Kamikochi", "name_ja": "上高地", "lat": 36.2489, "lng": 137.6360, "category": "nature", "emoji": "🏔️"},
    {"name": "Matsumoto Castle", "name_ja": "松本城", "lat": 36.2383, "lng": 137.9695, "category": "castle", "emoji": "🏯"},
    {"name": "Kanazawa Kenrokuen Garden", "name_ja": "兼六園", "lat": 36.5619, "lng": 136.6627, "category": "garden", "emoji": "🌸"},
    {"name": "Kanazawa Castle", "name_ja": "金沢城", "lat": 36.5649, "lng": 136.6581, "category": "castle", "emoji": "🏯"},
    {"name": "Higashi Chaya (Kanazawa)", "name_ja": "ひがし茶屋街", "lat": 36.5678, "lng": 136.6654, "category": "street", "emoji": "🛍️"},
    {"name": "Myoko Kogen", "name_ja": "妙高高原", "lat": 36.9034, "lng": 138.1505, "category": "nature", "emoji": "🏔️"},
    {"name": "Jigokudani Monkey Park", "name_ja": "地獄谷野猿公苑", "lat": 36.7839, "lng": 138.4903, "category": "nature", "emoji": "🐒"},
    {"name": "Tateyama Kurobe Alpine Route", "name_ja": "立山黒部アルペンルート", "lat": 36.5460, "lng": 137.6000, "category": "nature", "emoji": "🏔️"},

    # ─── TOHOKU ─────────────────────────────────────────────────────────────
    {"name": "Hirosaki Castle", "name_ja": "弘前城", "lat": 40.6094, "lng": 140.4610, "category": "castle", "emoji": "🏯"},
    {"name": "Zao Fox Village", "name_ja": "蔵王きつね村", "lat": 38.0786, "lng": 140.7137, "category": "nature", "emoji": "🦊"},
    {"name": "Chuson-ji Temple", "name_ja": "中尊寺", "lat": 38.9852, "lng": 141.1098, "category": "temple", "emoji": "⛩️"},
    {"name": "Matsushima Bay", "name_ja": "松島", "lat": 38.3550, "lng": 141.0715, "category": "nature", "emoji": "🌊"},
    {"name": "Goshogawara Tachineputa Museum", "name_ja": "ねぶたの家 ワ・ラッセ", "lat": 40.8110, "lng": 140.7221, "category": "museum", "emoji": "🏛️"},
    {"name": "Nyuto Onsen", "name_ja": "乳頭温泉郷", "lat": 39.7142, "lng": 140.6567, "category": "nature", "emoji": "♨️"},
    {"name": "Oirase Stream", "name_ja": "奥入瀬渓流", "lat": 40.5929, "lng": 140.9477, "category": "nature", "emoji": "🌿"},
    {"name": "Yamadera Temple", "name_ja": "山寺（立石寺）", "lat": 38.3350, "lng": 140.2582, "category": "temple", "emoji": "⛩️"},
    {"name": "Zao Onsen", "name_ja": "蔵王温泉", "lat": 38.1480, "lng": 140.4417, "category": "nature", "emoji": "♨️"},
    {"name": "Zao Snow Monsters", "name_ja": "蔵王の樹氷", "lat": 38.1703, "lng": 140.4311, "category": "nature", "emoji": "🌨️"},

    # ─── CHUGOKU ────────────────────────────────────────────────────────────
    {"name": "Okayama Korakuen Garden", "name_ja": "後楽園", "lat": 34.6646, "lng": 133.9358, "category": "garden", "emoji": "🌸"},
    {"name": "Okayama Castle", "name_ja": "岡山城", "lat": 34.6619, "lng": 133.9338, "category": "castle", "emoji": "🏯"},
    {"name": "Kurashiki Bikan", "name_ja": "倉敷美観地区", "lat": 34.5840, "lng": 133.7690, "category": "street", "emoji": "🛍️"},
    {"name": "Izumo Taisha", "name_ja": "出雲大社", "lat": 35.3957, "lng": 132.6864, "category": "shrine", "emoji": "⛩️"},
    {"name": "Adachi Museum Garden", "name_ja": "足立美術館", "lat": 35.4920, "lng": 133.0644, "category": "garden", "emoji": "🌸"},
    {"name": "Tottori Sand Dunes", "name_ja": "鳥取砂丘", "lat": 35.5370, "lng": 134.2151, "category": "nature", "emoji": "🏜️"},

    # ─── SHIKOKU ────────────────────────────────────────────────────────────
    {"name": "Ritsurin Garden", "name_ja": "栗林公園", "lat": 34.3193, "lng": 134.0454, "category": "garden", "emoji": "🌸"},
    {"name": "Konpira-san (Kotohira-gu)", "name_ja": "金刀比羅宮", "lat": 34.1650, "lng": 133.8045, "category": "shrine", "emoji": "⛩️"},
    {"name": "Dogo Onsen", "name_ja": "道後温泉", "lat": 33.8444, "lng": 132.7917, "category": "nature", "emoji": "♨️"},
    {"name": "Naruto Whirlpools", "name_ja": "鳴門の渦潮", "lat": 34.2259, "lng": 134.6200, "category": "nature", "emoji": "🌊"},
    {"name": "Iya Valley Kazurabashi", "name_ja": "祖谷のかずら橋", "lat": 33.8454, "lng": 133.8145, "category": "nature", "emoji": "🌉"},

    # ─── MT. FUJI AREA ──────────────────────────────────────────────────────
    {"name": "Mt. Fuji 5th Station", "name_ja": "富士山五合目", "lat": 35.3606, "lng": 138.7310, "category": "viewpoint", "emoji": "🗻"},
    {"name": "Chureito Pagoda", "name_ja": "忠霊塔", "lat": 35.5019, "lng": 138.8007, "category": "temple", "emoji": "⛩️"},
    {"name": "Lake Kawaguchi", "name_ja": "河口湖", "lat": 35.5000, "lng": 138.7640, "category": "nature", "emoji": "🌊"},
    {"name": "Fuji-Q Highland", "name_ja": "富士急ハイランド", "lat": 35.4835, "lng": 138.7814, "category": "attraction", "emoji": "🏰"},
    {"name": "Oshino Hakkai", "name_ja": "忍野八海", "lat": 35.4783, "lng": 138.8439, "category": "nature", "emoji": "🌊"},
    {"name": "Arakurayama Sengen Park", "name_ja": "新倉山浅間公園", "lat": 35.5025, "lng": 138.8013, "category": "park", "emoji": "🌸"},

    # ─── OTHER FAMOUS ───────────────────────────────────────────────────────
    {"name": "Nagasaki Peace Park", "name_ja": "長崎平和公園", "lat": 32.7747, "lng": 129.8739, "category": "park", "emoji": "🌳"},
    {"name": "Glover Garden (Nagasaki)", "name_ja": "グラバー園", "lat": 32.7389, "lng": 129.8729, "category": "garden", "emoji": "🌸"},
    {"name": "Kanazawa 21st Century Museum", "name_ja": "金沢21世紀美術館", "lat": 36.5595, "lng": 136.6560, "category": "museum", "emoji": "🏛️"},
    {"name": "Osaka Museum of Housing and Living", "name_ja": "くらしの今昔館", "lat": 34.6974, "lng": 135.5125, "category": "museum", "emoji": "🏛️"},
    {"name": "Ghibli Museum", "name_ja": "三鷹の森ジブリ美術館", "lat": 35.6961, "lng": 139.5704, "category": "museum", "emoji": "🏛️"},
    {"name": "teamLab Borderless", "name_ja": "チームラボボーダレス", "lat": 35.6257, "lng": 139.7758, "category": "museum", "emoji": "🏛️"},
]

def main():
    # Remove duplicates by name
    seen = set()
    unique = []
    for spot in SPOTS:
        if spot["name"] not in seen:
            seen.add(spot["name"])
            unique.append(spot)
    
    # Category counts
    cats = {}
    for s in unique:
        cats[s["category"]] = cats.get(s["category"], 0) + 1
    
    print(f"Total spots: {len(unique)}")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    # Save
    with open("data/scenic_spots_famous.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved to data/scenic_spots_famous.json")

if __name__ == "__main__":
    main()
