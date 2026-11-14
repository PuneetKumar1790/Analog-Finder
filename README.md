# Analog Finder (NASA Space Apps Challenge 2026)

> **"Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars."**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel%20Production-38bdf8?style=for-the-badge&logo=vercel)](https://analog-finder-amber.vercel.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-PuneetKumar1790%2FAnalog--Finder-181717?style=for-the-badge&logo=github)](https://github.com/PuneetKumar1790/Analog-Finder)
[![Open In Colab](https://img.shields.io/badge/Open%20In%20Colab-Google%20Colab-F9AB00?style=for-the-badge&logo=googlecolab)](https://colab.research.google.com/github/PuneetKumar1790/Analog-Finder/blob/main/notebooks/Analog_Finder_Colab.ipynb)

🌐 **Live Web Application:** [https://analog-finder-amber.vercel.app/](https://analog-finder-amber.vercel.app/)

*Analog Finder* is an open-source, reproducible geospatial analysis pipeline and interactive web application that quantitatively matches candidate lunar and Martian exploration sites against terrestrial environments using standardized 10-kilometer terrain fingerprints and macroclimate constraints.

---

## 🌌 Key Highlights & Differentiation
- **Authoritative Planetary Datasets:** Direct integration of NASA Mars Global Surveyor (MGS MOLA), NASA Lunar Reconnaissance Orbiter (LRO LOLA), NOAA ETOPO 2022, and WorldClim 2.1.
- **Scale-Matched Geomorphometry:** Resolves the fractal scale dilemma by standardizing all three celestial bodies at a uniform **~10 km spatial block scale**.
- **Collinearity De-correlation:** Employs Mahalanobis distance with precision covariance inversion to remove the 98.7% collinearity between roughness and local relief.
- **Client-Side Real-Time Re-weighting:** Dragging feature sliders recalculates similarity across 2,500 candidate cells in **$< 2\text{ ms}$** in the browser.
- **Ground Truth Validation Table:** Validated against 6 recognized terrestrial analogs (Atacama ranks in Top 0.01% for Jezero; Iceland Highlands ranks in Top 0.01% for Shackleton).
- **Novel Discoveries:** Uncovers 3 new planetary analog candidates per target (e.g. Qaidam Basin, San Juan Precordillera, Ellesmere Island Highlands).
- **Zero-Backend Static Architecture:** Shipped static payload is only **3.09 MB** (budget: < 50 MB) with each raster overlay $< 1\text{ MB}$ (budget: < 10 MB).

---

## 🏛️ Project Architecture

```
Analog Finder/
├── pipeline/                     # Reproducible Python Geospatial Pipeline
│   ├── config.yaml               # Central configuration, weights, and verified URLs
│   ├── 01_fetch.py               # Streamlined fetching of MOLA, LOLA, and WorldClim rasters
│   ├── 02_features.py            # ~10 km block feature extraction (slope, roughness, relief)
│   ├── 03_similarity.py          # Z-score normalization, Cosine & Mahalanobis similarity
│   ├── 04_validate.py            # Ground truth validation against 6 analogs & discovery
│   └── 05_export.py              # Generates 6x PNG overlays (<1MB) and JSON metadata
├── data_raw/                     # Cached raw data (MOLA, LOLA, WorldClim, ETOPO)
├── data_processed/               # Compressed NumPy feature arrays and JSON reports
├── data_out/                     # Static web data bundle (PNG overlays, JSON tables)
├── web/                          # Static Web Application (Vite + MapLibre GL)
│   ├── index.html                # Responsive UI with glassmorphic planetary panels
│   ├── style.css                 # Dark aerospace styling, responsive layout
│   ├── vercel.json               # 1-click Vercel deployment config
│   ├── src/main.js               # MapLibre GL controller & client-side re-weighting
│   └── public/data/              # Static data served to the map
├── .github/workflows/deploy.yml  # Automated GitHub Pages CI/CD workflow
├── DATA_SOURCES.md               # Complete verified citations, DOIs, and URLs
├── METHOD.md                     # Mathematical formulation and scientific limitations
├── DEPLOYMENT.md                 # Deployment guide for Vercel, GitHub Pages, and local
├── DEMO_SCRIPT.md                # 2-minute hackathon pitch script
└── README.md                     # Master documentation
```

---

## 🚀 Quickstart & Reproduction Guide

### Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- Tested on: Windows 10, Dual-Core i3, 12 GB RAM (runs in $< 3\text{ minutes}$ total).

### 1. Python Environment Setup
```powershell
pip install numpy scipy pandas pyyaml rasterio
```

### 2. Run Pipeline (Google Colab or Local Terminal)
```powershell
# Step 1: Fetch target planetary and climate data
python pipeline/01_fetch.py

# Step 2: Extract standardized features at ~10 km block scale
python pipeline/02_features.py

# Step 3: Compute Cosine & Mahalanobis similarity across 500,073 cells
python pipeline/03_similarity.py

# Step 4: Run ground truth validation and novel analog discovery
python pipeline/04_validate.py

# Step 5: Export lightweight web assets (< 1 MB overlays)
python pipeline/05_export.py
```

### 3. Launch Web Application
```powershell
cd web
npm install
npm run dev
```
Open your browser to `http://localhost:5173/`.

---

## 📊 Ground Truth Validation Results

Evaluated across **500,073 valid arid Earth cells**:

| Target Site | Known Earth Analog | Target Match | Cosine Similarity | Earth Rank | Percentile |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Mars — Jezero Crater** | **Atacama Desert (Yungay)** | Primary | **0.9908** | **#51** | **Top 0.01%** |
| | **Mojave Desert (Cima/Kelso)** | Primary | **0.9805** | **#419** | **Top 0.08%** |
| | **Iceland Highlands (Askja)** | Primary | **0.9719** | **#2,674** | **Top 0.53%** |
| | **Death Valley (Badwater)** | Primary | **0.9629** | **#10,633** | **Top 2.13%** (Mahalanobis Top 0.07%) |
| **Mars — Gale Crater** | **Death Valley (Badwater)** | Primary | **0.9982** | **#4,027** | **Top 0.81%** (Mahalanobis Top 0.08%) |
| | **Mojave Desert (Cima/Kelso)** | Primary | **0.9963** | **#12,734** | **Top 2.55%** (Mahalanobis Top 0.11%) |
| | **Atacama Desert (Yungay)** | Primary | **0.9938** | **#26,244** | **Top 5.25%** |
| **Moon — Shackleton Rim** | **Iceland Highlands (Askja)** | Primary | **0.9996** | **#41** | **Top 0.01%** |
| | **Mojave Desert (Cima/Kelso)** | Volcanic | **0.9995** | **#54** | **Top 0.01%** |
| | **Death Valley (Badwater)** | Extreme | **0.9984** | **#237** | **Top 0.05%** |
| | **McMurdo Dry Valleys** | Primary | **0.9958** | **#1,180** | **Top 0.24%** (Steepest Earth analog: 8.52°) |

---

## 🔭 Discovered Novel Analog Candidates

1. **For Jezero Crater:** **Qaidam Basin Yardangs & Clay Playas (Tibetan Plateau, China)** — high-altitude enclosed basin with lacustrine evaporites and wind-carved yardang deflation.
2. **For Gale Crater:** **San Juan Precordillera (Argentina)** — dry intermontane basin replicating Mount Sharp's 5.5 km vertical relief and layered cuestas.
3. **For Shackleton Crater Rim:** **Bowers Mountains Nunataks (Antarctica)** and **Quttinirpaaq Highlands (High Canadian Arctic)** — bare fractured bedrock peaks emerging from polar ice sheets.

---

## 🌐 1-Click Deployment
- **Vercel:** Import repository, set root to `web`, build command `npm run build`, output `dist`.
- **GitHub Pages:** Automated via [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).
- **Details:** See [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

## 📜 Scientific Methodology & Integrity
- Mathematical formulations, covariance de-correlation, and honest limitations (atmospheric vacuum vs greenhouse effect, absence of mineralogy) are detailed in [`METHOD.md`](METHOD.md).
- Full dataset citations, direct endpoints, and DOIs are in [`DATA_SOURCES.md`](DATA_SOURCES.md).
- 2-minute hackathon pitch script is in [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md).
