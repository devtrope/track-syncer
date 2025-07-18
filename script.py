import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

API_URL = os.getenv('TRACKBOX_API_URL')
FOLDER_PATH = os.getenv('TRACKBOX_FOLDER_PATH')
ACCEPTED_EXTENSIONS = ['.mp3', '.wav']

files_infos = []

if not os.path.exists(FOLDER_PATH):
    raise Exception(f"Folder {FOLDER_PATH} does not exist.")

for (root, dirs, files) in os.walk(FOLDER_PATH):
    for file in files:
        if not any(file.endswith(ext) for ext in ACCEPTED_EXTENSIONS):
            continue

        absolute_path = os.path.join(root, file)
        relative_path = os.path.relpath(absolute_path, FOLDER_PATH)
        stat = os.stat(absolute_path)

        file_info = {
            'path': relative_path,
            'size_bytes': stat.st_size,
            'modified_ts': stat.st_mtime,
            'modified_iso': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(stat.st_mtime)),  # ISO forma
        }

        files_infos.append(file_info)

print(files_infos)

message = 'This is a test message.'
response = requests.post(
    API_URL,
    json={'message': message}
)
#print(response.json())