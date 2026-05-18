// ============================================================
// Hyakumeiten Nearby Finder - Main Application
// ============================================================

// --- Internationalization ---
const i18n = {
    ja: {
        subtitle: "食べログ百名店をあなたの近くで探そう",
        findNearMe: "近くの名店を探す",
        allGenres: "すべてのジャンル",
        radius: "範囲：",
        searchPlaceholder: "店名で検索...",
        searchAddressPlaceholder: "住所・都市名で検索...",
        searchingAddress: "検索中...",
        addressNotFound: "場所が見つかりませんでした",
        footer: "データ提供：食べログ百名店 2026 | 地図：OpenStreetMap",
        resultsCount: "件が見つかりました",
        noResults: "該当する店舗が見つかりませんでした",
        noLocation: "位置情報を許可して「近くの名店を探す」ボタンを押してください",
        distance: "約{dist}km",
        directions: "🗺️ 案内",
        tabelog: "📋 食べログ",
        holiday: "定休日",
        phone: "電話",
        budget: "予算",
        seats: "席数",
        address: "住所",
        station: "最寄駅",
        walk: "徒歩{min}分",
        singleResult: "{name} ({genre}) — 選択中",
        genres: {
            "ラーメン": "ラーメン",
            "中国料理": "中国料理",
            "焼肉": "焼肉",
            "イタリアン": "イタリアン",
            "寿司": "寿司",
            "カレー": "カレー",
            "アジア・エスニック": "エスニック",
            "うどん": "うどん",
            "和菓子・甘味処": "和菓子",
            "フレンチ": "フレンチ",
            "パン": "パン",
            "日本料理": "日本料理",
            "スイーツ": "スイーツ",
            "焼き鳥": "焼き鳥",
            "居酒屋": "居酒屋",
            "ステーキ": "ステーキ",
            "洋食": "洋食",
            "カフェ": "カフェ",
            "そば": "そば",
            "食堂": "食堂",
            "スペイン料理": "スペイン料理",
            "ハンバーガー": "ハンバーガー",
            "とんかつ": "とんかつ",
            "鳥料理": "鳥料理",
            "バー": "バー",
            "創作料理・イノベーティブ": "創作料理",
            "ピザ": "ピザ",
            "天ぷら": "天ぷら",
            "すき焼き・しゃぶしゃぶ": "すき焼き・しゃぶしゃぶ",
            "うなぎ": "うなぎ",
            "餃子": "餃子",
            "アイス・ジェラート": "ジェラート",
            "立ち飲み": "立ち飲み",
            "お好み焼き": "お好み焼き",
            "喫茶": "喫茶"
        }
    },
    en: {
        subtitle: "Find Tabelog Hyakumeiten restaurants near you",
        findNearMe: "📍 Find near me",
        allGenres: "All genres",
        radius: "Radius:",
        searchPlaceholder: "Search by name...",
        searchAddressPlaceholder: "Search address or city name...",
        searchingAddress: "Searching...",
        addressNotFound: "Location not found. Please try again.",
        footer: "Data: Tabelog Hyakumeiten 2026 | Maps: OpenStreetMap",
        resultsCount: "restaurants found",
        noResults: "No restaurants found matching your criteria",
        noLocation: "Please enable location services and click 'Find near me'",
        distance: "~{dist}km away",
        directions: "🗺️ Directions",
        tabelog: "📋 Tabelog",
        holiday: "Closed",
        phone: "Phone",
        budget: "Budget",
        seats: "Seats",
        address: "Address",
        station: "Nearest station",
        walk: "{min} min walk",
        singleResult: "{name} ({genre}) — Selected",
        genres: {
            "ラーメン": "Ramen",
            "中国料理": "Chinese",
            "焼肉": "Yakiniku",
            "イタリアン": "Italian",
            "寿司": "Sushi",
            "カレー": "Curry",
            "アジア・エスニック": "Asian/Ethnic",
            "うどん": "Udon",
            "和菓子・甘味処": "Wagashi/Sweets",
            "フレンチ": "French",
            "パン": "Bakery",
            "日本料理": "Japanese",
            "スイーツ": "Sweets",
            "焼き鳥": "Yakitori",
            "居酒屋": "Izakaya",
            "ステーキ": "Steak",
            "洋食": "Western",
            "カフェ": "Cafe",
            "そば": "Soba",
            "食堂": "Diner",
            "スペイン料理": "Spanish",
            "ハンバーガー": "Burger",
            "とんかつ": "Tonkatsu",
            "鳥料理": "Chicken",
            "バー": "Bar",
            "創作料理・イノベーティブ": "Creative",
            "ピザ": "Pizza",
            "天ぷら": "Tempura",
            "すき焼き・しゃぶしゃぶ": "Sukiyaki/Shabu-shabu",
            "うなぎ": "Eel",
            "餃子": "Gyoza",
            "アイス・ジェラート": "Ice Cream/Gelato",
            "立ち飲み": "Standing Bar",
            "お好み焼き": "Okonomiyaki",
            "喫茶": "Kissaten"
        }
    }
};

let currentLang = 'ja';

function t(key) {
    const lang = i18n[currentLang];
    if (key.startsWith('genres.')) {
        const genre = key.replace('genres.', '');
        return lang.genres[genre] || genre;
    }
    return lang[key] || key;
}

function applyI18n() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.textContent = t(key);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        el.placeholder = t(key);
    });
    const genreSelect = document.getElementById('genre-filter');
    const currentVal = genreSelect.value;
    populateGenreFilter();
    genreSelect.value = currentVal;
    renderResults(filteredRestaurants);
}

// --- Data normalization (compressed keys → full names) ---
function normalizeRecord(r) {
    return {
        id: r.id,
        name: r.n,
        area: r.a,
        genre: r.g,
        tabelog_url: r.u,
        image_url: r.i || '',
        lat: r.la,
        lng: r.lo,
        holiday: r.h || null,
        rating: r.r || null,
        review_count: r.c || 0,
        budget_lunch: r.bl || null,
        budget_dinner: r.bd || null,
        phone: r.p || null,
        seats: r.s || null,
        address: r.addr || null,
        station_name: r.st || null,
        is_new: r.nw || false,
        sub_genres: r.sg || null,
    };
}

// --- Data ---
let allRestaurants = [];
let filteredRestaurants = [];
let userLat = null;
let userLng = null;

// --- Interaction State ---
let selectedRestaurant = null;  // When a marker is clicked
let clickedAreaLocation = null;  // When map background is clicked
let viewportBounds = null;       // Current map visible bounds
let viewportFilterActive = false; // Whether to filter by visible bounds

// --- Haversine Distance ---
function haversine(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) ** 2 +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

// --- Debounce ---
function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// --- Map ---
let map;
let markers = [];
let userMarker = null;
let selectedMarker = null; // Highlight ring for selected restaurant
let debouncedApplyFilters; // Module-level for searchAddress access

function initMap() {
    map = L.map('map', { preferCanvas: true }).setView([35.6762, 139.6503], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // B: Map move/zoom events → update restaurant list (debounced)
    debouncedApplyFilters = debounce(() => {
        viewportBounds = map.getBounds();
        viewportFilterActive = true;
        clickedAreaLocation = null;
        applyFilters();
    }, 300);
    map.on('moveend zoomend', debouncedApplyFilters);

    // A: Click map background → deselect single restaurant, filter by same genre in area
    map.on('click', (e) => {
        // If a restaurant was selected, clicking map shows same-genre in that area
        if (selectedRestaurant) {
            clickedAreaLocation = { lat: e.latlng.lat, lng: e.latlng.lng };
            // Keep the genre of the previously selected restaurant
            selectedRestaurant = null;
            clearSelectedMarker();
            applyFilters();
        } else {
            // Not selecting anything, just clear selection
            selectedRestaurant = null;
            clearSelectedMarker();
            clickedAreaLocation = { lat: e.latlng.lat, lng: e.latlng.lng };
            applyFilters();
        }
    });
}

function clearMarkers() {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
}

function clearSelectedMarker() {
    if (selectedMarker) {
        map.removeLayer(selectedMarker);
        selectedMarker = null;
    }
}

function addMarkers(restaurants, highlightId) {
    clearMarkers();
    clearSelectedMarker();

    // Don't show markers at very low zoom (too many restaurants, map hangs)
    const currentZoom = map.getZoom();
    if (currentZoom < 10) {
        const statusBar = document.getElementById('status-bar');
        const count = restaurants.length;
        statusBar.textContent = `📍 ${count} restaurants. Zoom in to see markers on map (zoom 10+).`;
        return;
    }

    const bounds = L.latLngBounds();
    let count = 0;
    // Strict limit: keep DOM markers low for smooth panning
    const MAX_MARKERS = 50;

    for (const r of restaurants) {
        if (!r.lat || !r.lng) continue;

        const isHighlight = highlightId && r.id === highlightId;

        // Restore proper arrow/teardrop pins
        let icon;
        if (isHighlight) {
            icon = L.divIcon({
                className: 'restaurant-marker highlighted',
                html: '<div class="marker-pin highlighted"></div>',
                iconSize: [30, 42],
                iconAnchor: [15, 42],
                popupAnchor: [0, -42]
            });
        } else {
            icon = L.divIcon({
                className: 'restaurant-marker',
                html: '<div class="marker-pin"></div>',
                iconSize: [25, 35],
                iconAnchor: [12.5, 35],
                popupAnchor: [0, -35]
            });
        }

        const genreLabel = t(`genres.${r.genre}`);
        const popupContent = `
            <div class="marker-popup">
                <b>${r.name}</b><br>
                <span class="popup-genre">${genreLabel}</span><br>
                ${r.rating ? `⭐ ${r.rating}` : ''}
            </div>
        `;

        const marker = L.marker([r.lat, r.lng], { icon })
            .addTo(map)
            .bindPopup(popupContent);

        marker.on('click', () => {
            selectedRestaurant = r;
            clearSelectedMarker();
            selectedMarker = L.circleMarker([r.lat, r.lng], {
                radius: 18,
                color: '#ff6b35',
                weight: 3,
                fillColor: '#ff6b35',
                fillOpacity: 0.2
            }).addTo(map);
            filteredRestaurants = [r];
            renderResults([r]);
            viewportFilterActive = false;
        });

        markers.push(marker);
        bounds.extend([r.lat, r.lng]);
        count++;

        if (count >= MAX_MARKERS) break;
    }

    // Status message
    const statusBar = document.getElementById('status-bar');
    if (restaurants.length > MAX_MARKERS) {
        statusBar.textContent = `📍 Showing ${count} of ${restaurants.length} restaurants. Zoom in or filter to see more.`;
    }

    // Only auto-fit bounds if marker set is small and clustered (not spread across a whole city)
    if (!selectedRestaurant && count > 0 && count < MAX_MARKERS && currentZoom >= 12) {
        try {
            map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
        } catch(e) {
            // Ignore fitBounds errors with single point
        }
    }
}

function updateUserMarker(lat, lng) {
    if (userMarker) map.removeLayer(userMarker);

    const userIcon = L.divIcon({
        className: 'user-marker',
        html: '<div style="background:#2196F3;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 0 8px rgba(33,150,243,0.6)"></div>',
        iconSize: [16, 16]
    });
    userMarker = L.marker([lat, lng], { icon: userIcon })
        .addTo(map)
        .bindPopup('📍 You are here');
    map.setView([lat, lng], 12);
}

// --- Genre Filter ---
function populateGenreFilter() {
    const select = document.getElementById('genre-filter');
    select.innerHTML = `<option value="">${t('allGenres')}</option>`;

    const genreCounts = {};
    for (const r of allRestaurants) {
        genreCounts[r.genre] = (genreCounts[r.genre] || 0) + 1;
    }

    for (const [genre, count] of Object.entries(genreCounts).sort((a, b) => b[1] - a[1])) {
        const label = t(`genres.${genre}`);
        const opt = document.createElement('option');
        opt.value = genre;
        opt.textContent = `${label} (${count})`;
        select.appendChild(opt);
    }
}

// --- Filtering ---
function applyFilters() {
    const genre = document.getElementById('genre-filter').value;
    const search = document.getElementById('search-input').value.toLowerCase();
    const radius = parseInt(document.getElementById('radius-slider').value);

    // A: If a single restaurant is selected, show only it
    if (selectedRestaurant) {
        filteredRestaurants = [selectedRestaurant];
        renderResults([selectedRestaurant]);
        return;
    }

    let results = allRestaurants;

    // B: Filter by visible map bounds
    if (viewportFilterActive && viewportBounds) {
        results = results.filter(r => {
            if (!r.lat || !r.lng) return false;
            return viewportBounds.contains([r.lat, r.lng]);
        });
    }

    // Genre filter
    if (genre) {
        results = results.filter(r => r.genre === genre);
    }

    // Search filter (name)
    if (search) {
        results = results.filter(r =>
            r.name.toLowerCase().includes(search) ||
            (r.area && r.area.toLowerCase().includes(search)) ||
            (r.sub_genres && r.sub_genres.some(s => s.includes(search)))
        );
    }

    // Distance filter (if user location known)
    if (userLat && userLng) {
        results = results
            .map(r => ({
                ...r,
                distance: haversine(userLat, userLng, r.lat, r.lng)
            }))
            .filter(r => r.distance <= radius)
            .sort((a, b) => a.distance - b.distance);
    }

    filteredRestaurants = results;
    renderResults(results);

    // Update markers
    if (results.length > 0 && results.some(r => r.lat && r.lng)) {
        addMarkers(results);
    } else {
        clearMarkers();
    }
}

// --- Rendering ---
function renderResults(restaurants) {
    const container = document.getElementById('results');
    const countEl = document.getElementById('results-count');

    // A: Single restaurant selected
    if (selectedRestaurant) {
        const genreLabel = t(`genres.${selectedRestaurant.genre}`);
        countEl.textContent = t('singleResult')
            .replace('{name}', selectedRestaurant.name)
            .replace('{genre}', genreLabel);
    } else {
        countEl.textContent = `${restaurants.length} ${t('resultsCount')}`;
    }

    if (restaurants.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">🍽️</div>
                <p>${t('noResults')}</p>
            </div>
        `;
        return;
    }

    container.innerHTML = restaurants.slice(0, 50).map(r => {
        const genreLabel = t(`genres.${r.genre}`);
        const distanceStr = r.distance !== undefined ?
            `<div class="card-distance">📍 ${t('distance').replace('{dist}', r.distance.toFixed(1))}</div>` : '';

        const tags = [];
        if (r.budget_lunch) tags.push(r.budget_lunch);
        if (r.budget_dinner) tags.push(r.budget_dinner);
        if (r.seats) tags.push(`${r.seats}席`);
        if (r.holiday) tags.push(`${t('holiday')}: ${r.holiday}`);

        const badges = [];
        if (r.is_new) badges.push('<span class="card-badge">初選出</span>');
        if (r.rating) badges.push(`<span class="card-rating"><span class="score">⭐ ${r.rating}</span><span class="count">(${r.review_count || 0})</span></span>`);

        const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${r.lat},${r.lng}`;

        return `
            <div class="restaurant-card" data-id="${r.id}">
                <div class="card-header">
                    <img class="card-image" src="${r.image_url || ''}" alt="${r.name}" loading="lazy" onerror="this.style.display='none'">
                    <div class="card-info">
                        <h3>${r.name} ${badges.join('')}</h3>
                        <div class="card-meta">${genreLabel} · ${r.area || ''}</div>
                        ${distanceStr}
                    </div>
                </div>
                <div class="card-body">
                    ${tags.length > 0 ? `<div class="card-tags">${tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
                    <div class="card-actions">
                        <a href="${r.tabelog_url}" target="_blank" rel="noopener">${t('tabelog')}</a>
                        ${r.lat && r.lng ? `<a href="${directionsUrl}" target="_blank" rel="noopener">${t('directions')}</a>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    if (restaurants.length > 50) {
        container.innerHTML += `<div style="text-align:center;padding:20px;color:var(--text-secondary)">
            +${restaurants.length - 50} ${t('resultsCount')}
        </div>`;
    }

    // Click card → pan map to restaurant and select it
    container.querySelectorAll('.restaurant-card').forEach(card => {
        card.addEventListener('click', (e) => {
            // Don't select if clicking a link
            if (e.target.tagName === 'A') return;
            const id = card.dataset.id;
            const r = allRestaurants.find(x => x.id === id);
            if (r) {
                map.setView([r.lat, r.lng], 15);
                selectedRestaurant = r;
                clearSelectedMarker();
                selectedMarker = L.circleMarker([r.lat, r.lng], {
                    radius: 18,
                    color: '#ff6b35',
                    weight: 3,
                    fillColor: '#ff6b35',
                    fillOpacity: 0.2
                }).addTo(map);
                filteredRestaurants = [r];
                renderResults([r]);
                viewportFilterActive = false;
                // Also show the popup on the matching marker
                markers.forEach(m => {
                    const lat = m.getLatLng();
                    if (Math.abs(lat.lat - r.lat) < 0.0001 && Math.abs(lat.lng - r.lng) < 0.0001) {
                        m.openPopup();
                    }
                });
            }
        });
    });
}

// --- Geolocation ---
function geolocate() {
    const statusBar = document.getElementById('status-bar');
    statusBar.textContent = '位置情報取得中...';

    if (!navigator.geolocation) {
        statusBar.textContent = 'お使いのブラウザは位置情報をサポートしていません';
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            userLat = pos.coords.latitude;
            userLng = pos.coords.longitude;
            statusBar.textContent = `📍 現在地: ${userLat.toFixed(4)}, ${userLng.toFixed(4)}`;
            // Reset map-based filters when using geolocation
            clickedAreaLocation = null;
            viewportFilterActive = false;
            selectedRestaurant = null;
            clearSelectedMarker();
            updateUserMarker(userLat, userLng);
            applyFilters();
        },
        (err) => {
            statusBar.textContent = `❌ ${t('noLocation')} (${err.message})`;
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}

// --- C: Address/City Search via Nominatim ---
async function searchAddress() {
    const input = document.getElementById('address-search');
    const query = input.value.trim();
    const statusBar = document.getElementById('status-bar');

    if (!query) return;

    statusBar.textContent = t('searchingAddress');

    try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1&addressdetails=1&accept-language=ja,en`;
        const resp = await fetch(url, {
            headers: { 'User-Agent': 'HyakumeitenNearbyFinder/1.0' }
        });
        const data = await resp.json();

        if (data.length === 0) {
            statusBar.textContent = t('addressNotFound');
            return;
        }

        const result = data[0];
        const lat = parseFloat(result.lat);
        const lng = parseFloat(result.lon);

        // Reset filters
        selectedRestaurant = null;
        clearSelectedMarker();
        clickedAreaLocation = { lat, lng };
        userLat = null;
        userLng = null;
        if (userMarker) map.removeLayer(userMarker);

        // Move map WITHOUT triggering moveend handler — temporarily remove listener
        map.off('moveend zoomend');
        map.setView([lat, lng], 13);
        viewportBounds = map.getBounds();
        viewportFilterActive = true;  // Enable viewport filter so we don't process all 3000+
        map.on('moveend zoomend', debouncedApplyFilters);

        statusBar.textContent = `📍 ${result.display_name}`;

        // Add a temporary marker for the searched location
        L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'search-marker',
                html: '<div style="background:#ff6b35;width:14px;height:14px;border-radius:50%;border:3px solid white;box-shadow:0 0 8px rgba(255,107,53,0.6)"></div>',
                iconSize: [14, 14]
            })
        }).addTo(map).bindPopup(`📍 ${query}`).openPopup();

        applyFilters();
    } catch (err) {
        statusBar.textContent = `❌ ${t('addressNotFound')}: ${err.message}`;
    }
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    const statusBar = document.getElementById('status-bar');
    statusBar.textContent = '⏳ データ読み込み中...';

    // Load data
    if (typeof HYAKUMEITEN_DATA !== 'undefined') {
        allRestaurants = HYAKUMEITEN_DATA.map(normalizeRecord);
        statusBar.textContent = `✅ ${allRestaurants.length}件の百名店データ読み込み完了`;
    } else {
        // Fallback: load from data.json
        fetch('data.json')
            .then(r => r.json())
            .then(data => {
                allRestaurants = data.map(normalizeRecord);
                statusBar.textContent = `✅ ${allRestaurants.length}件の百名店データ読み込み完了`;
                populateGenreFilter();
                applyFilters();
            })
            .catch(() => {
                statusBar.textContent = '❌ データ読み込みに失敗しました';
            });
        return;
    }

    populateGenreFilter();
    applyFilters();

    // Event listeners
    document.getElementById('geolocate-btn').addEventListener('click', geolocate);
    document.getElementById('genre-filter').addEventListener('change', applyFilters);
    document.getElementById('radius-slider').addEventListener('input', (e) => {
        document.getElementById('radius-value').textContent = e.target.value;
        applyFilters();
    });
    document.getElementById('search-input').addEventListener('input', applyFilters);

    // C: Address search
    document.getElementById('address-search').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') searchAddress();
    });

    // Language toggle
    document.getElementById('lang-toggle').addEventListener('click', () => {
        currentLang = currentLang === 'ja' ? 'en' : 'ja';
        document.documentElement.lang = currentLang;
        applyI18n();
    });
});
