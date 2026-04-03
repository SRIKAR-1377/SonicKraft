# 🎵 SonicKraft

A high-performance web application for music enthusiasts - download Spotify content and translate music links across platforms (Apple Music, YouTube, SoundCloud).

## Features

### ✅ Cross-Platform Link Translation
Convert Spotify links to equivalent links on:
- Apple Music
- YouTube Music
- YouTube
- SoundCloud

### 📥 Pro-Grade Downloads (Local Only)
- Multiple audio formats: MP3 (320kbps), FLAC, M4A
- Batch download entire playlists
- Real-time progress tracking
- Smart library management with history

### 🎨 Premium UI
- Glassmorphism design with aurora effects
- Floating music note particles
- Real-time equalizer
- Fully responsive layout
- Dark mode optimized

## Quick Start

### Option 1: Deploy to Vercel (Link Translation Only)
Click the button below to deploy the link translator to Vercel:

[Deploy to Vercel](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/sonickraft)

**Note**: Downloads are not available on Vercel's serverless functions

### Option 2: Run Locally (Full Features)

#### Requirements
- Python 3.11+
- FFmpeg installed

#### Setup
```bash
# Clone repository
git clone <your-repo>
cd SonicKraft

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit `http://localhost:5000`

## Deployment Options

### Vercel (Recommended for Link Translation)
✅ Free tier  
✅ Lightning fast  
✅ Works with link translator  
❌ No downloads (serverless limitation)

👉 [Vercel Deployment Guide](VERCEL_DEPLOYMENT.md)

### Render / Railway (Full Features)
✅ Free tier  
✅ Supports long-running processes  
✅ Works with downloads  
⚠️ Cold starts on free tier

## Technology Stack

**Backend**: Python (Flask)  
**Frontend**: JavaScript (ES6+), HTML5, CSS3  
**APIs**: Song.link (Odesli), spotdl  
**Deployment**: Vercel, Render, Railway, etc.

## Key Highlights

- Bypassed platform rate limits with decentralized audio routing
- Non-blocking background task system for massive playlists
- Custom CSS animations with high performance
- Asynchronous polling for real-time updates
- Local persistent storage for download history

## Environment Detection

The app automatically detects:
- **Running on Vercel?** → Shows link translator only
- **Running locally?** → Full features unlocked

## File Structure

```
SonicKraft/
├── api/
│   └── index.py           # Vercel serverless entry point
├── static/
│   ├── index.html         # Main UI
│   ├── script.js          # Frontend logic
│   └── style.css          # Glassmorphism styling
├── app.py                 # Local Flask server
├── requirements.txt       # Dependencies
├── vercel.json           # Vercel configuration
├── runtime.txt           # Python version
└── VERCEL_DEPLOYMENT.md  # Deployment guide
```

## License

MIT License - feel free to use and modify

## Support

For issues or suggestions, please create an issue in the repository.

---

Made with ❤️ by Srikar Kuchi
