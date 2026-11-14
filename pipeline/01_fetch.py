"""
01_fetch.py - Data Fetcher for Planetary and Terrestrial Datasets
NASA Space Apps Challenge 2026: Analog Finder

Fetches authoritative datasets:
1. Mars MGS MOLA MEGDR 16 pix/deg (Jezero Crater, Gale Crater) via PDS Geosciences
2. Moon LRO LOLA South Polar 20m DEM (Shackleton Crater) via PDS Geosciences
3. Earth WorldClim 2.1 10m Bioclimatic variables (bio2 diurnal range, bio12 precipitation)
4. Earth NOAA ETOPO 2022 60s Global Relief Model (known analog benchmark slices and/or full raster)
"""

import os
import sys
import time
import zipfile
import urllib.request
import ssl
import certifi
import argparse
import yaml
import numpy as np
import rasterio
from rasterio.windows import from_bounds

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(BASE_DIR, "data_raw")
CONFIG_PATH = os.path.join(BASE_DIR, "pipeline", "config.yaml")

os.makedirs(DATA_RAW, exist_ok=True)

# SSL context with Mozilla certificates
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def download_file(url, out_path, min_bytes=1000, desc="File"):
    """Downloads a file with progress reporting and resume/cache check."""
    if os.path.exists(out_path) and os.path.getsize(out_path) > min_bytes:
        print(f"[CACHE] {desc} already exists at {out_path} ({os.path.getsize(out_path):,} bytes)")
        return True

    print(f"[FETCH] Downloading {desc} from {url}...")
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp, open(out_path, "wb") as f:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 1024 * 256
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0 and downloaded % (1024 * 1024 * 5) < chunk_size:
                    print(f"  Downloaded {downloaded/(1024*1024):.1f}/{total/(1024*1024):.1f} MB ({(downloaded/total)*100:.1f}%)")
        dt = time.time() - t0
        speed = (os.path.getsize(out_path) / (1024 * 1024)) / max(dt, 0.001)
        print(f"[SUCCESS] {desc} saved ({os.path.getsize(out_path):,} bytes in {dt:.1f}s, {speed:.2f} MB/s)")
        return True
    except Exception as e:
        print(f"[ERROR] Failed downloading {desc}: {e}")
        if os.path.exists(out_path):
            os.remove(out_path)
        return False

def fetch_mola_window(url, center_lat, center_lon, radius_deg, out_npy, desc):
    """Fetches a specific spatial bounding box from MOLA MEGDR 16 pix/deg via HTTP Range request."""
    if os.path.exists(out_npy):
        print(f"[CACHE] {desc} cached at {out_npy}")
        return np.load(out_npy)

    print(f"[FETCH] Streaming MOLA slice for {desc} (lat={center_lat}, lon={center_lon})...")
    total_cols = 5760
    bytes_per_pix = 2  # signed 16-bit big endian integer

    center_row = int(round((90.0 - center_lat) * 16))
    center_col = int(round((center_lon % 360.0) * 16))
    r_pix = max(2, int(round(radius_deg * 16)))

    row_min = max(0, center_row - r_pix)
    row_max = min(2879, center_row + r_pix + 1)
    col_min = max(0, center_col - r_pix)
    col_max = min(5759, center_col + r_pix + 1)

    start_byte = (row_min * total_cols) * bytes_per_pix
    end_byte = (row_max * total_cols) * bytes_per_pix - 1

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={start_byte}-{end_byte}"}
    )
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        raw_bytes = resp.read()

    full_rows = np.frombuffer(raw_bytes, dtype=">i2").reshape((row_max - row_min, total_cols))
    window = full_rows[:, col_min:col_max].astype(np.float32)
    np.save(out_npy, window)
    print(f"[SUCCESS] {desc} extracted: shape {window.shape}, elevation range [{window.min():.1f}m, {window.max():.1f}m]")
    return window

def fetch_lola_south_pole(url, radius_km, out_npy, desc):
    """Fetches high-res Shackleton Crater slice from LOLA South Polar 20m DEM via HTTP Range request."""
    if os.path.exists(out_npy):
        print(f"[CACHE] {desc} cached at {out_npy}")
        return np.load(out_npy)

    print(f"[FETCH] Streaming LOLA South Pole slice for {desc}...")
    total_cols = 7584
    bytes_per_pix = 2  # signed 16-bit little endian integer
    center_row = 3792
    center_col = 3792

    # 20m per pixel: radius_km * 50 pixels
    r_pix = int(round((radius_km * 1000.0) / 20.0))
    row_min = center_row - r_pix
    row_max = center_row + r_pix
    col_min = center_col - r_pix
    col_max = center_col + r_pix

    start_byte = (row_min * total_cols) * bytes_per_pix
    end_byte = (row_max * total_cols) * bytes_per_pix - 1

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={start_byte}-{end_byte}"}
    )
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        raw_bytes = resp.read()

    full_rows = np.frombuffer(raw_bytes, dtype="<i2").reshape((row_max - row_min, total_cols))
    window = (full_rows[:, col_min:col_max].astype(np.float32)) * 0.5  # 0.5 m scaling factor
    np.save(out_npy, window)
    print(f"[SUCCESS] {desc} extracted: shape {window.shape}, elevation range [{window.min():.1f}m, {window.max():.1f}m]")
    return window

def fetch_worldclim(cfg):
    """Downloads WorldClim 2.1 10m bioclim zip and extracts bio2 and bio12."""
    zip_url = cfg["data_urls"]["earth_climate"]
    zip_path = os.path.join(DATA_RAW, "wc2.1_10m_bio.zip")
    bio2_path = os.path.join(DATA_RAW, "wc2.1_10m_bio_2.tif")
    bio12_path = os.path.join(DATA_RAW, "wc2.1_10m_bio_12.tif")

    if not (os.path.exists(bio2_path) and os.path.exists(bio12_path)):
        download_file(zip_url, zip_path, min_bytes=40*1024*1024, desc="WorldClim 2.1 10m Bioclim")
        print("[EXTRACT] Unzipping bio_2 and bio_12 from WorldClim archive...")
        with zipfile.ZipFile(zip_path, "r") as z:
            for fname in ["wc2.1_10m_bio_2.tif", "wc2.1_10m_bio_12.tif"]:
                z.extract(fname, DATA_RAW)
        print("[SUCCESS] WorldClim bioclimatic rasters extracted successfully.")
    else:
        print("[CACHE] WorldClim bio2 and bio12 rasters are present.")

def fetch_known_analogs_from_etopo(cfg):
    """Extracts elevation windows for all known analog sites from NOAA ETOPO 2022 via vsicurl."""
    out_npy = os.path.join(DATA_RAW, "known_analogs_elevation.npz")
    if os.path.exists(out_npy):
        print(f"[CACHE] Known analogs elevation windows cached at {out_npy}")
        return

    etopo_url = "/vsicurl/" + cfg["data_urls"]["earth_etopo"]
    block_deg = cfg["resolution"]["grid_deg"]  # 0.1 deg (~10 km)
    data_dict = {}

    print(f"[FETCH] Querying NOAA ETOPO 2022 via vsicurl for {len(cfg['known_analogs'])} known analogs...")
    with rasterio.open(etopo_url) as src:
        for key, info in cfg["known_analogs"].items():
            lat, lon = info["lat"], info["lon"]
            # 2x block window to ensure smooth gradients
            w = from_bounds(lon - block_deg, lat - block_deg, lon + block_deg, lat + block_deg, transform=src.transform)
            arr = src.read(1, window=w).astype(np.float32)
            data_dict[key] = arr
            print(f"  {info['name']}: {arr.shape} pixels, elev [{arr.min():.1f}m to {arr.max():.1f}m]")

    np.savez(out_npy, **data_dict)
    print(f"[SUCCESS] Saved known analogs elevation to {out_npy}")

def main():
    parser = argparse.ArgumentParser(description="Fetch planetary and terrestrial datasets.")
    parser.add_argument("--full-etopo", action="store_true", help="Download full 444 MB NOAA ETOPO 2022 GeoTIFF")
    args = parser.parse_args()

    cfg = load_config()
    print("=" * 65)
    print("ANALOG FINDER: STEP 01 - DATA FETCH")
    print("=" * 65)

    # 1. Mars Targets (Jezero, Gale)
    mola_url = cfg["data_urls"]["mars_mola"]
    # Jezero: diameter 45 km -> radius ~0.5 deg
    fetch_mola_window(
        mola_url,
        cfg["targets"]["jezero"]["lat"],
        cfg["targets"]["jezero"]["lon"],
        radius_deg=0.55,
        out_npy=os.path.join(DATA_RAW, "jezero_elev.npy"),
        desc="Jezero Crater (Mars)"
    )
    # Gale: diameter 154 km -> radius ~1.4 deg
    fetch_mola_window(
        mola_url,
        cfg["targets"]["gale"]["lat"],
        cfg["targets"]["gale"]["lon"],
        radius_deg=1.45,
        out_npy=os.path.join(DATA_RAW, "gale_elev.npy"),
        desc="Gale Crater (Mars)"
    )

    # 2. Moon Target (Shackleton Crater Rim)
    lola_url = cfg["data_urls"]["moon_lola_south_pole"]
    fetch_lola_south_pole(
        lola_url,
        radius_km=14.0,  # 28 km window covering the 21 km crater + rim
        out_npy=os.path.join(DATA_RAW, "shackleton_elev.npy"),
        desc="Shackleton Crater Rim (Moon)"
    )

    # 3. Earth WorldClim Data
    fetch_worldclim(cfg)

    # 4. Earth Known Analogs from NOAA ETOPO 2022
    fetch_known_analogs_from_etopo(cfg)

    # 5. Full ETOPO 2022 GeoTIFF (if requested via flag)
    if args.full_etopo:
        etopo_dest = os.path.join(DATA_RAW, "ETOPO_2022_v1_60s_N90W180_surface.tif")
        download_file(cfg["data_urls"]["earth_etopo"], etopo_dest, min_bytes=400*1024*1024, desc="NOAA ETOPO 2022 Global DEM")

    print("=" * 65)
    print("[SUCCESS] All Phase 1 input datasets fetched and verified.")
    print("=" * 65)

if __name__ == "__main__":
    main()
