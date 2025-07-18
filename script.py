import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('TRACKBOX_API_URL')
FOLDER_PATH = os.getenv('TRACKBOX_FOLDER_PATH')

for (root, dirs, files) in os.walk(FOLDER_PATH):
    for file in files:
        absolute_path = os.path.join(root, file)
        relative_path = os.path.relpath(absolute_path, FOLDER_PATH)
        print(f'File: {relative_path}')

files = os.listdir(FOLDER_PATH)
for file in files:
    info = os.stat(os.path.join(FOLDER_PATH, file))
    #print(info)

message = 'This is a test message.'
response = requests.post(
    API_URL,
    json={'message': message}
)
#print(response.json())