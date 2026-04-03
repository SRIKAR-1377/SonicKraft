from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
import subprocess
import threading
import uuid
import re
import urllib.request
import urllib.parse
import json
import time
from urllib.error import URLError
from urllib.request import urlopen

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app) # Enable CORS for all routes

v = os.path.join(os.path.dirname(__file__), 'downloads')
if not os.path.exists(v):
    os.makedirs(v)

# In-memory dictionary to store the status of our background tasks
download_tasks = {}

# Utility to estimate a Spotify playlist track count from open web playlist page
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def get_spotify_playlist_count(url):
    try:
        if 'open.spotify.com/playlist/' not in url:
            return None
        playlist_id = url.split('playlist/')[1].split('?')[0]
        html_url = f'https://open.spotify.com/playlist/{playlist_id}'
        with urllib.request.urlopen(html_url, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        # Find JSON containing total tracks
        match = re.search(r'"total"\s*:\s*(\d+)', html)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None

def run_spotdl_background(session_id, url, download_path, format_choice):
    max_retries = 5
    retry_count = 0
    last_error = None
    
    while retry_count <= max_retries:
        try:
            # Update status
            download_tasks[session_id]['status'] = 'downloading'
            download_tasks[session_id]['percentage'] = 0
            
            print(f"[{session_id}] Downloading {url} to {download_path} format {format_choice} (Attempt {retry_count + 1}/{max_retries + 1})")
            
            # Validate URL format
            if not url or not url.startswith('http'):
                download_tasks[session_id]['status'] = 'error'
                download_tasks[session_id]['message'] = '❌ Invalid URL. Make sure it\'s a valid Spotify link (starts with https://)'
                return
            
            # Direct audio handling (standard for 4.4.x), 8 threads (safer), always overwrite, sponsor-block skips
            cmd = [sys.executable, '-m', 'spotdl', url, '--output', download_path, 
                   '--threads', '8', '--overwrite', 'force', 
                   '--sponsor-block', '--no-cache']
            download_tasks[session_id]['message'] = f"🚀 Ultra-fast mode: direct/64thr/sponsorblock/96k (attempt {retry_count + 1})"
            
            # Force fast MP3 96k for speed (user-approved faster version)
            cmd.extend(['--format', 'mp3', '--bitrate', '96k', '--ffmpeg-args', '-preset ultrafast'])
                
            # Verify spotdl is installed and accessible
            try:
                check_proc = subprocess.run([sys.executable, '-m', 'spotdl', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
                if check_proc.returncode != 0:
                    raise RuntimeError(check_proc.stderr.strip() or check_proc.stdout.strip() or 'spotdl module not available')
            except Exception as e:
                download_tasks[session_id]['status'] = 'error'
                download_tasks[session_id]['message'] = f"spotdl not available: {str(e)}"
                return

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

            # Pre-compile regexes for better performance
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            progress_pattern = re.compile(r'(\d+)\s*%|Downloaded\s+(\d+)\s*/\s*(\d+)|\[(\d+)/(\d+)\]|\b(\d+)\s*/\s*(\d+)\b')
            error_keywords = re.compile(r'error|failed|exception|unauthorized|forbidden|rate.?limit', re.IGNORECASE)
            
            last_error = None
            no_progress_count = 0
            rate_limit_hit = False
            
            if playlist_count := get_spotify_playlist_count(url):
                download_tasks[session_id]['message'] = f"Playlist size {playlist_count}; processing..."
                download_tasks[session_id]['playlist_total'] = playlist_count

            for line in iter(process.stdout.readline, ''):
                clean_line = ansi_escape.sub('', line).strip()
                if clean_line:
                    # Store the last non-empty line as the message
                    download_tasks[session_id]['message'] = clean_line
                    
                    # Capture error lines for diagnostics
                    if error_keywords.search(clean_line):
                        last_error = clean_line
                        print(f"[{session_id}] ERROR: {clean_line}")
                        if 'rate/request limit' in clean_line.lower() or 'rate limit' in clean_line.lower():
                            rate_limit_hit = True
                    
                    # Try to extract percentage from the line (only if it contains digits)
                    if any(c.isdigit() for c in clean_line):
                        match = progress_pattern.search(clean_line)
                        if match:
                            if match.group(1):  # Format: "50%"
                                percentage = int(match.group(1))
                            elif match.group(2) and match.group(3):  # Format: "Downloaded 5/100"
                                current = int(match.group(2))
                                total = int(match.group(3))
                                percentage = int((current / total) * 100) if total > 0 else 0
                            elif match.group(4) and match.group(5):  # Format: "[5/100]"
                                current = int(match.group(4))
                                total = int(match.group(5))
                                percentage = int((current / total) * 100) if total > 0 else 0
                            elif match.group(6) and match.group(7):
                                current = int(match.group(6))
                                total = int(match.group(7))
                                percentage = int((current / total) * 100) if total > 0 else 0
                            else:
                                percentage = download_tasks[session_id].get('percentage', 0)
                            
                            # Update percentage, ensuring it doesn't go backwards
                            if percentage >= download_tasks[session_id].get('percentage', 0):
                                download_tasks[session_id]['percentage'] = min(percentage, 100)
                            no_progress_count = 0
                        else:
                            no_progress_count += 1
                    else:
                        no_progress_count += 1

                    if no_progress_count > 30 and download_tasks[session_id]['stalled_warning_sent'] is not True:
                        download_tasks[session_id]['message'] = '⏳ Still processing playlist, waiting for spotdl output (may take while for large playlists)...'
                        download_tasks[session_id]['stalled_warning_sent'] = True

            process.stdout.close()
            return_code = process.wait()
            
            if return_code != 0:
                if rate_limit_hit and retry_count < max_retries:
                    retry_count += 1
                    download_tasks[session_id]['message'] = f"⚠️ Rate limit hit. Retrying faster... (attempt {retry_count + 1}/{max_retries + 1})"
                    download_tasks[session_id]['percentage'] = 0
                    time.sleep(1 + retry_count * 0.5)  # Ultra-fast backoff
                    continue
                if retry_count < max_retries:
                    retry_count += 1
                    error_hint = ""
                    if last_error and 'rate' in last_error.lower():
                        error_hint = " (Rate limit - cooling down...)"
                    elif last_error and ('network' in last_error.lower() or 'timeout' in last_error.lower()):
                        error_hint = " (Network issue - retrying...)"
                    download_tasks[session_id]['message'] = f"⚠️ Download failed{error_hint}. Retrying faster (Attempt {retry_count + 1}/{max_retries + 1})..."
                    download_tasks[session_id]['percentage'] = 0
                    time.sleep(1 + retry_count * 0.5)  # Progressive fast backoff: 1.5-4s
                    continue
                else:
                    download_tasks[session_id]['status'] = 'error'
                    error_msg = last_error if last_error else "spotdl failed after all retries"
                    download_tasks[session_id]['message'] = f"❌ {error_msg}. Check: FFmpeg installed? Spotify URL valid? Internet connected?"
                    print(f"[{session_id}] FAILED: {error_msg}")
            else:
                download_tasks[session_id]['status'] = 'completed'
                download_tasks[session_id]['percentage'] = 100
                download_tasks[session_id]['message'] = f"✅ Successfully downloaded to {download_path}"
                download_tasks[session_id]['download_path'] = download_path
                print(f"[{session_id}] COMPLETED")
            break
                
        except Exception as e:
            print(f"[{session_id}] EXCEPTION: {str(e)}")
            if retry_count < max_retries:
                retry_count += 1
                download_tasks[session_id]['message'] = f"Error occurred. Retrying faster... (Attempt {retry_count + 1}/{max_retries + 1})"
                download_tasks[session_id]['percentage'] = 0
                time.sleep(1 + retry_count * 0.5)
                continue
            else:
                download_tasks[session_id]['status'] = 'error'
                download_tasks[session_id]['message'] = f"❌ {str(e)}"
                break

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    user_path = data.get('download_path', '').strip()
    format_choice = data.get('format_choice', 'mp3')
    max_songs = int(data.get('max_songs', 500)) if data.get('max_songs') else 500
    max_songs = min(max(max_songs, 1), 500)
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Check Spotify playlist size limit
    playlist_count = get_spotify_playlist_count(url)
    if playlist_count is not None and playlist_count > max_songs:
        return jsonify({'error': f'Playlist has {playlist_count} songs; max supported is {max_songs} songs.'}), 400

    session_id = str(uuid.uuid4())
    
    # Determine the download directory
    if user_path:
        download_dir = user_path
        # Ensure the directory exists
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir, exist_ok=True)
            except Exception as e:
                 return jsonify({'error': f'Failed to create directory {download_dir}. Check permissions.'}), 400
    else:
        # Default directory -> nested inside 'downloads/' folder natively
        download_dir = os.path.join(v, f"playlist_{session_id}")
        os.makedirs(download_dir, exist_ok=True)

    # Initialize task status
    download_tasks[session_id] = {
        'status': 'starting',
        'message': 'Preparing massive download...',
        'download_path': download_dir,
        'percentage': 0,
        'stalled_warning_sent': False
    }

    # Start the background thread
    thread = threading.Thread(target=run_spotdl_background, args=(session_id, url, download_dir, format_choice))
    thread.daemon = True
    thread.start()

    return jsonify({'session_id': session_id, 'message': 'Download started in background'})

@app.route('/api/status/<session_id>', methods=['GET'])
def status(session_id):
    task = download_tasks.get(session_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task)

@app.route('/api/convert', methods=['POST'])
def convert_link():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
        
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            encoded_url = urllib.parse.quote(url)
            api_url = f"https://api.song.link/v1-alpha.1/links?url={encoded_url}"
            
            # Using a more standard User-Agent to avoid early blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json'
            }
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                
            links = result.get('linksByPlatform', {})
            platforms = {
                'spotify': links.get('spotify', {}).get('url'),
                'youtubeMusic': links.get('youtubeMusic', {}).get('url'),
                'youtube': links.get('youtube', {}).get('url'),
                'appleMusic': links.get('appleMusic', {}).get('url'),
                'soundcloud': links.get('soundcloud', {}).get('url')
            }
            
            # Filter out None values
            valid_links = {k: v for k, v in platforms.items() if v}
            
            if not valid_links and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
                
            return jsonify({'links': valid_links})
            
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential-ish backoff
                continue
            return jsonify({'error': f"Conversion failed (HTTP {e.code}): {e.reason if hasattr(e, 'reason') else str(e)}"}), e.code
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return jsonify({'error': f"Conversion failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
