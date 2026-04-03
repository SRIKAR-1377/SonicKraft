from flask import Flask, request, jsonify, send_from_directory
import os
import urllib.request
import urllib.parse
import json
import uuid

# Get the static folder path for Vercel environment
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
app = Flask(__name__, static_folder=static_path, static_url_path='/static')

@app.route('/')
def index():
    return send_from_directory(static_path, 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(static_path, path)

@app.route('/api/download', methods=['POST'])
def download():
    # Vercel Limitation: Subprocess and Threading are not supported.
    return jsonify({'error': 'The Downloader feature is only available in the local Python environment. Vercel Serverless Functions do not support long-running processes or ffmpeg. Please run the project locally to use this tool.'}), 503

@app.route('/api/status/<session_id>', methods=['GET'])
def status(session_id):
    return jsonify({'error': 'Task not found or serverless function expired.'}), 404

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
            
            valid_links = {k: v for k, v in platforms.items() if v}
            
            if not valid_links and attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                continue
                
            return jsonify({'links': valid_links})
            
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                import time
                time.sleep(retry_delay * (attempt + 1))
                continue
            return jsonify({'error': f"Conversion failed (HTTP {e.code}): {str(e)}"}), e.code
        except Exception as e:
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                continue
            return jsonify({'error': f"Conversion failed: {str(e)}"}), 500

# For Vercel Serverless
def handler(event, context):
    return app(event, context)
