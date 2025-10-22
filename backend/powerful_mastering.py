#!/usr/bin/env python3
"""
Powerful Mastering DSP - Simple but effective mastering that WORKS
Based on proven loudness standards and aggressive processing
"""

import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def master_audio_powerful(input_path: str, output_path: str, target_lufs: float = -11.0) -> bool:
    """
    Create LOUD, professional master with clear difference from input.
    Uses proven DSP chain for streaming platforms.
    
    Args:
        input_path: Input audio file
        output_path: Output audio file
        target_lufs: Target loudness (-9 to -14 LUFS, default -11 for modern loud)
    
    Returns:
        True if successful
    """
    
    try:
        logger.info(f"🔥 Starting POWERFUL mastering: target {target_lufs} LUFS")
        
        # PROVEN MASTERING CHAIN - Competition loud with quality
        filter_chain = ",".join([
            # 1. Clean up subsonic rumble
            "highpass=f=25",
            
            # 2. Gentle saturation for warmth and glue (simplified)
            "aexciter=amount=0.15",
            
            # 3. POWERFUL EQ - Shape the sound
            "equalizer=f=60:width_type=h:width=0.8:g=2.0",      # Sub bass punch
            "equalizer=f=90:width_type=h:width=0.7:g=1.5",       # Bass power
            "equalizer=f=250:width_type=h:width=0.5:g=-1.5",     # Clean muddy mids
            "equalizer=f=1200:width_type=h:width=0.6:g=0.8",     # Vocal presence
            "equalizer=f=3500:width_type=h:width=0.6:g=2.0",     # High-mid clarity
            "equalizer=f=6000:width_type=h:width=0.7:g=1.5",     # Presence boost
            "equalizer=f=10000:width_type=h:width=0.8:g=1.2",    # Air/sparkle
            
            # 4. POWERFUL COMPRESSION - Single-stage aggressive
            "acompressor=threshold=-20dB:ratio=6.0:attack=5:release=50:makeup=8",
            
            # 5. LOUDNESS NORMALIZATION - This makes it LOUD
            f"loudnorm=I={target_lufs}:TP=-1.0:LRA=7",
            
            # 6. Final brick-wall limiter - Maximum loudness  
            "alimiter=limit=0.95:attack=1:release=25"
        ])
        
        # Run FFmpeg with powerful processing
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-af", filter_chain,
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "320k",
            "-f", "mp3",
            str(output_path)
        ]
        
        logger.info(f"🎛️  Applying powerful mastering chain...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            logger.error(f"Mastering failed: {result.stderr}")
            return False
        
        logger.info(f"✅ Powerful master created at {target_lufs} LUFS")
        return True
        
    except Exception as e:
        logger.error(f"❌ Powerful mastering error: {e}")
        return False


def master_audio_genre_optimized(input_path: str, output_path: str, genre: str = "general") -> bool:
    """
    Genre-optimized mastering with proven loudness targets.
    
    Genre loudness targets (based on streaming standards):
    - Trap/Hip-hop: -10.5 LUFS (very loud, bass-heavy)
    - Pop: -11.0 LUFS (loud and clear)
    - R&B: -12.0 LUFS (smooth but powerful)
    - Drill/Amapiano: -10.0 LUFS (competition loud)
    - Dancehall/Afro: -10.5 LUFS (energetic and loud)
    - Ballad/Slow: -13.0 LUFS (dynamic but present)
    """
    
    # Genre-specific LUFS targets
    genre_targets = {
        "trap": -10.5,
        "hiphop": -11.0,
        "drill": -10.0,
        "amapiano": -10.0,
        "pop": -11.0,
        "dancehall": -10.5,
        "afro": -10.5,
        "rnb": -12.0,
        "slow song": -13.0,
        "ballad": -13.0,
        "general": -11.0
    }
    
    target_lufs = genre_targets.get(genre.lower(), -11.0)
    logger.info(f"🎯 Genre: {genre} → Target: {target_lufs} LUFS")
    
    return master_audio_powerful(input_path, output_path, target_lufs)


def create_preview_with_watermark(input_path: str, output_path: str) -> bool:
    """
    Create watermarked preview with light mastering.
    """
    try:
        # Lighter mastering for preview
        preview_chain = ",".join([
            "highpass=f=30",
            "equalizer=f=80:width_type=h:width=0.7:g=1.0",
            "equalizer=f=3000:width_type=h:width=0.6:g=1.2",
            "acompressor=threshold=-18dB:ratio=2.5:attack=5:release=50:makeup=2",
            "loudnorm=I=-14:TP=-1:LRA=9",
            "alimiter=limit=-1.0"
        ])
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-f", "lavfi", "-i", "sine=frequency=880:duration=0.3",
            "-filter_complex",
            f"[0:a]{preview_chain}[clean];"
            "[1:a]volume=0.08[beep];"
            "[clean][beep]amix=inputs=2:duration=first:dropout_transition=0[out]",
            "-map", "[out]",
            "-ac", "2", "-ar", "44100", "-b:a", "128k",
            "-t", "30",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Preview creation error: {e}")
        return False
