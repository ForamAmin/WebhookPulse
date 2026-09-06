from fastapi import FastAPI
import uuid

from src.routes.auth_routes import router as auth_router
from src.routes.endpoint_routes import router as endpoint_router
from src.routes.webhook_routes import router as webhook_router


app = FastAPI(
    title="WebhookPulse",
    description="Provider-agnostic webhook reliability and observability platform",
    version="0.1.0",
)


app.include_router(auth_router)
app.include_router(endpoint_router)
app.include_router(webhook_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "webhookpulse",
    }