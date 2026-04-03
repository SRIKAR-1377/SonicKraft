# SonicKraft - Vercel Deployment Guide

## Features by Environment

### ✅ Works on Vercel (Serverless)
- **Link Translation**: Convert Spotify links to other platforms (Apple Music, YouTube, SoundCloud, etc.)
- **Beautiful UI**: Full glassmorphism interface with aurora effects

### ❌ NOT Available on Vercel (Local Only)
- **Downloads**: Spotify playlist/track downloads (requires spotdl + ffmpeg + long-running processes)

---

## Deployment to Vercel

### Prerequisites
- Vercel account (free tier available)
- GitHub repository with your code

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/sonickraft.git
git push -u origin main
```

### Step 2: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select your GitHub repository
4. Framework: **Other**
5. Root Directory: **./
6. Build Command: `pip install -r requirements.txt`
7. Install Command: `pip install -r requirements.txt`
8. Click Deploy

### Step 3: Your app is live!
- Access at: `https://your-project-name.vercel.app`
- Link translation works immediately
- Download feature shows helpful message

---

## Local Development (Full Features)

To use the download feature locally:

```bash
pip install -r requirements.txt
python app.py
```

Visit: `http://localhost:5000`

---

## Troubleshooting

**Issue**: Download button shows error on Vercel
- **Expected behavior** ✓ Downloads aren't supported on serverless
- **Solution**: Run locally or use a traditional server (Render, Railway, etc.)

**Issue**: Static files not loading
- Make sure `vercel.json` has correct rewrites
- Check that `static/` folder exists with `index.html`

**Issue**: API calls failing
- Verify API routes work locally first
- Check browser console for CORS errors
- Song.link API might be rate-limited

---

## Local vs. Server Comparison

| Feature | Local | Vercel |
|---------|-------|--------|
| Link Translation | ✅ | ✅ |
| Downloads | ✅ | ❌ |
| FFmpeg Processing | ✅ | ❌ |
| Long-running Tasks | ✅ | ❌ |
| Startup Speed | ~2s | instant |
| Cost | Free | Free (generous limits) |

---

## Environment Detection
The app automatically detects if it's running on Vercel and disables the download feature with a friendly message.
