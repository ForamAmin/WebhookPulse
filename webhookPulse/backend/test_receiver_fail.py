import requests


response = requests.post(
    "http://127.0.0.1:8000/test-receiver/fail",
    json={
        "event": "test.failure",
        "message": "intentional failure",
    },
)

print("Status:", response.status_code)
print("Response:", response.text)