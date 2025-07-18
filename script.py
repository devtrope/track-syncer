import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('TRACKBOX_API_URL')
FOLDER_PATH = os.getenv('TRACKBOX_FOLDER_PATH')

files = os.listdir(FOLDER_PATH)
for file in files:
    info = os.stat(os.path.join(FOLDER_PATH, file))
    print(info)

message = 'This is a test message.'
response = requests.post(
    API_URL,
    json={'message': message}
)
print(response.json())