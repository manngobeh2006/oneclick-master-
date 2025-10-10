# 🚀 Quick Deployment Guide

## Option 1: Render.com (FREE & EASIEST)

1. **Go to [render.com](https://render.com) and sign up**

2. **Connect your GitHub repository**
   - Connect: `https://github.com/manngobeh2006/oneclick-master-.git`

3. **The app will auto-deploy using the `infra/render.yaml` file**
   - Frontend will be deployed as a static site
   - Backend will be deployed as a web service with FFmpeg

4. **Your app will be live in ~5 minutes** 🎉

## Option 2: Vercel (Frontend) + Railway (Backend)

### Frontend on Vercel:
```bash
npm i -g vercel
cd frontend
vercel --prod
```

### Backend on Railway:
1. Go to [railway.app](https://railway.app)
2. Deploy from GitHub repo
3. Set environment variables from your `.env`

## Option 3: Netlify + Heroku

### Frontend on Netlify:
1. Go to [netlify.com](https://netlify.com)
2. Connect GitHub repo
3. Build settings:
   - Build command: `cd frontend && npm run build`
   - Publish directory: `frontend/dist`

### Backend on Heroku:
1. Install Heroku CLI
2. Run:
```bash
cd backend
heroku create oneclick-master-api
heroku buildpacks:add --index 1 heroku-community/apt
echo "ffmpeg" > Aptfile
git subtree push --prefix=backend heroku main
```

## Environment Variables to Set:

```
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID_SINGLE=price_...
STRIPE_PRICE_ID_SUB_MONTHLY=price_...
FRONTEND_URL=https://your-frontend-url.com
CORS_ORIGINS=https://your-frontend-url.com
```

## 🎵 That's it! Your audio mastering app is now live!

The recommended approach is **Render.com** as it:
- ✅ Deploys both frontend and backend
- ✅ Installs FFmpeg automatically
- ✅ Has a generous free tier
- ✅ Auto-deploys on git push
- ✅ Handles SSL certificates

**Your app will be accessible at the Render-provided URLs within minutes!**