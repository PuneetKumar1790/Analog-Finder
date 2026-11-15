import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
import imageio_ffmpeg
import win32com.client
import wave
import contextlib

def generate_video():
    print("=== Step 1: Synthesizing Narration Audio ===")
    speaker = win32com.client.Dispatch('SAPI.SpVoice')
    speaker.Rate = 3  # Paced for ~28.4s
    stream = win32com.client.Dispatch('SAPI.SpFileStream')
    wav_path = os.path.abspath('narration_final.wav')
    if os.path.exists(wav_path):
        os.remove(wav_path)
    stream.Open(wav_path, 3)
    speaker.AudioOutputStream = stream

    script = (
        'Before astronauts land on the Moon or explore Mars, every rover and habitat must be tested on Earth. '
        'How do we find true planetary analogs? '
        'Analog Finder standardizes NASA MOLA, LOLA, and NOAA elevation data to a uniform 10-kilometer scale across 500,000 Earth cells. '
        'Our Mahalanobis engine decouples terrain roughness, ranking Atacama in the top 0.01% globally, '
        'and discovering novel high-altitude analogs in Tibet and the Andes. '
        'Zero-backend, 100% open-source, and live on Vercel. '
        'Analog Finder: accelerating planetary exploration.'
    )
    speaker.Speak(script)
    stream.Close()

    with contextlib.closing(wave.open(wav_path, 'r')) as f:
        audio_dur = f.getnframes() / float(f.getframerate())
    print(f"Synthesized audio duration: {audio_dur:.2f} seconds")

    total_duration = 29.0  # Strictly < 30s limit
    fps = 30
    total_frames = int(total_duration * fps)  # 870 frames
    width, height = 1920, 1080

    print(f"=== Step 2: Preparing Visual Assets ({total_frames} frames @ {fps} fps, 1080p) ===")
    screenshot_main_path = r"C:/Users/Raju/.gemini/antigravity/brain/cde62d75-5c98-46e9-a993-758ebd81a512/.system_generated/steps/151/media_0.png"
    screenshot_inspect_path = r"C:/Users/Raju/.gemini/antigravity/brain/cde62d75-5c98-46e9-a993-758ebd81a512/.system_generated/steps/172/media_0.png"
    screenshot_modal_path = r"C:/Users/Raju/.gemini/antigravity/brain/cde62d75-5c98-46e9-a993-758ebd81a512/.system_generated/steps/226/media_0.png"

    img_main = Image.open(screenshot_main_path).convert('RGB')
    img_inspect = Image.open(screenshot_inspect_path).convert('RGB')
    img_modal = Image.open(screenshot_modal_path).convert('RGB')

    # Fonts
    try:
        font_large = ImageFont.truetype('arialbd.ttf', 56)
        font_medium = ImageFont.truetype('arialbd.ttf', 38)
        font_small = ImageFont.truetype('arial.ttf', 24)
        font_mono = ImageFont.truetype('consola.ttf', 22)
        font_mono_large = ImageFont.truetype('consolab.ttf', 28)
    except:
        font_large = ImageFont.truetype('arial.ttf', 56)
        font_medium = ImageFont.truetype('arial.ttf', 38)
        font_small = ImageFont.truetype('arial.ttf', 24)
        font_mono = ImageFont.truetype('arial.ttf', 22)
        font_mono_large = ImageFont.truetype('arial.ttf', 28)

    # Helper: Draw telemetry lower third banner
    def draw_telemetry_banner(draw, sec_tag, title, subtitle):
        # Banner background
        draw.rectangle([0, height - 120, width, height], fill=(13, 17, 23))
        draw.line([0, height - 120, width, height - 120], fill=(48, 54, 61), width=2)
        # Category pill
        draw.rectangle([60, height - 95, 180, height - 65], fill=(22, 29, 42), outline=(56, 189, 248), width=1)
        draw.text((75, height - 90), sec_tag, fill=(56, 189, 248), font=font_mono)
        # Title & subtitle
        draw.text((205, height - 98), title, fill=(240, 246, 252), font=font_mono_large)
        draw.text((205, height - 66), subtitle, fill=(139, 148, 158), font=font_small)
        # Timer / Watermark on right
        draw.text((width - 380, height - 85), "NASA SPACE APPS 2026", fill=(234, 179, 8), font=font_mono)

    # Helper: Ken Burns smooth zoom / pan
    def get_ken_burns(img, progress, zoom_start=1.0, zoom_end=1.12, pan_x=0, pan_y=0):
        cur_zoom = zoom_start + (zoom_end - zoom_start) * progress
        cur_w = int(width / cur_zoom)
        cur_h = int(height / cur_zoom)

        # Scale original image to cover target
        scale_ratio = max(width / img.width, height / img.height)
        scaled_w = int(img.width * scale_ratio)
        scaled_h = int(img.height * scale_ratio)
        scaled_img = img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

        # Crop window
        max_x = max(0, scaled_w - cur_w)
        max_y = max(0, scaled_h - cur_h)
        crop_x = int(max_x * (0.5 + pan_x * progress * 0.5))
        crop_y = int(max_y * (0.5 + pan_y * progress * 0.5))

        crop_x = max(0, min(crop_x, scaled_w - cur_w))
        crop_y = max(0, min(crop_y, scaled_h - cur_h))

        cropped = scaled_img.crop((crop_x, crop_y, crop_x + cur_w, crop_y + cur_h))
        return cropped.resize((width, height), Image.Resampling.LANCZOS)

    temp_video_path = os.path.abspath('temp_video.mp4')
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)

    writer = imageio.get_writer(temp_video_path, fps=fps, codec='libx264', quality=8, pixelformat='yuv420p')

    print("=== Step 3: Rendering Video Frames ===")
    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)

        if frame_idx % 90 == 0:
            print(f"Rendering frame {frame_idx}/{total_frames} ({t:.1f}s / {total_duration:.1f}s)...")

        # SCENE 1: 0.0s -> 6.5s (Title & Problem Setup)
        if t < 6.5:
            prog = t / 6.5
            frame = Image.new('RGB', (width, height), color=(11, 15, 23))
            draw = ImageDraw.Draw(frame)

            # Background subtle tech grid
            for gx in range(0, width, 120):
                draw.line([gx, 0, gx, height], fill=(18, 24, 35), width=1)
            for gy in range(0, height, 120):
                draw.line([0, gy, width, gy], fill=(18, 24, 35), width=1)

            # Central title card
            alpha = min(1.0, t * 1.5)
            y_offset = int(20 * (1.0 - alpha))

            # Header tag
            draw.text((120, 260 + y_offset), "NASA SPACE APPS CHALLENGE 2026 // GLOBAL ENTRY", fill=(56, 189, 248), font=font_mono_large)
            # Main Title
            draw.text((120, 310 + y_offset), "ANALOG FINDER", fill=(240, 246, 252), font=font_large)
            # Subtitle
            draw.text((120, 385 + y_offset), "Quantitative Planetary Surface Analog Discovery via Standardized Geomorphometry", fill=(234, 179, 8), font=font_medium)

            # Divider line
            draw.line([120, 450 + y_offset, width - 120, 450 + y_offset], fill=(48, 54, 61), width=2)

            # Mission target chips
            draw.text((120, 480 + y_offset), "MISSION TARGET SITES:", fill=(139, 148, 158), font=font_mono)
            targets = [
                ("MOON: SHACKLETON CRATER RIM", "89.90°S, 0.00°E • LRO LOLA (60m DEM) • Permanent Shadow & Cold Traps"),
                ("MARS: JEZERO CRATER DELTA", "18.38°N, 77.58°E • MGS MOLA MEGDR • Ancient Paleolake & Delta Deposits"),
                ("MARS: GALE CRATER / MT. SHARP", "5.40°S, 137.80°E • MGS MOLA MEGDR • 5.5 km Layered Sedimentary Peak")
            ]
            for i, (tgt_name, tgt_desc) in enumerate(targets):
                ty = 520 + i * 65 + y_offset
                draw.rectangle([120, ty, width - 120, ty + 50], fill=(22, 29, 42), outline=(48, 54, 61), width=1)
                draw.text((140, ty + 12), tgt_name, fill=(56, 189, 248), font=font_mono_large)
                draw.text((620, ty + 15), tgt_desc, fill=(139, 148, 158), font=font_small)

            draw_telemetry_banner(draw, "SEC 01", "THE ANALOG DILEMMA: QUALITATIVE GUESSWORK vs QUANTITATIVE MATH", "Every rover, drill, and astronaut habitat must be tested on Earth before flight.")

        # SCENE 2: 6.5s -> 13.5s (Scale Harmonization & Live Workstation Interface)
        elif t < 13.5:
            prog = (t - 6.5) / 7.0
            frame = get_ken_burns(img_main, prog, zoom_start=1.0, zoom_end=1.08, pan_x=0.2, pan_y=-0.1)
            draw = ImageDraw.Draw(frame)

            # Highlight telemetry callout
            draw_telemetry_banner(
                draw,
                "SEC 02",
                "SCALE HARMONIZATION // ~10.0 KM EQUAL-AREA APERTURE",
                "Ingests NOAA ETOPO 2022, MGS MOLA & LRO LOLA • 500,073 Valid Arid Earth Cells (Precip < 500mm)"
            )

        # SCENE 3: 13.5s -> 21.5s (Mahalanobis Decoupling & Station Diagnostics)
        elif t < 21.5:
            prog = (t - 13.5) / 8.0
            frame = get_ken_burns(img_inspect, prog, zoom_start=1.02, zoom_end=1.12, pan_x=0.3, pan_y=0.1)
            draw = ImageDraw.Draw(frame)

            draw_telemetry_banner(
                draw,
                "SEC 03",
                "MAHALANOBIS COVARIANCE DECOUPLING // det(Σ) = 0.0142",
                "Decouples 98.7% roughness/relief collinearity • Validates Atacama in Top 0.01% for Jezero Crater"
            )

        # SCENE 4: 21.5s -> 29.0s (Validation Matrix & Final CTA)
        else:
            prog = (t - 21.5) / 7.5
            if prog < 0.5:
                # Show Validation Modal
                sub_prog = prog / 0.5
                frame = get_ken_burns(img_modal, sub_prog, zoom_start=1.0, zoom_end=1.06, pan_x=0.0, pan_y=0.0)
                draw = ImageDraw.Draw(frame)
                draw_telemetry_banner(
                    draw,
                    "SEC 04",
                    "GROUND-TRUTH BENCHMARK MATRIX & DISCOVERIES",
                    "Atacama #51 (Top 0.01%) • Iceland #41 (Top 0.01%) • Qaidam Basin • San Juan • Bowers Nunataks"
                )
            else:
                # Final Call To Action Screen
                sub_prog = (prog - 0.5) / 0.5
                frame = Image.new('RGB', (width, height), color=(11, 15, 23))
                draw = ImageDraw.Draw(frame)

                # Tech Grid
                for gx in range(0, width, 120):
                    draw.line([gx, 0, gx, height], fill=(18, 24, 35), width=1)
                for gy in range(0, height, 120):
                    draw.line([0, gy, width, gy], fill=(18, 24, 35), width=1)

                draw.text((120, 240), "NASA SPACE APPS CHALLENGE 2026 // PROJECT DEMO", fill=(56, 189, 248), font=font_mono_large)
                draw.text((120, 290), "ANALOG FINDER IS LIVE", fill=(240, 246, 252), font=font_large)
                draw.text((120, 365), "Zero-Backend • Sub-2ms Dynamic Re-weighting • 100% Open Science", fill=(234, 179, 8), font=font_medium)
                draw.line([120, 430, width - 120, 430], fill=(48, 54, 61), width=2)

                draw.text((120, 470), "🌐 LIVE INTERACTIVE WORKSTATION:", fill=(139, 148, 158), font=font_mono)
                draw.text((120, 505), "https://analog-finder-amber.vercel.app/", fill=(56, 189, 248), font=font_large)

                draw.text((120, 600), "📁 OPEN-SOURCE CODE & DATA ASSETS:", fill=(139, 148, 158), font=font_mono)
                draw.text((120, 635), "https://github.com/PuneetKumar1790/Analog-Finder", fill=(240, 246, 252), font=font_medium)

                draw.text((120, 730), "🚀 READY FOR ARTEMIS & MARS SURFACE MISSION PLANNING", fill=(35, 134, 54), font=font_mono_large)

                draw_telemetry_banner(
                    draw,
                    "READY",
                    "SUBMISSION DEMO // 29.0s COMPLIANT WITH NASA HARD LIMIT (≤ 30s)",
                    "Deployed on Vercel Edge • Google Colab Notebook • Reproducible Python Pipeline"
                )

        # Subtle fade out at the very end (last 0.8s)
        if t > 28.2:
            fade = max(0.0, (29.0 - t) / 0.8)
            frame_arr = np.array(frame, dtype=np.float32) * fade
            frame = Image.fromarray(frame_arr.astype(np.uint8))

        writer.append_data(np.array(frame))

    writer.close()
    print("Video track rendered successfully!")

    print("=== Step 4: Muxing Audio & Video with FFmpeg ===")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_mp4_root = os.path.abspath("Analog_Finder_Demo_30s.mp4")
    out_mp4_public = os.path.abspath("web/public/analog_finder_demo.mp4")

    # Command: mux video + audio, trim strictly to 29.0 seconds, high quality AAC audio
    cmd = [
        ffmpeg_exe, "-y",
        "-i", temp_video_path,
        "-i", wav_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "29.0",
        "-movflags", "+faststart",
        out_mp4_root
    ]
    subprocess.run(cmd, check=True)

    # Copy to web/public for live web serving
    import shutil
    shutil.copyfile(out_mp4_root, out_mp4_public)

    # Clean up temp files
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)
    if os.path.exists(wav_path):
        os.remove(wav_path)

    size_mb = os.path.getsize(out_mp4_root) / (1024 * 1024)
    print(f"✅ FINAL DEMO VIDEO CREATED: {out_mp4_root} ({size_mb:.2f} MB, Duration: 29.00s)")
    print(f"✅ STAGED FOR WEB: {out_mp4_public}")

if __name__ == "__main__":
    generate_video()
