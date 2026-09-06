from fastapi import FastAPI

from src.routes.auth_routes import router as auth_router


app = FastAPI(
    title="WebhookPulse",
    description="Provider-agnostic webhook reliability and observability platform",
    version="0.1.0",
)


app.include_router(auth_router)


@app.get("/health")
def health():
    return {
        "status": "running webhookPulse backend / healthy !",
        "service": "webhookpulse",
    }