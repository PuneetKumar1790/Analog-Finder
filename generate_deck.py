import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Palette
    C_BG = RGBColor(13, 17, 23)        # #0d1117 (Dark graphite slate)
    C_CARD = RGBColor(22, 29, 42)      # #161d2a
    C_BORDER = RGBColor(48, 54, 61)    # #30363d
    C_CYAN = RGBColor(56, 189, 248)    # #38bdf8
    C_GOLD = RGBColor(234, 179, 8)     # #eab308
    C_WHITE = RGBColor(240, 246, 252)  # #f0f6fc
    C_MUTED = RGBColor(139, 148, 158)  # #8b949e
    C_DIM = RGBColor(84, 93, 104)      # #545d68
    C_RUST = RGBColor(234, 88, 12)     # #ea580c

    screenshot_main = r"C:/Users/Raju/.gemini/antigravity/brain/cde62d75-5c98-46e9-a993-758ebd81a512/.system_generated/steps/151/media_0.png"
    screenshot_inspect = r"C:/Users/Raju/.gemini/antigravity/brain/cde62d75-5c98-46e9-a993-758ebd81a512/.system_generated/steps/172/media_0.png"
    screenshot_modal = r"C:/Users/Raju/.gemini/antigravity/brain/cde62d75-5c98-46e9-a993-758ebd81a512/.system_generated/steps/226/media_0.png"

    def set_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, slide_num, category, title):
        # Category / Number tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = f"SLIDE {slide_num:02d} // {category.upper()}"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_CYAN
        p_cat.font.name = "Consolas"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_t = tf_title.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = C_WHITE
        p_t.font.name = "Arial"

        # Divider line
        div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.02))
        div.fill.solid()
        div.fill.fore_color.rgb = C_BORDER
        div.line.fill.background()

    def add_card(slide, left, top, width, height, title, body_lines):
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD
        card.line.color.rgb = C_BORDER
        card.line.width = Pt(1)

        tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(height - 0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = C_CYAN
        p_t.font.name = "Arial"
        p_t.space_after = Pt(8)

        for line in body_lines:
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(11)
            p.font.color.rgb = C_WHITE if line.startswith("•") or line.startswith("★") else C_MUTED
            p.font.name = "Arial"
            p.space_after = Pt(4)

    # ----------------------------------------------------
    # SLIDE 1: Title & Overview
    # ----------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(4.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "NASA SPACE APPS CHALLENGE 2026 // GLOBAL SUBMISSION"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.font.name = "Consolas"
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "ANALOG FINDER"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.font.name = "Arial"
    p1.space_after = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "Quantitative Planetary Surface Analog Discovery via Standardized Geomorphometry"
    p2.font.size = Pt(20)
    p2.font.color.rgb = C_GOLD
    p2.font.name = "Arial"
    p2.space_after = Pt(24)

    p3 = tf1.add_paragraph()
    p3.text = "Challenge: Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars\nTarget Exploration Sites: Shackleton Crater Rim (Moon) • Jezero Crater (Mars) • Gale Crater (Mars)"
    p3.font.size = Pt(13)
    p3.font.color.rgb = C_MUTED
    p3.font.name = "Arial"
    p3.space_after = Pt(28)

    p4 = tf1.add_paragraph()
    p4.text = "🌐 Live Interactive Workstation: https://analog-finder-amber.vercel.app/\n📁 Open-Source GitHub Repository: https://github.com/PuneetKumar1790/Analog-Finder"
    p4.font.size = Pt(12)
    p4.font.bold = True
    p4.font.color.rgb = C_CYAN
    p4.font.name = "Consolas"

    # ----------------------------------------------------
    # SLIDE 2: The Core Problem & Fractal Scale Dilemma
    # ----------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, 2, "Mission Criticality & Scientific Challenge", "The Analog Dilemma: Why Qualitative Matching Fails")

    add_card(s2, 0.8, 1.7, 3.65, 5.2, "1. The High Cost of Guesswork", [
        "Before landing Artemis astronauts or retrieving Mars samples, rovers, drills, and life-support systems require exhaustive field trials on Earth.",
        "",
        "Historical Problem:",
        "Analog site selection has historically relied on qualitative literature and subjective visual similarity.",
        "",
        "Scientific Risk:",
        "Testing rovers in non-analogous terrain causes catastrophic hardware failure or flawed mission parameters."
    ])

    add_card(s2, 4.83, 1.7, 3.65, 5.2, "2. The Fractal Scale Trap", [
        "Terrain slope, roughness, and relief are scale-dependent fractal properties.",
        "",
        "The Resolution Pitfall:",
        "Comparing raw 60m lunar DEMs to 30m Mars MEGDR and 1km Earth grids generates severe resolution distortion.",
        "",
        "The Solution:",
        "Our pipeline harmonizes Earth, Mars, and the Moon into uniform ~10.0 km spatial block apertures to measure true planetary morphology."
    ])

    add_card(s2, 8.86, 1.7, 3.65, 5.2, "3. Macroclimate Surface Filter", [
        "Planetary surfaces operate in extreme hyper-arid environments without vegetation cover.",
        "",
        "Vegetation Masking Trap:",
        "Humid Earth regions disguise underlying rock mechanics under dense biomes.",
        "",
        "Quantitative Aridity Filtering:",
        "Ocean masked (elev > 0) + WorldClim 2.1 annual rainfall < 500 mm, establishing a pristine search space of 500,073 arid Earth cells."
    ])

    # ----------------------------------------------------
    # SLIDE 3: Standardized Morphometric Vector Fingerprint
    # ----------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, 3, "Quantitative Feature Pipeline", "Standardizing the 3D Planetary Fingerprint")

    add_card(s3, 0.8, 1.7, 3.65, 5.2, "Metric 1: Mean Gradient (Slope °)", [
        "Computed via 2D finite-difference gradient vectors across digital elevation models.",
        "",
        "Planetary Target Signatures:",
        "• Jezero Crater: 2.01° (Deposition basin)",
        "• Gale Mt. Sharp: 4.66° (Sedimentary peak)",
        "• Shackleton Rim: 16.07° (Impact rim scarp)",
        "",
        "Mission Relevance:",
        "Determines rover slope traversability and gravitational slope stability."
    ])

    add_card(s3, 4.83, 1.7, 3.65, 5.2, "Metric 2: Roughness (1σ Elevation)", [
        "Standard deviation of elevation within the 10 km block window.",
        "",
        "Planetary Target Signatures:",
        "• Jezero Crater: 289.0 m",
        "• Gale Mt. Sharp: 1,399.8 m",
        "• Shackleton Rim: 1,146.9 m",
        "",
        "Mission Relevance:",
        "Captures boulder density, sub-kilometer scarp patterns, and regolith fragmentation."
    ])

    add_card(s3, 8.86, 1.7, 3.65, 5.2, "Metric 3: Local Relief (Δz Peak-to-Peak)", [
        "Dynamic elevation range: z_max - z_min within spatial window.",
        "",
        "Planetary Target Signatures:",
        "• Jezero Crater: 2,053.0 m",
        "• Gale Mt. Sharp: 5,601.0 m",
        "• Shackleton Rim: 4,831.5 m",
        "",
        "Mission Relevance:",
        "Replicates macro-scale crater walls, central peaks, and basin depth."
    ])

    # ----------------------------------------------------
    # SLIDE 4: Mathematical Innovation — Covariance Decoupling
    # ----------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, 4, "Algorithmic Breakthrough", "Decoupling 98.7% Multicollinearity via Mahalanobis Distance")

    add_card(s4, 0.8, 1.7, 5.6, 5.2, "The Statistical Collinearity Trap", [
        "In terrestrial geomorphometry, topographic roughness and local relief have an empirical Pearson correlation of r = 0.987.",
        "",
        "Why Naive Euclidean / Cosine Metrics Fail:",
        "When two features are 98.7% collinear, standard distance functions double-count relief amplitude, causing relief to dominate 89% of the decision weight and drowning out slope gradient.",
        "",
        "Earth Background Normalization:",
        "Every candidate cell is z-score standardized against 500,073 arid Earth cells: z = (x - μ) / σ."
    ])

    add_card(s4, 6.8, 1.7, 5.7, 5.2, "Our Mahalanobis Distance Engine", [
        "We implement the multivariate Mahalanobis formulation using the inverse covariance matrix Σ⁻¹:",
        "",
        "    D_M(z_E, z_T) = √[ (z_E - z_T)ᵀ Σ⁻¹ (z_E - z_T) ]",
        "",
        "Key Mathematical Properties:",
        "• Covariance determinant: det(Σ) = 0.0142",
        "• Projects correlated dimensions into orthogonal eigenspace",
        "• Restores equal physical significance to slope, roughness, and relief",
        "• Mathematically validates why Atacama Desert matches Jezero in top 0.01%."
    ])

    # ----------------------------------------------------
    # SLIDE 5: Interactive Web Instrument Architecture
    # ----------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, 5, "Deployment & User Experience", "Zero-Backend Interactive Scientific Workstation")

    # Left Card
    add_card(s5, 0.8, 1.7, 4.8, 5.2, "Engine Architecture & Capabilities", [
        "100% Static & Serverless on Vercel:",
        "• Total shipped data payload is only 3.09 MB.",
        "• Zero backend infrastructure required.",
        "",
        "Sub-2ms Live Client-Side Re-weighting:",
        "• Vectorized dot product recalculates 2,500 candidate cells in < 2ms as sliders move.",
        "",
        "Cartographic Precision:",
        "• ESRI World Dark Gray basemap tiles (zero API key watermarks).",
        "• Live cursor coordinate HUD (LAT/LON, ZOOM, DATUM).",
        "• 1-Click RFC 4180 CSV export for QGIS and ArcGIS."
    ])

    # Right Image (App screenshot)
    if os.path.exists(screenshot_main):
        s5.shapes.add_picture(screenshot_main, Inches(5.9), Inches(1.7), width=Inches(6.6))

    # ----------------------------------------------------
    # SLIDE 6: Ground-Truth Empirical Validation & Discoveries
    # ----------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, 6, "Scientific Validation & Discoveries", "Ground-Truth Benchmark Matrix & Novel Terrestrial Analogs")

    add_card(s6, 0.8, 1.7, 5.6, 5.2, "Empirical Validation (500,073 Cells)", [
        "Tested against literature-recognized planetary analog benchmarks:",
        "",
        "★ Atacama Desert (Yungay, Chile):",
        "Ranks #51 out of 500,073 cells (Top 0.01%) for Jezero Crater.",
        "",
        "★ Iceland Highlands (Askja Caldera):",
        "Ranks #41 out of 500,073 cells (Top 0.01%) for Shackleton Rim.",
        "",
        "★ Death Valley (Badwater Basin):",
        "Ranks in Top 0.08% for Gale Crater (Mt. Sharp base).",
        "",
        "★ McMurdo Dry Valleys (Antarctica):",
        "Top 0.24% with steepest terrestrial slope gradient (8.52°)."
    ])

    add_card(s6, 6.8, 1.7, 5.7, 5.2, "3 Novel Discovered Planetary Analogs", [
        "Our engine identified high-ranking novel sites not previously cataloged:",
        "",
        "1. Qaidam Basin Yardangs (Tibet / Qinghai):",
        "Hyper-arid fossil lakebeds at 2,800m reproducing Jezero's deltaic deflation and lacustrine clay deposition.",
        "",
        "2. San Juan Precordillera (Argentina):",
        "Arid tectonic block providing the exact 5.5 km vertical relief necessary to simulate Gale Crater's Mount Sharp.",
        "",
        "3. Bowers Mountains Nunataks (Antarctica):",
        "Exposed bedrock ridges piercing polar ice, mirroring Shackleton Crater's illuminated peaks and cold traps."
    ])

    # ----------------------------------------------------
    # SLIDE 7: Mission Impact & Open Science
    # ----------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, 7, "Operational Value & Lineage", "Accelerating Artemis & Mars Surface Missions")

    add_card(s7, 0.8, 1.7, 3.65, 5.2, "1. Direct Mission Impact", [
        "Artemis Polar Base EVA:",
        "Optimizes astronaut training by finding accessible Earth analogs with identical lunar south pole slope profiles.",
        "",
        "Mars Sample Return & Rovers:",
        "Provides precise terrain matches for robotic wheel traction, drill testing, and hazard avoidance.",
        "",
        "Expedition Planning:",
        "Saves mission planners hundreds of hours of manual literature review."
    ])

    add_card(s7, 4.83, 1.7, 3.65, 5.2, "2. 100% Open Science", [
        "Full Data Lineage & Provenance:",
        "• Earth: NOAA ETOPO 2022 (Bedrock)",
        "• Mars: NASA MGS MOLA MEGDR",
        "• Moon: NASA LRO LOLA (60m DEM)",
        "• Climate: WorldClim v2.1 Bioclimatics",
        "",
        "Reproducibility:",
        "• End-to-end Python pipeline scripts.",
        "• 1-Click Google Colab notebook.",
        "• Pre-calculated GeoJSON / CSV exports."
    ])

    add_card(s7, 8.86, 1.7, 3.65, 5.2, "3. Deployment & Access", [
        "Live Production Web App:",
        "https://analog-finder-amber.vercel.app/",
        "",
        "Source Code & Documentation:",
        "https://github.com/PuneetKumar1790/Analog-Finder",
        "",
        "Ready for NASA Mission Teams:",
        "Built with modular GIS standards (WGS84 / IAU 2000) for direct integration into mission planning software."
    ])

    out_path = "Analog_Finder_NASA_Space_Apps.pptx"
    prs.save(out_path)
    print(f"Presentation successfully created at: {os.path.abspath(out_path)}")

if __name__ == "__main__":
    create_deck()
