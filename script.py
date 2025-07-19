"""Trackbox File Sync Script"""
import time
import os
from requests.exceptions import RequestException
from dotenv import load_dotenv
from flask import Flask, jsonify
from utils import compute_file_hash, get_files_list, upload_file_in_chunks

load_dotenv()

API_URL = os.getenv('TRACKBOX_API_URL')
FOLDER_PATH = os.getenv('TRACKBOX_FOLDER_PATH')
ACCEPTED_EXTENSIONS = ['.mp3', '.wav']

app = Flask(__name__)

@app.route('/sync')
def sync_files() -> jsonify:
    """Sync files from the specified folder to the remote server in chunks."""
    if not os.path.exists(FOLDER_PATH):
        return jsonify({'success': False, 'message': f'Folder {FOLDER_PATH} does not exist.'}), 404
    
    uploaded_files = []
    files = get_files_list(FOLDER_PATH, ACCEPTED_EXTENSIONS)

    for file_info in files:
        try:
            status_code, response = upload_file_in_chunks(file_info, FOLDER_PATH, API_URL)
            if status_code == 200:
                uploaded_files.append({
                    'path': file_info['path'],
                    'status': status_code,
                    'hash': file_info['hash'],
                })
        except (RequestException, OSError) as e:
            uploaded_files.append({'path': file_info['path'], 'status': 'error', 'response': str(e)})

    return jsonify({'success': True, 'uploaded_files': uploaded_files})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
