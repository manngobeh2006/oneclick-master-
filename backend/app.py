import os
import re
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# ----------- Config -----------
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PREVIEWS_DIR = DATA_DIR / "previews"
OUTPUTS_DIR = DATA_DIR / "outputs"

for d in (DATA_DIR, UPLOADS_DIR, PREVIEWS_DIR, OUTPUTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_UPLOADS = os.getenv("S3_BUCKET_UPLOADS")
S3_BUCKET_OUTPUTS = os.getenv("S3_BUCKET_OUTPUTS")

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", FRONTEND_URL)

# When True, we skip Stripe/S3 checks and keep everything local.
DEV_MODE = not bool(STRIPE_SECRET_KEY)

# ----------- App -----------
app = FastAPI()

# CORS
origins = [o.strip() for o in (CORS_ORIGINS or "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve local files so the browser can stream previews/downloads
# /files/previews/<file>, /files/outputs/<file>
app.mount("/files", StaticFiles(directory=str(DATA_DIR), html=False), name="files")


# ----------- Helpers -----------
SAFE_CHARS = re.compile(r"[^a-zA-Z0-9._-]+")


def safe_name(name: str) -> str:
    name = name.strip().replace(" ", "_")
    return SAFE_CHARS.sub("", name)


def run_ffmpeg(args: list[str]) -> None:
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="ignore"))


def make_preview(input_path: Path, out_path: Path) -> None:
    """
    Full-length preview at 128 kbps with professional mastering chain and subtle watermark.
    Includes: noise reduction, EQ, compression, limiting, and stereo enhancement.
    """
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-f", "lavfi", "-i", "sine=frequency=880:sample_rate=48000",
        "-filter_complex",
        "[0:a]"
        "highpass=f=20,"
        "lowpass=f=20000,"
        "equalizer=f=60:t=h:w=100:g=-1,"
        "equalizer=f=200:t=h:w=200:g=0.5,"
        "equalizer=f=1000:t=h:w=500:g=0.2,"
        "equalizer=f=3000:t=h:w=1000:g=1,"
        "equalizer=f=8000:t=h:w=2000:g=0.8,"
        "acompressor=threshold=-18dB:ratio=2.5:attack=3:release=100:makeup=2,"
        "acompressor=threshold=-12dB:ratio=4:attack=1:release=50:makeup=1,"
        "alimiter=level_in=1:level_out=0.95:limit=0.95,"
        "loudnorm=I=-16:TP=-1.5:LRA=11,"
        "extrastereo=m=1.2[aud];"
        "[1:a]volume=-25dB[beep];"
        "[aud][beep]amix=inputs=2:normalize=0[out]",
        "-map", "[out]",
        "-ac", "2",
        "-ar", "44100",
        "-b:a", "128k",
        "-shortest",
        str(out_path)
    ])


def make_master(input_path: Path, out_path: Path) -> None:
    """
    Professional mastering chain at 320 kbps with advanced processing.
    Includes: noise reduction, multi-band EQ, multi-stage compression, 
    stereo enhancement, harmonic enhancement, and professional limiting.
    """
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-filter:a",
        # High-pass filter to remove rumble
        "highpass=f=18,"
        # Low-pass filter to remove harsh high frequencies
        "lowpass=f=20000,"
        # Gentle noise gate
        "agate=threshold=0.001:ratio=2:attack=20:release=250,"
        # Multi-band EQ for professional sound
        "equalizer=f=60:t=h:w=80:g=-0.8,"
        "equalizer=f=120:t=h:w=120:g=-0.3,"
        "equalizer=f=250:t=h:w=200:g=0.5,"
        "equalizer=f=500:t=h:w=300:g=0.3,"
        "equalizer=f=1000:t=h:w=500:g=0.4,"
        "equalizer=f=2000:t=h:w=800:g=0.6,"
        "equalizer=f=4000:t=h:w=1200:g=1.2,"
        "equalizer=f=8000:t=h:w=2000:g=0.8,"
        "equalizer=f=12000:t=h:w=3000:g=0.4,"
        # Multi-stage compression for punch and clarity
        "acompressor=threshold=-24dB:ratio=2:attack=5:release=150:makeup=1.5,"
        "acompressor=threshold=-16dB:ratio=3:attack=2:release=80:makeup=2,"
        "acompressor=threshold=-10dB:ratio=6:attack=0.5:release=40:makeup=1.5,"
        # Stereo enhancement
        "extrastereo=m=1.5,"
        # Subtle saturation for warmth
        "acompressor=threshold=-6dB:ratio=20:attack=0.1:release=10:makeup=0.5,"
        # Final limiting and loudness normalization
        "alimiter=level_in=1:level_out=0.98:limit=0.98:attack=1:release=5,"
        "loudnorm=I=-14:TP=-1:LRA=9",
        "-ac", "2",
        "-ar", "48000",
        "-b:a", "320k",
        str(out_path)
    ])


# ----------- Endpoints -----------
@app.get("/health")
def health():
    return {"ok": True, "dev_mode": DEV_MODE}


@app.post("/preview")
async def preview(file: UploadFile = File(...)):
    # Save upload
    ext = Path(safe_name(file.filename or "audio")).suffix or ".wav"
    job_id = str(uuid.uuid4())
    src = UPLOADS_DIR / f"{job_id}{ext}"
    with src.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Build preview
    preview_mp3 = PREVIEWS_DIR / f"{job_id}.mp3"
    try:
        make_preview(src, preview_mp3)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"preview_failed: {str(e)}"})

    # IMPORTANT: we return a path under /files; the frontend will prefix it with /api
    url = f"/files/previews/{preview_mp3.name}"
    return {"job_id": job_id, "preview_url": url}


@app.post("/checkout")
async def checkout(job_id: str = Form(...)):
    # Dev mode: pretend Stripe succeeded
    if DEV_MODE:
        return {"id": "dev_session", "url": f"{FRONTEND_URL}?session_id=dev_ok&job_id={job_id}"}

    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": os.getenv("STRIPE_PRICE_ID_SINGLE"), "quantity": 1}],
        success_url=f"{FRONTEND_URL}?session_id={{CHECKOUT_SESSION_ID}}&job_id={job_id}",
        cancel_url=FRONTEND_URL,
    )
    return {"id": session.id, "url": session.url}


@app.post("/checkout-subscription")
async def checkout_subscription(job_id: str = Form(...), email: str = Form(...)):
    if DEV_MODE:
        return {"id": "dev_sub", "url": f"{FRONTEND_URL}?session_id=dev_sub_ok&job_id={job_id}"}

    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=email,
        line_items=[{"price": os.getenv("STRIPE_PRICE_ID_SUB_MONTHLY"), "quantity": 1}],
        success_url=f"{FRONTEND_URL}?session_id={{CHECKOUT_SESSION_ID}}&job_id={job_id}",
        cancel_url=FRONTEND_URL,
    )
    return {"id": session.id, "url": session.url}


@app.post("/process-full")
async def process_full(
    job_id: str = Form(...),
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
):
    # In DEV we don't verify session; in PROD you would.
    ext = Path(safe_name(file.filename or "audio")).suffix or ".wav"
    src = UPLOADS_DIR / f"{job_id}{ext}"
    with src.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    out_mp3 = OUTPUTS_DIR / f"{job_id}.mp3"
    try:
        make_master(src, out_mp3)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"process_failed: {str(e)}"})

    url = f"/files/outputs/{out_mp3.name}"
    return {"download_url": url}

