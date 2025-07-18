import requests
import os
from dotenv import load_dotenv
import time
import hashlib
from flask import Flask, jsonify

load_dotenv()

API_URL = os.getenv('TRACKBOX_API_URL')
FOLDER_PATH = os.getenv('TRACKBOX_FOLDER_PATH')
ACCEPTED_EXTENSIONS = ['.mp3', '.wav']

app = Flask(__name__)

def compute_file_hash(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def updload_file(file_info):
    file_path = os.path.join(FOLDER_PATH, file_info['path'])
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {'path': file_info['path']}
        response = requests.post(API_URL + '/upload.php', files=files, data=data)
        return response.status_code, response.json()

def get_files_list():
    files_infos = []

    for (root, dirs, files) in os.walk(FOLDER_PATH):
        for file in files:
            if not any(file.lower().endswith(ext) for ext in ACCEPTED_EXTENSIONS):
                continue

            absolute_path = os.path.join(root, file)
            relative_path = os.path.relpath(absolute_path, FOLDER_PATH)
            stat = os.stat(absolute_path)

            file_info = {
                'path': relative_path,
                'size_bytes': stat.st_size,
                'modified_ts': stat.st_mtime,
                'modified_iso': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(stat.st_mtime)),
                'hash': compute_file_hash(absolute_path)
            }

            files_infos.append(file_info)

    return files_infos

@app.route('/sync', methods=['POST'])
def sync_files():
    if not os.path.exists(FOLDER_PATH):
        return jsonify({'success': False, 'message': f'Folder {FOLDER_PATH} does not exist.'}), 404
    uploaded = []

    for file_info in get_files_list():
        status_code, response = updload_file(file_info)
        uploaded.append({'path': file_info['path'], 'status': status_code, 'response': response})
    
    return jsonify({'success': True, 'uploaded': uploaded})

if __name__ == '__main__':
    app.run(port=5001, debug=True)