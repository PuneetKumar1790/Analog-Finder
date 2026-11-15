# 2-MINUTE HACKATHON DEMO SCRIPT

**Project:** Analog Finder (NASA Space Apps Challenge 2026)  
**Presenter:** Geospatial & Full-Stack Engineer  
**Timing:** Exactly 120 seconds  

---

### [0:00 – 0:20] THE HOOK: The Planetary Challenge
> *"Before NASA lands astronauts at the Lunar South Pole or retrieves samples from Jezero Crater on Mars, every rover, drill, and habitat must be tested right here on Earth. But how do mission planners find Earth locations that physically mimic Moon and Mars? Historically, it's been qualitative guesswork. Today, we built **Analog Finder**—an end-to-end, quantitative planetary analog discovery engine that matches Moon and Mars target sites to Earth terrain using real NASA and NOAA orbital data."*

---

### [0:20 – 0:50] THE ARCHITECTURE & INNOVATION
*(Show Architecture diagram or quick slide)*
> *"Our pipeline addresses a critical geospatial problem: **fractal scale dependency**. Comparing a 20-meter lunar laser scan directly to a 1-kilometer Earth elevation model yields misleading slope numbers. We harmonized each body into target-appropriate geomorphic footprints: a **~20 km window** for the Moon, a **~220 km box** for Mars, and a **~55–111 km footprint** across Earth.*  
> *For every footprint, we compute Mean Slope, Elevation Roughness, and Local Relief. We mask out oceans and humid zones using WorldClim 2.1 aridity grids, leaving **500,073 valid arid Earth cells**. Every metric is z-score standardized, and our Mahalanobis distance [$D_M = \sqrt{(\mathbf{z}_a - \mathbf{z}_t)^T \mathbf{\Sigma}^{-1} (\mathbf{z}_a - \mathbf{z}_t)}$] de-correlates the 98.7% collinearity between roughness and relief. Crucially, because relief and roughness depend on window size, our ranks represent relative geomorphic comparisons rather than absolute matches."*

---

### [0:50 – 1:15] LIVE INTERACTIVE MAP DEMO
*(Screen share the live app running in the browser)*
> *"Here is the application. Notice it loads in under 1 second with a zero-backend, fully static architecture—our entire data payload is just 3.1 megabytes.*  
> *When we select **Jezero Crater**, the headline immediately asks: 'Where on Earth looks like Jezero Crater?' and the inspection station surfaces the top 5 matches with a clear one-line geomorphic rationale.*  
> *Notice our primary metric: **Mahalanobis Distance ($D_M$)**, which eliminates collinearity between roughness and relief. Under Mahalanobis, **Mojave Desert (Cima/Kelso)** ranks **#275 out of 500,073 cells (Top 0.05%)** and **Atacama Desert (Yungay)** ranks **#1,122 (Top 0.22%)**!*  
> *Now, watch the client-side re-weighting sliders: if mission scientists want to prioritize slope over relief, we drag the slope slider to 70%. In under **2 milliseconds**, 2,500 pre-filtered candidate cells recalculate live in JavaScript without a single server round-trip."*

---

### [1:15 – 1:35] CONTROLS, ABLATION & ROBUSTNESS (NEW)
*(Click '[01] BENCHMARK MATRIX' -> switch to tab '[02] CONTROLS & ROBUSTNESS')*
> *"To ensure scientific integrity, we don't just celebrate high rankings—we run negative controls and sensitivity tests.*  
> *Under our primary Mahalanobis metric, **every negative control ranks below every primary analog**. Hyper-flat salt playas like **Lake Eyre** drop to rank **#367,751 (in the bottom 26% of Earth)**, and all 7 primary analogs beat the random-sample 90th percentile (#50,289).*  
> *Furthermore, across **200 random weight vector perturbations**, Atacama's ranking is rock-solid with an Interquartile Range of just **7 ranks** (median #49). Even when dropping slope or roughness in our ablation test, the core ranking topology holds firm."*

---

### [1:35 – 1:50] GROUND TRUTH BENCHMARKS & NOVEL DISCOVERIES
*(Switch back to tab '[01] BENCHMARK MATRIX')*
> *"We benchmarked against **7 literature-recognized planetary analogs**. Under our primary Mahalanobis metric, **all 7 place in Earth's Top 0.05% to 5.6%**—including Kilbourne Hole at #6,485 (Top 1.30%) and Haughton Crater at #18,944 (Top 3.79%). Cosine is available as a secondary directional toggle.*  
> *Our honest boundary: terrain screening finds where to test rover mobility and relief; mineralogy and cold-trap physics are the natural next steps for impact breccia and ice traps.*  
> *Beyond known analogs, our algorithm discovered **genuine new candidate clusters**: the **Qaidam Basin yardangs** (Cosine Rank #969, Mahalanobis Top 1.3%) in Tibet for Jezero's deltaic deflation, the **San Juan Precordillera** (Mahalanobis Rank #7, Cosine Rank #14, top 0.003%) in Argentina for Mount Sharp's 5 km relief, and **Bowers Mountains Nunataks** (Cosine Rank #5, Mahalanobis Rank #493) in Antarctica for Shackleton's sharp crater rim."*

---

### [1:50 – 2:00] IMPACT & CONCLUSION
> *"Analog Finder is 100% open source, fully reproducible in Python and Colab, and deployable in 30 seconds to Vercel or GitHub Pages. By turning qualitative field intuition into reproducible quantitative science, Analog Finder accelerates humanity's journey to the Moon and Mars. Thank you!"*
