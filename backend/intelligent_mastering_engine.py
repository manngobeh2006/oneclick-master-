#!/usr/bin/env python3
"""
Intelligent Mastering Engine
AI-powered mastering system that uses training data for smart mastering decisions
"""

import os
import json
import subprocess
import tempfile
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import logging
from dataclasses import dataclass

from advanced_audio_analyzer import AdvancedAudioAnalyzer
from training_database import TrainingDataManager

logger = logging.getLogger(__name__)

@dataclass
class MasteringParameters:
    """Optimized mastering parameters from AI analysis"""
    
    # EQ Parameters
    highpass_freq: float = 30.0
    lowpass_freq: float = 20000.0
    eq_bands: Dict[str, Dict[str, float]] = None
    
    # Dynamics
    multiband_compression: Dict[str, Dict[str, float]] = None
    bus_compression: Dict[str, float] = None
    
    # Stereo Processing
    stereo_width: float = 1.0
    bass_mono_freq: float = 80.0
    
    # Saturation/Enhancement
    saturation_amount: float = 0.05
    harmonic_enhancement: float = 0.02
    
    # Final Limiting
    limiter_ceiling: float = -0.8
    limiter_release: float = 35
    
    # Target Loudness
    target_lufs: float = -14.0
    preserve_dynamics: bool = False
    
    # Processing Intensity
    gentle_processing: bool = False
    
    def __post_init__(self):
        if self.eq_bands is None:
            self.eq_bands = {
                "sub_bass": {"freq": 45, "gain": 0.0, "q": 1.2},
                "bass": {"freq": 85, "gain": 0.0, "q": 1.3},
                "low_mid": {"freq": 200, "gain": 0.0, "q": 2.0},
                "mid": {"freq": 1200, "gain": 0.0, "q": 1.4},
                "high_mid": {"freq": 3200, "gain": 0.0, "q": 1.6},
                "presence": {"freq": 5500, "gain": 0.0, "q": 1.8},
                "air": {"freq": 12000, "gain": 0.0, "q": 2.0}
            }
        
        if self.multiband_compression is None:
            self.multiband_compression = {
                "low": {"threshold": -20, "ratio": 2.0, "attack": 10, "release": 100},
                "mid": {"threshold": -18, "ratio": 2.5, "attack": 5, "release": 50},
                "high": {"threshold": -15, "ratio": 3.0, "attack": 2, "release": 25}
            }
        
        if self.bus_compression is None:
            self.bus_compression = {"threshold": -8, "ratio": 2.0, "attack": 3, "release": 30}


class IntelligentMasteringEngine:
    """AI-powered mastering engine using training data"""
    
    def __init__(self):
        self.analyzer = AdvancedAudioAnalyzer()
        self.data_manager = TrainingDataManager()
        
        # Load genre templates from training data
        self.genre_templates = self._load_genre_templates()
        
        # Mastering profiles with AI-optimized parameters
        self.ai_profiles = self._initialize_ai_profiles()
        
        logger.info("🧠 Intelligent Mastering Engine initialized")
    
    def _load_genre_templates(self) -> Dict[str, Dict]:
        """Load genre-specific mastering templates from training database"""
        
        templates = {}
        
        try:
            # Get all trained genres from database
            import sqlite3
            db_path = self.data_manager.database.db_path
            
            with sqlite3.connect(db_path) as conn:
                genres = conn.execute("SELECT genre, COUNT(*) FROM training_tracks GROUP BY genre").fetchall()
                
                for genre, count in genres:
                    if count >= 5:  # Only use genres with sufficient data
                        # Create basic template from database statistics
                        stats = conn.execute("""
                            SELECT AVG(integrated_lufs), AVG(dynamic_range_db), 
                                   AVG(bass_emphasis), AVG(high_emphasis), AVG(stereo_width)
                            FROM training_tracks WHERE genre = ?
                        """, (genre,)).fetchone()
                        
                        if stats and stats[0] is not None:
                            templates[genre] = {
                                "genre": genre,
                                "target_parameters": {
                                    "lufs_target": stats[0],
                                    "dynamic_range_target": stats[1],
                                    "bass_emphasis": stats[2],
                                    "high_emphasis": stats[3],
                                    "stereo_width": stats[4]
                                },
                                "reference_count": count,
                                "processing_recommendations": {
                                    "compression": {"ratio": 2.5},
                                    "eq": {"bass_boost": max(0, stats[2] - 0.3)},
                                    "limiting": {"ceiling": -0.8}
                                }
                            }
                            logger.info(f"📊 Loaded {genre} template: {count} references")
        
        except Exception as e:
            logger.warning(f"Could not load genre templates: {e}")
        
        return templates
    
    def _initialize_ai_profiles(self) -> Dict[str, MasteringParameters]:
        """Initialize AI-optimized mastering profiles"""
        
        profiles = {}
        
        # Modern pop profile (data-driven)
        profiles["modern_pop"] = MasteringParameters(
            target_lufs=-13.5,
            eq_bands={
                "sub_bass": {"freq": 40, "gain": -1.0, "q": 1.5},
                "bass": {"freq": 80, "gain": 0.8, "q": 1.3},
                "low_mid": {"freq": 180, "gain": -0.5, "q": 2.2},
                "mid": {"freq": 1200, "gain": 1.0, "q": 1.4},
                "high_mid": {"freq": 3000, "gain": 1.5, "q": 1.6},
                "presence": {"freq": 5500, "gain": 1.2, "q": 1.8},
                "air": {"freq": 12000, "gain": 0.8, "q": 2.0}
            },
            multiband_compression={
                "low": {"threshold": -18, "ratio": 2.5, "attack": 8, "release": 80},
                "mid": {"threshold": -16, "ratio": 3.0, "attack": 3, "release": 40},
                "high": {"threshold": -14, "ratio": 3.5, "attack": 1, "release": 20}
            },
            stereo_width=1.15,
            saturation_amount=0.06,
            limiter_ceiling=-0.5,
            limiter_release=30
        )
        
        # Hip-hop/trap profile (bass-heavy, loud)
        profiles["bass_heavy_modern"] = MasteringParameters(
            target_lufs=-12.0,
            eq_bands={
                "sub_bass": {"freq": 35, "gain": 2.5, "q": 1.2},
                "bass": {"freq": 85, "gain": 2.0, "q": 1.3},
                "low_mid": {"freq": 200, "gain": -1.0, "q": 2.1},
                "mid": {"freq": 1000, "gain": 0.5, "q": 1.4},
                "high_mid": {"freq": 3500, "gain": 1.8, "q": 1.6},
                "presence": {"freq": 6000, "gain": 1.0, "q": 1.8},
                "air": {"freq": 10000, "gain": 0.5, "q": 2.0}
            },
            multiband_compression={
                "low": {"threshold": -15, "ratio": 3.0, "attack": 12, "release": 100},
                "mid": {"threshold": -14, "ratio": 2.8, "attack": 4, "release": 45},
                "high": {"threshold": -12, "ratio": 3.2, "attack": 1, "release": 25}
            },
            stereo_width=1.0,  # Keep bass mono-focused
            bass_mono_freq=120,
            saturation_amount=0.08,
            limiter_ceiling=-0.3,
            limiter_release=25
        )
        
        # R&B/smooth profile (vocal-focused)
        profiles["smooth_vocal_focus"] = MasteringParameters(
            target_lufs=-15.0,
            eq_bands={
                "sub_bass": {"freq": 40, "gain": -0.5, "q": 1.5},
                "bass": {"freq": 80, "gain": 1.0, "q": 1.2},
                "low_mid": {"freq": 180, "gain": -0.8, "q": 2.2},
                "mid": {"freq": 1000, "gain": 1.5, "q": 1.3},
                "high_mid": {"freq": 2800, "gain": 2.2, "q": 1.5},
                "presence": {"freq": 5000, "gain": 2.0, "q": 1.7},
                "air": {"freq": 10000, "gain": 1.2, "q": 2.0}
            },
            multiband_compression={
                "low": {"threshold": -20, "ratio": 2.0, "attack": 15, "release": 120},
                "mid": {"threshold": -18, "ratio": 2.2, "attack": 6, "release": 60},
                "high": {"threshold": -16, "ratio": 2.8, "attack": 2, "release": 35}
            },
            stereo_width=1.2,
            saturation_amount=0.04,
            limiter_ceiling=-0.8,
            limiter_release=45,
            preserve_dynamics=True
        )
        
        # Drill profile (aggressive, punchy)
        profiles["aggressive_urban"] = MasteringParameters(
            target_lufs=-11.5,
            eq_bands={
                "sub_bass": {"freq": 45, "gain": 1.8, "q": 1.2},
                "bass": {"freq": 90, "gain": 1.5, "q": 1.3},
                "low_mid": {"freq": 200, "gain": -0.5, "q": 2.0},
                "mid": {"freq": 1200, "gain": 0.8, "q": 1.4},
                "high_mid": {"freq": 3500, "gain": 2.5, "q": 1.5},
                "presence": {"freq": 6000, "gain": 2.0, "q": 1.7},
                "air": {"freq": 12000, "gain": 1.0, "q": 1.9}
            },
            multiband_compression={
                "low": {"threshold": -16, "ratio": 3.2, "attack": 8, "release": 70},
                "mid": {"threshold": -14, "ratio": 3.5, "attack": 2, "release": 35},
                "high": {"threshold": -12, "ratio": 4.0, "attack": 1, "release": 20}
            },
            stereo_width=1.05,
            saturation_amount=0.1,
            harmonic_enhancement=0.05,
            limiter_ceiling=-0.2,
            limiter_release=20
        )
        
        # Amapiano profile (log drums, spatial)
        profiles["log_drum_emphasis"] = MasteringParameters(
            target_lufs=-12.5,
            eq_bands={
                "sub_bass": {"freq": 45, "gain": 2.2, "q": 1.1},
                "bass": {"freq": 85, "gain": 1.8, "q": 1.3},
                "low_mid": {"freq": 200, "gain": -1.2, "q": 2.1},
                "mid": {"freq": 1200, "gain": 0.8, "q": 1.4},
                "high_mid": {"freq": 3200, "gain": 1.5, "q": 1.6},
                "presence": {"freq": 5500, "gain": 0.6, "q": 1.8},
                "air": {"freq": 12000, "gain": 1.1, "q": 1.9}
            },
            multiband_compression={
                "low": {"threshold": -18, "ratio": 2.8, "attack": 15, "release": 120},
                "mid": {"threshold": -16, "ratio": 2.2, "attack": 8, "release": 60},
                "high": {"threshold": -12, "ratio": 2.5, "attack": 3, "release": 35}
            },
            stereo_width=1.35,  # Wide for log drums
            bass_mono_freq=90,
            saturation_amount=0.08,
            limiter_ceiling=-0.8,
            limiter_release=45
        )
        
        # Ballad/slow song profile (dynamic preservation)
        profiles["dynamic_preservation"] = MasteringParameters(
            target_lufs=-16.0,
            eq_bands={
                "sub_bass": {"freq": 35, "gain": -1.5, "q": 1.8},
                "bass": {"freq": 80, "gain": 0.5, "q": 1.2},
                "low_mid": {"freq": 180, "gain": -0.8, "q": 2.2},
                "mid": {"freq": 1000, "gain": 1.2, "q": 1.3},
                "high_mid": {"freq": 2800, "gain": 2.1, "q": 1.5},
                "presence": {"freq": 5000, "gain": 1.8, "q": 1.7},
                "air": {"freq": 10000, "gain": 1.5, "q": 2.0}
            },
            multiband_compression={
                "low": {"threshold": -24, "ratio": 1.8, "attack": 25, "release": 200},
                "mid": {"threshold": -20, "ratio": 2.0, "attack": 12, "release": 100},
                "high": {"threshold": -18, "ratio": 2.2, "attack": 5, "release": 60}
            },
            bus_compression={"threshold": -12, "ratio": 1.4, "attack": 8, "release": 80},
            stereo_width=1.15,
            saturation_amount=0.03,
            limiter_ceiling=-1.5,
            limiter_release=80,
            preserve_dynamics=True,
            gentle_processing=True
        )
        
        logger.info(f"🎯 Initialized {len(profiles)} AI mastering profiles")
        return profiles
    
    def analyze_and_master(self, input_path: Path, output_path: Path, target_platform: str = "streaming") -> Dict[str, Any]:
        """Intelligent analysis and mastering using AI"""
        
        logger.info(f"🧠 Starting intelligent mastering: {input_path.name}")
        
        # Step 1: Comprehensive analysis
        analysis = self.analyzer.analyze_comprehensive(input_path)
        
        # Step 2: AI-powered parameter optimization
        optimal_params = self._optimize_mastering_parameters(analysis)
        
        # Step 3: Apply intelligent mastering
        result = self._apply_intelligent_mastering(input_path, output_path, optimal_params, analysis)
        
        return {
            "success": result["success"],
            "analysis": analysis,
            "optimal_parameters": optimal_params.__dict__,
            "processing_details": result,
            "ai_decisions": self._explain_ai_decisions(analysis, optimal_params)
        }
    
    def _optimize_mastering_parameters(self, analysis: Dict[str, Any]) -> MasteringParameters:
        """Use AI to optimize mastering parameters based on analysis"""
        
        genre = analysis.get("genre", "").lower()
        mastering_profile = analysis.get("mastering_profile", "balanced_modern")
        
        # Start with base profile
        if mastering_profile in self.ai_profiles:
            params = self._copy_params(self.ai_profiles[mastering_profile])
        else:
            params = self._copy_params(self.ai_profiles["modern_pop"])
        
        # Apply genre-specific optimizations from training data
        if genre in self.genre_templates:
            params = self._apply_genre_template(params, self.genre_templates[genre])
        
        # Apply track-specific optimizations
        params = self._apply_track_specific_optimizations(params, analysis)
        
        logger.info(f"🎯 Optimized parameters for {genre} using profile: {mastering_profile}")
        return params
    
    def _apply_genre_template(self, params: MasteringParameters, template: Dict[str, Any]) -> MasteringParameters:
        """Apply genre template learned from training data"""
        
        target_params = template.get("target_parameters", {})
        processing_recs = template.get("processing_recommendations", {})
        
        # Update LUFS target
        if "lufs_target" in target_params:
            params.target_lufs = target_params["lufs_target"]
        
        # Update dynamic range handling
        if "dynamic_range_target" in target_params:
            dr_target = target_params["dynamic_range_target"]
            if dr_target > 10:
                params.preserve_dynamics = True
                params.gentle_processing = True
        
        # Update stereo width
        if "stereo_width" in target_params:
            params.stereo_width = max(0.8, min(1.5, target_params["stereo_width"]))
        
        # Apply EQ recommendations
        if "eq" in processing_recs:
            eq_recs = processing_recs["eq"]
            
            # Bass adjustments
            if "bass_boost" in eq_recs and eq_recs["bass_boost"] > 0:
                params.eq_bands["bass"]["gain"] += eq_recs["bass_boost"]
                params.eq_bands["sub_bass"]["gain"] += eq_recs["bass_boost"] * 0.7
            
            # High frequency adjustments
            if "high_boost" in eq_recs and eq_recs["high_boost"] > 0:
                params.eq_bands["presence"]["gain"] += eq_recs["high_boost"]
                params.eq_bands["air"]["gain"] += eq_recs["high_boost"] * 0.8
            
            # Low-mid cleanup
            if "low_mid_cut" in eq_recs and eq_recs["low_mid_cut"] > 0:
                params.eq_bands["low_mid"]["gain"] -= eq_recs["low_mid_cut"]
        
        # Apply compression recommendations
        if "compression" in processing_recs:
            comp_recs = processing_recs["compression"]
            
            if "ratio" in comp_recs:
                for band in params.multiband_compression.values():
                    band["ratio"] = comp_recs["ratio"]
        
        # Apply limiting recommendations
        if "limiting" in processing_recs:
            limit_recs = processing_recs["limiting"]
            
            if "ceiling" in limit_recs:
                params.limiter_ceiling = limit_recs["ceiling"]
            
            if "release" in limit_recs:
                params.limiter_release = limit_recs["release"]
        
        return params
    
    def _apply_track_specific_optimizations(self, params: MasteringParameters, analysis: Dict[str, Any]) -> MasteringParameters:
        """Apply track-specific optimizations based on analysis"""
        
        loudness = analysis.get("loudness_analysis", {})
        dynamics = analysis.get("dynamic_analysis", {})
        frequency = analysis.get("frequency_analysis", {})
        stereo = analysis.get("stereo_analysis", {})
        
        current_lufs = loudness.get("integrated_lufs", -18.0)
        dynamic_range = dynamics.get("dynamic_range_db", 10.0)
        bass_emphasis = frequency.get("bass_emphasis", 0.3)
        high_emphasis = frequency.get("high_emphasis", 0.3)
        stereo_width = stereo.get("stereo_width", 0.7)
        
        # Adjust based on current loudness
        if current_lufs > -12:  # Already very loud
            params.gentle_processing = True
            params.limiter_ceiling = max(-1.0, params.limiter_ceiling)
            params.target_lufs = max(-13.0, current_lufs - 1.0)
        elif current_lufs < -20:  # Very quiet, needs more processing
            params.target_lufs = min(-13.0, params.target_lufs)
        
        # Adjust based on dynamic range
        if dynamic_range > 15:  # Very dynamic, preserve it
            params.preserve_dynamics = True
            params.gentle_processing = True
            for band in params.multiband_compression.values():
                band["ratio"] *= 0.8  # Gentler ratios
                band["threshold"] -= 2  # Higher thresholds
        elif dynamic_range < 4:  # Already heavily compressed
            params.gentle_processing = True
            params.target_lufs = max(-15.0, params.target_lufs)
        
        # Adjust EQ based on frequency analysis
        if bass_emphasis > 0.45:  # Bass-heavy track
            params.eq_bands["low_mid"]["gain"] -= 1.0  # Clean up muddiness
            params.bass_mono_freq = min(120, params.bass_mono_freq + 20)
        elif bass_emphasis < 0.25:  # Lacks bass
            params.eq_bands["bass"]["gain"] += 1.0
            params.eq_bands["sub_bass"]["gain"] += 0.5
        
        if high_emphasis > 0.4:  # Bright track
            params.eq_bands["presence"]["gain"] = max(0.0, params.eq_bands["presence"]["gain"] - 0.5)
        elif high_emphasis < 0.2:  # Dull track
            params.eq_bands["presence"]["gain"] += 1.0
            params.eq_bands["air"]["gain"] += 0.8
        
        # Adjust stereo processing
        if stereo_width > 0.8:  # Already very wide
            params.stereo_width *= 0.9
        elif stereo_width < 0.4:  # Too narrow
            params.stereo_width = min(1.3, params.stereo_width + 0.2)
        
        return params
    
    def _apply_intelligent_mastering(self, input_path: Path, output_path: Path, 
                                   params: MasteringParameters, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intelligent mastering with optimized parameters"""
        
        try:
            # Build advanced filter chain
            filter_chain = self._build_intelligent_filter_chain(params)
            
            # Apply mastering
            master_cmd = [
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-af", filter_chain,
                "-ar", "44100",
                "-ac", "2",
                "-b:a", "320k",
                "-f", "mp3",
                str(output_path)
            ]
            
            result = subprocess.run(master_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise RuntimeError(f"Mastering failed: {result.stderr}")
            
            return {
                "success": True,
                "filter_chain": filter_chain,
                "processing_approach": "intelligent_ai_driven",
                "optimization_applied": True
            }
            
        except Exception as e:
            logger.error(f"Intelligent mastering failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _build_intelligent_filter_chain(self, params: MasteringParameters) -> str:
        """Build advanced FFmpeg filter chain from AI-optimized parameters"""
        
        filters = []
        
        # 1. Input conditioning
        filters.append(f"highpass=f={params.highpass_freq}")
        filters.append(f"lowpass=f={params.lowpass_freq}")
        
        # 2. Intelligent saturation
        if params.saturation_amount > 0:
            filters.append(f"aexciter=amount={params.saturation_amount}:harmonics=8.5:scope=0")
        
        # 3. AI-optimized EQ
        for band_name, band_params in params.eq_bands.items():
            if abs(band_params["gain"]) > 0.1:  # Only apply significant adjustments
                filters.append(
                    f"equalizer=f={band_params['freq']}:width_type=h:width={1/band_params['q']}:g={band_params['gain']}"
                )
        
        # 4. Intelligent multiband compression
        mb = params.multiband_compression
        
        # Create multiband processing
        multiband_filter = (
            "asplit=3[low][mid][high];"
            f"[low]lowpass=f=250,acompressor="
            f"threshold={mb['low']['threshold']}dB:"
            f"ratio={mb['low']['ratio']}:"
            f"attack={mb['low']['attack']}:"
            f"release={mb['low']['release']}:"
            f"makeup=2[low_out];"
            
            f"[mid]bandpass=f=250:f=2500,acompressor="
            f"threshold={mb['mid']['threshold']}dB:"
            f"ratio={mb['mid']['ratio']}:"
            f"attack={mb['mid']['attack']}:"
            f"release={mb['mid']['release']}:"
            f"makeup=2[mid_out];"
            
            f"[high]highpass=f=2500,acompressor="
            f"threshold={mb['high']['threshold']}dB:"
            f"ratio={mb['high']['ratio']}:"
            f"attack={mb['high']['attack']}:"
            f"release={mb['high']['release']}:"
            f"makeup=1[high_out];"
            
            "[low_out][mid_out][high_out]amix=inputs=3[mb_out]"
        )
        
        filters.append(multiband_filter)
        
        # 5. Stereo enhancement
        if params.stereo_width != 1.0:
            filters.append(f"extrastereo=m={params.stereo_width-1.0}:c=0")
        
        # 6. Bus compression
        bus_comp = params.bus_compression
        filters.append(
            f"acompressor="
            f"threshold={bus_comp['threshold']}dB:"
            f"ratio={bus_comp['ratio']}:"
            f"attack={bus_comp['attack']}:"
            f"release={bus_comp['release']}:"
            f"makeup=1"
        )
        
        # 7. Harmonic enhancement
        if params.harmonic_enhancement > 0:
            filters.append(f"aexciter=amount={params.harmonic_enhancement}:harmonics=12:scope=1")
        
        # 8. Intelligent loudness normalization
        filters.append(f"loudnorm=I={params.target_lufs}:TP=-1.0:LRA=7:measured_I=-18:measured_TP=-5:measured_LRA=12")
        
        # 9. Final intelligent limiting
        filters.append(
            f"alimiter="
            f"level_in=1:"
            f"level_out=0.95:"
            f"limit={params.limiter_ceiling}:"
            f"attack=1:"
            f"release={params.limiter_release}"
        )
        
        return ",".join(filters)
    
    def _explain_ai_decisions(self, analysis: Dict[str, Any], params: MasteringParameters) -> Dict[str, Any]:
        """Explain the AI's mastering decisions"""
        
        decisions = {
            "target_lufs": {
                "value": params.target_lufs,
                "reason": f"Optimized for {analysis.get('genre', 'unknown')} genre based on training data"
            },
            "preserve_dynamics": {
                "value": params.preserve_dynamics,
                "reason": "Based on dynamic range analysis and genre characteristics"
            },
            "stereo_processing": {
                "value": params.stereo_width,
                "reason": f"Optimized for stereo width of {analysis.get('stereo_analysis', {}).get('stereo_width', 'unknown')}"
            },
            "eq_adjustments": [],
            "compression_style": {
                "multiband_ratios": [band["ratio"] for band in params.multiband_compression.values()],
                "reason": "AI-optimized ratios based on frequency content and dynamics"
            }
        }
        
        # Explain EQ decisions
        for band_name, band_params in params.eq_bands.items():
            if abs(band_params["gain"]) > 0.5:
                decisions["eq_adjustments"].append({
                    "band": band_name,
                    "frequency": band_params["freq"],
                    "gain": band_params["gain"],
                    "reason": f"AI optimization based on spectral analysis"
                })
        
        return decisions
    
    def _copy_params(self, source: MasteringParameters) -> MasteringParameters:
        """Create a copy of mastering parameters"""
        import copy
        return copy.deepcopy(source)
    
    def create_enhanced_preview(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """Create enhanced preview using AI optimization"""
        
        # Analyze the track
        analysis = self.analyzer.analyze_comprehensive(input_path)
        
        # Get optimized parameters but make them gentler for preview
        params = self._optimize_mastering_parameters(analysis)
        params.gentle_processing = True
        params.target_lufs = -16.0  # Quieter for preview
        params.limiter_ceiling = -1.0
        
        # Reduce all processing amounts
        for band in params.eq_bands.values():
            band["gain"] *= 0.6
        
        params.saturation_amount *= 0.5
        params.stereo_width = 1.0 + (params.stereo_width - 1.0) * 0.5
        
        try:
            # Build preview filter chain
            preview_chain = self._build_intelligent_filter_chain(params)
            
            # Add watermark
            watermark_cmd = [
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-f", "lavfi", "-i", "sine=frequency=880:duration=0.3",
                "-filter_complex",
                f"[0:a]{preview_chain}[clean];"
                "[1:a]volume=0.08[beep];"
                "[clean][beep]amix=inputs=2:duration=first:weights=1 0.08[out]",
                "-map", "[out]",
                "-ac", "2", "-ar", "44100", "-b:a", "128k",
                "-t", "30",  # 30-second preview
                str(output_path)
            ]
            
            result = subprocess.run(watermark_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Preview creation failed: {result.stderr}")
            
            return {
                "success": True,
                "preview_type": "ai_optimized",
                "analysis_used": analysis.get("mastering_profile", "balanced"),
                "processing_applied": "intelligent_gentle"
            }
            
        except Exception as e:
            logger.error(f"AI preview creation failed: {e}")
            return {"success": False, "error": str(e)}


# Integration wrapper for existing processing.py
def create_intelligent_master(input_path: Path, output_path: Path, target_platform: str = "streaming") -> Dict[str, Any]:
    """High-level function for intelligent mastering"""
    
    engine = IntelligentMasteringEngine()
    return engine.analyze_and_master(input_path, output_path, target_platform)


if __name__ == "__main__":
    # Test the intelligent mastering engine
    engine = IntelligentMasteringEngine()
    
    # Example usage
    test_file = Path("training_workspace/Training_songs/trap").glob("*.mp3")
    test_file = next(test_file, None)
    
    if test_file:
        output_file = Path("test_intelligent_master.mp3")
        result = engine.analyze_and_master(test_file, output_file)
        
        print("🧠 Intelligent Mastering Result:")
        print(json.dumps(result, indent=2))
    else:
        print("No test file found")