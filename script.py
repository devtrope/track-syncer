"""Trackbox File Sync Script"""
import time
import hashlib
import os
import requests # type: ignore
from requests.exceptions import RequestException
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

API_URL = os.getenv('TRACKBOX_API_URL')
FOLDER_PATH = os.getenv('TRACKBOX_FOLDER_PATH')
ACCEPTED_EXTENSIONS = ['.mp3', '.wav']

app = Flask(__name__)

def compute_file_hash(file_path):
    """Compute the SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()

def upload_file_in_chunks(file_info, chunk_size=1024 * 1024):
    """Upload a file in chunks to the remote server."""
    file_path = os.path.join(FOLDER_PATH, file_info['path'])
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size + chunk_size - 1) // chunk_size
    filename = os.path.basename(file_info['path'])

    with open(file_path, 'rb') as f:
        for chunk_index in range(total_chunks):
            chunk_data = f.read(chunk_size)

            files = {
                'chunk': (f'{filename}.part{chunk_index}', chunk_data),
            }
            data = {
                'filename': filename,
                'chunk_index': chunk_index,
                'total_chunks': total_chunks,
            }

            response = requests.post(API_URL + '/upload.php', files=files, data=data, timeout=120)

            if response.status_code != 200:
                raise requests.HTTPError(
                    f"Failed to upload chunk {chunk_index} for {file_info['path']}: {response.text}"
                )

    return 200, {"message": f"{filename} uploaded in {total_chunks} chunks."}

def get_files_list():
    """Get a list of files in the specified folder with their metadata."""
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
    """Sync files from the specified folder to the remote server in chunks."""
    print(">>> /sync endpoint hit")

    if not os.path.exists(FOLDER_PATH):
        return jsonify({'success': False, 'message': f'Folder {FOLDER_PATH} does not exist.'}), 404

    uploaded = []
    files = get_files_list()
    print(f">>> Found {len(files)} file(s) to upload")

    for file_info in files:
        print(f">>> Uploading {file_info['path']}")
        try:
            status_code, response = upload_file_in_chunks(file_info)
            uploaded.append({
                'path': file_info['path'],
                'status': status_code,
                'response': response
            })
            print(f">>> Done: {file_info['path']} - {status_code}")
        except (RequestException, OSError) as e:
            print(f">>> Error uploading {file_info['path']}: {e}")
            uploaded.append({'path': file_info['path'], 'status': 'error', 'response': str(e)})

    print(">>> Sync completed")

    return jsonify({'success': True, 'uploaded': uploaded})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
