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

### [0:50 – 1:25] LIVE INTERACTIVE MAP DEMO
*(Screen share the live app running in the browser)*
> *"Here is the application. Notice it loads in under 1 second with a zero-backend, fully static architecture—our entire data payload is just 3.09 megabytes.*  
> *When we select **Jezero Crater**, our global similarity heatmap instantly highlights Earth's most compatible lacustrine and deltaic terrains. Look at the gold pins: **Atacama Desert (Yungay)** ranks **#51 out of 500,000 cells—in the Top 0.01% on Earth**!*  
> *Now, watch the client-side re-weighting sliders: if mission scientists want to prioritize slope over relief, we drag the slope slider to 70%. In under **2 milliseconds**, 2,500 candidate cells recalculate live in JavaScript without a single server round-trip.*  
> *When we click on a candidate region, our inspection sidebar generates an automated **'Why It Matches'** geological breakdown alongside comparative bar charts."*

---

### [1:25 – 1:45] GROUND TRUTH VALIDATION & NOVEL DISCOVERIES
*(Click the 'Validation Table' button in the navbar to open modal)*
> *"Validation is the key differentiator. We benchmarked our algorithm against 6 known international analogs:*  
> *- **Atacama Desert:** Top 0.01% for Jezero.*  
> *- **Death Valley:** Top 0.08% for Gale Crater.*  
> *- **Iceland Highlands:** Top 0.01% (Rank #41) for Shackleton Crater Rim.*  
> *- **McMurdo Dry Valleys:** Top 0.24% with the steepest terrestrial slopes (8.5°).*  
> *Beyond validating known sites, the algorithm discovered **genuine new candidate regions**: the **Qaidam Basin yardangs** in the Tibetan Plateau for Jezero, the **San Juan Precordillera** in Argentina for Mount Sharp's 5 km relief, and the **Bowers Mountains nunataks** in Antarctica for Shackleton's sharp crater rim."*

---

### [1:45 – 2:00] IMPACT & CONCLUSION
> *"Analog Finder is 100% open source, fully reproducible in Python and Colab, and deployable in 30 seconds to Vercel or GitHub Pages. By turning qualitative field intuition into reproducible quantitative science, Analog Finder accelerates humanity's journey to the Moon and Mars. Thank you!"*
