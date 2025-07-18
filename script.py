import requests

response = requests.get('http://localhost:8084/index.php')
print(response.json())