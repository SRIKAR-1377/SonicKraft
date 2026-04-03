from flask import Flask, request, jsonify, send_file
import os
import sys
import subprocess
import threading
import uuid
import re
import urllib.request
import urllib.parse
import json

app = Flask(__name__, static_folder='static', static_url_path='')

v = os.path.join(os.path.dirname(__file__), 'downloads')
if not os.path.exists(v):
    os.makedirs(v)

# In-memory dictionary to store the status of our background tasks
download_tasks = {}

def run_spotdl_background(session_id, url, download_path, format_choice):
    try:
        # Update status
        download_tasks[session_id]['status'] = 'downloading'
        
        print(f"[{session_id}] Downloading {url} to {download_path} format {format_choice}")
        
        # spotdl command
        # using --audio piped to bypass the user's active 24-hr YouTube IP ban
        cmd = [sys.executable, '-m', 'spotdl', url, '--output', download_path, '--threads', '4', '--audio', 'piped']
        
        if format_choice == 'mp3':
            cmd.extend(['--format', 'mp3', '--bitrate', '320k'])
        elif format_choice == 'flac':
            cmd.extend(['--format', 'flac'])
        elif format_choice == 'm4a':
            cmd.extend(['--format', 'm4a'])
            
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        for line in iter(process.stdout.readline, ''):
            clean_line = ansi_escape.sub('', line).strip()
            if clean_line:
                # Ensure we only capture meaningful text, ignore empty clears
                # We can store the last non-empty line as the message
                download_tasks[session_id]['message'] = clean_line

        process.stdout.close()
        return_code = process.wait()
        
        if return_code != 0:
            download_tasks[session_id]['status'] = 'error'
            download_tasks[session_id]['message'] = f"spotdl failed. Check server logs."
        else:
            download_tasks[session_id]['status'] = 'completed'
            download_tasks[session_id]['message'] = f"Successfully downloaded to {download_path}"
            download_tasks[session_id]['download_path'] = download_path
            
    except Exception as e:
        download_tasks[session_id]['status'] = 'error'
        download_tasks[session_id]['message'] = str(e)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    user_path = data.get('download_path', '').strip()
    format_choice = data.get('format_choice', 'mp3')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

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
        'download_path': download_dir
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
        
    try:
        encoded_url = urllib.parse.quote(url)
        api_url = f"https://api.song.link/v1-alpha.1/links?url={encoded_url}"
        
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
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
        
        return jsonify({'links': valid_links})
        
    except Exception as e:
        return jsonify({'error': f"Conversion failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
