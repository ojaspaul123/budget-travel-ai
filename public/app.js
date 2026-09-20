/**
 * Budget Travel AI - Frontend Logic
 * High-performance Vanilla JS with Leaflet Map, Route Optimizer & Local Storage
 */

// --- Map Layer Providers ---
const TILE_PROVIDERS = {
  topo: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    options: { attribution: "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ", maxZoom: 18 }
  },
  dark: {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    options: { attribution: "&copy; OpenStreetMap contributors &copy; CARTO", maxZoom: 19, subdomains: 'abcd' }
  },
  street: {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    options: { attribution: "&copy; OpenStreetMap contributors", maxZoom: 19 }
  },
  satellite: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    options: { attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community", maxZoom: 18 }
  }
};

// --- State ---
const state = {
  lat: null,
  lng: null,
  locationName: "",
  radiusKm: 5.0,
  places: [],
  filteredPlaces: [],
  savedPlaces: JSON.parse(localStorage.getItem("bt_saved_places") || "{}"),
  map: null,
  currentTileLayer: null,
  activeTileKey: "topo",
  markersLayer: null,
  radiusCircle: null,
  originMarker: null,
  
  // Phase 3 Routing & Tour State
  routeLayer: null,
  routeMode: "walking", // "walking" | "driving"
  activeRoutePlaces: [],
  activeRouteTitle: "",
  showWalkRings: false,
  walkRingsLayer: null,
};

// --- DOM Elements ---
const locationInput = document.getElementById("location-input");
const geocodeDropdown = document.getElementById("geocode-dropdown");
const locationStatus = document.getElementById("location-status");
const gpsBtn = document.getElementById("gps-btn");
const queryInput = document.getElementById("query-input");
const budgetSelect = document.getElementById("budget-select");
const radiusSlider = document.getElementById("radius-slider");
const radiusVal = document.getElementById("radius-val");
const searchForm = document.getElementById("search-form");
const resultsSection = document.getElementById("results-section");
const placesList = document.getElementById("places-list");
const emptyState = document.getElementById("empty-state");
const loadingOverlay = document.getElementById("loading-overlay");

// Analytics
const statTotal = document.getElementById("stat-total");
const statRating = document.getElementById("stat-rating");
const statCheap = document.getElementById("stat-cheap");
const statModerate = document.getElementById("stat-moderate");

// Secondary Filters & Actions
const categoryFilter = document.getElementById("category-filter");
const sortSelect = document.getElementById("sort-select");
const openNowCheckbox = document.getElementById("open-now-checkbox");
const quickTourBtn = document.getElementById("quick-tour-btn");

// Route Tour UI
const routeTourPanel = document.getElementById("route-tour-panel");
const routeTitle = document.getElementById("route-title");
const routeDist = document.getElementById("route-dist");
const routeTime = document.getElementById("route-time");
const routeStopsCount = document.getElementById("route-stops-count");
const routeStopsList = document.getElementById("route-stops-list");
const routeGmapsBtn = document.getElementById("route-gmaps-btn");
const closeRouteBtn = document.getElementById("close-route-btn");
const toggleWalkRingsBtn = document.getElementById("toggle-walk-rings-btn");

// Drawer
const savedDrawer = document.getElementById("saved-drawer");
const drawerBackdrop = document.getElementById("drawer-backdrop");
const openSavedBtn = document.getElementById("open-saved-btn");
const closeSavedBtn = document.getElementById("close-saved-btn");
const clearSavedBtn = document.getElementById("clear-saved-btn");
const savedPlacesList = document.getElementById("saved-places-list");
const savedCountBadge = document.getElementById("saved-count-badge");
const savedActionsBar = document.getElementById("saved-actions-bar");
const planSavedTourBtn = document.getElementById("plan-saved-tour-btn");

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  updateSavedBadge();
  renderSavedPlaces();
});

// --- Event Listeners ---
function initEventListeners() {
  // Radius slider update
  radiusSlider.addEventListener("input", (e) => {
    state.radiusKm = parseFloat(e.target.value);
    radiusVal.textContent = `${state.radiusKm.toFixed(1)} km`;
    if (state.radiusCircle && state.lat && state.lng) {
      state.radiusCircle.setRadius(state.radiusKm * 1000);
    }
  });

  // Query preset pills
  document.querySelectorAll(".pill-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      queryInput.value = btn.dataset.query;
      if (state.lat && state.lng) {
        performSearch();
      }
    });
  });

  // GPS Geolocation
  gpsBtn.addEventListener("click", handleGPSLocation);

  // Geocoding Autocomplete with debounce
  let debounceTimeout = null;
  locationInput.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    clearTimeout(debounceTimeout);
    if (val.length < 2) {
      hideGeocodeDropdown();
      return;
    }
    debounceTimeout = setTimeout(() => fetchGeocodeSuggestions(val), 350);
  });

  // Hide dropdown on click outside
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".location-group")) {
      hideGeocodeDropdown();
    }
  });

  // Search Form Submit
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!state.lat || !state.lng) {
      const placeText = locationInput.value.trim();
      if (placeText) {
        showLoading("Resolving location...");
        fetch(`/api/geocode?place=${encodeURIComponent(placeText)}`)
          .then((r) => r.json())
          .then((data) => {
            hideLoading();
            if (data.matches && data.matches.length > 0) {
              const match = data.matches[0];
              setLocation(match.lat, match.lng, match.formatted_address);
              performSearch();
            } else {
              alert("Location not found. Please pick from suggested matches or use GPS.");
            }
          })
          .catch((err) => {
            hideLoading();
            alert("Error locating place. Please try again.");
          });
        return;
      } else {
        alert("Please specify a search location.");
        return;
      }
    }
    performSearch();
  });

  // Filter toolbar changes
  categoryFilter.addEventListener("change", applyFiltersAndRender);
  sortSelect.addEventListener("change", applyFiltersAndRender);
  openNowCheckbox.addEventListener("change", applyFiltersAndRender);

  // Quick Tour Button
  if (quickTourBtn) {
    quickTourBtn.addEventListener("click", () => {
      const candidates = state.filteredPlaces.slice(0, 5);
      if (candidates.length === 0) {
        alert("No places available to route. Try searching or adjusting filters.");
        return;
      }
      buildAndRenderOptimizedTour(candidates, "⚡ Quick Walking Tour (Top Spots)");
    });
  }

  // Map Tile Switcher Buttons
  document.querySelectorAll(".tile-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const layerKey = btn.dataset.layer;
      switchMapTileLayer(layerKey);
      document.querySelectorAll(".tile-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  // Walking Isochrone Rings Toggle
  if (toggleWalkRingsBtn) {
    toggleWalkRingsBtn.addEventListener("click", () => {
      state.showWalkRings = !state.showWalkRings;
      toggleWalkRingsBtn.classList.toggle("active", state.showWalkRings);
      renderWalkingRings();
    });
  }

  // Route Tour Controls (Mode Toggle & Close)
  document.querySelectorAll(".btn-mode").forEach((btn) => {
    btn.addEventListener("click", () => {
      const mode = btn.dataset.mode;
      if (mode === state.routeMode) return;
      state.routeMode = mode;
      document.querySelectorAll(".btn-mode").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      if (state.activeRoutePlaces.length > 0) {
        buildAndRenderOptimizedTour(state.activeRoutePlaces, state.activeRouteTitle, false);
      }
    });
  });

  if (closeRouteBtn) {
    closeRouteBtn.addEventListener("click", clearActiveRoute);
  }

  // Drawer Tour Button
  if (planSavedTourBtn) {
    planSavedTourBtn.addEventListener("click", () => {
      const savedList = Object.values(state.savedPlaces);
      if (savedList.length === 0) {
        alert("No saved places to tour yet. Click the heart icon on places to add them.");
        return;
      }
      closeDrawer();
      buildAndRenderOptimizedTour(savedList, "🗺️ Saved Bucket-List Tour");
      resultsSection.classList.remove("hidden");
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  // Saved Drawer toggle
  openSavedBtn.addEventListener("click", openDrawer);
  closeSavedBtn.addEventListener("click", closeDrawer);
  drawerBackdrop.addEventListener("click", closeDrawer);
  clearSavedBtn.addEventListener("click", () => {
    state.savedPlaces = {};
    localStorage.removeItem("bt_saved_places");
    updateSavedBadge();
    renderSavedPlaces();
    renderPlacesList();
  });
}

// --- GPS Geolocation ---
function handleGPSLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }
  locationStatus.textContent = "Detecting GPS location...";
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      setLocation(lat, lng, `My Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`);
      locationStatus.textContent = `📍 GPS Detected: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    },
    (err) => {
      locationStatus.textContent = "⚠️ GPS permission denied. Please type a place name.";
    },
    { timeout: 10000 }
  );
}

// --- Geocoding Suggestions ---
async function fetchGeocodeSuggestions(query) {
  try {
    const res = await fetch(`/api/geocode?place=${encodeURIComponent(query)}`);
    if (!res.ok) return;
    const data = await res.json();
    const matches = data.matches || [];
    renderGeocodeDropdown(matches);
  } catch (err) {
    console.error("Geocoding fetch error:", err);
  }
}

function renderGeocodeDropdown(matches) {
  if (!matches || matches.length === 0) {
    hideGeocodeDropdown();
    return;
  }
  geocodeDropdown.innerHTML = matches
    .map(
      (m) =>
        `<div class="geocode-item" data-lat="${m.lat}" data-lng="${m.lng}" data-address="${m.formatted_address}">
          📍 ${m.formatted_address}
        </div>`
    )
    .join("");

  geocodeDropdown.classList.remove("hidden");

  geocodeDropdown.querySelectorAll(".geocode-item").forEach((item) => {
    item.addEventListener("click", () => {
      const lat = parseFloat(item.dataset.lat);
      const lng = parseFloat(item.dataset.lng);
      const addr = item.dataset.address;
      setLocation(lat, lng, addr);
      hideGeocodeDropdown();
    });
  });
}

function setLocation(lat, lng, address) {
  state.lat = lat;
  state.lng = lng;
  state.locationName = address;
  locationInput.value = address;
  locationStatus.textContent = `📍 Coordinates: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
}

function hideGeocodeDropdown() {
  geocodeDropdown.classList.add("hidden");
  geocodeDropdown.innerHTML = "";
}

// --- Search Execution ---
async function performSearch() {
  const query = queryInput.value.trim() || "restaurant";
  const maxBudget = parseInt(budgetSelect.value, 10);
  const radiusMeters = Math.round(state.radiusKm * 1000);

  showLoading(`Discovering budget ${query} near ${state.locationName}...`);

  try {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        lat: state.lat,
        lng: state.lng,
        radius: radiusMeters,
        max_budget_level: maxBudget,
      }),
    });

    if (!res.ok) {
      throw new Error(`Search request failed (${res.status})`);
    }

    const data = await res.json();
    state.places = data.results || [];

    hideLoading();
    resultsSection.classList.remove("hidden");

    // Clear active route when new search is made
    clearActiveRoute();

    // Populate category dropdown
    populateCategoryFilter();

    // Apply filters, render metrics, map, and cards
    applyFiltersAndRender();

    // Scroll smoothly to results
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    hideLoading();
    alert(`Could not complete search: ${err.message}`);
  }
}

// --- Filter, Sort & Render ---
function populateCategoryFilter() {
  const categories = Array.from(
    new Set(state.places.map((p) => p.category || "Place").filter(Boolean))
  ).sort();

  categoryFilter.innerHTML = `<option value="all">All Categories</option>` +
    categories.map((c) => `<option value="${c}">${c}</option>`).join("");
}

function applyFiltersAndRender() {
  const selectedCategory = categoryFilter.value;
  const sortBy = sortSelect.value;
  const openOnly = openNowCheckbox.checked;

  let list = [...state.places];

  // Category filter
  if (selectedCategory !== "all") {
    list = list.filter((p) => (p.category || "Place") === selectedCategory);
  }

  // Open now filter
  if (openOnly) {
    list = list.filter((p) => p.open_now === true);
  }

  // Sorting
  if (sortBy === "rating") {
    list.sort((a, b) => (b.rating || 0) - (a.rating || 0) || (b.user_rating_count || 0) - (a.user_rating_count || 0));
  } else if (sortBy === "reviews") {
    list.sort((a, b) => (b.user_rating_count || 0) - (a.user_rating_count || 0));
  } else if (sortBy === "budget") {
    list.sort((a, b) => (a.price_score ?? 1) - (b.price_score ?? 1));
  }

  state.filteredPlaces = list;

  // Update Metrics
  updateAnalytics();

  // Render Map & Cards
  renderMap();
  renderPlacesList();
}

function updateAnalytics() {
  const total = state.filteredPlaces.length;
  statTotal.textContent = total;

  if (total > 0) {
    const avg = state.filteredPlaces.reduce((sum, p) => sum + (p.rating || 0), 0) / total;
    statRating.textContent = `${avg.toFixed(2)} / 5.0`;
  } else {
    statRating.textContent = "0.0";
  }

  const cheapCount = state.filteredPlaces.filter((p) => (p.price_score ?? 1) <= 1).length;
  const moderateCount = state.filteredPlaces.filter((p) => (p.price_score ?? 1) === 2).length;

  statCheap.textContent = cheapCount;
  statModerate.textContent = moderateCount;
}

// --- Leaflet Map Rendering ---
function renderMap() {
  if (!state.map) {
    // Initialize map
    state.map = L.map("map", {
      center: [state.lat || 20.2961, state.lng || 85.8245],
      zoom: 13,
      fullscreenControl: true,
    });

    // Mount initial tile provider
    switchMapTileLayer(state.activeTileKey);

    state.markersLayer = L.layerGroup().addTo(state.map);
    state.walkRingsLayer = L.layerGroup().addTo(state.map);
    state.routeLayer = L.layerGroup().addTo(state.map);
  } else if (state.lat && state.lng) {
    state.map.setView([state.lat, state.lng], 13);
    state.markersLayer.clearLayers();
    if (state.radiusCircle) state.map.removeLayer(state.radiusCircle);
    if (state.originMarker) state.map.removeLayer(state.originMarker);
  }

  if (!state.lat || !state.lng) return;

  // Add search origin marker
  const originIcon = L.divIcon({
    className: "custom-pin-wrapper",
    html: `<div class="pin-origin">📍</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });

  state.originMarker = L.marker([state.lat, state.lng], { icon: originIcon })
    .bindPopup(`<div class="popup-card"><b>🎯 Search Origin</b><br>Radius: ${state.radiusKm.toFixed(1)} km</div>`)
    .addTo(state.map);

  // Add search radius circle
  state.radiusCircle = L.circle([state.lat, state.lng], {
    radius: state.radiusKm * 1000,
    color: "#0d9488",
    weight: 2,
    fillColor: "#14b8a6",
    fillOpacity: 0.1,
    dashArray: "6, 6",
  }).addTo(state.map);

  // Render walking rings if enabled
  renderWalkingRings();

  // Add Place Markers
  state.filteredPlaces.forEach((p, idx) => {
    if (!p.location || !p.location.latitude || !p.location.longitude) return;

    const lat = p.location.latitude;
    const lng = p.location.longitude;
    const score = p.price_score ?? 1;
    const symbol = p.price_symbol || "$";
    const bg = score <= 1 ? "#10b981" : score === 2 ? "#f59e0b" : "#ef4444";

    const pinIcon = L.divIcon({
      className: "custom-pin-wrapper",
      html: `<div class="custom-pin" style="background: ${bg}; color: white;">#${idx + 1} ${symbol}</div>`,
      iconSize: [50, 24],
      iconAnchor: [25, 12],
    });

    const openBadge = p.open_now === true
      ? '<span style="color: #6ee7b7; float: right; font-size: 11px; font-weight: 600;">🟢 Open</span>'
      : p.open_now === false
      ? '<span style="color: #fca5a5; float: right; font-size: 11px; font-weight: 600;">🔴 Closed</span>'
      : '';

    const gmapsUrl = p.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;

    const popupHtml = `
      <div class="popup-card">
        <div class="popup-title">#${idx + 1}. ${escapeHtml(p.name)}</div>
        <div class="popup-meta">🏷️ ${p.category || 'Place'} | <b>${p.price_symbol || '$'} ${p.price_level || 'Budget'}</b></div>
        <div style="font-size: 12px; margin-bottom: 6px;">
          ⭐ <b>${p.rating || 'N/A'}</b> <span style="color: #94a3b8; font-size: 11px;">(${p.user_rating_count || 0} reviews)</span>
          ${openBadge}
        </div>
        <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">📍 ${escapeHtml(p.address || '')}</div>
        <a href="${gmapsUrl}" target="_blank" rel="noopener noreferrer" class="popup-btn">🧭 Open in Google Maps ↗</a>
      </div>
    `;

    L.marker([lat, lng], { icon: pinIcon })
      .bindPopup(popupHtml, { maxWidth: 280 })
      .addTo(state.markersLayer);
  });
}

// --- Map Tile Layer Switcher ---
function switchMapTileLayer(layerKey) {
  const provider = TILE_PROVIDERS[layerKey] || TILE_PROVIDERS.topo;
  state.activeTileKey = layerKey;

  if (state.map) {
    if (state.currentTileLayer) {
      state.map.removeLayer(state.currentTileLayer);
    }
    state.currentTileLayer = L.tileLayer(provider.url, provider.options).addTo(state.map);
  }
}

// --- Walking Isochrone Rings (15 min & 30 min) ---
function renderWalkingRings() {
  if (!state.map || !state.walkRingsLayer) return;
  state.walkRingsLayer.clearLayers();

  if (!state.showWalkRings || !state.lat || !state.lng) return;

  // 15-min walk (~1.2 km at 4.8 km/h)
  const ring15 = L.circle([state.lat, state.lng], {
    radius: 1200,
    color: "#10b981",
    weight: 1.8,
    fillColor: "#10b981",
    fillOpacity: 0.06,
    dashArray: "4, 6",
  }).bindTooltip("🚶 15-min walk (~1.2 km)", { permanent: false, direction: "top" });

  // 30-min walk (~2.4 km)
  const ring30 = L.circle([state.lat, state.lng], {
    radius: 2400,
    color: "#f59e0b",
    weight: 1.8,
    fillColor: "#f59e0b",
    fillOpacity: 0.04,
    dashArray: "4, 6",
  }).bindTooltip("🚶 30-min walk (~2.4 km)", { permanent: false, direction: "top" });

  state.walkRingsLayer.addLayer(ring15);
  state.walkRingsLayer.addLayer(ring30);
}

// =========================================================
// PHASE 3: MULTI-STOP ROUTE OPTIMIZER & OSRM ENGINE
// =========================================================

/**
 * Haversine Distance helper (in meters)
 */
function getDistanceMeters(lat1, lon1, lat2, lon2) {
  const R = 6371e3; // Earth radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

/**
 * TSP Nearest-Neighbor Algorithm:
 * Returns places sorted in optimal sequential visiting order from origin.
 */
function optimizeStopOrder(originLat, originLng, places) {
  const validPlaces = places.filter(p => p.location && p.location.latitude && p.location.longitude);
  if (validPlaces.length <= 1) return validPlaces;

  let currentLat = originLat;
  let currentLng = originLng;
  const unvisited = [...validPlaces];
  const ordered = [];

  while (unvisited.length > 0) {
    let nearestIdx = 0;
    let nearestDist = Infinity;

    for (let i = 0; i < unvisited.length; i++) {
      const p = unvisited[i];
      const dist = getDistanceMeters(currentLat, currentLng, p.location.latitude, p.location.longitude);
      if (dist < nearestDist) {
        nearestDist = dist;
        nearestIdx = i;
      }
    }

    const nextPlace = unvisited.splice(nearestIdx, 1)[0];
    ordered.push(nextPlace);
    currentLat = nextPlace.location.latitude;
    currentLng = nextPlace.location.longitude;
  }

  return ordered;
}

/**
 * Fetch real route path from OSRM (Walking or Driving)
 */
async function fetchOSRMRoute(waypoints, mode = "walking") {
  // OSRM coordinates format: lng,lat;lng,lat;...
  const coordsParam = waypoints.map(wp => `${wp.lng.toFixed(6)},${wp.lat.toFixed(6)}`).join(";");
  const osrmMode = mode === "driving" ? "driving" : "foot";
  const url = `https://router.project-osrm.org/route/v1/${osrmMode}/${coordsParam}?overview=full&geometries=geojson`;

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("OSRM routing request failed");
    const data = await res.json();
    if (data.code === "Ok" && data.routes && data.routes.length > 0) {
      const route = data.routes[0];
      const geometry = route.geometry.coordinates.map(c => [c[1], c[0]]); // Leaflet is [lat, lng]
      return {
        success: true,
        coordinates: geometry,
        distanceMeters: route.distance,
        durationSeconds: route.duration,
      };
    }
    throw new Error("No route geometry returned");
  } catch (err) {
    console.warn("OSRM routing unavailable, using straight-line geodesic fallback:", err);
    // Fallback: straight lines
    let totalDist = 0;
    const fallbackCoords = waypoints.map(wp => [wp.lat, wp.lng]);
    for (let i = 0; i < waypoints.length - 1; i++) {
      totalDist += getDistanceMeters(waypoints[i].lat, waypoints[i].lng, waypoints[i+1].lat, waypoints[i+1].lng);
    }
    const speedKmh = mode === "driving" ? 35 : 4.5;
    const durationSeconds = (totalDist / (speedKmh * 1000 / 3600));

    return {
      success: true,
      coordinates: fallbackCoords,
      distanceMeters: totalDist,
      durationSeconds: durationSeconds,
      isFallback: true,
    };
  }
}

/**
 * Build & Render the Multi-Stop Tour
 */
async function buildAndRenderOptimizedTour(places, title = "Optimized Tour", reorder = true) {
  if (!state.lat || !state.lng) {
    alert("Please set a location first.");
    return;
  }

  showLoading("Calculating optimal multi-stop route...");

  // Optimize stop sequence
  const orderedPlaces = reorder
    ? optimizeStopOrder(state.lat, state.lng, places)
    : places;

  state.activeRoutePlaces = orderedPlaces;
  state.activeRouteTitle = title;

  // Create waypoints list: Origin -> Stop 1 -> Stop 2 ...
  const waypoints = [
    { lat: state.lat, lng: state.lng, name: "Start (Origin)", isOrigin: true }
  ];

  orderedPlaces.forEach((p, idx) => {
    if (p.location && p.location.latitude && p.location.longitude) {
      waypoints.push({
        lat: p.location.latitude,
        lng: p.location.longitude,
        name: p.name,
        category: p.category,
        price_symbol: p.price_symbol,
        rating: p.rating,
        id: p.id || `stop_${idx}`,
      });
    }
  });

  if (waypoints.length < 2) {
    hideLoading();
    alert("Not enough locations to build a route.");
    return;
  }

  // Fetch routing geometry
  const routeResult = await fetchOSRMRoute(waypoints, state.routeMode);

  hideLoading();

  // Clear previous route layer
  if (!state.routeLayer) {
    state.routeLayer = L.layerGroup().addTo(state.map);
  } else {
    state.routeLayer.clearLayers();
  }

  // Draw Route Polyline with modern gradient glow
  const polyline = L.polyline(routeResult.coordinates, {
    color: state.routeMode === "driving" ? "#3b82f6" : "#14b8a6",
    weight: 5,
    opacity: 0.9,
    lineJoin: "round",
  }).addTo(state.routeLayer);

  // Add subtle outer glow line
  L.polyline(routeResult.coordinates, {
    color: state.routeMode === "driving" ? "#60a5fa" : "#5eead4",
    weight: 10,
    opacity: 0.25,
    lineJoin: "round",
  }).addTo(state.routeLayer);

  // Add Waypoint Numbered Markers
  orderedPlaces.forEach((p, idx) => {
    if (!p.location || !p.location.latitude || !p.location.longitude) return;
    const lat = p.location.latitude;
    const lng = p.location.longitude;

    const waypointIcon = L.divIcon({
      className: "custom-pin-wrapper",
      html: `<div class="route-waypoint-pin">${idx + 1}</div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    });

    const gmapsUrl = p.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;

    const popupHtml = `
      <div class="popup-card">
        <div class="popup-title">Stop #${idx + 1}: ${escapeHtml(p.name)}</div>
        <div class="popup-meta">🏷️ ${p.category || 'Place'} | <b>${p.price_symbol || '$'}</b> | ⭐ ${p.rating || 'N/A'}</div>
        <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">📍 ${escapeHtml(p.address || '')}</div>
        <a href="${gmapsUrl}" target="_blank" rel="noopener noreferrer" class="popup-btn">🧭 Directions in Google Maps ↗</a>
      </div>
    `;

    L.marker([lat, lng], { icon: waypointIcon })
      .bindPopup(popupHtml, { maxWidth: 280 })
      .addTo(state.routeLayer);
  });

  // Fit Map bounds to show entire route
  state.map.fitBounds(polyline.getBounds(), { padding: [40, 40] });

  // Update Route Tour Panel UI
  const distKm = (routeResult.distanceMeters / 1000).toFixed(2);
  const totalMins = Math.round(routeResult.durationSeconds / 60);
  const hours = Math.floor(totalMins / 60);
  const mins = totalMins % 60;
  const timeStr = hours > 0 ? `${hours}h ${mins}m` : `${mins} mins`;

  routeTitle.textContent = `${state.routeMode === "driving" ? "🚗 Driving" : "🚶 Walking"} ${title}`;
  routeDist.textContent = `📏 ${distKm} km`;
  routeTime.textContent = `⏱️ ~${timeStr}`;
  routeStopsCount.textContent = `📍 ${orderedPlaces.length} Stops`;

  // Build Multi-Waypoint Google Maps Navigation Link
  // Google Maps directions format: https://www.google.com/maps/dir/lat0,lng0/lat1,lng1/lat2,lng2/...
  const gmapsCoords = [
    `${state.lat},${state.lng}`,
    ...orderedPlaces.map(p => `${p.location.latitude},${p.location.longitude}`)
  ].join("/");
  const gmapsTravelMode = state.routeMode === "driving" ? "driving" : "walking";
  routeGmapsBtn.href = `https://www.google.com/maps/dir/${gmapsCoords}/data=!4m2!4m1!3e${gmapsTravelMode === "driving" ? "0" : "2"}`;

  // Render Horizontal Stop Chips
  routeStopsList.innerHTML = `
    <div class="route-stop-chip" onclick="focusOnCoordinate(${state.lat}, ${state.lng})">
      <span class="stop-num-badge origin">📍</span>
      <div class="stop-info">
        <span class="stop-name">Start</span>
        <span class="stop-meta">Origin Location</span>
      </div>
    </div>
  ` + orderedPlaces.map((p, idx) => `
    <div class="route-stop-chip" onclick="focusOnCoordinate(${p.location.latitude}, ${p.location.longitude})">
      <span class="stop-num-badge">${idx + 1}</span>
      <div class="stop-info">
        <span class="stop-name">${escapeHtml(p.name)}</span>
        <span class="stop-meta">${p.category || 'Spot'} • ⭐ ${p.rating || 'N/A'}</span>
      </div>
    </div>
  `).join("");

  // Show Route Panel
  routeTourPanel.classList.remove("hidden");
}

window.focusOnCoordinate = function(lat, lng) {
  if (state.map) {
    state.map.setView([lat, lng], 16, { animate: true });
  }
};

function clearActiveRoute() {
  if (state.routeLayer) {
    state.routeLayer.clearLayers();
  }
  state.activeRoutePlaces = [];
  state.activeRouteTitle = "";
  if (routeTourPanel) {
    routeTourPanel.classList.add("hidden");
  }
}

// --- Render Places Cards ---
function renderPlacesList() {
  if (state.filteredPlaces.length === 0) {
    placesList.innerHTML = "";
    emptyState.classList.remove("hidden");
    return;
  }

  emptyState.classList.add("hidden");

  placesList.innerHTML = state.filteredPlaces
    .map((p, idx) => {
      const pid = p.id || `place_${idx}`;
      const isSaved = !!state.savedPlaces[pid];
      const score = p.price_score ?? 1;
      const budgetClass = score === 0 ? "badge-free" : score === 1 ? "badge-inexpensive" : "badge-moderate";
      const openBadge = p.open_now === true
        ? '<span class="badge badge-open">🟢 Open Now</span>'
        : p.open_now === false
        ? '<span class="badge badge-closed">🔴 Closed</span>'
        : '';
      const gmapsUrl = p.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(p.name)}`;

      return `
        <div class="place-card" data-id="${pid}">
          <div class="card-top">
            <h4 class="card-title">#${idx + 1}. ${escapeHtml(p.name)}</h4>
            <div class="card-rating">⭐ ${p.rating || 'N/A'} <small>(${p.user_rating_count || 0})</small></div>
          </div>
          <div class="card-badges">
            <span class="badge ${budgetClass}">${p.price_symbol || '$'} ${p.price_level || 'Budget'}</span>
            <span class="badge badge-category">${p.category || 'Place'}</span>
            ${openBadge}
          </div>
          <div class="card-address">
            <i class="fa-solid fa-location-dot"></i>
            <span>${escapeHtml(p.address || 'No address available')}</span>
          </div>
          <div class="card-actions">
            <a href="${gmapsUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-card">
              <i class="fa-solid fa-location-arrow"></i> Directions
            </a>
            ${p.website_url ? `<a href="${p.website_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-card"><i class="fa-solid fa-globe"></i> Website</a>` : ''}
            <button type="button" class="btn btn-outline btn-card btn-save ${isSaved ? 'saved' : ''}" onclick="toggleSavePlace('${pid}')">
              <i class="fa-${isSaved ? 'solid' : 'regular'} fa-heart"></i> ${isSaved ? 'Saved' : 'Save'}
            </button>
          </div>
        </div>
      `;
    })
    .join("");
}

// --- Save / Trip Bucket List ---
window.toggleSavePlace = function (pid) {
  const place = state.places.find((p) => (p.id || `place_${state.places.indexOf(p)}`) === pid);
  if (!place && !state.savedPlaces[pid]) return;

  if (state.savedPlaces[pid]) {
    delete state.savedPlaces[pid];
  } else {
    state.savedPlaces[pid] = place;
  }

  localStorage.setItem("bt_saved_places", JSON.stringify(state.savedPlaces));
  updateSavedBadge();
  renderSavedPlaces();
  renderPlacesList();
};

function updateSavedBadge() {
  const count = Object.keys(state.savedPlaces).length;
  savedCountBadge.textContent = count;
  if (savedActionsBar) {
    savedActionsBar.classList.toggle("hidden", count === 0);
  }
}

function renderSavedPlaces() {
  const keys = Object.keys(state.savedPlaces);
  if (keys.length === 0) {
    savedPlacesList.innerHTML = `<p class="drawer-empty">No places saved yet. Click the heart icon on any card to save places for your trip.</p>`;
    if (savedActionsBar) savedActionsBar.classList.add("hidden");
    return;
  }

  if (savedActionsBar) savedActionsBar.classList.remove("hidden");

  savedPlacesList.innerHTML = keys
    .map((k) => {
      const p = state.savedPlaces[k];
      const gmapsUrl = p.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(p.name)}`;
      return `
        <div class="place-card" style="margin-bottom: 0.8rem;">
          <div class="card-top">
            <h4 class="card-title">${escapeHtml(p.name)}</h4>
            <span class="card-rating">⭐ ${p.rating || 'N/A'}</span>
          </div>
          <div class="card-address">📍 ${escapeHtml(p.address || '')}</div>
          <div class="card-actions" style="margin-top: 0.5rem;">
            <a href="${gmapsUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-card btn-full">
              🧭 Directions
            </a>
            <button type="button" class="btn btn-outline btn-card" onclick="toggleSavePlace('${k}')">
              🗑️
            </button>
          </div>
        </div>
      `;
    })
    .join("");
}

function openDrawer() {
  savedDrawer.classList.add("open");
  drawerBackdrop.classList.remove("hidden");
}

function closeDrawer() {
  savedDrawer.classList.remove("open");
  drawerBackdrop.classList.add("hidden");
}

// --- Loading UI Helpers ---
function showLoading(msg = "Loading...") {
  document.getElementById("loading-text").textContent = msg;
  loadingOverlay.classList.remove("hidden");
}

function hideLoading() {
  loadingOverlay.classList.add("hidden");
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[m]));
}
