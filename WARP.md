# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

OneClick Master is a professional AI audio mastering web application with a React TypeScript frontend and FastAPI Python backend. It provides one-click audio mastering with Stripe payment integration and supports multiple deployment platforms.

## Architecture

### Backend (FastAPI + Python)
- **Core API** (`backend/app.py`): Main FastAPI application with audio processing endpoints
- **Audio Processing** (`backend/processing.py`): FFmpeg-based audio mastering pipeline with noise reduction, EQ, compression, and limiting
- **Payment System** (`backend/payments.py`): Stripe checkout and subscription management
- **Storage** (`backend/storage.py`): S3 integration for file storage (optional, falls back to local)

### Frontend (React + TypeScript)
- **Main App** (`frontend/src/App.tsx`): Single-page application with drag-and-drop upload, audio comparison, and payment flow
- **API Client** (`frontend/src/api.ts`): XMLHttpRequest-based client with upload progress tracking
- **Styling**: Custom CSS with glassmorphism design and responsive layout

### Audio Processing Pipeline
The application implements a sophisticated mastering chain:
- **Preview**: 128kbps with watermark (880Hz tone every 12s)
- **Master**: 320kbps professional quality with multi-band EQ, multi-stage compression, stereo enhancement, and LUFS normalization

## Development Commands

### Quick Start (Recommended)
```bash
docker-compose up
```
Starts both frontend (port 5173) and backend (port 8000) with hot reloading.

### Frontend Development
```bash
cd frontend
npm install
npm run dev         # Start development server
npm run build       # Production build
npm run lint        # ESLint code checking
npm run preview     # Preview production build
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Frontend tests
cd frontend && npm test

# Backend tests  
cd backend && pytest

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Key Configuration

### Environment Variables (.env)
```bash
# Stripe (required for production)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID_SINGLE=price_...
STRIPE_PRICE_ID_SUB_MONTHLY=price_...

# Frontend URL for CORS and redirects
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173

# Optional AWS S3 storage
AWS_REGION=us-east-1
S3_BUCKET_UPLOADS=uploads-bucket
S3_BUCKET_OUTPUTS=outputs-bucket
```

### Development Mode
When `STRIPE_SECRET_KEY` is not set, the app automatically enters development mode with:
- Mock payment sessions
- Local file processing only
- No external API calls

## Deployment Options

### Option 1: Render.com (Recommended)
Uses `infra/render.yaml` for automatic deployment:
```bash
# Auto-deploys both frontend (static) and backend (web service)
# Installs FFmpeg automatically
# Free tier available
```

### Option 2: AWS App Runner  
Uses `apprunner.yaml`:
```bash
# Handles both frontend build and backend deployment
# Includes FFmpeg installation
```

### Option 3: Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## File Structure Patterns

### Backend Modules
- `app.py`: Main FastAPI app with all endpoints
- `processing.py`: Audio processing utilities using FFmpeg
- `payments.py`: Stripe integration helpers
- `storage.py`: S3 file management utilities

### Frontend Structure
- `App.tsx`: Main React component with all UI logic
- `api.ts`: API client with progress tracking
- `theme.css`: Professional styling with glassmorphism effects
- Vite configuration handles development proxy and production builds

## Audio Processing Details

### Preview Generation (`make_preview`)
Complex FFmpeg filter chain:
- Noise reduction and frequency filtering
- Multi-band EQ (5 bands)
- Dual-stage compression  
- Stereo enhancement
- Loudness normalization (-16 LUFS)
- Watermark injection (880Hz at -25dB)

### Master Generation (`make_master`)  
Professional mastering chain:
- High/low-pass filtering and noise gating
- 9-band professional EQ
- 3-stage compression with different ratios
- Stereo enhancement and harmonic saturation
- Final limiting and loudness normalization (-14 LUFS)

## Common Development Workflows

### Adding New Audio Processing Features
1. Modify FFmpeg filter chains in `backend/processing.py`
2. Test with various audio formats (MP3, WAV, M4A, AIFF, FLAC)
3. Update preview and master generation functions
4. Verify loudness normalization meets streaming standards

### Frontend UI Changes
1. Modify React components in `frontend/src/App.tsx`
2. Update CSS in `frontend/src/theme.css` 
3. Test responsive design on different screen sizes
4. Ensure audio player controls work properly

### Payment Integration Updates
1. Update Stripe price IDs in environment variables
2. Modify checkout flows in `backend/payments.py`
3. Test both one-time and subscription payment flows
4. Verify webhook handling for production use

### Deployment Updates
1. Update `infra/render.yaml` for Render.com deployment
2. Modify `apprunner.yaml` for AWS App Runner
3. Ensure environment variables are set correctly
4. Test FFmpeg installation in deployment environment

## Dependencies

### Runtime Requirements
- **FFmpeg**: Required for audio processing (installed in Docker/deployment)
- **Python 3.11+**: Backend runtime
- **Node.js 18+**: Frontend development

### Key Libraries
- **FastAPI**: Backend API framework
- **React 19**: Frontend UI framework  
- **Stripe**: Payment processing
- **Boto3**: AWS S3 integration (optional)
- **Vite**: Frontend build tool with fast HMR

## Notes

- The application supports both local file storage (development) and S3 storage (production)
- Audio processing is CPU-intensive; ensure adequate server resources for production
- Stripe webhooks should be implemented for production subscription management
- The frontend uses XMLHttpRequest for upload progress tracking instead of fetch API
- All audio processing maintains high quality with proper loudness standards for streaming platforms