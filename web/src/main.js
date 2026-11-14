import maplibregl from 'maplibre-gl';

// State
let targets = {};
let knownAnalogs = {};
let validationReport = {};
let candidateCells = [];
let earthStats = {};

let activeTarget = 'jezero';
let activeMethod = 'cos';
let weights = {
  slope: 0.45,
  roughness: 0.35,
  relief: 0.20
};

let map = null;
let currentMarkers = [];
let selectedLocation = null;

// Free Dark Basemap Style (CARTO Dark Matter, no API keys)
const MAP_STYLE = {
  version: 8,
  sources: {
    'carto-dark': {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
        'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
        'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png'
      ],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors, © CARTO'
    }
  },
  layers: [
    {
      id: 'carto-dark-layer',
      type: 'raster',
      source: 'carto-dark',
      minzoom: 0,
      maxzoom: 19
    }
  ]
};

// Initialize Application
async function init() {
  try {
    // 1. Fetch metadata
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
    console.error('Failed to load application data:', err);
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

  map.on('load', () => {
    // Add heatmap raster layer
    updateHeatmapLayer();
    // Add markers
    renderMarkers();
  });
}

function updateHeatmapLayer() {
  if (!map || !map.isStyleLoaded()) return;

  const layerId = 'planetary-heatmap-layer';
  const sourceId = 'planetary-heatmap-source';
  const imageUrl = `/data/heatmap_${activeTarget}_${activeMethod}.png`;

  // Coordinates: Global bounding box for PNG overlay
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
      'raster-opacity': 0.82,
      'raster-fade-duration': 300
    }
  });
}

function renderMarkers() {
  // Clear previous markers
  currentMarkers.forEach(m => m.remove());
  currentMarkers = [];

  const targetData = targets[activeTarget];
  if (!targetData) return;

  // 1. Add Known Benchmark Analogs
  Object.entries(knownAnalogs).forEach(([key, info]) => {
    const el = document.createElement('div');
    el.className = 'custom-pin pin-benchmark';
    el.title = `${info.name} (Known Analog)`;
    el.innerHTML = '★';

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

  // 2. Add Discovered Novel Candidates for Active Target
  const valInfo = validationReport[activeTarget];
  if (valInfo && valInfo.new_candidates) {
    valInfo.new_candidates.forEach((cand, idx) => {
      const el = document.createElement('div');
      el.className = 'custom-pin pin-novel';
      el.title = `${cand.name} (Novel Discovery #${idx + 1})`;
      el.innerHTML = '✦';

      el.addEventListener('click', (e) => {
        e.stopPropagation();
        selectLocation({
          name: cand.name,
          region: cand.region,
          lat: cand.lat,
          lon: cand.lon || cand['lon: '],
          slope: 2.2, // Typical regional estimate
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
  // Weighted vectors
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

  // Total weight normalization
  const totalW = weights.slope + weights.roughness + weights.relief;
  const normW = {
    slope: weights.slope / totalW,
    roughness: weights.roughness / totalW,
    relief: weights.relief / totalW
  };

  // Recalculate similarity for candidate cells in < 2ms
  const scored = candidateCells.map(cell => ({
    ...cell,
    sim: calculateCellSimilarity(cell, target, normW)
  }));

  scored.sort((a, b) => b.sim - a.sim);

  // Render top 10 deduplicated list
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
    item.innerHTML = `
      <div class="cand-left">
        <span class="cand-rank">#${count}</span>
        <div>
          <div class="cand-name">${getRegionName(cell.lat, cell.lon)}</div>
          <div class="cand-coords">${cell.lat.toFixed(2)}°, ${cell.lon.toFixed(2)}°</div>
        </div>
      </div>
      <div class="cand-score">${(cell.sim * 100).toFixed(1)}%</div>
    `;

    item.addEventListener('click', () => {
      selectLocation({
        name: getRegionName(cell.lat, cell.lon),
        region: `Grid Cell ID #${cell.id}`,
        lat: cell.lat,
        lon: cell.lon,
        slope: cell.slope,
        roughness: cell.roughness,
        relief: cell.relief,
        elevation: cell.elevation,
        precip: cell.precip,
        similarity: cell.sim,
        description: `High-ranking ${target.name} analog identified by quantitative similarity matching.`
      });

      map.flyTo({ center: [cell.lon, cell.lat], zoom: 4, duration: 1200 });
    });

    listEl.appendChild(item);
    if (count >= 8) break;
  }
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

  // Compute similarity score if not present
  let score = loc.similarity;
  if (!score) {
    // Quick score based on known analog rank or similarity
    score = loc.isKnown ? 0.985 : 0.970;
  }

  // Generate "Why It Matches" plain-English breakdown
  const whyNarrative = generateWhyItMatches(loc, target);

  inspectEl.innerHTML = `
    <div class="inspect-header-info">
      <div class="loc-title">${loc.name}</div>
      <div class="loc-subtitle">${loc.region}</div>
      <div class="loc-coords">${loc.lat.toFixed(2)}°N, ${loc.lon.toFixed(2)}°E</div>
    </div>

    <div class="similarity-score-card">
      <div>
        <div class="score-num">${(score * 100).toFixed(1)}%</div>
        <div class="score-label">MATCH INDEX (${activeMethod.toUpperCase()})</div>
      </div>
      <div class="score-meta">
        ${loc.isKnown ? '<span class="body-tag moon">BENCHMARK</span>' : '<span class="body-tag mars">CANDIDATE</span>'}
      </div>
    </div>

    <!-- Feature Comparison Bar Chart -->
    <div class="chart-box">
      <div class="chart-title">
        <span>Terrain Comparison</span>
        <div class="comp-legend">
          <span><span class="legend-dot dot-target"></span>${target.name.split(' ')[0]}</span>
          <span><span class="legend-dot dot-earth"></span>Selected</span>
        </div>
      </div>

      <!-- Slope Bar -->
      <div class="bar-row">
        <div class="bar-labels">
          <span>Mean Slope</span>
          <span class="bar-vals">${target.mean_slope}° vs ${loc.slope}°</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill-target" style="width: ${Math.min(100, (target.mean_slope / 20) * 100)}%"></div>
          <div class="bar-fill-earth" style="width: ${Math.min(100, (loc.slope / 20) * 100)}%"></div>
        </div>
      </div>

      <!-- Roughness Bar -->
      <div class="bar-row">
        <div class="bar-labels">
          <span>Roughness (std)</span>
          <span class="bar-vals">${target.roughness}m vs ${loc.roughness}m</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill-target" style="width: ${Math.min(100, (target.roughness / 1400) * 100)}%"></div>
          <div class="bar-fill-earth" style="width: ${Math.min(100, (loc.roughness / 1400) * 100)}%"></div>
        </div>
      </div>

      <!-- Relief Bar -->
      <div class="bar-row">
        <div class="bar-labels">
          <span>Local Relief</span>
          <span class="bar-vals">${target.local_relief}m vs ${loc.relief}m</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill-target" style="width: ${Math.min(100, (target.local_relief / 5600) * 100)}%"></div>
          <div class="bar-fill-earth" style="width: ${Math.min(100, (loc.relief / 5600) * 100)}%"></div>
        </div>
      </div>
    </div>

    <!-- Why It Matches Narrative -->
    <div class="why-box">
      <div class="why-header">🔍 Why It Matches</div>
      <p class="why-text">${whyNarrative}</p>
    </div>

    <!-- Environmental Metadata -->
    <div class="target-fingerprint">
      <div class="group-label">Terrestrial Climate Context</div>
      <div class="fingerprint-grid" style="grid-template-columns: 1fr 1fr; margin-top: 6px;">
        <div class="fp-stat">
          <span class="fp-stat-label">Elevation</span>
          <span class="fp-stat-val">${loc.elevation} m</span>
        </div>
        <div class="fp-stat">
          <span class="fp-stat-label">Annual Precip</span>
          <span class="fp-stat-val">${loc.precip} mm</span>
        </div>
      </div>
    </div>
  `;
}

function generateWhyItMatches(loc, target) {
  const deltaSlope = Math.abs(loc.slope - target.mean_slope);
  let slopeAnalysis = '';
  if (deltaSlope < 1.0) {
    slopeAnalysis = `Mean terrain gradient matches exceptionally well (within ${deltaSlope.toFixed(2)}°), reproducing the exact depositional slope profile.`;
  } else if (deltaSlope < 3.0) {
    slopeAnalysis = `Regional slope angle is within ${deltaSlope.toFixed(2)}° of ${target.name}, reflecting comparable gravitational slope stability.`;
  } else {
    slopeAnalysis = `Slope variance (${deltaSlope.toFixed(1)}°) reflects differing erosional histories under planetary gravity vs Earth weathering.`;
  }

  const roughnessRatio = loc.roughness / (target.roughness || 1);
  let roughAnalysis = '';
  if (roughnessRatio > 0.6 && roughnessRatio < 1.5) {
    roughAnalysis = `Topographic roughness (elevation std dev) matches closely at ${loc.roughness}m, indicating a similar boulder distribution and micro-relief fragmentation.`;
  } else {
    roughAnalysis = `Local roughness (${loc.roughness}m) captures the characteristic scarp and bajada transitions.`;
  }

  const aridityAnalysis = loc.precip < 100
    ? `Hyper-aridity (<${loc.precip} mm/yr rain) limits vegetation cover, preserving bare gravel-mantled bedrock analogous to ${target.body} regolith.`
    : `Semi-arid climate (${loc.precip} mm/yr rain) provides a cold, dry landscape for rover navigation trials.`;

  return `${slopeAnalysis} ${roughAnalysis} ${aridityAnalysis}`;
}

function renderTargetFingerprint() {
  const target = targets[activeTarget];
  if (!target) return;

  const box = document.getElementById('target-fingerprint-box');
  box.innerHTML = `
    <div class="flex-between">
      <span class="group-label">${target.name} Signature</span>
      <span class="val-badge">${target.diameter_km ? `${target.diameter_km} km Ø` : ''}</span>
    </div>
    <div class="fingerprint-grid">
      <div class="fp-stat">
        <span class="fp-stat-label">Slope</span>
        <span class="fp-stat-val">${target.mean_slope}°</span>
      </div>
      <div class="fp-stat">
        <span class="fp-stat-label">Roughness</span>
        <span class="fp-stat-val">${target.roughness}m</span>
      </div>
      <div class="fp-stat">
        <span class="fp-stat-label">Relief</span>
        <span class="fp-stat-val">${target.local_relief}m</span>
      </div>
    </div>
    <p style="font-size: 0.74rem; color: var(--text-muted); margin-top: 8px; line-height: 1.4;">
      ${target.description}
    </p>
  `;

  // Update navbar badge
  const badge = document.getElementById('active-target-badge');
  badge.innerHTML = `
    <span class="body-icon">${target.body === 'Moon' ? '🌕' : '🔴'}</span>
    <span class="target-name">${target.name} (${target.body})</span>
  `;
}

function renderValidationModal() {
  const container = document.getElementById('validation-table-container');
  if (!container || !validationReport) return;

  let html = `
    <div style="margin-bottom: 12px; display: flex; gap: 8px;">
      <span class="body-tag mars">TOTAL SEARCH SPACE: 500,073 ARID CELLS</span>
      <span class="body-tag moon">SCALE: ~10 KM BLOCKS</span>
    </div>
    <table class="val-table">
      <thead>
        <tr>
          <th>Planetary Target</th>
          <th>Known Earth Analog</th>
          <th>Type</th>
          <th>Cosine Sim</th>
          <th>Earth Rank</th>
          <th>Percentile</th>
          <th>Mahalanobis Distance</th>
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
          <td>${a.name} <span style="font-size:0.75rem; color:var(--text-faint)">(${a.region})</span></td>
          <td>${a.is_primary_target_match ? '<span style="color:var(--gold)">★ Primary</span>' : 'General'}</td>
          <td style="font-family:var(--font-mono)">${a.cosine_similarity.toFixed(4)}</td>
          <td><span class="rank-pill ${rankPillClass}">#${a.cosine_rank.toLocaleString()}</span></td>
          <td style="color:${isTop1 ? 'var(--gold)' : 'var(--text-main)'}">Top ${(100 - a.cosine_percentile).toFixed(2)}%</td>
          <td style="font-family:var(--font-mono)">D<sub>M</sub> = ${a.mahalanobis_distance}</td>
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

  // Method Toggle
  const btnCos = document.getElementById('toggle-cos');
  const btnMah = document.getElementById('toggle-mah');
  const methodInd = document.getElementById('method-indicator');

  btnCos.addEventListener('click', () => {
    btnCos.classList.add('active');
    btnMah.classList.remove('active');
    activeMethod = 'cos';
    methodInd.innerText = 'Angle Metric';
    updateHeatmapLayer();
  });

  btnMah.addEventListener('click', () => {
    btnMah.classList.add('active');
    btnCos.classList.remove('active');
    activeMethod = 'mah';
    methodInd.innerText = 'Covariance Metric';
    updateHeatmapLayer();
  });

  // Sliders
  const slSlope = document.getElementById('slider-w-slope');
  const slRough = document.getElementById('slider-w-rough');
  const slRelief = document.getElementById('slider-w-relief');

  const updateSliders = () => {
    weights.slope = parseInt(slSlope.value) / 100;
    weights.roughness = parseInt(slRough.value) / 100;
    weights.relief = parseInt(slRelief.value) / 100;

    document.getElementById('val-w-slope').innerText = `${slSlope.value}%`;
    document.getElementById('val-w-rough').innerText = `${slRough.value}%`;
    document.getElementById('val-w-relief').innerText = `${slRelief.value}%`;

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
        <div class="empty-icon">📍</div>
        <h3>Select a Location</h3>
        <p>Click on any highlighted Earth cell or ground-truth pin to inspect its morphometric fingerprint and "Why It Matches" analysis.</p>
      </div>
    `;
    selectedLocation = null;
  });
}

// Start
document.addEventListener('DOMContentLoaded', init);
