from flask import Flask, request, jsonify
import os
import urllib.request
import urllib.parse
import json
import uuid

app = Flask(__name__, static_folder='../static', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

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
        
        valid_links = {k: v for k, v in platforms.items() if v}
        return jsonify({'links': valid_links})
        
    except Exception as e:
        return jsonify({'error': f"Conversion failed: {str(e)}"}), 500

# For Vercel Serverless
def handler(event, context):
    return app(event, context)
