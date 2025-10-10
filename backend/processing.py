# backend/processing.py  (REPLACE ENTIRE FILE)
import os, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
MODEL = ROOT / "rnnoise-models" / "mcdnnsn_rnnoise_model.bin"
USE_ARNNDN = os.getenv("USE_ARNNDN", "1") == "1"

_FILTER_CACHE = {}

def _has_filter(name: str) -> bool:
    if name in _FILTER_CACHE:
        return _FILTER_CACHE[name]
    try:
        out = subprocess.check_output(
            ["ffmpeg", "-hide_banner", "-filters"],
            stderr=subprocess.STDOUT,
            text=True
        )
        _FILTER_CACHE[name] = (name in out)
        return _FILTER_CACHE[name]
    except Exception:
        _FILTER_CACHE[name] = False
        return False

def _denoise_filter():
    # Prefer arnndn if available and the model exists; fallback to afftdn otherwise
    if USE_ARNNDN and _has_filter("arnndn") and MODEL.exists():
        return f"arnndn=m={MODEL}"
    return "afftdn=nr=20:nf=-25"  # robust fallback

def _core_filters():
    # Neutral, pleasant polish
    return ",".join([
        _denoise_filter(),
        "highpass=f=60",
        "compand=attacks=0.005:decays=0.25:points=-90/-90|-30/-24|-6/-3|0/0:gain=5:volume=0:delay=0",
        "loudnorm=I=-14:TP=-1:LRA=11:dual_mono=true:linear=true",
        "alimiter=limit=-1"
    ])

def process_file_to_preview_full(src_path: str, dest_path: str):
    """
    Full-length preview with a light watermark beep every ~12s,
    exported at 96 kbps MP3 so users can audition end to end.
    """
    # Filter graph:
    # [0:a] <core filters> [aud];
    # sine->volume periodic gating [beep];
    # [aud][beep] amix -> output
    filter_complex = (
        f"[0:a]{_core_filters()}[aud];"
        "sine=frequency=880:sample_rate=44100,volume='if(lt(mod(t,12),0.25),0.35,0)'[beep];"
        "[aud][beep]amix=inputs=2:duration=first:dropout_transition=0"
    )
    cmd = [
        "ffmpeg", "-y", "-i", src_path,
        "-filter_complex", filter_complex,
        "-c:a", "mp3", "-b:a", "96k",
        dest_path,
    ]
    subprocess.check_call(cmd)

def process_full(src_path: str, dest_path: str):
    # Paid export: clean chain at higher bitrate (192 kbps)
    cmd = [
        "ffmpeg", "-y", "-i", src_path,
        "-af", _core_filters(),
        "-c:a", "mp3", "-b:a", "192k",
        dest_path,
    ]
    subprocess.check_call(cmd)

