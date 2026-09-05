from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

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
    event = await request.json()
    print("Payment done:", event)
    return {"message": "webhook received"}