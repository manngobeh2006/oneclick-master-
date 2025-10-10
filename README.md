# OneClick Master 🎵

**Professional AI Audio Mastering in One Click**

A modern web application that provides professional audio mastering services powered by AI and advanced audio processing algorithms. Upload your tracks, get instant previews, and download professional-quality masters.

## ✨ Features

### 🎧 Audio Processing
- **Professional Mastering Chain**: Multi-band EQ, compression, limiting, and stereo enhancement
- **AI-Powered Processing**: Advanced algorithms for optimal sound quality
- **Multiple Format Support**: MP3, WAV, M4A, AIFF, FLAC
- **High-Quality Output**: 320kbps MP3 with professional mastering

### 🎨 User Experience
- **Drag & Drop Upload**: Intuitive file upload interface
- **Before/After Comparison**: Side-by-side audio preview with play buttons
- **Real-time Progress**: Upload and processing progress indicators
- **Responsive Design**: Works perfectly on desktop and mobile
- **Professional UI**: Modern, clean interface inspired by industry tools

### 💳 Payment Integration
- **Stripe Integration**: Secure payment processing
- **Two Pricing Tiers**: Single track ($4.99) or unlimited monthly ($19.99)
- **Subscription Support**: Recurring billing for pro users
- **Development Mode**: Built-in development mode for testing

### 🔧 Technical Features
- **React + TypeScript**: Modern frontend with type safety
- **FastAPI Backend**: High-performance Python API
- **FFmpeg Processing**: Industry-standard audio processing
- **Docker Support**: Easy deployment with Docker Compose
- **Progress Tracking**: Real-time upload and processing feedback

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)
- FFmpeg (installed in Docker container)

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/manngobeh2006/oneclick-master-.git
cd oneclick-master-
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run with Docker Compose**
```bash
docker-compose up
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Development

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
oneclick-master/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── api.ts           # API client with progress tracking
│   │   ├── theme.css        # Professional styling
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI Python backend
│   ├── app.py              # Main API application
│   ├── processing.py       # Audio processing logic
│   ├── payments.py         # Stripe integration
│   ├── storage.py          # File storage handling
│   ├── requirements.txt
│   └── Dockerfile
├── infra/                   # Infrastructure configuration
│   └── render.yaml         # Render.com deployment
├── docker-compose.yml       # Development environment
├── .env                    # Environment variables
└── README.md
```

## 🎵 Audio Processing Pipeline

### Preview Generation
- **Quality**: 128kbps MP3 with watermark
- **Processing**: EQ, compression, limiting, stereo enhancement
- **Watermark**: Subtle 880Hz tone at -25dB
- **Features**: Multi-band EQ, professional dynamics

### Master Generation
- **Quality**: 320kbps MP3, professional grade
- **Processing Chain**:
  - High/Low-pass filtering
  - Noise gating
  - 9-band professional EQ
  - Multi-stage compression
  - Stereo enhancement
  - Harmonic saturation
  - Professional limiting
  - Loudness normalization (-14 LUFS)

## 🔧 API Endpoints

### Core Endpoints
- `POST /preview` - Generate preview with progress tracking
- `POST /checkout` - Create Stripe checkout session
- `POST /checkout-subscription` - Create subscription checkout
- `POST /process-full` - Process full-quality master
- `GET /health` - API health check

### File Serving
- `/files/previews/{id}.mp3` - Preview files
- `/files/outputs/{id}.mp3` - Master files

## 💳 Payment Configuration

### Stripe Setup
```bash
# Required environment variables
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID_SINGLE=price_...
STRIPE_PRICE_ID_SUB_MONTHLY=price_...
```

### Development Mode
When `STRIPE_SECRET_KEY` is not set, the app runs in development mode with:
- Mock payment sessions
- Local file processing
- No external API calls

## 🚀 Deployment

### Using Docker
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d
```

### Render.com
1. Connect your GitHub repository
2. Use the provided `infra/render.yaml` configuration
3. Set environment variables in Render dashboard
4. Deploy automatically on git push

### Environment Variables
```bash
# Required
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...
FRONTEND_URL=https://yourdomain.com

# Optional
AWS_REGION=us-east-1
S3_BUCKET_UPLOADS=your-uploads-bucket
S3_BUCKET_OUTPUTS=your-outputs-bucket
CORS_ORIGINS=https://yourdomain.com
```

## 🎨 UI/UX Features

### Modern Design
- **Glassmorphism**: Frosted glass effects with backdrop blur
- **Gradient Backgrounds**: Professional color schemes
- **Micro-interactions**: Smooth hover effects and transitions
- **Responsive Grid**: Adapts to all screen sizes

### Audio Comparison
- **Side-by-side Players**: Original vs. mastered comparison
- **One-click Switching**: Instant A/B comparison
- **Visual Feedback**: Clear labeling and progress indicators
- **Professional Controls**: Industry-standard audio controls

## 🔒 Security Features

- **CORS Protection**: Configurable origin restrictions
- **File Validation**: Type and size checking
- **Secure Uploads**: Temporary file handling
- **Payment Security**: Stripe-powered secure payments
- **Error Handling**: Graceful error recovery

## 🧪 Testing

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FFmpeg** - Powerful audio processing
- **React** - Modern frontend framework  
- **FastAPI** - High-performance Python API
- **Stripe** - Secure payment processing
- **Vite** - Lightning-fast development

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/manngobeh2006/oneclick-master-/issues)
- **Documentation**: Check the `/docs` folder for detailed guides
- **API Docs**: Visit `/docs` endpoint when running the application

---

**Built with ❤️ for musicians and audio professionals worldwide**