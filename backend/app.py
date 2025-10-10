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
    Full-length preview at 96 kbps with a very subtle watermark tone.
    """
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-f", "lavfi", "-i", "sine=frequency=1000:sample_rate=48000",
        "-filter_complex",
        "[0:a]loudnorm=I=-14:TP=-2.0:LRA=11,highpass=f=25,lowpass=f=18000,acompressor=threshold=-12dB:ratio=2:attack=20:release=200[aud];"
        "[1:a]volume=-20dB[beep];"
        "[aud][beep]amix=inputs=2:normalize=0[out]",
        "-map", "[out]",
        "-ac", "2",
        "-b:a", "96k",
        "-shortest",
        str(out_path)
    ])


def make_master(input_path: Path, out_path: Path) -> None:
    """
    Full-quality mastered file at 320 kbps (simple chain you can tweak later).
    """
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-filter:a",
        "loudnorm=I=-13:TP=-1.5:LRA=11,highpass=f=25,lowpass=f=19000,acompressor=threshold=-14dB:ratio=1.8:attack=15:release=150",
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

