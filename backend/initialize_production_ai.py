#!/usr/bin/env python3
"""
Production AI Initialization Script
Ensures AI mastering system is ready with training data in production environment.
"""

import os
import logging
from pathlib import Path
from intelligent_mastering_engine import IntelligentMasteringEngine
from training_database import TrainingDatabase

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_production_ai():
    """Initialize AI mastering system for production deployment."""
    try:
        logger.info("🚀 Initializing AI Mastering System for Production...")
        
        # Check if training database exists
        db_path = Path(__file__).parent / "training_data.db"
        
        if not db_path.exists():
            logger.warning("⚠️  Training database not found. Creating minimal database...")
            
            # Create minimal training database for production
            db = TrainingDatabase()
            
            # Add some basic genre templates if none exist
            basic_templates = {
                'hiphop': {'lufs_target': -11.5, 'compression_profile': 'aggressive'},
                'pop': {'lufs_target': -10.0, 'compression_profile': 'balanced'},
                'electronic': {'lufs_target': -9.5, 'compression_profile': 'punchy'},
                'rnb': {'lufs_target': -10.5, 'compression_profile': 'smooth'},
                'trap': {'lufs_target': -11.0, 'compression_profile': 'hard'}
            }
            
            logger.info("📊 Creating basic genre templates...")
            for genre, params in basic_templates.items():
                # Create mock training data entry
                track_data = {
                    'file_path': f'/production/reference/{genre}_reference.mp3',
                    'genre': genre,
                    'duration': 180.0,
                    'integrated_lufs': params['lufs_target'],
                    'lra': 8.0,
                    'true_peak': -1.0,
                    'compression_profile': params['compression_profile']
                }
                
                # Add basic spectral data
                for i in range(10):
                    track_data[f'spectral_centroid_{i}'] = 1000.0 + i * 500
                    track_data[f'spectral_rolloff_{i}'] = 5000.0 + i * 1000
                    track_data[f'zero_crossing_rate_{i}'] = 0.1 + i * 0.02
                    track_data[f'mfcc_{i}'] = float(i * 0.5)
                    track_data[f'chroma_{i}'] = 0.5 + i * 0.05
                    track_data[f'tempo_beat_{i}'] = 120.0 + i * 10
                
                db.store_track_analysis(track_data)
            
            logger.info("✅ Basic training database created")
        
        # Initialize AI engine
        logger.info("🧠 Loading AI Mastering Engine...")
        ai_engine = IntelligentMasteringEngine()
        
        logger.info(f"📊 AI Engine Status:")
        logger.info(f"   - Genre templates: {len(ai_engine.genre_templates)}")
        logger.info(f"   - AI profiles: {len(ai_engine.ai_profiles)}")
        
        if ai_engine.genre_templates:
            logger.info("🎯 Available genres:")
            for genre, template in ai_engine.genre_templates.items():
                logger.info(f"   - {genre}: {template['reference_count']} refs, LUFS: {template['target_parameters']['lufs_target']:.1f}")
        
        logger.info("🎉 AI Mastering System successfully initialized for production!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI system: {str(e)}")
        logger.error("🔄 Falling back to basic mastering mode...")
        return False

if __name__ == "__main__":
    success = initialize_production_ai()
    exit(0 if success else 1)