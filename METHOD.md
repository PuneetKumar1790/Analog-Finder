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

The algorithm's validity is evaluated by benchmarking where 6 internationally recognized planetary analog sites rank within the 500,073 candidate Earth cells:

1. **Atacama Desert (Yungay, Chile):** Mars hyper-arid soil & lakebed analog.
   - *Result for Jezero:* **Rank #51 out of 500,073 (Top 0.01%)**. Slope $2.63^\circ$ matches Jezero's $2.01^\circ$.
2. **Death Valley (Badwater Basin, California, USA):** Mars graben and alluvial fan analog.
   - *Result for Gale Crater:* **Top 0.08%** in Mahalanobis ($D_M = 11.2$).
3. **Mojave Desert (Cima / Kelso, California, USA):** Mars rover trial testbed.
   - *Result for Jezero:* **Rank #419 (Top 0.08%)**; *Result for Gale:* **Top 0.11%** in Mahalanobis.
4. **Iceland Highlands (Askja / Holuhraun, Iceland):** Lunar basaltic & Artemis testing analog.
   - *Result for Shackleton Rim:* **Rank #41 (Top 0.01%)**.
5. **McMurdo Dry Valleys (Antarctica):** Polar cold desert analog.
   - *Result for Shackleton Rim:* **Rank #1,180 (Top 0.24%)**. McMurdo has the steepest slope ($8.52^\circ$) and highest roughness ($448.5\text{ m}$) among terrestrial analogs.
6. **Haughton Impact Crater (Devon Island, Canada):** Impact structure in Arctic permafrost.
   - *Diagnostic Finding:* Ranks in the Top 7.45% in Mahalanobis, but lower in Cosine. Over 39 million years, Pleistocene continental glaciers heavily eroded Haughton's rim (leaving only $177\text{ m}$ of relief), whereas Jezero preserves over $2,000\text{ m}$ of un-eroded crater rim. Scientists value Haughton for its *impact breccia mineralogy*, not steep relief.

---

## 6. Honest Scientific Limitations

1. **Atmospheric & Thermal Dissimilarity:**
   The Moon is an airless vacuum ($0\text{ atm}$); Mars possesses a thin $CO_2$ atmosphere ($\sim 0.006\text{ atm}$); Earth possesses a dense atmosphere with a greenhouse effect ($\sim 1\text{ atm}$). Planetary diurnal temperature swings ($45\text{–}85\text{ K}$) are governed by radiative equilibrium, whereas Earth's diurnal range is damped by convection and moisture. Thermal range is isolated as an optional toggle to prevent skewing terrain matching.
2. **Spectral & Mineralogical Data:**
   This pipeline currently operates on geomorphometry and macroclimate aridity. Mineralogical properties (e.g., clays, olivine, perchlorates, phyllosilicates) from orbital spectrometers (CRISM, M3) require separate spectral library matching.
3. **Resolution Mismatch:**
   Although aggregated to uniform $\sim 10\text{ km}$ blocks, sub-kilometer microtopography (decimeter-scale rocks, small dunes) is below the Nyquist limit of global 60-arcsecond grids.
