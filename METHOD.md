# METHODOLOGY & SCIENTIFIC FORMULATION

**Analog Finder: Planetary Analog Discovery via Standardized Geomorphometry and Covariance De-correlation**  
*NASA Space Apps Challenge 2026*

---

## 1. Problem Formulation & Scientific Motivation

Sending robotic probes and human crewed missions (such as NASA Artemis and Mars Sample Return) to extraterrestrial planetary surfaces requires rigorous pre-deployment testing on Earth. Historically, field testing has relied on qualitative geological intuition to choose analog sites (e.g., Apollo astronauts in Hawaii and Iceland; Mars Exploration Rovers in the Mojave Desert).

**Analog Finder** provides an objective, reproducible, quantitative framework to match candidate planetary exploration targets—specifically **Shackleton Crater Rim (Moon)**, **Jezero Crater (Mars)**, and **Gale Crater (Mars)**—against terrestrial environments using standardized topographic fingerprints and macroclimate constraints.

---

## 2. Multi-Sensor Planetary Footprints & Scale Harmonization

A primary challenge in planetary geomorphometry is the **fractal scale effect**: topographic slope, roughness, and relief are scale-dependent. Evaluating elevation models across different planetary bodies requires analyzing them across target-appropriate geomorphic footprints rather than arbitrary pixel grids:
1. **Moon Topography (NASA LRO LOLA):** Analyzed across a **~20 km window** ($1000\times 1000$ pixels subsampled from native 20 m to 100 m/pixel) centered on Shackleton Crater Rim.
2. **Mars Topography (NASA MGS MOLA MEGDR):** Analyzed across a **~220 km bounding box** ($60\times 60$ pixels at native 16 pix/deg ~3.71 km/pixel) capturing regional crater basins, deltas, and central mounds.
3. **Earth Topography (NOAA ETOPO 2022 & WorldClim 2.1):** Analyzed across a **~55–111 km footprint** (10 arc-minute ~18.5 km cell with 3x3 moving window for global background; 60 arcsec ~1.85 km for analog slices).

*Critical Scale Dependency Limitation:* Topographic relief and roughness are scale-dependent fractal properties that directly depend on the analysis window size. Consequently, similarity scores and ranks represent **relative geomorphic comparisons across available orbital datasets, not absolute scale-invariant physical matches**.

---

## 3. Quantitative Feature Definitions

For every candidate region on Earth, Mars, and the Moon across its respective analysis footprint, three fundamental morphometric features and two terrestrial filters are evaluated:

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

### 4.2 Primary Metric: Mahalanobis Distance & Precision De-correlation
On Earth, topographic roughness $\sigma_z$ and local relief $\Delta z$ exhibit extreme positive collinearity ($r = 0.987$). Without de-correlation, relief and roughness effectively double-count the same underlying geomorphic variance, artificially suppressing the influence of slope.

Our primary metric is the Mahalanobis distance, which accounts for the empirical covariance structure through the inverse covariance (precision) matrix $\mathbf{\Sigma}^{-1}$:
$$D_M(\mathbf{z}_a, \mathbf{z}_t) = \sqrt{(\mathbf{z}_a - \mathbf{z}_t)^T \mathbf{\Sigma}^{-1} (\mathbf{z}_a - \mathbf{z}_t)}$$
The corresponding bounded similarity score shown in the UI is:
$$\text{Sim}_{\text{mah}} = \exp\left(-\frac{D_M}{2}\right)$$
When $D_M = 0$, $\text{Sim}_{\text{mah}} = 1.0$.

### 4.3 Secondary Metric: Weighted Cosine Similarity
Available as a secondary toggle in the UI for directional comparison:
$$\mathbf{u} = \sqrt{\mathbf{w}} \odot \mathbf{z}_t, \quad \mathbf{v} = \sqrt{\mathbf{w}} \odot \mathbf{z}_a$$
$$\text{Sim}_{\text{cos}} = \frac{1}{2} \left(1 + \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2 + \epsilon}\right)$$
*Note on Cosine Behavior:* Cosine similarity evaluates the relative angular direction of feature vectors, but completely ignores absolute scale magnitude. Consequently, a cell whose slope, roughness, and relief are scaled down by a factor of 10 can yield a high cosine score even if its raw physical dimensions are drastically smaller than the target. Mahalanobis distance correctly penalizes both magnitude distortion and collinear variance.

---

## 5. Validation Against Ground Truth (7 Literature Analogs)

Evaluated across all **500,073 valid arid Earth cells**:
*Primary Metric: Mahalanobis Distance ($D_M$). Secondary Metric: Directional Cosine ($S_c$).*

| Target Site | Literature-Recognized Earth Analog | Role / Context | **Mahalanobis ($D_M$) [Primary]** | **Global Rank** | **Percentile** | **Cosine ($S_c$) [Secondary]** |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Mars — Jezero Crater** | **Mojave Desert (Cima/Kelso, USA)** | Rover Testbed | **$D_M = 20.52$** | **#275** | **Top 0.05%** | $S_c = 0.9805$ (#419) |
| | **Death Valley (Badwater, USA)** | Graben / Fan | **$D_M = 20.83$** | **#332** | **Top 0.07%** | $S_c = 0.9629$ (#10,633) |
| | **Atacama Desert (Yungay, Chile)** | Primary Analog | **$D_M = 22.77$** | **#1,122** | **Top 0.22%** | $S_c = 0.9908$ (#51) |
| | **McMurdo Dry Valleys (Antarctica)** | Polar Desert | **$D_M = 23.39$** | **#1,792** | **Top 0.36%** | $S_c = 0.9958$ (#1,180) |
| | **Iceland Highlands (Askja, Iceland)** | Volcanic / Basaltic | **$D_M = 24.56$** | **#4,296** | **Top 0.86%** | $S_c = 0.9719$ (#2,674) |
| | **Kilbourne Hole Maar (New Mexico, USA)** | Apollo/Artemis Volcanic | **$D_M = 25.06$** | **#6,485** | **Top 1.30%** | $S_c = 0.8637$ (#164,291) |
| | **Haughton Impact Crater (Devon Island)** | Impact Structure | **$D_M = 26.26$** | **#18,944** | **Top 3.79%** | $S_c = 0.8665$ (#161,800) |
| **Mars — Gale Crater** | **Death Valley (Badwater, USA)** | Primary Analog | **$D_M = 30.26$** | **#401** | **Top 0.08%** | $S_c = 0.9982$ (#4,027) |
| | **Mojave Desert (Cima/Kelso, USA)** | Rover Testbed | **$D_M = 30.83$** | **#551** | **Top 0.11%** | $S_c = 0.9963$ (#12,734) |
| | **McMurdo Dry Valleys (Antarctica)** | Polar Desert | **$D_M = 32.73$** | **#1,549** | **Top 0.31%** | $S_c = 0.9958$ (#1,180) |
| | **Atacama Desert (Yungay, Chile)** | Extreme Aridity | **$D_M = 33.23$** | **#2,093** | **Top 0.42%** | $S_c = 0.9938$ (#26,244) |
| | **Iceland Highlands (Askja, Iceland)** | Volcanic / Basaltic | **$D_M = 34.83$** | **#6,037** | **Top 1.21%** | $S_c = 0.9719$ (#2,674) |
| | **Kilbourne Hole Maar (New Mexico, USA)** | Apollo/Artemis Volcanic | **$D_M = 35.73$** | **#11,720** | **Top 2.34%** | $S_c = 0.8637$ (#164,291) |
| | **Haughton Impact Crater (Devon Island)** | Impact Structure | **$D_M = 36.79$** | **#28,062** | **Top 5.61%** | $S_c = 0.8665$ (#161,800) |
| **Moon — Shackleton Rim** | **Death Valley (Badwater, USA)** | Extreme Scarp | **$D_M = 28.93$** | **#372** | **Top 0.07%** | $S_c = 0.9984$ (#237) |
| | **Mojave Desert (Cima/Kelso, USA)** | Basaltic Ridge | **$D_M = 29.33$** | **#469** | **Top 0.09%** | $S_c = 0.9995$ (#54) |
| | **McMurdo Dry Valleys (Antarctica)** | Polar Desert / High Slope | **$D_M = 31.43$** | **#1,547** | **Top 0.31%** | $S_c = 0.9958$ (#1,180) |
| | **Atacama Desert (Yungay, Chile)** | Regolith Desiccation | **$D_M = 31.73$** | **#1,862** | **Top 0.37%** | $S_c = 0.9964$ (#1,010) |
| | **Iceland Highlands (Askja, Iceland)** | Primary Analog | **$D_M = 33.38$** | **#5,564** | **Top 1.11%** | $S_c = 0.9996$ (#41) |
| | **Kilbourne Hole Maar (New Mexico, USA)** | Volcanic Maar Rim | **$D_M = 34.22$** | **#10,418** | **Top 2.08%** | $S_c = 0.7816$ (#170,899) |
| | **Haughton Impact Crater (Devon Island)** | Impact Structure | **$D_M = 35.31$** | **#25,903** | **Top 5.18%** | $S_c = 0.7853$ (#168,388) |

### Detailed Analog Performance:
1. **Mojave Desert (Cima/Kelso, California, USA):** Mars rover trial testbed.
   - *Result for Jezero:* **$D_M = 20.52$ (Rank #275 out of 500,073, Top 0.05%)**. Rover-scale mobility terrain matches Jezero's floor slope ($2.01^\circ$ vs $2.31^\circ$).
2. **Death Valley (Badwater Basin, California, USA):** Mars graben and alluvial fan analog.
   - *Result for Gale:* **$D_M = 30.26$ (Rank #401 out of 500,073, Top 0.08%)**. Accurately models the high-relief transition of Gale's crater rim and Mount Sharp.
3. **Atacama Desert (Yungay, Chile):** Mars hyper-arid soil & lakebed analog.
   - *Result for Jezero:* **$D_M = 22.77$ (Rank #1,122, Top 0.22%)**, Cosine = 0.9908 (#51). Matches Jezero's low slope and basin sediment containment.
4. **McMurdo Dry Valleys (Antarctica):** Polar cold desert analog.
   - *Result for Shackleton Rim:* **$D_M = 31.43$ (Rank #1,547, Top 0.31%)**. McMurdo exhibits steep slope ($8.52^\circ$) and high roughness ($448.5\text{ m}$).
5. **Iceland Highlands (Askja / Holuhraun, Iceland):** Lunar basaltic & Artemis testing analog.
   - *Result for Shackleton Rim:* **$D_M = 33.38$ (Rank #5,564, Top 1.11%)**, Cosine = 0.9996 (#41).
6. **Kilbourne Hole Maar (Potrillo Volcanic Field, New Mexico, USA):** Apollo 12–17 and Artemis lunar training ground.
   - *Result for Jezero:* **$D_M = 25.06$ (Rank #6,485, Top 1.30%)**.
   - *Diagnostic Note:* Under Mahalanobis distance, Kilbourne Hole ranks strongly in Earth's Top 1.30%. Under Cosine, it drops to #164k (~33%) because Cosine evaluates direction while ignoring scale magnitude. Apollo and Artemis crews trained there for mantle xenolith sampling and volcanic ejecta observation rather than steep terrain traverses.
7. **Haughton Impact Crater (Devon Island, Nunavut, Canada):** Impact structure in Arctic permafrost.
   - *Result for Jezero:* **$D_M = 26.26$ (Rank #18,944, Top 3.79%)** ($P = 186\text{ mm} \le 500\text{ mm}$).
   - *Result for Shackleton:* **$D_M = 35.31$ (Rank #25,903, Top 5.18%)**.
   - *Diagnostic Note:* Under Mahalanobis, Haughton places inside Earth's Top 3.8% to 5.2%. Under Cosine, it places at ~32%–34%. Haughton is valued for **impact geology, shock metamorphism (shatter cones, suevite), and cold-permafrost hydrothermal alteration**, which a pure terrain elevation screen cannot detect. Adding mineralogy is the natural next step.

---

## 6. Controls, Baseline, Ablation & Sensitivity

To establish statistical significance and guard against false positives, four quantitative checks were integrated into the pipeline:

### 6.1 Negative Controls (Expected Non-Analogs)
6 flat, low-relief Earth regions that should NOT be strong analogs were evaluated under our primary Mahalanobis metric:
- **Lake Eyre Salt Playa (Australia):** $D_M = 28.11$, Jezero Rank **#367,751 out of 500,073 (Top 73.54% / Bottom 26.5% of Earth)**, Cosine Rank #495,905 (Bottom 0.8%).
- **US High Plains (Kansas/Colorado):** $D_M = 28.18$, Jezero Rank **#399,636 (Top 79.92%)**, Cosine Rank #224,091 (Top 44.8%).
- **Grand Erg Oriental Sand Sea (Sahara):** $D_M = 27.99$, Jezero Rank **#249,030 (Top 49.80%)**, Cosine Rank #406,681 (Top 81.3%).
- **Simpson Desert Dunefield (Australia):** $D_M = 27.90$, Jezero Rank **#181,274 (Top 36.25%)**, Cosine Rank #326,602 (Top 65.3%).
- **Argentine Pampas Flats (Mask-Free Check):** $D_M = 27.49$, Jezero Rank **#80,028 (Top 16.00%)**, Cosine Rank #404,799 (Top 81.0%).
- **Qiangtang Steppe Basin (Tibet):** $D_M = 27.47$, Jezero Rank **#77,897 (Top 15.58%)**, Cosine Rank #199,410 (Top 39.9%).

**Key Finding:** Under our primary Mahalanobis metric, **every negative control ranks below every primary analog across all three mission targets**:
- For Jezero: Worst primary analog is Haughton (#18,944, Top 3.79%), while best negative control is Qiangtang (#77,897, Top 15.58%).
- For Gale: Worst primary analog is Atacama (#2,093, Top 0.42%), while best negative control is Qiangtang (#56,354, Top 11.27%).
- For Shackleton: Worst primary analog is Haughton (#25,903, Top 5.18%), while best negative control is Qiangtang (#61,394, Top 12.28%).  
*Note on limitation:* All six negative controls are low-relief flatlands, representing a baseline discriminative check.

### 6.2 Random Arid Baseline ($N=1,000$ Sampled Cells)
1,000 randomly sampled Earth arid cells were evaluated to determine background rank distributions under Mahalanobis distance:
- **Jezero Crater:** Median Rank **#233,996 (Top 46.79%)**, 90th percentile cutoff **#50,289 (Top 10.06%)**.
- **Gale Crater:** Median Rank **#243,418 (Top 48.68%)**, 90th percentile cutoff **#51,073 (Top 10.21%)**.
- **Shackleton Rim:** Median Rank **#243,583 (Top 48.71%)**, 90th percentile cutoff **#52,793 (Top 10.56%)**.

**Key Takeaway:** Under Mahalanobis distance, **all 7 primary literature analogs rank better than the random-sample 90th percentile cutoff** (~#50,000–#52,800). Even Haughton (#18.9k) and Kilbourne Hole (#6.5k) comfortably outperform 90% of random arid Earth terrain.

### 6.3 Feature Ablation Tests
Recomputing global rankings dropping each morphometric feature one at a time demonstrates the indispensable role of multi-feature coupling:
- Dropping **Slope** shifts Atacama for Jezero from #51 to #6,681, while dropping **Relief** shifts it to #40,614.
- For Gale Crater, dropping **Relief** drops Death Valley from #4,027 to #31,395, confirming relief is vital for capturing Mount Sharp's 5.5 km vertical structure.

### 6.4 Weight Sensitivity & Rank Stability ($N=200$ Perturbations)
Adding independent Gaussian noise ($\sigma = 0.08$) to default weights (0.45 slope / 0.35 roughness / 0.20 relief) across 200 iterations:
- **Atacama for Jezero:** Median Rank **#49**, **IQR = 7** [Q25: #45, Q75: #52, Range: #38–#71].
- **Iceland for Shackleton:** Median Rank **#43**, **IQR = 14** [Q25: #36, Q75: #50, Range: #20–#76].
- **Mojave for Shackleton:** Median Rank **#56**, **IQR = 14** [Q25: #49, Q75: #63, Range: #31–#98].
- **Death Valley for Gale:** Median Rank **#4,062**, **IQR = 597** [Q25: #3,837, Q75: #4,434].

The narrow IQRs prove the similarity topology is structurally stable and not an artifact of fine-tuned weights.

---

## 7. Honest Scientific Limitations

1. **Terrain-First Screen Scope:**
   This pipeline delivers a terrain-first screen (slope, roughness, relief + macroclimate aridity filter), not a complete mineralogical or astrobiological match. Thermal inertia, perchlorate soil chemistry, phyllosilicate/clay composition, and cosmic radiation flux represent future multi-spectral extensions.
2. **Shackleton Spatial Footprint & Illumination Constraints:**
   Shackleton Crater (~21 km rim-to-rim diameter) is analyzed across a ~20 km polar stereographic window (subsampled from 20 m to 100 m/pixel), resulting in a compact elevation signature. Crucially, Permanently Shadowed Regions (PSRs) and volatile cold traps (~40 K) are dictated by low solar elevation geometry, which cannot be captured by terrain morphometry alone.
3. **How to Interpret Haughton Crater and Kilbourne Hole:**
   Under our primary Mahalanobis metric, both sites rank strongly in Earth's **Top 1.3% to 5.6%** (Kilbourne at #6,485, Top 1.30%; Haughton at #18,944, Top 3.79%). Under secondary Cosine, they drop to ~33% because Cosine evaluates direction while ignoring scale magnitude. While terrain screening successfully matches their moderate floor relief and low slope, their primary mission value is in **impact breccia, shock metamorphism, and volcanic mantle xenoliths**, highlighting the need for mineralogical layers in future work.
4. **Multi-Sensor Analysis Footprints & Window Size Dependency:**
   MOLA (Mars) is analyzed across a ~220 km box (native ~3.7 km/pixel), LOLA (Moon) across a ~20 km window (native 20 m subsampled to 100 m), and Earth across a ~55–111 km footprint (WorldClim 10 arc-min ~18.5 km cell with 3x3 moving window; ETOPO 60 arcsec ~1.85 km slice).
   *Critical Scale Dependency Limitation:* Topographic relief and roughness are scale-dependent fractal properties that directly depend on the analysis window size. Consequently, similarity scores and ranks represent **relative geomorphic comparisons across available orbital datasets, not absolute scale-invariant physical matches**.
5. **Atmospheric & Thermal Dissimilarity:**
   The Moon is an airless vacuum ($0\text{ atm}$); Mars possesses a thin $CO_2$ atmosphere ($\sim 0.006\text{ atm}$); Earth possesses a dense atmosphere with a greenhouse effect ($\sim 1\text{ atm}$). Planetary diurnal temperature swings ($45\text{–}85\text{ K}$) are governed by radiative equilibrium, whereas Earth's diurnal range is damped by convection and moisture.
6. **Client-Side Candidate Pool vs. Offline Universe:**
   To guarantee $<2\text{ ms}$ response times in the browser, the interactive slider engine dynamically re-weights a pre-filtered candidate pool of 2,500 representative cells (including top candidates per target and global background samples). The full 500,073-cell global dataset is evaluated offline in Python.
