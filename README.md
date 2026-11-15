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
- **Client-Side Real-Time Re-weighting:** Dragging feature sliders recalculates similarity across 2,500 pre-filtered candidate cells in **$< 2\text{ ms}$** in JavaScript, while the full **500,073-cell** database is evaluated offline in Python.
- **Ground Truth Validation Table:** Benchmarked against **7 literature-recognized planetary analogs** (Atacama ranks in Top 0.01% for Jezero; Iceland Highlands ranks in Top 0.01% for Shackleton).
- **Controls & Robustness Verification:** Incorporates 6 negative control regions, 1,000-cell random arid baseline, feature ablation, and 200 random weight vector perturbations.
- **Algorithmic Discoveries:** Uncovers top-ranked terrestrial candidate clusters not previously identified as primary targets (e.g. Qaidam Basin, San Juan Precordillera, Ellesmere Island Highlands).
- **Zero-Backend Static Architecture:** Shipped static payload is only **3.11 MB** (budget: < 50 MB) with each raster overlay $< 1\text{ MB}$ (budget: < 10 MB).

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

## 📊 Ground Truth Validation Results (7 Literature Analogs)

Evaluated across all **500,073 valid arid Earth cells**:

| Target Site | Literature-Recognized Earth Analog | Role / Context | Cosine Sim | Global Rank | Percentile | Mahalanobis (Target $D_M$, Rank) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Mars — Jezero Crater** | **Atacama Desert (Yungay, Chile)** | Primary Analog | **0.9908** | **#51** | **Top 0.01%** | $D_M = 22.77$ (#1,122, Top 0.22%) |
| | **Mojave Desert (Cima/Kelso, USA)** | Rover Testbed | **0.9805** | **#419** | **Top 0.08%** | $D_M = 20.52$ (#275, Top 0.05%) |
| | **Iceland Highlands (Askja, Iceland)** | Volcanic / Basaltic | **0.9719** | **#2,674** | **Top 0.53%** | $D_M = 24.56$ (#4,296, Top 0.86%) |
| | **Death Valley (Badwater, USA)** | Graben / Fan | **0.9629** | **#10,633** | **Top 2.13%** | $D_M = 20.83$ (#332, Top 0.07%) |
| | **Haughton Impact Crater (Devon Island)** | Impact Structure | **0.8665** | **#161,800** | **Top 32.36%** | $D_M = 26.26$ (#18,944, Top 3.79%) |
| | **Kilbourne Hole Maar (New Mexico, USA)** | Apollo/Artemis Volcanic | **0.8637** | **#164,291** | **Top 32.85%** | $D_M = 25.06$ (#6,485, Top 1.30%) |
| **Mars — Gale Crater** | **Death Valley (Badwater, USA)** | Primary Analog | **0.9982** | **#4,027** | **Top 0.81%** | $D_M = 30.26$ (#401, Top 0.08%) |
| | **Mojave Desert (Cima/Kelso, USA)** | Rover Testbed | **0.9963** | **#12,734** | **Top 2.55%** | $D_M = 30.83$ (#551, Top 0.11%) |
| | **Atacama Desert (Yungay, Chile)** | Extreme Aridity | **0.9938** | **#26,244** | **Top 5.25%** | $D_M = 33.23$ (#2,093, Top 0.42%) |
| **Moon — Shackleton Rim** | **Iceland Highlands (Askja, Iceland)** | Primary Analog | **0.9996** | **#41** | **Top 0.01%** | $D_M = 33.38$ (#5,564, Top 1.11%) |
| | **Mojave Desert (Cima/Kelso, USA)** | Basaltic Ridge | **0.9995** | **#54** | **Top 0.01%** | $D_M = 29.33$ (#469, Top 0.09%) |
| | **Death Valley (Badwater, USA)** | Extreme Scarp | **0.9984** | **#237** | **Top 0.05%** | $D_M = 28.93$ (#372, Top 0.07%) |
| | **Atacama Desert (Yungay, Chile)** | Regolith Desiccation | **0.9964** | **#1,010** | **Top 0.20%** | $D_M = 31.73$ (#1,862, Top 0.37%) |
| | **McMurdo Dry Valleys (Antarctica)** | Polar Desert / High Slope | **0.9958** | **#1,180** | **Top 0.24%** | $D_M = 31.43$ (#1,547, Top 0.31%) |
| | **Haughton Impact Crater (Devon Island)** | Impact Structure | **0.7853** | **#168,388** | **Top 33.67%** | $D_M = 35.31$ (#25,903, Top 5.18%) |
| | **Kilbourne Hole Maar (New Mexico, USA)** | Volcanic Maar Rim | **0.7816** | **#170,899** | **Top 34.17%** | $D_M = 34.22$ (#10,418, Top 2.08%) |

---

## 🛡️ Negative Controls, Baseline & Robustness

### 1. Negative Controls (Expected Non-Analogs)
Flat, low-relief terrestrial regions tested to confirm the model does not produce false positives:

| Negative Control Region | Terrain Type | In Arid Mask? | Jezero Cosine | Global Rank | Percentile |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Lake Eyre Salt Playa (Australia)** | Hyper-flat salt playa | Yes | 0.5701 | **#495,905** | Bottom 0.83% of Earth |
| **Grand Erg Oriental (Sahara)** | Endless active dune sea | Yes | 0.7788 | **#406,681** | Top 81.32% (Bottom 19%) |
| **Argentine Pampas Flatlands** | Low-relief grassland | No (Mask-Free) | 0.7816 | **#404,799** | Top 80.95% (Bottom 19%) |
| **Simpson Desert Dunefield (Australia)** | Low-relief linear dunes | Yes | 0.8495 | **#326,602** | Top 65.31% (Bottom 35%) |
| **US High Plains (Kansas/Colorado)** | Flat agricultural steppe | Yes | 0.9080 | **#224,091** | Top 44.81% |
| **Qiangtang Steppe (Tibetan Plateau)** | High-altitude flat basin | Yes | 0.9200 | **#199,410** | Top 39.88% |

> **Key Takeaway:** Every negative control ranks below every primary analog (primary analogs place in the top 0.01% to 5.25%, whereas the best negative control only reaches top 39.88%).  
> *Note on limitation:* All six negative controls are low-relief flatlands, representing a baseline discriminative test.

### 2. Random Arid Baseline ($N=1,000$)
- **Jezero Crater:** Median Rank **#242,943** (48.6th percentile), 90th percentile: **#54,191** (10.8th percentile).
- **Gale Crater:** Median Rank **#245,618** (49.1th percentile), 90th percentile: **#54,820** (11.0th percentile).
- **Shackleton Rim:** Median Rank **#245,500** (49.1th percentile), 90th percentile: **#55,837** (11.2th percentile).
- **Key Takeaway:** All primary analogs rank better than the random-sample 90th percentile.

### 3. Feature Ablation Analysis
- Dropping **Slope** shifts Atacama for Jezero from #51 to #53, while dropping **Relief** shifts it to #108.
- For Gale Crater, dropping **Relief** degrades Death Valley from #4,027 to #10,633, confirming that relief is essential to capturing Mount Sharp's 5.5 km vertical structure.

### 4. Weight Sensitivity ($N=200$ Perturbations)
- **Atacama for Jezero:** Median Rank **#49**, **IQR = 7** [Q25: #45, Q75: #52, Range: #38–#71].
- **Iceland for Shackleton:** Median Rank **#43**, **IQR = 14** [Q25: #36, Q75: #50, Range: #20–#76].
- **Death Valley for Gale:** Median Rank **#4,062**, **IQR = 597** [Q25: #3,837, Q75: #4,434].

---

## 🔭 Algorithmic Discoveries (Expert-Validated Candidates)

Clusters of top-ranking cells identified by the unsupervised ranking model:
1. **For Jezero Crater:** **Qaidam Basin Yardangs & Clay Playas (Tibetan Plateau, China; Rank #969, Top 0.19%)** — hyper-arid enclosed basin with lacustrine evaporites and wind-carved yardang deflation.
2. **For Gale Crater:** **San Juan Precordillera (Argentina; Rank #14, Top 0.003%)** — dry intermontane basin replicating Mount Sharp's 5.5 km vertical relief and layered cuestas.
3. **For Shackleton Crater Rim:** **Quttinirpaaq Highlands (High Canadian Arctic; Rank #1, Top 0.0002%)** and **Bowers Mountains Nunataks (Antarctica; Rank #5, Top 0.001%)** — bare fractured bedrock peaks emerging from polar ice sheets.

---

## ⚠️ Honest Scientific Limitations

1. **Terrain-First Screen:**
   The algorithm screens for geomorphometric alignment (slope, roughness, relief + aridity filter). It does not model thermal inertia or orbital mineralogy (clays, sulfates, olivine), which are identified as future multi-spectral extensions.
2. **Shackleton Footprint & Permanent Shadow:**
   At ~21 km diameter, Shackleton Crater Rim covers only a few 10 km equal-area grid cells, resulting in a coarse elevation fingerprint. Furthermore, Permanently Shadowed Regions (PSRs) and ultra-cold volatile traps (~40 K) are dictated by solar elevation angles, not terrain geometry alone.
3. **How to Interpret Haughton Crater and Kilbourne Hole:**
   Terrain screening finds where to test rover mobility and relief. Haughton Crater (#161,800, Top 32.4%) and Kilbourne Hole (#164,291, Top 32.9%) rank lower because their primary scientific value lies in **impact breccia, shock metamorphism, and volcanic mantle xenoliths**, which a pure terrain elevation screen cannot detect. Adding mineralogy is the natural next step.

---

## 🌐 1-Click Deployment
- **Vercel:** Import repository, set root to `web`, build command `npm run build`, output `dist`.
- **GitHub Pages:** Automated via [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).
- **Details:** See [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

## 📜 Scientific Methodology & Integrity
- Mathematical formulations, covariance de-correlation, and honest limitations are detailed in [`METHOD.md`](METHOD.md).
- Full dataset citations, direct endpoints, and DOIs are in [`DATA_SOURCES.md`](DATA_SOURCES.md).
- 2-minute hackathon pitch script is in [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md).
