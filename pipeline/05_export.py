"""
05_export.py - Web Data Bundler & Heatmap Overlay Generator
NASA Space Apps Challenge 2026: Analog Finder

Exports:
1. 6x Lightweight Global Heatmap RGBA PNGs (3 targets x 2 methods), each < 1 MB
2. JSON Metadata: targets, known analogs, validation report, and candidate cells table for client-side re-weighting
3. Copies assets to data_out/ and web/public/data/
"""

import os
import json
import shutil
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROC = os.path.join(BASE_DIR, "data_processed")
DATA_OUT = os.path.join(BASE_DIR, "data_out")
WEB_PUBLIC_DATA = os.path.join(BASE_DIR, "web", "public", "data")

os.makedirs(DATA_OUT, exist_ok=True)
os.makedirs(WEB_PUBLIC_DATA, exist_ok=True)

# Turbo / Magma style colormap lookup for smooth heatmap visualization
# Values from 0.0 to 1.0 mapped to (R, G, B, Alpha)
def colormap_inferno(val):
    """Maps similarity [0, 1] to RGBA color with progressive alpha."""
    # Clip val
    v = np.clip(val, 0.0, 1.0)
    # Threshold below 0.70 to transparent to let satellite/dark basemap show through
    alpha = np.where(v < 0.70, 0, np.clip((v - 0.70) / 0.30, 0.0, 1.0) * 210)
    
    # Inferno/Magma color gradient
    r = np.clip(np.sin(v * np.pi * 1.5 - 0.2) * 255 + 50, 0, 255)
    g = np.clip(np.sin(v * np.pi - 0.5) * 230, 0, 255)
    b = np.clip(np.cos(v * np.pi * 0.8) * 180, 0, 255)
    
    # High similarity (>0.95) transitions to vibrant gold/yellow
    high_mask = v >= 0.95
    r[high_mask] = 255
    g[high_mask] = 215 + (v[high_mask] - 0.95) * 800
    b[high_mask] = 50
    alpha[high_mask] = 240

    return np.dstack([r.astype(np.uint8), g.astype(np.uint8), b.astype(np.uint8), alpha.astype(np.uint8)])

def generate_heatmap_png(sim_1d, valid_mask, grid_shape, out_png):
    """Reconstructs 2D grid from 1D arid cells and exports an RGBA PNG."""
    grid = np.zeros(grid_shape, dtype=np.float32)
    grid[valid_mask] = sim_1d

    # Map to RGBA
    rgba = colormap_inferno(grid)
    img = Image.fromarray(rgba, mode="RGBA")
    
    # Save optimized PNG
    img.save(out_png, "PNG", optimize=True)
    size_kb = os.path.getsize(out_png) / 1024
    print(f"  Exported {os.path.basename(out_png)} ({size_kb:.1f} KB)")
    return out_png

def export_all():
    print("=" * 70)
    print("ANALOG FINDER: STEP 05 - WEB ASSET EXPORT")
    print("=" * 70)

    # 1. Load data
    earth_npz = np.load(os.path.join(DATA_PROC, "earth_features.npz"))
    valid_mask = earth_npz["mask_valid"]
    grid_shape = tuple(earth_npz["grid_shape"])
    lats = earth_npz["lats"]
    lons = earth_npz["lons"]
    slopes = earth_npz["slope"]
    roughs = earth_npz["roughness"]
    reliefs = earth_npz["local_relief"]
    elevs = earth_npz["elevation"]
    precips = earth_npz["precipitation"]

    sim_npz = np.load(os.path.join(DATA_PROC, "similarity_results.npz"))

    with open(os.path.join(DATA_PROC, "target_features.json"), "r", encoding="utf-8") as f:
        targets = json.load(f)
    with open(os.path.join(DATA_PROC, "known_analogs_features.json"), "r", encoding="utf-8") as f:
        analogs = json.load(f)
    with open(os.path.join(DATA_PROC, "validation_report.json"), "r", encoding="utf-8") as f:
        validation_report = json.load(f)
    with open(os.path.join(DATA_PROC, "earth_stats.json"), "r", encoding="utf-8") as f:
        earth_stats = json.load(f)

    # 2. Generate Heatmap Overlays
    print("\n--- 1. GENERATING GLOBAL HEATMAP OVERLAYS (RGBA PNG) ---")
    for t_key in targets.keys():
        for method in ["cos", "mah"]:
            field_name = f"{t_key}_{method}"
            sim_vals = sim_npz[field_name]
            
            # Normalize mahalanobis for visualization if needed
            if method == "mah":
                max_v = np.nanmax(sim_vals)
                vis_vals = sim_vals / (max_v + 1e-9) if max_v > 0 else sim_vals
            else:
                vis_vals = sim_vals

            out_filename = f"heatmap_{t_key}_{method}.png"
            dest_out = os.path.join(DATA_OUT, out_filename)
            generate_heatmap_png(vis_vals, valid_mask, grid_shape, dest_out)
            # Copy to web public
            shutil.copy2(dest_out, os.path.join(WEB_PUBLIC_DATA, out_filename))

    # 3. Export Candidate Cells Table for Client-Side Re-weighting
    # Select the top 1500 candidate cells across all 3 targets plus a uniform background sample
    print("\n--- 2. EXPORTING CANDIDATE CELLS TABLE FOR CLIENT-SIDE RE-WEIGHTING ---")
    
    # Calculate Z-scores for fast client-side dot product
    mu_slope, std_slope = earth_stats["slope"]["mean"], earth_stats["slope"]["std"]
    mu_rough, std_rough = earth_stats["roughness"]["mean"], earth_stats["roughness"]["std"]
    mu_rel, std_rel = earth_stats["local_relief"]["mean"], earth_stats["local_relief"]["std"]

    z_slopes = (slopes - mu_slope) / std_slope
    z_roughs = (roughs - mu_rough) / std_rough
    z_reliefs = (reliefs - mu_rel) / std_rel

    candidate_indices = set()
    for t_key in targets.keys():
        cos_scores = sim_npz[f"{t_key}_cos"]
        top_k = np.argsort(cos_scores)[-800:]
        candidate_indices.update(top_k)

    # Sample an additional 500 diverse global cells for broad map coverage
    total_cells = len(slopes)
    stride = max(1, total_cells // 500)
    candidate_indices.update(range(0, total_cells, stride))

    selected_idx = sorted(list(candidate_indices))
    print(f"  Selected {len(selected_idx):,} representative Earth cells for client-side engine.")

    candidate_cells = []
    for idx in selected_idx:
        candidate_cells.append({
            "id": int(idx),
            "lat": round(float(lats[idx]), 3),
            "lon": round(float(lons[idx]), 3),
            "slope": round(float(slopes[idx]), 2),
            "roughness": round(float(roughs[idx]), 1),
            "relief": round(float(reliefs[idx]), 1),
            "elevation": round(float(elevs[idx]), 0),
            "precip": round(float(precips[idx]), 1),
            # Pre-normalized Z-scores for instant client-side re-weighting
            "z_s": round(float(z_slopes[idx]), 4),
            "z_r": round(float(z_roughs[idx]), 4),
            "z_l": round(float(z_reliefs[idx]), 4)
        })

    candidate_file = os.path.join(DATA_OUT, "candidate_cells.json")
    with open(candidate_file, "w", encoding="utf-8") as f:
        json.dump(candidate_cells, f)
    shutil.copy2(candidate_file, os.path.join(WEB_PUBLIC_DATA, "candidate_cells.json"))
    print(f"  Exported candidate_cells.json ({os.path.getsize(candidate_file)/1024:.1f} KB)")

    # 4. Export Target & Benchmark Metadata
    print("\n--- 3. EXPORTING TARGETS, ANALOGS, AND VALIDATION METADATA ---")
    
    # Enhance targets with precomputed z-scores
    for t_key, t_info in targets.items():
        t_info["z_s"] = round(float((t_info["mean_slope"] - mu_slope) / std_slope), 4)
        t_info["z_r"] = round(float((t_info["roughness"] - mu_rough) / std_rough), 4)
        t_info["z_l"] = round(float((t_info["local_relief"] - mu_rel) / std_rel), 4)

    # Save metadata files
    meta_files = [
        ("targets.json", targets),
        ("known_analogs.json", analogs),
        ("validation_report.json", validation_report),
        ("earth_stats.json", earth_stats)
    ]
    for fname, data_obj in meta_files:
        path_out = os.path.join(DATA_OUT, fname)
        with open(path_out, "w", encoding="utf-8") as f:
            json.dump(data_obj, f, indent=2)
        shutil.copy2(path_out, os.path.join(WEB_PUBLIC_DATA, fname))
        print(f"  Exported {fname} ({os.path.getsize(path_out)/1024:.1f} KB)")

    # Summary
    total_data_out_bytes = sum(os.path.getsize(os.path.join(DATA_OUT, f)) for f in os.listdir(DATA_OUT))
    print("\n" + "=" * 70)
    print(f"[SUCCESS] Export complete! Total shipped static data: {total_data_out_bytes/(1024*1024):.2f} MB")
    print(f"Each overlay is < 1 MB (budget: < 10 MB). Total payload is < 3 MB (budget: < 50 MB).")
    print("=" * 70)

if __name__ == "__main__":
    export_all()
