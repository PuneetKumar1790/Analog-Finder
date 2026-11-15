# METHODOLOGY & SCIENTIFIC FORMULATION

**Analog Finder: Planetary Analog Discovery via Standardized Geomorphometry and Covariance De-correlation**  
*NASA Space Apps Challenge 2026*

---

## 1. Problem Formulation & Scientific Motivation

Sending robotic probes and human crewed missions (such as NASA Artemis and Mars Sample Return) to extraterrestrial planetary surfaces requires rigorous pre-deployment testing on Earth. Historically, field testing has relied on qualitative geological intuition to choose analog sites (e.g., Apollo astronauts in Hawaii and Iceland; Mars Exploration Rovers in the Mojave Desert).

**Analog Finder** provides an objective, reproducible, quantitative framework to match candidate planetary exploration targets—specifically **Shackleton Crater Rim (Moon)**, **Jezero Crater (Mars)**, and **Gale Crater (Mars)**—against terrestrial environments using standardized topographic fingerprints and macroclimate constraints.

---

## 2. The Scale-Matching Principle (~10 km Block Normalization)

A primary failure mode in planetary geomorphometry is the **fractal scale effect**: topographic slope and roughness are scale-dependent. Evaluating slope at 1-meter laser resolution produces radically different distributions than evaluating slope at 1-kilometer gridded resolution.

To ensure physical and statistical comparability:
1. **Earth Topography (NOAA ETOPO 2022 / WorldClim Elev):** Aggregated to standardized 10-arcminute ($\sim 18.5\text{ km}$ at equator, $\sim 10\text{–}15\text{ km}$ mid-latitude) blocks.
2. **Mars Topography (NASA MGS MOLA MEGDR 16 pix/deg):** Evaluated at native $1/16^\circ$ ($\sim 3.7\text{ km/pixel}$), aggregated across $3 \times 3$ to $5 \times 5$ pixel moving blocks ($\sim 11\text{–}18\text{ km}$).
3. **Moon Topography (NASA LRO LOLA South Polar 20m DEM):** Polar stereographic grid downsampled by $5\times$ to $100\text{ m}$ to eliminate sub-pixel laser speckle and aggregated across regional crater rim blocks ($\sim 10\text{–}20\text{ km}$).

This uniform scale matching ensures that we compare *regional terrain landforms* rather than sensor artifacts.

---

## 3. Quantitative Feature Definitions

For every $\sim 10\text{ km}$ block on Earth, Mars, and the Moon, three fundamental morphometric features and two terrestrial filters are evaluated:

### 3.1 Mean Slope ($\theta$, degrees)
Evaluated using two-dimensional central finite difference gradients with metric spatial step sizes ($dx, dy$ in meters):
$$\frac{\partial z}{\partial y} = \frac{z_{i+1, j} - z_{i-1, j}}{2 \Delta y}, \quad \frac{\partial z}{\partial x} = \frac{z_{i, j+1} - z_{i, j-1}}{2 \Delta x}$$
where $\Delta y = R \cdot \Delta \phi$ and $\Delta x = R \cdot \cos(\phi) \cdot \Delta \lambda$. The local slope angle is:
$$\theta = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180^\circ}{\pi}$$
Mean slope is the spatial mean of $\theta$ within the block.

### 3.2 Topographic Roughness ($\sigma_z$, meters)
Measures the standard deviation of surface elevation within the block window:
$$\sigma_z = \sqrt{\frac{1}{N} \sum_{k=1}^N (z_k - \bar{z})^2} = \sqrt{\mathbb{E}[z^2] - (\mathbb{E}[z])^2}$$
Roughness captures surface fragmentation, boulder fields, and micro-escarpments.

### 3.3 Local Relief ($\Delta z$, meters)
Represents the maximum dynamic elevation range within the block neighborhood:
$$\Delta z = z_{\max} - z_{\min}$$
Relief distinguishes flat plains from deeply incised craters, grabens, or mountain massifs (e.g., Mount Sharp in Gale Crater).

### 3.4 Aridity & Ocean Masking (Earth Only)
Planetary surfaces lack oceans, dense vegetation, and humid weathering regimes. To isolate comparable terrestrial environments:
1. **Ocean Mask:** Elevation $> 0\text{ m}$ relative to sea level.
2. **Aridity Filter:** Annual precipitation $P_{\text{annual}} < 500\text{ mm}$ (WorldClim 2.1 `bio_12`), isolating hyper-arid, arid, semi-arid, and cold polar desert biomes.

Out of 2,332,800 global cells, **500,073 cells** satisfy these planetary-comparable criteria.

---

## 4. Normalization & Similarity Metrics

### 4.1 Z-Score Standardization
Raw features differ in units (degrees vs meters) and orders of magnitude. Every target feature vector $\mathbf{x}_T$ and Earth cell vector $\mathbf{x}_E$ is standardized against the empirical background distribution of Earth's arid landmass ($\mu_{\text{Earth}}, \sigma_{\text{Earth}}$):
$$z_i = \frac{x_i - \mu_{\text{Earth}, i}}{\sigma_{\text{Earth}, i}}$$

### 4.2 Weighted Cosine Similarity
Measures the directional alignment of feature profiles in normalized space:
$$\mathbf{u} = \sqrt{\mathbf{w}} \odot \mathbf{z}_T, \quad \mathbf{v} = \sqrt{\mathbf{w}} \odot \mathbf{z}_E$$
$$\text{Sim}_{\text{cos}} = \frac{1}{2} \left(1 + \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2 + \epsilon}\right)$$
Scaled to $[0, 1]$, where $1.0$ represents identical relative feature proportions.

### 4.3 Mahalanobis Distance & Precision De-correlation
On Earth, topographic roughness $\sigma_z$ and local relief $\Delta z$ exhibit a strong positive correlation ($\text{Corr} = 0.987$). Without de-correlation, relief and roughness effectively double-count the same underlying variance, diminishing the impact of slope.

The Mahalanobis distance uses the inverse covariance (precision) matrix $\mathbf{\Sigma}^{-1}$:
$$D_M(\mathbf{z}_E, \mathbf{z}_T) = \sqrt{(\mathbf{z}_E - \mathbf{z}_T)^T \mathbf{\Sigma}^{-1} (\mathbf{z}_E - \mathbf{z}_T)}$$
The corresponding similarity score is:
$$\text{Sim}_{\text{mah}} = \exp\left(-\frac{D_M}{2}\right)$$
When $D_M = 0$, $\text{Sim}_{\text{mah}} = 1.0$.

---

## 5. Validation Against Ground Truth

The algorithm's validity is evaluated by benchmarking where 7 literature-recognized planetary analog sites rank within Earth's 500,073 arid candidate cells:

1. **Atacama Desert (Yungay, Chile):** Mars hyper-arid soil & lakebed analog.
   - *Result for Jezero:* **Rank #51 out of 500,073 (Top 0.01%)**, Cosine = 0.9908. Mean slope $2.63^\circ$ matches Jezero's $2.01^\circ$.
   - *Result for Shackleton:* **Rank #1,010 (Top 0.20%)**.
2. **Iceland Highlands (Askja / Holuhraun, Iceland):** Lunar basaltic & Artemis testing analog.
   - *Result for Shackleton Rim:* **Rank #41 (Top 0.01%)**, Cosine = 0.9996.
   - *Result for Jezero:* **Rank #2,674 (Top 0.53%)**.
3. **Mojave Desert (Cima / Kelso, California, USA):** Mars rover trial testbed.
   - *Result for Shackleton Rim:* **Rank #54 (Top 0.01%)**, Cosine = 0.9995.
   - *Result for Jezero:* **Rank #419 (Top 0.08%)**.
4. **Death Valley (Badwater Basin, California, USA):** Mars graben and alluvial fan analog.
   - *Result for Gale Crater:* **Rank #4,027 (Top 0.81%)**, Mahalanobis Top 0.08% ($D_M = 11.2$).
   - *Result for Shackleton:* **Rank #237 (Top 0.05%)**.
5. **McMurdo Dry Valleys (Antarctica):** Polar cold desert analog.
   - *Result for Shackleton Rim:* **Rank #1,180 (Top 0.24%)**. McMurdo has the steepest slope ($8.52^\circ$) and highest roughness ($448.5\text{ m}$) among terrestrial analogs.
6. **Haughton Impact Crater (Devon Island, Nunavut, Canada; 75.37°N, 89.68°W):** Impact structure in Arctic permafrost.
   - *Terrain Diagnostic Finding:* Falls within the arid mask ($P = 186\text{ mm} \le 500\text{ mm}$), ranking #161,800 (Top 32.36%) for Jezero and #168,388 (Top 33.67%) for Shackleton. Because Pleistocene glaciers eroded Haughton's rim leaving only $219.2\text{ m}$ of local relief (vs >2,000 m on Mars/Moon rims), pure terrain morphometry ranks it modestly, highlighting that scientists value Haughton primarily for its *impact breccia, shatter cones, and permafrost hydrothermal deposits* rather than steep topographic relief.
7. **Kilbourne Hole Maar (Potrillo Volcanic Field, New Mexico, USA; 31.97°N, 106.96°W):** Apollo 12–17 and Artemis lunar training ground.
   - *Terrain Diagnostic Finding:* Arid mask compliant ($P = 241\text{ mm}$), ranking #164,291 (Top 32.85%) for Jezero. As an explosive volcanic maar crater set in flat desert plains (slope $0.49^\circ$, relief $225.5\text{ m}$), it represents an ejecta and mantle xenolith training ground rather than a deep regional relief match.

---

## 6. Controls, Baseline, Ablation & Sensitivity

To establish statistical significance and guard against false positives, four quantitative checks were integrated into the pipeline:

### 6.1 Negative Controls (Expected Non-Analogs)
6 flat, low-relief Earth regions that should NOT be strong analogs were evaluated:
- **Lake Eyre Salt Playa (Australia):** Jezero Rank **#495,905 out of 500,073 (Bottom 0.83% of Earth)**, Cosine = 0.5701.
- **Grand Erg Oriental Sand Sea (Sahara):** Jezero Rank **#406,681 (Top 81.32%)**, Cosine = 0.7788.
- **Argentine Pampas Flats (Mask-Free Check):** Jezero Rank **#404,799 (Top 80.95%)**, Cosine = 0.7816.
- **Simpson Desert Dunefield (Australia):** Jezero Rank **#326,602 (Top 65.31%)**, Cosine = 0.8495.
- **US High Plains (Kansas/Colorado):** Jezero Rank **#224,091 (Top 44.81%)**, Cosine = 0.9080.
- **Qiangtang Steppe Basin (Tibet):** Jezero Rank **#199,410 (Top 39.88%)**, Cosine = 0.9200.

Every negative control places far below the benchmark analogs, confirming the metric discriminates relief and texture.

### 6.2 Random Arid Baseline ($N=1,000$)
1,000 randomly sampled Earth arid cells were evaluated to determine background rank distributions:
- **Jezero Crater:** Median Rank **#242,943 (Top 48.58%)**, 90th percentile **#54,191 (Top 10.84%)**.
- **Gale Crater:** Median Rank **#245,618 (Top 49.12%)**, 90th percentile **#54,820 (Top 10.96%)**.
- **Shackleton Rim:** Median Rank **#245,500 (Top 49.09%)**, 90th percentile **#55,837 (Top 11.17%)**.

All primary literature analogs beat the 90th percentile of random arid terrain by 1 to 3 orders of magnitude.

### 6.3 Feature Ablation Tests
Recomputing global rankings dropping each morphometric feature one at a time demonstrates the indispensable role of multi-feature coupling:
- Dropping **Slope** shifts Atacama from #51 to #53, while dropping **Relief** shifts it to #108.
- For Gale Crater, dropping **Relief** drops Death Valley from #4,027 to #10,633, confirming relief is vital for capturing Mount Sharp's 5.5 km vertical structure.

### 6.4 Weight Sensitivity & Rank Stability ($N=200$ Perturbations)
Adding independent Gaussian noise ($\sigma = 0.08$) to default weights (0.45 slope / 0.35 roughness / 0.20 relief) across 200 iterations:
- **Atacama for Jezero:** Median Rank **#49**, **IQR = 7** [Q25: #45, Q75: #52, Range: #38–#71].
- **Iceland for Shackleton:** Median Rank **#43**, **IQR = 14** [Q25: #36, Q75: #50, Range: #20–#76].
- **Mojave for Shackleton:** Median Rank **#56**, **IQR = 14** [Q25: #49, Q75: #63, Range: #31–#98].
- **Death Valley for Gale:** Median Rank **#4,062**, **IQR = 597** [Q25: #3,837, Q75: #4,434].

The extremely narrow IQRs prove the similarity topology is structurally stable and not an artifact of fine-tuned weights.

---

## 7. Honest Scientific Limitations

1. **Terrain-First Screen Scope:**
   This pipeline delivers a terrain-first screen (slope, roughness, relief + macroclimate aridity filter), not a complete mineralogical or astrobiological match. Thermal inertia, perchlorate soil chemistry, phyllosilicate/clay composition, and cosmic radiation flux represent future multi-spectral extensions.
2. **Shackleton Spatial Footprint & Illumination Constraints:**
   Shackleton Crater (~21 km rim-to-rim diameter) spans only a few 10 km equal-area blocks, meaning its regional elevation signature is comparatively coarse. Crucially, Permanently Shadowed Regions (PSRs) and volatile cold traps (~40 K) are dictated by low solar elevation geometry, which cannot be captured by terrain morphometry alone.
3. **Glacial Erosion of Ancient Impact Structures:**
   Terrestrial craters like Haughton (39 Ma) have suffered extensive Pleistocene glacial planation, reducing rim relief to ~219 m. Terrestrial impact analogs are primarily valuable for impact shock metamorphism, suevite breccia, and endolithic habitats rather than pristine crater rim topography.
4. **Atmospheric & Thermal Dissimilarity:**
   The Moon is an airless vacuum ($0\text{ atm}$); Mars possesses a thin $CO_2$ atmosphere ($\sim 0.006\text{ atm}$); Earth possesses a dense atmosphere with a greenhouse effect ($\sim 1\text{ atm}$). Planetary diurnal temperature swings ($45\text{–}85\text{ K}$) are governed by radiative equilibrium, whereas Earth's diurnal range is damped by convection and moisture.
5. **Client-Side Candidate Pool vs. Offline Universe:**
   To guarantee $<2\text{ ms}$ response times in the browser, the interactive slider engine dynamically re-weights a pre-filtered candidate pool of 2,500 representative cells (including top candidates per target and global background samples). The full 500,073-cell global dataset is evaluated offline in Python.
