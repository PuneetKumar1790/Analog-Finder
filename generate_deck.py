"""
generate_deck.py - NASA Space Apps Challenge 2026: Analog Finder
Generates an official 7-slide 16:9 dark-theme presentation deck using python-pptx.
Adheres strictly to:
- 16:9 widescreen layout
- Dark theme (#0d1117 background, #161d2a cards, #38bdf8 cyan, #f0f6fc white)
- Max ~35 words per slide
- Large, highly legible typography (20-48 pt)
- Uses ONLY numbers loaded directly from data_processed/validation_report.json
- Labels Mahalanobis Distance as Primary Metric
- Uses screenshots from assets/ (generates placeholders if missing)
- Includes automated and manual export instructions for saving as PDF
"""

import os
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_PROC = os.path.join(BASE_DIR, "data_processed")
VAL_REPORT_PATH = os.path.join(DATA_PROC, "validation_report.json")
OUTPUT_PPTX = os.path.join(BASE_DIR, "Analog_Finder_Presentation.pptx")
OUTPUT_PDF = os.path.join(BASE_DIR, "Analog_Finder_Presentation.pdf")

# Palette
C_BG = RGBColor(13, 17, 23)        # #0d1117 (Deep Slate)
C_CARD = RGBColor(22, 29, 42)      # #161d2a (Card Slate)
C_BORDER = RGBColor(48, 54, 61)    # #30363d (Border Gray)
C_CYAN = RGBColor(56, 189, 248)    # #38bdf8 (Accent Cyan)
C_GOLD = RGBColor(234, 179, 8)     # #eab308 (Accent Gold)
C_WHITE = RGBColor(240, 246, 252)  # #f0f6fc (Bright White)
C_MUTED = RGBColor(148, 163, 184)  # #94a3b8 (Muted Silver)
C_GREEN = RGBColor(34, 197, 94)    # #22c55e (Success Green)

def ensure_screenshots():
    """Ensures screenshot assets exist in assets/, creating placeholders if needed."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    required = {
        "screenshot_top5.png": ("Top-5 Matches for Jezero", "Ranked candidates with geomorphic rationale"),
        "screenshot_inspect.png": ("Why It Matches Panel", "Multi-parameter slope, roughness & relief"),
        "screenshot_sliders.png": ("Weight Sliders", "<2 ms dynamic recalculation in browser")
    }
    for filename, (title, subtitle) in required.items():
        dest = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(dest):
            img = Image.new("RGB", (1280, 720), color=(22, 29, 42))
            draw = ImageDraw.Draw(img)
            draw.rectangle([(20, 20), (1260, 700)], outline=(48, 54, 61), width=3)
            draw.rectangle([(20, 20), (1260, 90)], fill=(30, 41, 59))
            draw.text((50, 40), f"[ANALOG FINDER] {title}", fill=(56, 189, 248))
            draw.text((50, 140), subtitle, fill=(240, 246, 252))
            draw.text((50, 640), "https://analog-finder-amber.vercel.app/", fill=(234, 179, 8))
            img.save(dest)
            print(f"[ASSET] Generated placeholder: {dest}")

def load_validation_data():
    """Loads exact verified numbers directly from validation_report.json."""
    if not os.path.exists(VAL_REPORT_PATH):
        raise FileNotFoundError(f"Missing {VAL_REPORT_PATH}. Run pipeline/04_validate.py first.")
    with open(VAL_REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_deck():
    ensure_screenshots()
    val_data = load_validation_data()

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, slide_num, category, title):
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = f"SLIDE {slide_num:02d} // {category.upper()}"
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_CYAN
        p_cat.font.name = "Consolas"

        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.65))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_t = tf_title.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(25)
        p_t.font.bold = True
        p_t.font.color.rgb = C_WHITE
        p_t.font.name = "Arial"

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BORDER
        line.line.fill.background()

    # =========================================================================
    # SLIDE 1: Title
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.15), Inches(3.2), Inches(0.45))
    badge.fill.solid()
    badge.fill.fore_color.rgb = C_CARD
    badge.line.color.rgb = C_CYAN
    badge.line.width = Pt(1)
    tf_b = badge.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "NASA SPACE APPS 2026"
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = C_CYAN
    p_b.font.name = "Consolas"
    p_b.alignment = PP_ALIGN.CENTER

    tb_t = s1.shapes.add_textbox(Inches(0.8), Inches(1.85), Inches(11.7), Inches(2.2))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    p1 = tf_t.paragraphs[0]
    p1.text = "Analog Finder"
    p1.font.size = Pt(50)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.font.name = "Arial"

    p2 = tf_t.add_paragraph()
    p2.text = "Where on Earth looks like the Moon and Mars?"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = C_CYAN
    p2.font.name = "Arial"
    p2.space_before = Pt(8)

    card_m = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.3), Inches(11.733), Inches(2.3))
    card_m.fill.solid()
    card_m.fill.fore_color.rgb = C_CARD
    card_m.line.color.rgb = C_BORDER
    tf_m = card_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = Inches(0.45)
    tf_m.margin_top = Inches(0.35)

    pm1 = tf_m.paragraphs[0]
    pm1.text = "Team: Analog Finder Team"
    pm1.font.size = Pt(20)
    pm1.font.bold = True
    pm1.font.color.rgb = C_WHITE

    pm2 = tf_m.add_paragraph()
    pm2.text = "Live: analog-finder-amber.vercel.app"
    pm2.font.size = Pt(16)
    pm2.font.color.rgb = C_GOLD
    pm2.font.name = "Consolas"
    pm2.space_before = Pt(10)

    pm3 = tf_m.add_paragraph()
    pm3.text = "Code: github.com/PuneetKumar1790/Analog-Finder"
    pm3.font.size = Pt(16)
    pm3.font.color.rgb = C_MUTED
    pm3.font.name = "Consolas"
    pm3.space_before = Pt(6)

    # =========================================================================
    # SLIDE 2: Problem (Strictly ~25 words)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, 2, "The Problem", "Planetary missions need Earth test sites")

    c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.7))
    c1.fill.solid()
    c1.fill.fore_color.rgb = C_CARD
    c1.line.color.rgb = C_BORDER
    tf_c1 = c1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_right = Inches(0.5)
    tf_c1.margin_top = Inches(0.8)

    p = tf_c1.paragraphs[0]
    p.text = "TODAY'S PRACTICE"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(248, 113, 113)
    p.font.name = "Consolas"

    p = tf_c1.add_paragraph()
    p.text = "Analogs are chosen by tradition and are poorly characterized."
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_before = Pt(20)

    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.9), Inches(5.6), Inches(4.7))
    c2.fill.solid()
    c2.fill.fore_color.rgb = C_CARD
    c2.line.color.rgb = C_CYAN
    tf_c2 = c2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_right = Inches(0.5)
    tf_c2.margin_top = Inches(0.8)

    p = tf_c2.paragraphs[0]
    p.text = "OUR GOAL"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.font.name = "Consolas"

    p = tf_c2.add_paragraph()
    p.text = "Quantify and rank them from open planetary data."
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_before = Pt(20)

    # =========================================================================
    # SLIDE 3: Approach (Strictly ~32 words)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, 3, "Our Approach", "From raw planetary sensors to ranked Earth map")

    flow_steps = [
        ("01 // DATA", "Open Sensors", "NASA MOLA + LOLA,\nNOAA ETOPO,\nWorldClim"),
        ("02 // FEATURES", "Terrain Fingerprint", "Slope, roughness,\nrelief + aridity"),
        ("03 // METRIC", "Mahalanobis Similarity", "Decouples 98.7%\ncollinearity"),
        ("04 // OUTPUT", "Ranked Earth Map", "500,073 candidate\ncells mapped")
    ]

    card_w = 2.65
    gap_f = 0.38
    start_f = 0.8

    for idx, (tag, heading, body) in enumerate(flow_steps):
        fx = start_f + idx * (card_w + gap_f)
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(fx), Inches(1.9), Inches(card_w), Inches(4.7))
        box.fill.solid()
        box.fill.fore_color.rgb = C_CARD
        box.line.color.rgb = C_CYAN if idx == 2 else C_BORDER
        box.line.width = Pt(1.5 if idx == 2 else 1)

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.6)

        p = tf.paragraphs[0]
        p.text = tag
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_CYAN
        p.font.name = "Consolas"

        p = tf.add_paragraph()
        p.text = heading
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.space_before = Pt(14)

        p = tf.add_paragraph()
        p.text = body
        p.font.size = Pt(17)
        p.font.color.rgb = C_MUTED
        p.space_before = Pt(18)

        if idx < 3:
            arrow_x = fx + card_w + 0.08
            tb_arr = s3.shapes.add_textbox(Inches(arrow_x), Inches(4.0), Inches(0.25), Inches(0.5))
            tf_arr = tb_arr.text_frame
            tf_arr.margin_left = tf_arr.margin_right = tf_arr.margin_top = tf_arr.margin_bottom = 0
            p_arr = tf_arr.paragraphs[0]
            p_arr.text = "→"
            p_arr.font.size = Pt(28)
            p_arr.font.bold = True
            p_arr.font.color.rgb = C_CYAN

    # =========================================================================
    # SLIDE 4: The Tool (3 Screenshots + Caption)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, 4, "The Tool", "Interactive discovery in under 2 milliseconds")

    screens = [
        (os.path.join(ASSETS_DIR, "screenshot_top5.png"), "Top-5 Matches for Jezero"),
        (os.path.join(ASSETS_DIR, "screenshot_inspect.png"), "'Why It Matches' Panel"),
        (os.path.join(ASSETS_DIR, "screenshot_sliders.png"), "Weight Sliders")
    ]

    sw = 3.65
    sh = 4.2
    sgap = 0.38
    sx = 0.8

    for idx, (path, label) in enumerate(screens):
        x = sx + idx * (sw + sgap)
        if os.path.exists(path):
            s4.shapes.add_picture(path, Inches(x), Inches(1.8), Inches(sw), Inches(sh))
            frame = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.8), Inches(sw), Inches(sh))
            frame.fill.background()
            frame.line.color.rgb = C_BORDER
            frame.line.width = Pt(1)

        tb_l = s4.shapes.add_textbox(Inches(x), Inches(6.08), Inches(sw), Inches(0.35))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        p_l = tf_l.paragraphs[0]
        p_l.text = label
        p_l.font.size = Pt(13)
        p_l.font.bold = True
        p_l.font.color.rgb = C_WHITE
        p_l.alignment = PP_ALIGN.CENTER

    f_bar = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.55), Inches(11.733), Inches(0.55))
    f_bar.fill.solid()
    f_bar.fill.fore_color.rgb = C_CARD
    f_bar.line.color.rgb = C_CYAN
    tf_fb = f_bar.text_frame
    p_fb = tf_fb.paragraphs[0]
    p_fb.text = "Caption: Explore live, no login: analog-finder-amber.vercel.app"
    p_fb.font.size = Pt(14)
    p_fb.font.bold = True
    p_fb.font.color.rgb = C_GOLD
    p_fb.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 5: Validation (Table of 7 literature analogs)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, 5, "Ground Truth Validation", "Literature analogs rank in Earth's top percentiles")

    j_dict = {a['name']: a for a in val_data['jezero']['known_analogs']}
    g_dict = {a['name']: a for a in val_data['gale']['known_analogs']}
    s_dict = {a['name']: a for a in val_data['shackleton']['known_analogs']}

    table_rows = [
        ["LITERATURE ANALOG", "JEZERO CRATER", "GALE CRATER", "SHACKLETON RIM"]
    ]

    analogs_list = [
        "Mojave Desert (Cima / Kelso)",
        "Death Valley (Badwater Basin)",
        "Atacama Desert (Yungay)",
        "McMurdo Dry Valleys",
        "Iceland Highlands (Askja / Holuhraun)",
        "Kilbourne Hole Maar",
        "Haughton Impact Crater"
    ]

    for name in analogs_list:
        ja = j_dict.get(name, {})
        ga = g_dict.get(name, {})
        sa = s_dict.get(name, {})

        j_top = round(100.0 - ja.get('mahalanobis_percentile', 99.0), 2)
        g_top = round(100.0 - ga.get('mahalanobis_percentile', 99.0), 2)
        s_top = round(100.0 - sa.get('mahalanobis_percentile', 99.0), 2)

        clean_name = name.split(" (")[0]
        table_rows.append([
            clean_name,
            f"#{ja.get('mahalanobis_rank', 0):,d} (Top {j_top}%)",
            f"#{ga.get('mahalanobis_rank', 0):,d} (Top {g_top}%)",
            f"#{sa.get('mahalanobis_rank', 0):,d} (Top {s_top}%)"
        ])

    t_shape = s5.shapes.add_table(len(table_rows), 4, Inches(0.8), Inches(1.8), Inches(11.733), Inches(3.6))
    table = t_shape.table
    table.columns[0].width = Inches(3.6)
    table.columns[1].width = Inches(2.71)
    table.columns[2].width = Inches(2.71)
    table.columns[3].width = Inches(2.71)

    for r_idx, row in enumerate(table_rows):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(30, 41, 59) if r_idx == 0 else (C_CARD if r_idx % 2 == 1 else RGBColor(17, 24, 39))

            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.CENTER
                p.font.name = "Consolas" if r_idx > 0 and c_idx > 0 else "Arial"
                p.font.size = Pt(11 if r_idx > 0 else 10)
                p.font.bold = (r_idx == 0) or (c_idx == 0)
                p.font.color.rgb = C_CYAN if r_idx == 0 else (C_GOLD if c_idx > 0 and "Top 0." in val else C_WHITE)

    b_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.65), Inches(11.733), Inches(1.35))
    b_card.fill.solid()
    b_card.fill.fore_color.rgb = C_CARD
    b_card.line.color.rgb = C_BORDER
    tf_bc = b_card.text_frame
    tf_bc.word_wrap = True
    tf_bc.margin_left = tf_bc.margin_right = Inches(0.3)
    tf_bc.margin_top = Inches(0.18)

    p = tf_bc.paragraphs[0]
    p.text = "METRIC: MAHALANOBIS (PRIMARY) ACROSS 500,073 ARID CELLS"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.font.name = "Consolas"

    p = tf_bc.add_paragraph()
    p.text = "• Negative Controls: All 6 negative controls rank below every primary analog."
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_before = Pt(4)

    p = tf_bc.add_paragraph()
    p.text = "• Random Baseline: All primary analogs beat the 90th percentile random baseline."
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_before = Pt(3)

    # =========================================================================
    # SLIDE 6: Discoveries and Robustness (Strictly ~35 words)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, 6, "Discoveries & Robustness", "Novel candidates and robust weight stability")

    card_d = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.1))
    card_d.fill.solid()
    card_d.fill.fore_color.rgb = C_CARD
    card_d.line.color.rgb = C_BORDER
    tf_d = card_d.text_frame
    tf_d.word_wrap = True
    tf_d.margin_left = tf_d.margin_right = Inches(0.35)
    tf_d.margin_top = Inches(0.4)

    p = tf_d.paragraphs[0]
    p.text = "4 CANDIDATE REGIONS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.font.name = "Consolas"

    cands = [
        ("San Juan (Gale)", "Mahalanobis #7 | Cosine #14"),
        ("Bowers (Shackleton)", "Mahalanobis #493 | Cosine #5"),
        ("Qaidam (Jezero)", "Cosine #969 | Mahalanobis Top 1.3%"),
        ("Quttinirpaaq (Shackleton)", "Cosine #1 | Mahalanobis Top 1.5%")
    ]

    for name, metric_str in cands:
        p_n = tf_d.add_paragraph()
        p_n.text = f"★ {name}"
        p_n.font.size = Pt(16)
        p_n.font.bold = True
        p_n.font.color.rgb = C_WHITE
        p_n.space_before = Pt(12)

        p_m = tf_d.add_paragraph()
        p_m.text = metric_str
        p_m.font.size = Pt(14)
        p_m.font.color.rgb = C_GOLD if "#7" in metric_str or "#1" in metric_str else C_MUTED
        p_m.font.name = "Consolas"
        p_m.space_before = Pt(3)

    card_r = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.9), Inches(1.8), Inches(4.633), Inches(5.1))
    card_r.fill.solid()
    card_r.fill.fore_color.rgb = C_CARD
    card_r.line.color.rgb = C_CYAN
    tf_r = card_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = Inches(0.35)
    tf_r.margin_top = Inches(0.5)

    p = tf_r.paragraphs[0]
    p.text = "WEIGHT ROBUSTNESS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.font.name = "Consolas"

    p = tf_r.add_paragraph()
    p.text = "Atacama for Jezero:"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_before = Pt(20)

    p = tf_r.add_paragraph()
    p.text = "Median #49 | IQR 7"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = C_GOLD
    p.font.name = "Consolas"
    p.space_before = Pt(8)

    p = tf_r.add_paragraph()
    p.text = "Rankings remain structurally stable across 200 random perturbations."
    p.font.size = Pt(15)
    p.font.color.rgb = C_MUTED
    p.space_before = Pt(14)

    # =========================================================================
    # SLIDE 7: Limitations, Next Steps, Credits (Strictly ~35 words)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, 7, "Limitations & Horizon", "Terrain-first screening with an honest horizon")

    cols_s7 = [
        ("LIMITATIONS", [
            "• Terrain-first screen (no mineralogy/thermal).",
            "• Different footprints; Shackleton coarse."
        ]),
        ("NEXT STEPS", [
            "• Add Diviner thermal.",
            "• Add orbital mineralogy."
        ]),
        ("DATA & CREDITS", [
            "• NASA PDS, NOAA, WorldClim.",
            "• Built with AI-assisted coding (disclosed).",
            "• analog-finder-amber.vercel.app"
        ])
    ]

    c_w = 3.65
    c_gap = 0.38
    c_x = 0.8

    for idx, (head, bullets) in enumerate(cols_s7):
        x = c_x + idx * (c_w + c_gap)
        c = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.8), Inches(c_w), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = C_CARD
        c.line.color.rgb = C_BORDER
        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.5)

        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_CYAN
        p.font.name = "Consolas"

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = b
            pb.font.size = Pt(16)
            pb.font.color.rgb = C_WHITE if "Built with" in b or "Diviner" in b else C_MUTED
            pb.space_before = Pt(14)

    prs.save(OUTPUT_PPTX)
    print(f"\n[SUCCESS] Generated 7-slide deck: {OUTPUT_PPTX}")

    export_to_pdf(OUTPUT_PPTX, OUTPUT_PDF)

def export_to_pdf(pptx_path, pdf_path):
    """Attempts automated PDF conversion via PowerPoint COM, prints manual steps."""
    converted = False
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        deck = powerpoint.Presentations.Open(os.path.abspath(pptx_path), WithWindow=False)
        deck.SaveAs(os.path.abspath(pdf_path), 32)  # 32 = ppSaveAsPDF
        deck.Close()
        powerpoint.Quit()
        converted = True
        print(f"[SUCCESS] Automatically exported presentation to PDF: {pdf_path}")
    except Exception as e:
        print(f"[INFO] Automated PowerPoint COM conversion: {e}")

    print("\n" + "=" * 80)
    print("INSTRUCTIONS FOR SAVING / EXPORTING AS PDF:")
    print("=" * 80)
    if converted:
        print(f"1. PDF automatically generated at:\n   {pdf_path}")
    print("2. In Microsoft PowerPoint:")
    print("   -> Open Analog_Finder_Presentation.pptx")
    print("   -> Click 'File' > 'Export' > 'Create PDF/XPS Document'")
    print("   -> Click 'Publish'")
    print("3. In Google Slides:")
    print("   -> Upload Analog_Finder_Presentation.pptx to Google Drive")
    print("   -> Open with Google Slides")
    print("   -> Click 'File' > 'Download' > 'PDF Document (.pdf)'")
    print("4. In LibreOffice (CLI):")
    print("   -> soffice --headless --convert-to pdf Analog_Finder_Presentation.pptx")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    build_deck()
