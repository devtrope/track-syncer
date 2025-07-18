import requests
import os

files = os.listdir('/home/tod/Bureau/test')
for file in files:
    info = os.stat(f'/home/tod/Bureau/test/{file}')
    print(info)

#message = 'This is a test message.'
#response = requests.post(
#    'http://localhost:8084/index.php',
#    json={'message': message}
#)
#print(response.json())