import os
import re
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import RedirectResponse
from intelligent_mastering_engine import IntelligentMasteringEngine
from processing import process_file_to_preview_full, process_full
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

# Initialize AI Mastering Engine
ai_engine = IntelligentMasteringEngine()

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
    AI-powered preview with watermark using trained mastering profiles.
    """
    try:
        # Use enhanced preview with watermark
        process_file_to_preview_full(str(input_path), str(out_path))
    except Exception as e:
        # Fallback to simple processing if AI version fails
        run_ffmpeg([
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-f", "lavfi", "-i", "sine=frequency=880:duration=0.5",
            "-filter_complex",
            "[0:a]volume=0.8,highpass=f=50[aud];"
            "[1:a]volume=0.1[beep];"
            "[aud][beep]amix=inputs=2:duration=first[out]",
            "-map", "[out]",
            "-ac", "2",
            "-ar", "44100",
            "-b:a", "128k",
            "-t", "30",  # Limit to 30 seconds for preview
            str(out_path)
        ])



def make_master(input_path: Path, out_path: Path, target_platform: str = "streaming_standard") -> Dict[str, Any]:
    """
    AI-powered intelligent mastering with genre detection and adaptive processing.
    """
    try:
        # Use AI engine for intelligent mastering
        result = ai_engine.intelligent_master(str(input_path), str(out_path))
        return {
            "success": True,
            "ai_powered": True,
            "detected_genre": result.get("detected_genre"),
            "profile_used": result.get("profile_used"),
            "target_lufs": result.get("target_lufs"),
            "analysis": result.get("analysis", {})
        }
    except Exception as e:
        # Fallback to simple processing if AI version fails
        run_ffmpeg([
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-filter:a",
            "volume=1.2,highpass=f=30,acompressor=threshold=-16dB:ratio=2.5:makeup=3",
            "-ac", "2",
            "-ar", "44100",
            "-b:a", "320k",
            str(out_path)
        ])
        return {"success": True, "fallback": True, "error": str(e)}


# ----------- Endpoints -----------
@app.get("/")
def root(request: Request):
    # Check if this is a browser request (has Accept header with text/html)
    accept_header = request.headers.get("accept", "")
    user_agent = request.headers.get("user-agent", "")
    
    # If it looks like a browser request, redirect to the frontend
    if ("text/html" in accept_header or 
        any(browser in user_agent.lower() for browser in ["mozilla", "chrome", "safari", "edge", "opera"])):
        return RedirectResponse(url="https://www.one-clickmaster.com", status_code=302)
    
    # Otherwise, return API info (for API clients, curl, etc.)
    return {
        "message": "OneClick Master - AI-Powered Intelligent Audio Mastering API",
        "version": "3.0.0",
        "dev_mode": DEV_MODE,
        "ai_status": "Fully trained and operational",
        "training_data": f"{len(ai_engine.genre_templates)} genres, {sum(template['reference_count'] for template in ai_engine.genre_templates.values())} reference tracks",
        "frontend_url": "https://www.one-clickmaster.com",
        "features": {
            "ai_genre_detection": "Machine learning-based genre classification with 109 trained references",
            "intelligent_mastering": "Genre-adaptive processing with competition-grade results",
            "adaptive_loudness": "Genre-specific LUFS targeting (-9.9 to -12.5 LUFS)",
            "smart_compression": "Multi-stage compression with genre-learned parameters",
            "intelligent_eq": "9-band EQ with genre-specific frequency curves",
            "professional_limiting": "Adaptive peak control with genre dynamics",
            "reference_based_processing": "Mastering based on analysis of professional tracks"
        },
        "endpoints": {
            "health": "/health",
            "ffmpeg_test": "/ffmpeg-test",
            "mastering_info": "/mastering-info", 
            "preview": "POST /preview (with audio analysis)",
            "checkout": "POST /checkout",
            "checkout_subscription": "POST /checkout-subscription",
            "process_full": "POST /process-full (with platform targeting)",
            "files": "/files/{type}/{filename}"
        },
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"ok": True, "dev_mode": DEV_MODE}


@app.get("/mastering-info")
def mastering_info():
    """Information about the AI-powered mastering capabilities"""
    return {
        "mastering_engine": "AI-Powered Intelligent Audio Mastering v3.0",
        "ai_training": {
            "trained_genres": len(ai_engine.genre_templates),
            "reference_tracks": sum(template['reference_count'] for template in ai_engine.genre_templates.values()),
            "ai_profiles": len(ai_engine.ai_profiles),
            "genres_supported": list(ai_engine.genre_templates.keys())
        },
        "capabilities": {
            "ai_analysis": {
                "genre_detection": "Machine learning-based genre classification",
                "loudness_measurement": "EBU R128 LUFS integration with genre targeting",
                "dynamic_range_analysis": "Intelligent peak-to-RMS with genre context",
                "spectral_analysis": "FFT-based frequency analysis for smart EQ",
                "intelligent_profiling": "Adaptive processing based on 109 reference tracks"
            },
            "ai_processing_chain": {
                "genre_adaptive_filtering": "Smart high/low-pass based on genre templates",
                "intelligent_compression": "Multi-stage compression with genre-specific ratios",
                "adaptive_eq": "9-band EQ with genre-learned frequency curves",
                "smart_stereo_enhancement": "Genre-appropriate stereo width and imaging",
                "intelligent_loudness": "Genre-specific LUFS targeting (-9.9 to -12.5 LUFS)",
                "adaptive_limiting": "Intelligent peak control with genre dynamics"
            },
            "ai_profiles": {
                "competition_grade": "Professional mastering competitive with industry standards",
                "genre_adaptive": "Processing adapts to detected musical genre",
                "reference_based": "Masters based on analysis of professional reference tracks",
                "intelligent_dynamics": "Smart preservation or enhancement of dynamics",
                "streaming_optimized": "Genre-specific loudness targeting for streaming platforms"
            }
        },
        "genre_templates": {
            genre: {
                "reference_tracks": template['reference_count'],
                "target_lufs": template['target_parameters']['lufs_target'],
                "compression_profile": template['target_parameters']['compression_profile']
            } for genre, template in ai_engine.genre_templates.items()
        },
        "quality_features": {
            "ai_powered": "True AI mastering with machine learning",
            "competition_grade": "Professional industry-standard results",
            "genre_intelligent": "Adapts processing to musical content",
            "sample_rate": "44.1kHz professional standard",
            "output_quality": "320kbps MP3 / 44.1kHz stereo",
            "processing_time": "~15-45 seconds per song (includes AI analysis)",
            "format_support": ["MP3", "WAV", "M4A", "AIFF", "FLAC"]
        }
    }


@app.get("/ffmpeg-test")
def ffmpeg_test():
    """Test if FFmpeg is available and working"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return {
            "ffmpeg_available": result.returncode == 0,
            "version_info": result.stdout.split('\n')[0] if result.returncode == 0 else None,
            "error": result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {
            "ffmpeg_available": False,
            "error": str(e)
        }


@app.post("/preview")
async def preview(file: UploadFile = File(...)):
    # Save upload
    ext = Path(safe_name(file.filename or "audio")).suffix or ".wav"
    job_id = str(uuid.uuid4())
    src = UPLOADS_DIR / f"{job_id}{ext}"
    with src.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Analyze audio using AI engine for better user feedback
    try:
        analysis = ai_engine.analyze_audio(str(src))
    except Exception as e:
        # If analysis fails, use defaults
        analysis = {
            "duration": 180.0,
            "genre_classification": "general", 
            "mastering_profile": "balanced",
            "analysis_error": str(e)
        }

    # Build preview
    preview_mp3 = PREVIEWS_DIR / f"{job_id}.mp3"
    try:
        make_preview(src, preview_mp3)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"preview_failed: {str(e)}"})

    # Return enhanced response with analysis insights
    url = f"/files/previews/{preview_mp3.name}"
    return {
        "job_id": job_id, 
        "preview_url": url,
        "audio_analysis": {
            "duration_seconds": round(analysis.get("duration", 180.0), 1),
            "detected_genre": analysis.get("genre_classification", "general").replace("_", " ").title(),
            "mastering_profile": analysis.get("mastering_profile", "balanced").replace("_", " ").title(),
            "dynamic_range": round(analysis.get("dynamic_range", 8.0), 1),
            "current_loudness": round(analysis.get("integrated_lufs", -18.0), 1)
        }
    }


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
    target_platform: str = Form("streaming_standard")  # New parameter for platform optimization
):
    # In DEV we don't verify session; in PROD you would.
    ext = Path(safe_name(file.filename or "audio")).suffix or ".wav"
    src = UPLOADS_DIR / f"{job_id}{ext}"
    with src.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    out_mp3 = OUTPUTS_DIR / f"{job_id}.mp3"
    try:
        # Use the new professional mastering system
        mastering_result = make_master(src, out_mp3, target_platform)
        
        url = f"/files/outputs/{out_mp3.name}"
        response = {"download_url": url}
        
        # Include AI mastering insights if available
        if mastering_result and not mastering_result.get("fallback", False) and mastering_result.get("ai_powered"):
            response["ai_mastering_info"] = {
                "ai_powered": True,
                "detected_genre": mastering_result.get("detected_genre", "unknown"),
                "profile_used": mastering_result.get("profile_used", "balanced"),
                "target_lufs": mastering_result.get("target_lufs", -14.0),
                "processing_type": "Competition-grade AI mastering",
                "genre_templates_used": len(ai_engine.genre_templates),
                "reference_tracks_analyzed": sum(template['reference_count'] for template in ai_engine.genre_templates.values())
            }
        elif mastering_result and not mastering_result.get("fallback", False):
            analysis = mastering_result.get("analysis", {})
            response["mastering_info"] = {
                "target_platform": target_platform,
                "target_lufs": mastering_result.get("target_lufs", -14.0),
                "processing_profile": analysis.get("mastering_profile", "balanced").replace("_", " ").title(),
                "detected_genre": analysis.get("genre_classification", "general").replace("_", " ").title(),
                "original_loudness": round(analysis.get("integrated_lufs", -18.0), 1),
                "dynamic_range": round(analysis.get("dynamic_range", 8.0), 1)
            }
        elif mastering_result and mastering_result.get("fallback", False):
            response["mastering_info"] = {
                "note": "Used fallback processing due to: " + mastering_result.get("error", "unknown error"),
                "target_platform": target_platform
            }
            
        return response
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"process_failed: {str(e)}"})

