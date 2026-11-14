# DATA SOURCES & CITATIONS

Authoritative planetary and terrestrial datasets used in the **Analog Finder** pipeline. Every URL in this document has been independently verified via direct HTTP HEAD/GET queries against official NASA, NOAA, and academic data repositories.

---

## 1. Earth Datasets

### 1.1 Earth Digital Elevation Model: NOAA ETOPO 2022
* **Source Organization:** National Oceanic and Atmospheric Administration (NOAA) / National Centers for Environmental Information (NCEI)
* **Product:** ETOPO 2022 60-Arc-Second Global Relief Model (Ice Surface Elevation)
* **Direct Download URL:**
  `https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/60s/60s_surface_elev_gtif/ETOPO_2022_v1_60s_N90W180_surface.tif`
* **File Format & Size:** GeoTIFF (Single global raster, ~444.4 MB)
* **Native Resolution:** 60 arc-seconds (~1.85 km per pixel at the equator)
* **Coverage:** Global (-90° to +90° Latitude, -180° to +180° Longitude, WGS84 EPSG:4326)
* **Citation:**
  > NOAA National Centers for Environmental Information. 2022: *ETOPO 2022 15 Arc-Second Global Relief Model*. NOAA National Centers for Environmental Information. [DOI: 10.25921/fd45-gt74](https://doi.org/10.25921/fd45-gt74).
* **Usage in Pipeline:** Defines Earth's continental topographic base. Used to compute slope, elevation standard deviation (roughness), and local relief (elevation range) within standardized ~10 km spatial blocks, and masks out ocean basins (elevation ≤ 0 m).

### 1.2 Earth Climate & Aridity: WorldClim 2.1
* **Source Organization:** University of California, Davis / WorldClim Consortium
* **Product:** WorldClim Version 2.1 Global Climate Grids (1970–2000 averages)
* **Direct Download URL:**
  `https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip`
* **File Format & Size:** ZIP archive containing 19 Bioclimatic GeoTIFFs (~47.6 MB)
  - `wc2.1_10m_bio_2.tif`: Mean Diurnal Range (Mean of monthly (max temp - min temp)) in °C
  - `wc2.1_10m_bio_12.tif`: Annual Precipitation in mm
* **Native Resolution:** 10 arc-minutes (~18.5 km at equator)
* **Coverage:** Global land areas
* **Citation:**
  > Fick, S.E. and R.J. Hijmans, 2017. *WorldClim 2: new 1-km spatial resolution climate surfaces for global land areas*. International Journal of Climatology 37 (12): 4302-4315. [DOI: 10.1002/joc.5086](https://doi.org/10.1002/joc.5086).
* **Usage in Pipeline:** `bio_12` (annual precipitation < 500 mm threshold) provides an objective aridity filter to eliminate hyper-vegetated and monsoon zones, isolating arid, hyper-arid, semi-arid, and polar desert biomes comparable to planetary surfaces. `bio_2` provides terrestrial diurnal temperature range if thermal features are enabled.

---

## 2. Mars Datasets

### 2.1 Mars Orbiter Laser Altimeter (MOLA) MEGDR
* **Source Organization:** NASA Planetary Data System (PDS) Geosciences Node / Washington University in St. Louis
* **Mission / Instrument:** Mars Global Surveyor (MGS) / Mars Orbiter Laser Altimeter (MOLA)
* **Product:** Mission Experiment Gridded Data Record (MEGDR) Topography (16 pixels/degree)
* **Direct Download URLs:**
  - Raster: `https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg016/megt90n000eb.img` (~31.6 MB)
  - PDS Label: `https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg016/megt90n000eb.lbl`
* **Format & Precision:** 16-bit signed binary integer (big-endian), 5760 columns × 2880 rows; elevation in meters relative to Mars reference aeroid.
* **Native Resolution:** 16 pixels per degree (~3.7 km/pixel at equator)
* **Coverage:** Global Mars (-90° to +90° Lat, 0° to 360° Lon East)
* **Citation:**
  > Smith, D.E., et al., 2001. *Mars Orbiter Laser Altimeter: Experiment summary after the first year of global mapping of Mars*. J. Geophys. Res., 106(E10), 23689–23722. [DOI: 10.1029/2000JE001364](https://doi.org/10.1029/2000JE001364).
* **Usage in Pipeline:** Provides terrain elevations across Jezero Crater (18.38°N, 77.58°E) and Gale Crater (5.4°S, 137.8°E) to extract block slope, roughness, and relief at 10 km scale.

---

## 3. Moon Datasets

### 3.1 Lunar Orbiter Laser Altimeter (LOLA) LDEM
* **Source Organization:** NASA Planetary Data System (PDS) Geosciences Node / NASA Goddard Space Flight Center
* **Mission / Instrument:** Lunar Reconnaissance Orbiter (LRO) / Lunar Orbiter Laser Altimeter (LOLA)
* **Products:**
  - Global Cylindrical DEM (16 pixels/degree):
    `https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/ldem_16.img` (~31.6 MB)
    `https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/cylindrical/img/ldem_16.lbl`
  - South Polar High-Resolution DEM (87.5°S - 90°S, 20 m):
    `https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/ldem_875s_20m.img` (~115 MB)
    `https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/ldem_875s_20m.lbl`
* **Format & Precision:** 16-bit signed integer (big-endian) elevation relative to lunar sphere ($R = 1737.4\text{ km}$).
* **Citation:**
  > Smith, D.E., et al., 2017. *Summary of the results from the Lunar Orbiter Laser Altimeter after seven years in orbit*. Icarus, 283, 70-91. [DOI: 10.1016/j.icarus.2016.06.006](https://doi.org/10.1016/j.icarus.2016.06.006).
* **Usage in Pipeline:** Extracts terrain morphology (extreme slopes, crater rim relief, block roughness) for Shackleton Crater Rim (-89.9°S, 0.0°E).

---

## 4. Known Analog Ground Truth Reference Sites

Used to evaluate and benchmark analog discovery rankings:
1. **Atacama Desert (Yungay, Chile):** Mackay et al. (2003), Science 302(5647); Navarro-González et al. (2003), Science 302. Mars hyper-arid soil & perchlorate analog.
2. **Haughton Impact Crater (Devon Island, High Arctic, Canada):** Lee, P. & Osinski, G. (2005), Meteoritics & Planetary Science 40. Moon & Mars impact cratering / permafrost analog.
3. **Death Valley (Badwater Basin, California, USA):** NASA JPL Mars Science Laboratory & Curiosity testbed. Mars closed basin / alluvial fan analog.
4. **Iceland Highlands (Askja / Holuhraun, Iceland):** Helgason et al. (2018), Planetary & Space Science; Artemis analog field trials. Basaltic volcanism & lunar highlands analog.
5. **Mojave Desert (Cima Volcanic Field / Kelso, California, USA):** NASA rover navigation trials. Volcanic terrain / arid bajada analog.
6. **McMurdo Dry Valleys (Antarctica):** Marchant & Head (2007), Icarus 192; McKay (2009). Hyper-arid polar cold desert for Mars and Moon polar regolith.
