# SonicKraft - Developer Setup Guide

## ⚙️ Local Development Setup

### 1. Prerequisites
- Python 3.11+ ([Download](https://www.python.org/))
- FFmpeg ([Installation Guide](https://ffmpeg.org/download.html))
- Git

### 2. Clone & Setup

```bash
# Clone repository
git clone https://github.com/your-username/sonickraft.git
cd SonicKraft

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## 🚀 Deploy to Vercel

### Option A: GitHub Integration (Recommended)

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/sonickraft.git
   git push -u origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Select your GitHub repository
   - Configure settings:
     - **Framework**: Other
     - **Root Directory**: `./`
     - **Build Command**: `pip install -r requirements.txt`
     - **Install Command**: `pip install -r requirements.txt`
   - Click "Deploy"

3. **Your app is live!**
   - URL: `https://your-project-name.vercel.app`

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow the prompts
```

---

## 📦 Project Structure

```
SonicKraft/
├── api/
│   └── index.py              # Vercel serverless entry point
├── static/
│   ├── index.html            # Main UI
│   ├── script.js             # Frontend (80+ KB min, handles env detection)
│   └── style.css             # Glassmorphism effects
├── app.py                    # Flask app (local development)
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
├── runtime.txt              # Python version specification
├── .gitignore               # Git exclusions
├── .vercelignore            # Vercel build exclusions
├── README.md                # Project overview
├── VERCEL_DEPLOYMENT.md     # Detailed deployment guide
└── SETUP.md                 # This file
```

---

## 🔧 Troubleshooting

### Issue: FFmpeg not found
**Solution**: 
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org), add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### Issue: Dependencies fail to install
**Solution**:
```bash
# Ensure pip is updated
python -m pip install --upgrade pip

# Re-install dependencies
pip install -r requirements.txt
```

### Issue: Port 5000 already in use
**Solution**: Modify in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=8000)  # Use port 8000 instead
```

### Issue: Download feature not working on Vercel
**Expected behavior** ✓ This is normal! Vercel serverless doesn't support:
- Long-running processes
- FFmpeg/system binaries
- Threading/background tasks

**Solution**: Run locally or use a traditional server (Render, Railway, etc.)

---

## 📝 Environment Comparison

| Feature | Local | Vercel | Render/Railway |
|---------|-------|--------|---|
| Link Translation | ✅ | ✅ | ✅ |
| Downloads | ✅ | ❌ | ✅ |
| Startup Speed | ~2s | <1s | 5-30s* |
| Cost | Free | Free | Free** |
| Background Tasks | ✅ | ❌ | ✅ |

*Cold starts on free tier  
**Limited free tier, generous for dev

---

## 🔨 Building Changes

### Frontend Changes (HTML/CSS/JS)
- Changes apply immediately in development
- No rebuild needed

### Backend Changes (Python)
- Restart the server:
  ```bash
  # Stop: Ctrl+C
  # Restart: python app.py
  ```

### Deploy to Vercel
```bash
git add .
git commit -m "Your changes"
git push origin main

# Vercel automatically deploys!
```

---

## 📚 Useful Commands

```bash
# Check Python version
python --version

# Check dependencies
pip list

# Update dependencies
pip install -r requirements.txt --upgrade

# Check if FFmpeg is installed
ffmpeg -version

# Run with different port
python -c "import app; app.app.run(port=8000)"

# Check Flask version
python -c "import flask; print(flask.__version__)"
```

---

## 🎯 Next Steps

1. ✅ Get it running locally
2. ✅ Test all features
3. ✅ Create GitHub repo
4. ✅ Deploy to Vercel
5. ✅ Share your app!

---

## 📞 Need Help?

- Check browser console for errors (F12)
- Check terminal for server logs
- Read [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for deployment issues
- Check [README.md](README.md) for feature overview

---

**Happy coding! 🎵**
