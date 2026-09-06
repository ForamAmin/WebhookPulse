# This script simulates a webhook request to the backend server for testing purposes.
import hashlib
import hmac
import json
import requests

ENDPOINT_ID = "ep_M9z6731d_JcEYG_2Qacx0Q"
SIGNING_SECRET = "test-secret"

payload = {
    "event": "payment.captured",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_test_001",
                "amount": 50000,
                "currency": "INR",
            }
        }
    },
}

raw_body = json.dumps(payload, separators=(",", ":")).encode()

signature = hmac.new(
    SIGNING_SECRET.encode(),
    raw_body,
    hashlib.sha256,
).hexdigest()

url = f"http://127.0.0.1:8000/webhooks/{ENDPOINT_ID}"

response = requests.post(
    url,
    data=raw_body,
    headers={
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
        "X-Razorpay-Event-Id": "evt_provider_test_002",
    },
)

print("Status:", response.status_code)
print("Response:", response.text)

