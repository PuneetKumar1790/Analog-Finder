"""
03_similarity.py - Quantitative Planetary Similarity Engine
NASA Space Apps Challenge 2026: Analog Finder

Computes similarity between planetary targets and Earth's surface cells using:
1. Z-Score Normalization against Earth's background feature distribution
2. Weighted Cosine Similarity
3. Mahalanobis Distance / Similarity (accounting for feature covariance)
"""

import os
import json
import yaml
import time
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROC = os.path.join(BASE_DIR, "data_processed")
CONFIG_PATH = os.path.join(BASE_DIR, "pipeline", "config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def compute_similarity():
    cfg = load_config()
    print("=" * 70)
    print("ANALOG FINDER: STEP 03 - SIMILARITY CALCULATION")
    print("=" * 70)

    # 1. Load Earth feature matrix
    earth_npz = os.path.join(DATA_PROC, "earth_features.npz")
    earth_data = np.load(earth_npz)
    lats = earth_data["lats"]
    lons = earth_data["lons"]
    slopes = earth_data["slope"]
    roughs = earth_data["roughness"]
    reliefs = earth_data["local_relief"]
    diurnals = earth_data["diurnal_range"]
    elevs = earth_data["elevation"]
    precips = earth_data["precipitation"]

    include_diurnal = cfg["features"].get("include_diurnal_range", False)

    # Build feature matrices
    if include_diurnal:
        features_list = ["slope", "roughness", "local_relief", "diurnal_range"]
        X_earth = np.column_stack([slopes, roughs, reliefs, diurnals])
        weights = np.array([
            cfg["similarity"]["weights"]["mean_slope"],
            cfg["similarity"]["weights"]["roughness"],
            cfg["similarity"]["weights"]["local_relief"],
            cfg["similarity"]["weights"]["diurnal_range"]
        ], dtype=np.float32)
    else:
        features_list = ["slope", "roughness", "local_relief"]
        X_earth = np.column_stack([slopes, roughs, reliefs])
        # Default weights adjusted for colinearity (slope 0.45, roughness 0.35, relief 0.20)
        weights = np.array([0.45, 0.35, 0.20], dtype=np.float32)

    # Normalize weights to sum to 1.0
    weights = weights / np.sum(weights)

    # 2. Z-score normalization against Earth's distribution
    mu = np.nanmean(X_earth, axis=0)
    sigma = np.nanstd(X_earth, axis=0)
    # Prevent division by zero
    sigma = np.where(sigma == 0, 1e-6, sigma)

    Z_earth = (X_earth - mu) / sigma
    # Replace any residual NaNs with 0
    Z_earth = np.nan_to_num(Z_earth, nan=0.0)

    # 3. Covariance and Precision Matrix for Mahalanobis
    cov = np.cov(Z_earth, rowvar=False) + 1e-4 * np.eye(len(features_list))
    inv_cov = np.linalg.pinv(cov).astype(np.float32)

    print(f"[INFO] Evaluating {len(Z_earth):,} valid arid Earth cells across {len(features_list)} features.")
    print(f"[INFO] Weights applied: {dict(zip(features_list, [round(float(w), 3) for w in weights]))}")

    # Weighted representation for cosine similarity
    w_sqrt = np.sqrt(weights)
    Z_w = Z_earth * w_sqrt
    norm_earth_w = np.linalg.norm(Z_w, axis=1)

    # 4. Load Targets
    with open(os.path.join(DATA_PROC, "target_features.json"), "r", encoding="utf-8") as f:
        targets = json.load(f)

    sim_results = {}
    top_candidates = {}

    for t_key, t_info in targets.items():
        t0 = time.time()
        print(f"\n[CALC] Processing Target: {t_info['name']} ({t_info['body']})...")

        if include_diurnal:
            raw_target = np.array([
                t_info["mean_slope"],
                t_info["roughness"],
                t_info["local_relief"],
                t_info["diurnal_range"]
            ], dtype=np.float32)
        else:
            raw_target = np.array([
                t_info["mean_slope"],
                t_info["roughness"],
                t_info["local_relief"]
            ], dtype=np.float32)

        # Target Z-Score using Earth distribution
        z_t = (raw_target - mu) / sigma
        z_tw = z_t * w_sqrt
        norm_t_w = np.linalg.norm(z_tw)

        # A. Cosine Similarity: dot(u, v) / (|u| * |v|)
        cos_sim = np.dot(Z_w, z_tw) / (norm_earth_w * norm_t_w + 1e-9)
        # Scaled to [0, 1] range
        cos_sim_scaled = np.clip((cos_sim + 1.0) / 2.0, 0.0, 1.0).astype(np.float32)

        # B. Mahalanobis Distance: sqrt((x - y)^T * inv_cov * (x - y))
        diff = Z_earth - z_t
        dm = np.sqrt(np.maximum(0.0, np.sum(np.dot(diff, inv_cov) * diff, axis=1))).astype(np.float32)
        # Similarity conversion: exponential decay
        mah_sim = np.exp(-dm / 2.0).astype(np.float32)

        dt = time.time() - t0
        print(f"  Computed similarity in {dt:.3f}s: Cosine max={cos_sim_scaled.max():.4f}, Mahalanobis max={mah_sim.max():.4f}")

        sim_results[f"{t_key}_cos"] = cos_sim_scaled
        sim_results[f"{t_key}_mah"] = mah_sim
        sim_results[f"{t_key}_dm"] = dm

        # Extract top 50 non-clustered candidates for web export
        top_idx_cos = np.argsort(cos_sim_scaled)[::-1]
        top_list = []
        seen_coords = []
        for idx in top_idx_cos:
            lat_i = float(lats[idx])
            lon_i = float(lons[idx])
            if any(abs(lat_i - clat) < 1.0 and abs(lon_i - clon) < 1.0 for clat, clon in seen_coords):
                continue
            seen_coords.append((lat_i, lon_i))
            top_list.append({
                "rank": len(top_list) + 1,
                "lat": round(lat_i, 3),
                "lon": round(lon_i, 3),
                "cosine_sim": round(float(cos_sim_scaled[idx]), 4),
                "mahalanobis_sim": round(float(mah_sim[idx]), 4),
                "mahalanobis_dist": round(float(dm[idx]), 2),
                "slope": round(float(slopes[idx]), 2),
                "roughness": round(float(roughs[idx]), 1),
                "local_relief": round(float(reliefs[idx]), 1),
                "elevation": round(float(elevs[idx]), 0),
                "annual_precip": round(float(precips[idx]), 1)
            })
            if len(top_list) >= 50:
                break

        top_candidates[t_key] = top_list

    # 5. Save similarity results
    out_sim_npz = os.path.join(DATA_PROC, "similarity_results.npz")
    np.savez_compressed(
        out_sim_npz,
        lats=lats,
        lons=lons,
        **sim_results
    )
    print(f"\n[SUCCESS] Similarity matrices saved to {out_sim_npz}")

    out_top_json = os.path.join(DATA_PROC, "top_analogs_per_target.json")
    with open(out_top_json, "w", encoding="utf-8") as f:
        json.dump(top_candidates, f, indent=2)
    print(f"[SUCCESS] Top candidate locations saved to {out_top_json}")

if __name__ == "__main__":
    compute_similarity()
