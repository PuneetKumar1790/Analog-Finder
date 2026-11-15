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
> *"Our pipeline addresses a critical geospatial problem: **fractal scale dependency**. Comparing a 20-meter lunar laser scan directly to a 1-kilometer Earth elevation model yields misleading slope numbers. We standardized Earth (NOAA ETOPO 2022), Mars (MGS MOLA), and the Moon (LRO LOLA) to a uniform **10-kilometer block scale**.*  
> *For every block, we compute Mean Slope, Elevation Roughness, and Local Relief. We mask out oceans and humid zones using WorldClim 2.1 aridity grids, leaving **500,073 valid arid Earth cells**. Every metric is z-score standardized, and our Mahalanobis distance de-correlates the 98.7% collinearity between roughness and relief."*

---

### [0:50 – 1:15] LIVE INTERACTIVE MAP DEMO
*(Screen share the live app running in the browser)*
> *"Here is the application. Notice it loads in under 1 second with a zero-backend, fully static architecture—our entire data payload is just 3.1 megabytes.*  
> *When we select **Jezero Crater**, the headline immediately asks: 'Where on Earth looks like Jezero Crater?' and the inspection station surfaces the top 5 matches with a clear one-line geomorphic rationale.*  
> *Look at the gold pins: **Atacama Desert (Yungay)** ranks **#51 out of 500,073 cells—in the Top 0.01% on Earth**!*  
> *Now, watch the client-side re-weighting sliders: if mission scientists want to prioritize slope over relief, we drag the slope slider to 70%. In under **2 milliseconds**, 2,500 pre-filtered candidate cells recalculate live in JavaScript without a single server round-trip."*

---

### [1:15 – 1:35] CONTROLS, ABLATION & ROBUSTNESS (NEW)
*(Click '[01] BENCHMARK MATRIX' -> switch to tab '[02] CONTROLS & ROBUSTNESS')*
> *"To ensure scientific integrity, we don't just celebrate high rankings—we run negative controls and ablation tests.*  
> *Notice our negative controls: flat arid regions like **Lake Eyre Salt Playa** rank **#495,905 out of 500,073 (in the bottom 0.8% of Earth)**, and the **Sahara Sand Sea (Grand Erg Oriental)** drops to rank **#406,681**. Random arid land averages the 49th percentile, proving known analogs decisively beat chance.*  
> *Furthermore, across **200 random weight vector perturbations**, Atacama's ranking is rock-solid with an Interquartile Range of just **7 ranks** (median #49). Even when dropping slope or roughness in our ablation test, the core ranking topology holds firm."*

---

### [1:35 – 1:50] GROUND TRUTH BENCHMARKS & NOVEL DISCOVERIES
*(Switch back to tab '[01] BENCHMARK MATRIX')*
> *"We benchmarked against **7 literature-recognized planetary analogs**, including Haughton Impact Crater in Devon Island and Apollo/Artemis training ground Kilbourne Hole.*  
> *Beyond known analogs, our algorithm discovered **genuine new candidate clusters**: the **Qaidam Basin yardangs** (Rank #969, top 0.19%) in Tibet for Jezero's deltaic deflation, the **San Juan Precordillera** (Rank #14, top 0.003%) in Argentina for Mount Sharp's 5 km relief, and **Bowers Mountains Nunataks** (Rank #5, top 0.001%) in Antarctica for Shackleton's sharp crater rim."*

---

### [1:50 – 2:00] IMPACT & CONCLUSION
> *"Analog Finder is 100% open source, fully reproducible in Python and Colab, and deployable in 30 seconds to Vercel or GitHub Pages. By turning qualitative field intuition into reproducible quantitative science, Analog Finder accelerates humanity's journey to the Moon and Mars. Thank you!"*
