import requests

message = 'This is a test message.'
response = requests.post(
    'http://localhost:8084/index.php',
    json={'message': message}
)
print(response.json())