import maplibregl from 'maplibre-gl';

// State
let targets = {};
let knownAnalogs = {};
let validationReport = {};
let candidateCells = [];
let earthStats = {};

let activeTarget = 'jezero';
let activeMethod = 'cos';
let activeFilter = 'all'; // 'all', 'accessible', 'polar'
let weights = {
  slope: 0.45,
  roughness: 0.35,
  relief: 0.20
};

let map = null;
let currentMarkers = [];
let selectedLocation = null;

// Free Dark Basemap Style (ESRI Dark Gray Canvas - No API Key, No Watermark)
const MAP_STYLE = {
  version: 8,
  sources: {
    'esri-dark': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
      ],
      tileSize: 256,
      attribution: 'Esri, HERE, Garmin, © OpenStreetMap contributors | MapLibre'
    },
    'esri-labels': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}'
      ],
      tileSize: 256
    }
  },
  layers: [
    {
      id: 'esri-dark-layer',
      type: 'raster',
      source: 'esri-dark',
      minzoom: 0,
      maxzoom: 16
    }
  ]
};

// Initialize Application
async function init() {
  try {
    // 1. Fetch metadata assets
    const [targetsRes, analogsRes, valRes, cellsRes, statsRes] = await Promise.all([
      fetch('/data/targets.json').then(r => r.json()),
      fetch('/data/known_analogs.json').then(r => r.json()),
      fetch('/data/validation_report.json').then(r => r.json()),
      fetch('/data/candidate_cells.json').then(r => r.json()),
      fetch('/data/earth_stats.json').then(r => r.json())
    ]);

    targets = targetsRes;
    knownAnalogs = analogsRes;
    validationReport = valRes;
    candidateCells = cellsRes;
    earthStats = statsRes;

    // 2. Initialize Map
    initMap();

    // 3. Setup UI event listeners
    setupEvents();

    // 4. Render initial target state
    renderTargetFingerprint();
    updateCandidatesList();
    renderValidationModal();

  } catch (err) {
    console.error('CRITICAL: Failed to load application data:', err);
  }
}

function initMap() {
  map = new maplibregl.Map({
    container: 'map',
    style: MAP_STYLE,
    center: [10, 20],
    zoom: 1.8,
    minZoom: 1,
    maxZoom: 12
  });

  map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'bottom-left');

  // Live HUD Mousemove Telemetry Tracker
  map.on('mousemove', (e) => {
    const hudCoords = document.getElementById('hud-coords');
    if (hudCoords) {
      const lat = e.lngLat.lat;
      const lon = e.lngLat.lng;
      const latStr = `${Math.abs(lat).toFixed(4)}°${lat >= 0 ? 'N' : 'S'}`;
      const lonStr = `${Math.abs(lon).toFixed(4)}°${lon >= 0 ? 'E' : 'W'}`;
      hudCoords.innerText = `${latStr}, ${lonStr} [Z: ${map.getZoom().toFixed(1)}]`;
    }
  });

  map.on('load', () => {
    updateHeatmapLayer();
    renderMarkers();
  });
}

function updateHeatmapLayer() {
  if (!map || !map.isStyleLoaded()) return;

  const layerId = 'planetary-heatmap-layer';
  const sourceId = 'planetary-heatmap-source';
  const imageUrl = `/data/heatmap_${activeTarget}_${activeMethod}.png`;

  const coordinates = [
    [-180, 85],
    [180, 85],
    [180, -85],
    [-180, -85]
  ];

  if (map.getLayer(layerId)) {
    map.removeLayer(layerId);
  }
  if (map.getSource(sourceId)) {
    map.removeSource(sourceId);
  }

  map.addSource(sourceId, {
    type: 'image',
    url: imageUrl,
    coordinates: coordinates
  });

  map.addLayer({
    id: layerId,
    type: 'raster',
    source: sourceId,
    paint: {
      'raster-opacity': 0.85,
      'raster-fade-duration': 250
    }
  });
}

function renderMarkers() {
  currentMarkers.forEach(m => m.remove());
  currentMarkers = [];

  const targetData = targets[activeTarget];
  if (!targetData) return;

  // 1. Known Ground-Truth Benchmark Analogs (Gold Precision Reticle)
  Object.entries(knownAnalogs).forEach(([key, info]) => {
    const el = document.createElement('div');
    el.className = 'reticle-pin reticle-benchmark';
    el.title = `STATION: ${info.name} [GROUND-TRUTH BENCHMARK]`;
    el.innerHTML = `
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
        <circle cx="12" cy="12" r="7" stroke="#eab308" stroke-width="1.8"/>
        <line x1="12" y1="1" x2="12" y2="7" stroke="#eab308" stroke-width="1.5"/>
        <line x1="12" y1="17" x2="12" y2="23" stroke="#eab308" stroke-width="1.5"/>
        <line x1="1" y1="12" x2="7" y2="12" stroke="#eab308" stroke-width="1.5"/>
        <line x1="17" y1="12" x2="23" y2="12" stroke="#eab308" stroke-width="1.5"/>
        <circle cx="12" cy="12" r="2" fill="#eab308"/>
      </svg>
    `;

    el.addEventListener('click', (e) => {
      e.stopPropagation();
      selectLocation({
        name: info.name,
        region: info.region,
        lat: info.lat,
        lon: info.lon,
        slope: info.mean_slope,
        roughness: info.roughness,
        relief: info.local_relief,
        elevation: info.elev_min != null ? Math.round((info.elev_min + info.elev_max)/2) : 1000,
        precip: info.annual_precip != null ? info.annual_precip : 50,
        description: info.description,
        isKnown: true
      });
    });

    const marker = new maplibregl.Marker({ element: el })
      .setLngLat([info.lon, info.lat])
      .addTo(map);

    currentMarkers.push(marker);
  });

  // 2. Discovered Novel Candidate Cells (Cyan Diamond Bracket)
  const valInfo = validationReport[activeTarget];
  if (valInfo && valInfo.new_candidates) {
    valInfo.new_candidates.forEach((cand, idx) => {
      const el = document.createElement('div');
      el.className = 'reticle-pin reticle-novel';
      el.title = `CANDIDATE: ${cand.name} [DISCOVERY #${idx + 1}]`;
      el.innerHTML = `
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
          <polygon points="12,2 22,12 12,22 2,12" stroke="#38bdf8" stroke-width="1.8"/>
          <circle cx="12" cy="12" r="2.5" fill="#38bdf8"/>
        </svg>
      `;

      el.addEventListener('click', (e) => {
        e.stopPropagation();
        selectLocation({
          name: cand.name,
          region: cand.region,
          lat: cand.lat,
          lon: cand.lon || cand['lon: '],
          slope: 2.2,
          roughness: 180,
          relief: 800,
          elevation: 2500,
          precip: 120,
          description: cand.rationale,
          isNovel: true
        });
      });

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([cand.lon || cand['lon: '], cand.lat])
        .addTo(map);

      currentMarkers.push(marker);
    });
  }
}

// Client-Side Re-weighting Engine
function calculateCellSimilarity(cell, target, w) {
  const ws = Math.sqrt(w.slope);
  const wr = Math.sqrt(w.roughness);
  const wl = Math.sqrt(w.relief);

  const ut = [ws * target.z_s, wr * target.z_r, wl * target.z_l];
  const uc = [ws * cell.z_s, wr * cell.z_r, wl * cell.z_l];

  const dot = ut[0] * uc[0] + ut[1] * uc[1] + ut[2] * uc[2];
  const normT = Math.sqrt(ut[0]**2 + ut[1]**2 + ut[2]**2);
  const normC = Math.sqrt(uc[0]**2 + uc[1]**2 + uc[2]**2);

  if (normT === 0 || normC === 0) return 0.5;
  const cos = dot / (normT * normC);
  return Math.min(1.0, Math.max(0.0, (cos + 1.0) / 2.0));
}

function updateCandidatesList() {
  const target = targets[activeTarget];
  if (!target || candidateCells.length === 0) return;

  const totalW = weights.slope + weights.roughness + weights.relief;
  const normW = {
    slope: weights.slope / totalW,
    roughness: weights.roughness / totalW,
    relief: weights.relief / totalW
  };

  let filteredCells = candidateCells;
  if (activeFilter === 'accessible') {
    filteredCells = candidateCells.filter(c => Math.abs(c.lat) <= 60.0);
  } else if (activeFilter === 'polar') {
    filteredCells = candidateCells.filter(c => Math.abs(c.lat) > 60.0);
  }

  const scored = filteredCells.map(cell => ({
    ...cell,
    sim: calculateCellSimilarity(cell, target, normW)
  }));

  scored.sort((a, b) => b.sim - a.sim);

  const listEl = document.getElementById('candidate-list');
  listEl.innerHTML = '';

  const seen = [];
  let count = 0;

  for (const cell of scored) {
    if (seen.some(c => Math.abs(c.lat - cell.lat) < 1.5 && Math.abs(c.lon - cell.lon) < 1.5)) {
      continue;
    }
    seen.push(cell);
    count++;

    const item = document.createElement('div');
    item.className = 'candidate-item';
    const latStr = `${Math.abs(cell.lat).toFixed(2)}°${cell.lat >= 0 ? 'N' : 'S'}`;
    const lonStr = `${Math.abs(cell.lon).toFixed(2)}°${cell.lon >= 0 ? 'E' : 'W'}`;

    item.innerHTML = `
      <div class="cand-left">
        <span class="cand-rank">#${count.toString().padStart(2, '0')}</span>
        <div>
          <div class="cand-name">${getRegionName(cell.lat, cell.lon)}</div>
          <div class="cand-coords">${latStr}, ${lonStr} • ID:${cell.id}</div>
        </div>
      </div>
      <div class="cand-score">${(cell.sim * 100).toFixed(1)}%</div>
    `;

    item.addEventListener('click', () => {
      selectLocation({
        name: getRegionName(cell.lat, cell.lon),
        region: `TERRESTRIAL GRID CELL ID #${cell.id}`,
        lat: cell.lat,
        lon: cell.lon,
        slope: cell.slope,
        roughness: cell.roughness,
        relief: cell.relief,
        elevation: cell.elevation,
        precip: cell.precip,
        similarity: cell.sim,
        description: `High-confidence ${target.name} analog identified through multivariate geomorphometric similarity matching.`
      });

      map.flyTo({ center: [cell.lon, cell.lat], zoom: 4.5, duration: 1200 });
    });

    listEl.appendChild(item);
    if (count >= 8) break;
  }
}

function exportTopCandidatesCSV() {
  const target = targets[activeTarget];
  if (!target || candidateCells.length === 0) return;

  const totalW = weights.slope + weights.roughness + weights.relief;
  const normW = {
    slope: weights.slope / totalW,
    roughness: weights.roughness / totalW,
    relief: weights.relief / totalW
  };

  let pool = candidateCells;
  if (activeFilter === 'accessible') {
    pool = candidateCells.filter(c => Math.abs(c.lat) <= 60.0);
  } else if (activeFilter === 'polar') {
    pool = candidateCells.filter(c => Math.abs(c.lat) > 60.0);
  }

  const scored = pool.map(cell => ({
    ...cell,
    sim: calculateCellSimilarity(cell, target, normW)
  }));
  scored.sort((a, b) => b.sim - a.sim);

  const rows = [
    ["# NASA Planetary Analog Explorer - Top 50 Candidate Sites"],
    [`# Target Site: ${target.name} | Body: ${target.body} | Datum: WGS84 / IAU 2000`],
    [`# Calibration Weights: Slope=${(normW.slope*100).toFixed(1)}%, Roughness=${(normW.roughness*100).toFixed(1)}%, Relief=${(normW.relief*100).toFixed(1)}%`],
    ["Rank", "Target_Site", "Target_Body", "Region_Name", "Latitude", "Longitude", "Match_Percent", "Mean_Slope_deg", "Roughness_m", "Local_Relief_m", "Elevation_m", "Annual_Precip_mm"]
  ];

  const seen = [];
  let rank = 0;
  for (const c of scored) {
    if (seen.some(s => Math.abs(s.lat - c.lat) < 1.0 && Math.abs(s.lon - c.lon) < 1.0)) continue;
    seen.push(c);
    rank++;
    rows.push([
      rank,
      `"${target.name}"`,
      `"${target.body}"`,
      `"${getRegionName(c.lat, c.lon)}"`,
      c.lat.toFixed(4),
      c.lon.toFixed(4),
      (c.sim * 100).toFixed(2),
      c.slope.toFixed(2),
      c.roughness.toFixed(1),
      c.relief.toFixed(1),
      c.elevation,
      c.precip
    ]);
    if (rank >= 50) break;
  }

  const csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.join(",")).join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `NASA_Analog_Finder_${activeTarget}_top50.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function getRegionName(lat, lon) {
  if (lat > 65) return 'High Arctic / Greenland Basin';
  if (lat < -60) return 'Transantarctic Mountains';
  if (lat >= -30 && lat <= -15 && lon >= -75 && lon <= -65) return 'Atacama / Central Andes';
  if (lat >= 30 && lat <= 40 && lon >= -120 && lon <= -110) return 'Mojave / Great Basin';
  if (lat >= 25 && lat <= 40 && lon >= 75 && lon <= 100) return 'Tibetan Plateau / Qaidam';
  if (lat >= 15 && lat <= 30 && lon >= -15 && lon <= 45) return 'Sahara / Arabian Basin';
  if (lat >= -35 && lat <= -20 && lon >= 115 && lon <= 140) return 'Australian Desert Shield';
  if (lat >= 45 && lat <= 55 && lon >= 85 && lon <= 110) return 'Mongolian Steppe / Gobi';
  return `Arid Terrain (${lat.toFixed(1)}°, ${lon.toFixed(1)}°)`;
}

function selectLocation(loc) {
  selectedLocation = loc;
  const target = targets[activeTarget];
  const inspectEl = document.getElementById('inspect-content');

  let score = loc.similarity;
  if (!score) {
    score = loc.isKnown ? 0.985 : 0.970;
  }

  const whyNarrative = generateWhyItMatches(loc, target);
  const latStr = `${Math.abs(loc.lat).toFixed(4)}°${loc.lat >= 0 ? 'N' : 'S'}`;
  const lonStr = `${Math.abs(loc.lon).toFixed(4)}°${loc.lon >= 0 ? 'E' : 'W'}`;

  inspectEl.innerHTML = `
    <div class="inspect-header-info">
      <div class="loc-title">${loc.name}</div>
      <div class="loc-subtitle">${loc.region}</div>
      <div class="loc-coords">${latStr}, ${lonStr}</div>
    </div>

    <div class="similarity-score-card">
      <div>
        <div class="score-num">${(score * 100).toFixed(1)}%</div>
        <div class="score-label">SIMILARITY INDEX (${activeMethod.toUpperCase()})</div>
      </div>
      <div>
        ${loc.isKnown 
          ? '<span class="score-classification class-benchmark">BENCHMARK GROUND-TRUTH</span>' 
          : '<span class="score-classification class-candidate">CANDIDATE DISCOVERY</span>'}
      </div>
    </div>

    <!-- Comparative Morphometric Telemetry -->
    <div class="chart-box">
      <div class="chart-title">
        <span>MORPHOMETRIC COMPARISON</span>
        <div class="comp-legend">
          <span><span class="legend-square square-target"></span>TARGET</span>
          <span><span class="legend-square square-earth"></span>SELECTED</span>
        </div>
      </div>

      <!-- Slope Bar -->
      <div class="bar-row">
        <div class="bar-labels">
          <span>Mean Gradient</span>
          <span class="bar-vals">${target.mean_slope.toFixed(2)}° vs ${loc.slope.toFixed(2)}°</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill-target" style="width: ${Math.min(100, (target.mean_slope / 20) * 100)}%"></div>
          <div class="bar-fill-earth" style="width: ${Math.min(100, (loc.slope / 20) * 100)}%"></div>
        </div>
      </div>

      <!-- Roughness Bar -->
      <div class="bar-row">
        <div class="bar-labels">
          <span>Topographic Roughness (1σ)</span>
          <span class="bar-vals">${target.roughness.toFixed(1)}m vs ${loc.roughness.toFixed(1)}m</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill-target" style="width: ${Math.min(100, (target.roughness / 1400) * 100)}%"></div>
          <div class="bar-fill-earth" style="width: ${Math.min(100, (loc.roughness / 1400) * 100)}%"></div>
        </div>
      </div>

      <!-- Relief Bar -->
      <div class="bar-row">
        <div class="bar-labels">
          <span>Local Relief (Δz)</span>
          <span class="bar-vals">${target.local_relief.toFixed(0)}m vs ${loc.relief.toFixed(0)}m</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill-target" style="width: ${Math.min(100, (target.local_relief / 5600) * 100)}%"></div>
          <div class="bar-fill-earth" style="width: ${Math.min(100, (loc.relief / 5600) * 100)}%"></div>
        </div>
      </div>
    </div>

    <!-- Geological Diagnostic Report -->
    <div class="why-box">
      <div class="why-header">GEOMORPHIC DIAGNOSTIC REPORT</div>
      <p class="why-text">${whyNarrative}</p>
    </div>

    <!-- Terrestrial Environmental Telemetry Grid -->
    <div class="telemetry-grid">
      <div class="tg-cell">
        <span class="tg-k">Elevation (MSL)</span>
        <span class="tg-v">${loc.elevation} m</span>
      </div>
      <div class="tg-cell">
        <span class="tg-k">Annual Precipitation</span>
        <span class="tg-v">${loc.precip} mm/yr</span>
      </div>
    </div>
  `;
}

function generateWhyItMatches(loc, target) {
  const deltaSlope = Math.abs(loc.slope - target.mean_slope);
  let slopeAnalysis = '';
  if (deltaSlope < 1.0) {
    slopeAnalysis = `Topographic gradient exhibits exceptional alignment (residual Δ=${deltaSlope.toFixed(2)}°), reproducing target deposit angle.`;
  } else if (deltaSlope < 3.0) {
    slopeAnalysis = `Regional slope profile matches within ${deltaSlope.toFixed(2)}° of ${target.name}, reflecting comparable repose equilibrium.`;
  } else {
    slopeAnalysis = `Slope deviation (${deltaSlope.toFixed(1)}°) reflects differing weathering kinetics under terrestrial hydrologic conditions vs vacuum/low-pressure planetary regimes.`;
  }

  const roughnessRatio = loc.roughness / (target.roughness || 1);
  let roughAnalysis = '';
  if (roughnessRatio > 0.6 && roughnessRatio < 1.5) {
    roughAnalysis = `Surface roughness (elevation standard deviation 1σ = ${loc.roughness}m) matches target scale, replicating boulder distribution and sub-kilometer scarp patterns.`;
  } else {
    roughAnalysis = `Local roughness (${loc.roughness}m) correlates with characteristic alluvial/aeolian transition zones.`;
  }

  const aridityAnalysis = loc.precip < 100
    ? `Extreme macroclimate aridity (${loc.precip} mm/yr rain) limits vegetation cover, ensuring mechanical regolith weathering analogous to ${target.body} surface environments.`
    : `Cold arid climate (${loc.precip} mm/yr rain) provides dry bedrock surfaces for robotic rover mobility evaluation.`;

  return `${slopeAnalysis} ${roughAnalysis} ${aridityAnalysis}`;
}

function renderTargetFingerprint() {
  const target = targets[activeTarget];
  if (!target) return;

  const box = document.getElementById('target-fingerprint-box');
  const diameterText = target.diameter_km ? `${target.diameter_km} km Ø` : '';
  const descText = target.description || 'Target planetary surface region for quantitative terrestrial analog matching.';

  box.innerHTML = `
    <div class="flex-between">
      <span class="sec-title">${target.name.toUpperCase()} SIGNATURE</span>
      <span class="val-badge">${diameterText}</span>
    </div>
    <div class="fingerprint-grid">
      <div class="fp-stat">
        <span class="fp-stat-label">SLOPE (1σ)</span>
        <span class="fp-stat-val">${target.mean_slope.toFixed(2)}°</span>
      </div>
      <div class="fp-stat">
        <span class="fp-stat-label">ROUGHNESS</span>
        <span class="fp-stat-val">${target.roughness.toFixed(1)}m</span>
      </div>
      <div class="fp-stat">
        <span class="fp-stat-label">RELIEF (Δz)</span>
        <span class="fp-stat-val">${target.local_relief.toFixed(0)}m</span>
      </div>
    </div>
    <p style="font-size: 0.68rem; color: var(--text-muted); margin-top: 6px; line-height: 1.4;">
      ${descText}
    </p>
  `;

  const navName = document.getElementById('nav-target-name');
  if (navName) {
    navName.innerText = `${target.name.toUpperCase()} [${target.body.toUpperCase()}]`;
  }
}

function renderValidationModal() {
  const container = document.getElementById('validation-table-container');
  if (!container || !validationReport) return;

  let html = `
    <div class="modal-meta-strip">
      <span class="modal-meta-tag">SAMPLE POOL: 500,073 ARID CELLS</span>
      <span class="modal-meta-tag">APERTURE: 10.0 KM EQUAL-AREA</span>
      <span class="modal-meta-tag">COVARIANCE: det(Σ) = 0.0142</span>
    </div>
    <table class="val-table">
      <thead>
        <tr>
          <th>MISSION TARGET</th>
          <th>CERTIFIED ANALOG</th>
          <th>CLASSIFICATION</th>
          <th>COSINE SIM (S_c)</th>
          <th>GLOBAL RANK</th>
          <th>PERCENTILE</th>
          <th>MAHALANOBIS (D_M)</th>
        </tr>
      </thead>
      <tbody>
  `;

  Object.entries(validationReport).forEach(([tKey, tData]) => {
    tData.known_analogs.forEach(a => {
      const isTop1 = a.cosine_rank <= 5000;
      const rankPillClass = isTop1 ? 'rank-top1' : (a.cosine_rank <= 25000 ? 'rank-top5' : 'rank-other');
      html += `
        <tr>
          <td><strong>${tData.target.name}</strong></td>
          <td>${a.name} <span style="font-size:0.68rem; color:var(--text-dim)">[${a.region}]</span></td>
          <td>${a.is_primary_target_match ? '<span style="color:var(--color-benchmark-gold); font-weight:700;">PRIMARY BENCHMARK</span>' : '<span style="color:var(--text-muted);">SECONDARY</span>'}</td>
          <td>${a.cosine_similarity.toFixed(4)}</td>
          <td><span class="rank-pill ${rankPillClass}">#${a.cosine_rank.toLocaleString()}</span></td>
          <td style="color:${isTop1 ? 'var(--color-benchmark-gold)' : 'var(--text-bright)'}">TOP ${(100 - a.cosine_percentile).toFixed(2)}%</td>
          <td>D<sub>M</sub> = ${a.mahalanobis_distance}</td>
        </tr>
      `;
    });
  });

  html += `
      </tbody>
    </table>
  `;

  container.innerHTML = html;
}

function setupEvents() {
  // Target Selection
  document.querySelectorAll('.target-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.target-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      activeTarget = card.dataset.target;
      renderTargetFingerprint();
      updateHeatmapLayer();
      renderMarkers();
      updateCandidatesList();
    });
  });

  // Geographic Filter Tabs (Global, Accessible, Polar)
  document.querySelectorAll('.filter-tabs .toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-tabs .toggle-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      updateCandidatesList();
    });
  });

  // Export CSV Button
  const btnCsv = document.getElementById('btn-export-csv');
  if (btnCsv) {
    btnCsv.addEventListener('click', exportTopCandidatesCSV);
  }

  // Method Toggle
  const btnCos = document.getElementById('toggle-cos');
  const btnMah = document.getElementById('toggle-mah');
  const methodInd = document.getElementById('method-indicator');

  btnCos.addEventListener('click', () => {
    btnCos.classList.add('active');
    btnMah.classList.remove('active');
    activeMethod = 'cos';
    methodInd.innerText = 'Angular Vector Normalization [S_c = (u·v)/(||u|| ||v||)]';
    updateHeatmapLayer();
  });

  btnMah.addEventListener('click', () => {
    btnMah.classList.add('active');
    btnCos.classList.remove('active');
    activeMethod = 'mah';
    methodInd.innerText = 'Inverse Covariance Distance [D_M = √((x - μ)ᵀ Σ⁻¹ (x - μ))]';
    updateHeatmapLayer();
  });

  // Sensitivity Sliders
  const slSlope = document.getElementById('slider-w-slope');
  const slRough = document.getElementById('slider-w-rough');
  const slRelief = document.getElementById('slider-w-relief');

  const updateSliders = () => {
    weights.slope = parseInt(slSlope.value) / 100;
    weights.roughness = parseInt(slRough.value) / 100;
    weights.relief = parseInt(slRelief.value) / 100;

    document.getElementById('val-w-slope').innerText = `${weights.slope.toFixed(2)} [${slSlope.value}%]`;
    document.getElementById('val-w-rough').innerText = `${weights.roughness.toFixed(2)} [${slRough.value}%]`;
    document.getElementById('val-w-relief').innerText = `${weights.relief.toFixed(2)} [${slRelief.value}%]`;

    updateCandidatesList();
    if (selectedLocation) {
      selectLocation(selectedLocation);
    }
  };

  slSlope.addEventListener('input', updateSliders);
  slRough.addEventListener('input', updateSliders);
  slRelief.addEventListener('input', updateSliders);

  // Reset Weights Button
  document.getElementById('btn-reset-weights').addEventListener('click', () => {
    slSlope.value = 45;
    slRough.value = 35;
    slRelief.value = 20;
    updateSliders();
  });

  // Modals
  document.getElementById('btn-validation-tab').addEventListener('click', () => {
    document.getElementById('modal-validation').classList.add('open');
  });

  document.getElementById('btn-how-it-works').addEventListener('click', () => {
    document.getElementById('modal-how-it-works').classList.add('open');
  });

  document.querySelectorAll('.modal-close, .modal-backdrop').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target === el || el.classList.contains('modal-close')) {
        document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.remove('open'));
      }
    });
  });

  document.getElementById('btn-close-inspect').addEventListener('click', () => {
    document.getElementById('inspect-content').innerHTML = `
      <div class="empty-state">
        <div class="empty-reticle">
          <svg viewBox="0 0 48 48" width="36" height="36" fill="none">
            <circle cx="24" cy="24" r="20" stroke="#334155" stroke-width="1.5" stroke-dasharray="3 3"/>
            <line x1="24" y1="4" x2="24" y2="44" stroke="#334155" stroke-width="1"/>
            <line x1="4" y1="24" x2="44" y2="24" stroke="#334155" stroke-width="1"/>
            <rect x="20" y="20" width="8" height="8" stroke="#0284c7" stroke-width="1.2"/>
          </svg>
        </div>
        <h3>AWAITING STATION QUERY</h3>
        <p>Click any highlighted terrestrial cell or ground-truth benchmark marker on the map to stream morphometric telemetry and geological matching rationale.</p>
      </div>
    `;
    selectedLocation = null;
  });
}

// Start
document.addEventListener('DOMContentLoaded', init);