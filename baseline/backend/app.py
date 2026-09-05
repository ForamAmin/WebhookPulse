from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import json
from datetime import datetime, timezone

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

#Connect to mongodb :
client = MongoClient(MONGODB_URI)

db = client["webhookpulse_baseline"]
webhook_events = db["webhook_events"]

client.admin.command("ping")

print("MongoDB connected successfully!")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MockGateway (Razorpay simulation) credentials and base URL
BASE_URL = "https://mockgateway.com/api/base/razorpay-qhez1i"
USERNAME = "rzp_test_ce8dg8vJOuaX8a"
KEY_SECRET = "JeWY3svcs3ajLQz8gydE"


@app.get("/")
def hello():
    return {"message": "backend working"}


# for talking to mockgateway
@app.post("/create-payment")
async def create_payment(request: Request):
    body = await request.json()
    amount = body.get("amount")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/payment_links",
            auth=(USERNAME, KEY_SECRET),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json={
                "amount": amount,
                "currency": "INR",
                "return_url": "http://127.0.0.1:3000/baseline/frontend/index.html",
            },
        )

    data = response.json()
    print("MockGateway response:", response.status_code, data)  # debug visibility

    if response.status_code >= 400 or not data.get("short_url"):
        return {
            "message": "payment creation failed",
            "mockgateway_status": response.status_code,
            "mockgateway_response": data,
        }

    return {
        "message": "payment created",
        "payment_id": data.get("id"),
        "redirect_url": data.get("short_url"),  # send the buyer straight to MockGateway's real hosted page
    }


# for receiving the event from MockGateway.
# This URL must be registered in MockGateway's dashboard under
# Webhooks > Configurations, using a publicly reachable address
# (e.g. an ngrok tunnel to this local server) - MockGateway cannot
# reach "127.0.0.1" since it's a real internet-hosted service.
@app.post("/webhook")
async def webhook(request: Request):

    # Capture the raw request body
    raw_body = await request.body()

    # Capture headers
    headers = dict(request.headers)

    # Try to identify the provider from recognizable headers
    provider = "unknown"

    if "x-github-event" in headers:
        provider = "github"
    elif "x-razorpay-signature" in headers:
        provider = "razorpay"
    elif "stripe-signature" in headers:
        provider = "stripe"

    # Try to parse JSON
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        payload = None

    # Determine event type when possible
    event_type = None

    if provider == "github":
        event_type = headers.get("x-github-event")

    elif isinstance(payload, dict):
        event_type = (
            payload.get("event")
            or payload.get("event_type")
            or payload.get("type")
        )

    # Store the webhook
    webhook_document = {
        "received_at": datetime.now(timezone.utc),
        "provider": provider,
        "event_type": event_type,

        "request": {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "source_ip": request.client.host if request.client else None,
            "headers": headers
        },

        "raw_body": raw_body.decode("utf-8", errors="replace"),

        "payload": payload
    }

    result = webhook_events.insert_one(webhook_document)

    print("WEBHOOK RECEIVED")
    print("Provider:", provider)
    print("Event type:", event_type)
    print("Stored MongoDB ID:", result.inserted_id)

    return {
        "message": "webhook received",
        "stored": True
    }