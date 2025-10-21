#!/usr/bin/env python3
"""
Training Database System
Stores and manages comprehensive audio analysis data for AI training
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TrainingDatabase:
    """SQLite database for storing comprehensive training analysis"""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent / "training_data.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- File info
                    duration REAL,
                    sample_rate INTEGER,
                    channels INTEGER,
                    file_size INTEGER,
                    codec TEXT,
                    
                    -- Loudness analysis
                    integrated_lufs REAL,
                    loudness_range_lu REAL,
                    true_peak_dbfs REAL,
                    momentary_max_lufs REAL,
                    short_term_max_lufs REAL,
                    crest_factor REAL,
                    loudness_category TEXT,
                    
                    -- Dynamic analysis
                    dynamic_range_db REAL,
                    peak_to_rms_ratio REAL,
                    compression_ratio REAL,
                    dynamic_character TEXT,
                    transient_presence REAL,
                    micro_dynamics REAL,
                    
                    -- Frequency analysis
                    sub_bass_energy REAL,
                    bass_energy REAL,
                    low_mid_energy REAL,
                    mid_energy REAL,
                    high_mid_energy REAL,
                    presence_energy REAL,
                    air_energy REAL,
                    spectral_centroid REAL,
                    spectral_tilt REAL,
                    bass_emphasis REAL,
                    high_emphasis REAL,
                    midrange_character TEXT,
                    
                    -- Stereo analysis
                    stereo_correlation REAL,
                    stereo_width REAL,
                    mono_compatibility REAL,
                    side_content REAL,
                    phantom_center REAL,
                    spatial_character TEXT,
                    
                    -- Transient analysis
                    transient_ratio REAL,
                    transient_character TEXT,
                    attack_speed REAL,
                    percussive_content REAL,
                    drum_presence REAL,
                    
                    -- Harmonic analysis
                    harmonic_richness REAL,
                    thd_estimate REAL,
                    even_harmonics REAL,
                    odd_harmonics REAL,
                    saturation_character TEXT,
                    analog_character REAL,
                    
                    -- Phase analysis
                    phase_coherence REAL,
                    phase_issues REAL,
                    mono_compatibility_score REAL,
                    phase_character TEXT,
                    
                    -- Temporal analysis
                    estimated_tempo INTEGER,
                    rhythm_strength REAL,
                    structural_complexity REAL,
                    time_signature_estimate TEXT,
                    rhythmic_character TEXT,
                    
                    -- Mastering characteristics
                    mastering_loudness REAL,
                    processing_intensity TEXT,
                    limiting_character TEXT,
                    eq_character TEXT,
                    compression_style TEXT,
                    mastering_era TEXT,
                    streaming_optimized BOOLEAN,
                    mastering_quality TEXT,
                    
                    -- Derived profiles
                    mastering_profile TEXT,
                    
                    -- Full analysis JSON (for complex nested data)
                    full_analysis_json TEXT,
                    analysis_time REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS genre_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    genre TEXT UNIQUE NOT NULL,
                    track_count INTEGER DEFAULT 0,
                    avg_lufs REAL,
                    avg_dynamic_range REAL,
                    avg_bass_emphasis REAL,
                    avg_high_emphasis REAL,
                    avg_stereo_width REAL,
                    common_mastering_profile TEXT,
                    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_start TIMESTAMP,
                    session_end TIMESTAMP,
                    total_tracks_processed INTEGER,
                    genres_processed TEXT,
                    session_notes TEXT
                )
            """)
            
            # Create indexes separately to avoid multi-statement issue
            conn.execute("CREATE INDEX IF NOT EXISTS idx_genre ON training_tracks(genre)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mastering_profile ON training_tracks(mastering_profile)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lufs ON training_tracks(integrated_lufs)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dynamic_range ON training_tracks(dynamic_range_db)")
            
            conn.commit()
            logger.info(f"✅ Training database initialized: {self.db_path}")
    
    def store_track_analysis(self, analysis: Dict[str, Any]) -> int:
        """Store comprehensive track analysis in database"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Extract nested data for flat storage
            file_info = analysis.get("file_info", {})
            loudness = analysis.get("loudness_analysis", {})
            dynamics = analysis.get("dynamic_analysis", {})
            frequency = analysis.get("frequency_analysis", {})
            stereo = analysis.get("stereo_analysis", {})
            transients = analysis.get("transient_analysis", {})
            harmonics = analysis.get("harmonic_analysis", {})
            phase = analysis.get("phase_analysis", {})
            temporal = analysis.get("temporal_analysis", {})
            mastering = analysis.get("mastering_characteristics", {})
            
            # Extract frequency bands
            freq_bands = frequency.get("frequency_bands", {})
            
            cursor = conn.execute("""
                INSERT OR REPLACE INTO training_tracks (
                    file_path, file_name, genre,
                    duration, sample_rate, channels, file_size, codec,
                    integrated_lufs, loudness_range_lu, true_peak_dbfs, 
                    momentary_max_lufs, short_term_max_lufs, crest_factor, loudness_category,
                    dynamic_range_db, peak_to_rms_ratio, compression_ratio, 
                    dynamic_character, transient_presence, micro_dynamics,
                    sub_bass_energy, bass_energy, low_mid_energy, mid_energy,
                    high_mid_energy, presence_energy, air_energy,
                    spectral_centroid, spectral_tilt, bass_emphasis, 
                    high_emphasis, midrange_character,
                    stereo_correlation, stereo_width, mono_compatibility,
                    side_content, phantom_center, spatial_character,
                    transient_ratio, transient_character, attack_speed,
                    percussive_content, drum_presence,
                    harmonic_richness, thd_estimate, even_harmonics,
                    odd_harmonics, saturation_character, analog_character,
                    phase_coherence, phase_issues, mono_compatibility_score, phase_character,
                    estimated_tempo, rhythm_strength, structural_complexity,
                    time_signature_estimate, rhythmic_character,
                    mastering_loudness, processing_intensity, limiting_character,
                    eq_character, compression_style, mastering_era,
                    streaming_optimized, mastering_quality,
                    mastering_profile, full_analysis_json, analysis_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.get("file_path", ""),
                Path(analysis.get("file_path", "")).name,
                analysis.get("genre", ""),
                
                file_info.get("duration", 0),
                file_info.get("sample_rate", 44100),
                file_info.get("channels", 2),
                file_info.get("file_size", 0),
                file_info.get("codec", ""),
                
                loudness.get("integrated_lufs", -18.0),
                loudness.get("loudness_range_lu", 8.0),
                loudness.get("true_peak_dbfs", -3.0),
                loudness.get("momentary_max_lufs", -15.0),
                loudness.get("short_term_max_lufs", -16.0),
                loudness.get("crest_factor", 15.0),
                loudness.get("loudness_category", "medium"),
                
                dynamics.get("dynamic_range_db", 10.0),
                dynamics.get("peak_to_rms_ratio", 10.0),
                dynamics.get("compression_ratio", 2.5),
                dynamics.get("dynamic_character", "moderate"),
                dynamics.get("transient_presence", 0.67),
                dynamics.get("micro_dynamics", 0.5),
                
                freq_bands.get("sub_bass", {}).get("energy_ratio", 0.2),
                freq_bands.get("bass", {}).get("energy_ratio", 0.2),
                freq_bands.get("low_mid", {}).get("energy_ratio", 0.2),
                freq_bands.get("mid", {}).get("energy_ratio", 0.2),
                freq_bands.get("high_mid", {}).get("energy_ratio", 0.2),
                freq_bands.get("presence", {}).get("energy_ratio", 0.2),
                freq_bands.get("air", {}).get("energy_ratio", 0.2),
                frequency.get("spectral_centroid", 1000.0),
                frequency.get("spectral_tilt", 0.0),
                frequency.get("bass_emphasis", 0.4),
                frequency.get("high_emphasis", 0.4),
                frequency.get("midrange_character", "balanced"),
                
                stereo.get("stereo_correlation", 0.5),
                stereo.get("stereo_width", 0.7),
                stereo.get("mono_compatibility", 0.8),
                stereo.get("side_content", 0.5),
                stereo.get("phantom_center", 0.5),
                stereo.get("spatial_character", "moderate_width"),
                
                transients.get("transient_ratio", 8.0),
                transients.get("transient_character", "moderate"),
                transients.get("attack_speed", 0.5),
                transients.get("percussive_content", 0.3),
                transients.get("drum_presence", 0.6),
                
                harmonics.get("harmonic_richness", 15.0),
                harmonics.get("thd_estimate", 0.015),
                harmonics.get("even_harmonics", 9.0),
                harmonics.get("odd_harmonics", 6.0),
                harmonics.get("saturation_character", "clean"),
                harmonics.get("analog_character", 0.3),
                
                phase.get("phase_coherence", 0.85),
                phase.get("phase_issues", 0.15),
                phase.get("mono_compatibility_score", 0.77),
                phase.get("phase_character", "good"),
                
                temporal.get("estimated_tempo", 120),
                temporal.get("rhythm_strength", 0.7),
                temporal.get("structural_complexity", 0.6),
                temporal.get("time_signature_estimate", "4/4"),
                temporal.get("rhythmic_character", "moderate_groove"),
                
                mastering.get("mastering_loudness", -14.0),
                mastering.get("processing_intensity", "moderate"),
                mastering.get("limiting_character", "transparent"),
                mastering.get("eq_character", "balanced"),
                mastering.get("compression_style", "gentle"),
                mastering.get("mastering_era", "modern"),
                mastering.get("streaming_optimized", True),
                mastering.get("mastering_quality", "professional"),
                
                analysis.get("mastering_profile", "balanced_modern"),
                json.dumps(analysis),
                analysis.get("analysis_time", 0.0)
            ))
            
            track_id = cursor.lastrowid
            conn.commit()
            
            # Update genre statistics
            self._update_genre_statistics(analysis.get("genre", ""), conn)
            
            return track_id
    
    def _update_genre_statistics(self, genre: str, conn: sqlite3.Connection):
        """Update genre-specific statistics"""
        
        # Calculate genre averages
        stats = conn.execute("""
            SELECT 
                COUNT(*) as track_count,
                AVG(integrated_lufs) as avg_lufs,
                AVG(dynamic_range_db) as avg_dynamic_range,
                AVG(bass_emphasis) as avg_bass_emphasis,
                AVG(high_emphasis) as avg_high_emphasis,
                AVG(stereo_width) as avg_stereo_width
            FROM training_tracks 
            WHERE genre = ?
        """, (genre,)).fetchone()
        
        # Get most common mastering profile
        profile_result = conn.execute("""
            SELECT mastering_profile, COUNT(*) as count
            FROM training_tracks 
            WHERE genre = ?
            GROUP BY mastering_profile
            ORDER BY count DESC
            LIMIT 1
        """, (genre,)).fetchone()
        
        common_profile = profile_result[0] if profile_result else "balanced_modern"
        
        # Update or insert genre statistics
        conn.execute("""
            INSERT OR REPLACE INTO genre_statistics (
                genre, track_count, avg_lufs, avg_dynamic_range,
                avg_bass_emphasis, avg_high_emphasis, avg_stereo_width,
                common_mastering_profile, updated_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            genre,
            stats[0],  # track_count
            stats[1],  # avg_lufs
            stats[2],  # avg_dynamic_range
            stats[3],  # avg_bass_emphasis
            stats[4],  # avg_high_emphasis
            stats[5],  # avg_stereo_width
            common_profile
        ))
    
    def get_genre_insights(self, genre: str) -> Dict[str, Any]:
        """Get comprehensive insights for a specific genre"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Genre statistics
            stats = conn.execute("""
                SELECT * FROM genre_statistics WHERE genre = ?
            """, (genre,)).fetchone()
            
            if not stats:
                return {"error": f"No data found for genre: {genre}"}
            
            # Detailed analysis
            tracks = conn.execute("""
                SELECT 
                    integrated_lufs, dynamic_range_db, bass_emphasis, high_emphasis,
                    stereo_width, mastering_profile, processing_intensity,
                    file_name, analysis_date
                FROM training_tracks 
                WHERE genre = ?
                ORDER BY analysis_date DESC
            """, (genre,)).fetchall()
            
            return {
                "genre": genre,
                "statistics": {
                    "track_count": stats[2],
                    "avg_lufs": round(stats[3], 1),
                    "avg_dynamic_range": round(stats[4], 1),
                    "avg_bass_emphasis": round(stats[5], 2),
                    "avg_high_emphasis": round(stats[6], 2),
                    "avg_stereo_width": round(stats[7], 2),
                    "common_mastering_profile": stats[8]
                },
                "tracks": [{
                    "file_name": track[7],
                    "lufs": track[0],
                    "dynamic_range": track[1],
                    "bass_emphasis": track[2],
                    "high_emphasis": track[3],
                    "stereo_width": track[4],
                    "mastering_profile": track[5],
                    "processing_intensity": track[6],
                    "analysis_date": track[8]
                } for track in tracks]
            }
    
    def get_mastering_template(self, genre: str) -> Dict[str, Any]:
        """Generate mastering template based on genre analysis"""
        
        insights = self.get_genre_insights(genre)
        if "error" in insights:
            return insights
        
        stats = insights["statistics"]
        
        return {
            "genre": genre,
            "recommended_profile": stats["common_mastering_profile"],
            "target_parameters": {
                "lufs_target": stats["avg_lufs"],
                "dynamic_range_target": stats["avg_dynamic_range"],
                "bass_emphasis": stats["avg_bass_emphasis"],
                "high_emphasis": stats["avg_high_emphasis"],
                "stereo_width": stats["avg_stereo_width"]
            },
            "processing_recommendations": self._generate_processing_recommendations(stats),
            "reference_count": stats["track_count"]
        }
    
    def _generate_processing_recommendations(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate processing recommendations from statistics"""
        
        lufs = stats["avg_lufs"]
        dr = stats["avg_dynamic_range"]
        bass = stats["avg_bass_emphasis"]
        highs = stats["avg_high_emphasis"]
        
        return {
            "compression": {
                "style": "gentle" if dr > 10 else "moderate" if dr > 6 else "assertive",
                "ratio": 1.8 if dr > 10 else 2.5 if dr > 6 else 3.2
            },
            "eq": {
                "bass_boost": max(0, (bass - 0.3) * 3),  # Boost if bass-heavy
                "high_boost": max(0, (highs - 0.3) * 2),  # Boost if bright
                "low_mid_cut": max(0, (0.4 - bass) * 2)  # Cut if not bass-heavy
            },
            "limiting": {
                "ceiling": -0.3 if lufs > -12 else -0.8 if lufs > -16 else -1.2,
                "release": 25 if lufs > -12 else 35 if lufs > -16 else 50
            }
        }
    
    def get_all_genres(self) -> List[Dict[str, Any]]:
        """Get overview of all analyzed genres"""
        
        with sqlite3.connect(self.db_path) as conn:
            genres = conn.execute("""
                SELECT * FROM genre_statistics 
                ORDER BY track_count DESC
            """).fetchall()
            
            return [{
                "genre": genre[1],
                "track_count": genre[2],
                "avg_lufs": round(genre[3], 1) if genre[3] else 0,
                "avg_dynamic_range": round(genre[4], 1) if genre[4] else 0,
                "common_profile": genre[8],
                "updated": genre[9]
            } for genre in genres]
    
    def start_training_session(self) -> int:
        """Start a new training session"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO training_sessions (session_start, session_notes)
                VALUES (CURRENT_TIMESTAMP, 'Training session started')
            """)
            session_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"🎓 Training session started: {session_id}")
            return session_id
    
    def end_training_session(self, session_id: int, total_tracks: int, genres: List[str]):
        """End training session with summary"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE training_sessions
                SET session_end = CURRENT_TIMESTAMP,
                    total_tracks_processed = ?,
                    genres_processed = ?
                WHERE id = ?
            """, (total_tracks, json.dumps(genres), session_id))
            conn.commit()
            
            logger.info(f"✅ Training session {session_id} completed: {total_tracks} tracks, {len(genres)} genres")
    
    def get_training_progress(self) -> Dict[str, Any]:
        """Get current training progress and statistics"""
        
        with sqlite3.connect(self.db_path) as conn:
            total_tracks = conn.execute("SELECT COUNT(*) FROM training_tracks").fetchone()[0]
            
            genre_counts = conn.execute("""
                SELECT genre, COUNT(*) 
                FROM training_tracks 
                GROUP BY genre 
                ORDER BY COUNT(*) DESC
            """).fetchall()
            
            recent_session = conn.execute("""
                SELECT * FROM training_sessions 
                ORDER BY session_start DESC 
                LIMIT 1
            """).fetchone()
            
            return {
                "total_tracks_analyzed": total_tracks,
                "genres_trained": len(genre_counts),
                "genre_breakdown": {genre: count for genre, count in genre_counts},
                "last_training_session": {
                    "id": recent_session[0] if recent_session else None,
                    "start": recent_session[1] if recent_session else None,
                    "end": recent_session[2] if recent_session else None,
                    "tracks_processed": recent_session[3] if recent_session else 0
                } if recent_session else None
            }
    
    def export_genre_data(self, genre: str, output_path: Path):
        """Export genre data for external analysis"""
        
        insights = self.get_genre_insights(genre)
        template = self.get_mastering_template(genre)
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "genre": genre,
            "insights": insights,
            "mastering_template": template
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"📤 Exported {genre} data to {output_path}")
    
    def backup_database(self, backup_path: Path):
        """Create database backup"""
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"💾 Database backed up to {backup_path}")


class TrainingDataManager:
    """High-level manager for training data operations"""
    
    def __init__(self, db_path: Path = None):
        self.database = TrainingDatabase(db_path)
        
    def process_batch_analysis(self, batch_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Process and store batch analysis results"""
        
        session_id = self.database.start_training_session()
        total_stored = 0
        genres_processed = []
        
        try:
            for genre, tracks in batch_results.items():
                logger.info(f"💾 Storing {len(tracks)} {genre} tracks...")
                
                for track_analysis in tracks:
                    try:
                        self.database.store_track_analysis(track_analysis)
                        total_stored += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to store track {track_analysis.get('file_path', 'unknown')}: {e}")
                
                genres_processed.append(genre)
                logger.info(f"✅ Completed storing {genre} tracks")
            
            self.database.end_training_session(session_id, total_stored, genres_processed)
            
            return {
                "session_id": session_id,
                "total_tracks_stored": total_stored,
                "genres_processed": genres_processed,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return {
                "session_id": session_id,
                "total_tracks_stored": total_stored,
                "error": str(e),
                "success": False
            }
    
    def get_genre_mastering_profile(self, genre: str) -> Dict[str, Any]:
        """Get optimized mastering profile for genre"""
        return self.database.get_mastering_template(genre)
    
    def get_training_overview(self) -> Dict[str, Any]:
        """Get complete training overview"""
        
        progress = self.database.get_training_progress()
        genres = self.database.get_all_genres()
        
        return {
            "training_progress": progress,
            "genre_details": genres,
            "database_path": str(self.database.db_path),
            "ready_for_ai_training": progress["total_tracks_analyzed"] > 50
        }


if __name__ == "__main__":
    # Test the database system
    manager = TrainingDataManager()
    
    # Example test data
    test_analysis = {
        "file_path": "/test/track.mp3",
        "genre": "test",
        "file_info": {"duration": 180, "sample_rate": 44100, "channels": 2},
        "loudness_analysis": {"integrated_lufs": -14.0},
        "dynamic_analysis": {"dynamic_range_db": 8.0},
        "frequency_analysis": {"bass_emphasis": 0.4, "frequency_bands": {"bass": {"energy_ratio": 0.3}}},
        "analysis_time": 1.5
    }
    
    # Store test analysis
    track_id = manager.database.store_track_analysis(test_analysis)
    print(f"Stored test track with ID: {track_id}")
    
    # Get overview
    overview = manager.get_training_overview()
    print(f"Training overview: {overview}")