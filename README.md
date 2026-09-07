# WebhookPulse

> A provider-agnostic webhook reliability and observability layer built with FastAPI, Redis Streams, and MongoDB.

WebhookPulse sits inline between a webhook provider and your backend, adding signature verification, deduplication, fast acknowledgement, async delivery, retries with backoff, a dead-letter queue, replay, and structural schema-drift detection — so webhook failures are visible and recoverable instead of reconstructed from logs.

```
Provider → WebhookPulse → Redis Queue → Worker → Your Backend
                │
                ├── Signature verification
                ├── Idempotency / deduplication
                ├── Retry + backoff + jitter
                ├── Dead Letter Queue + Replay
                └── Event Intelligence (schema drift)
```

## Why

Webhooks are simple until: backends return 500s, go temporarily down, deliver duplicates, time out, or change payload shape without warning. WebhookPulse provides one pipeline for **Receive → Verify → Deduplicate → Queue → Deliver → Retry → Observe → Recover**, instead of every app reinventing it.

## Features

- **Multi-tenancy & Auth** — JWT-based, every record scoped to the authenticated tenant.
- **Ingestion & Signature Verification** — `POST /webhooks/{endpoint_id}`, provider-specific logic isolated in adapters.
- **Idempotency** — dedupes on provider event ID or a SHA-256 payload hash, enforced at the DB layer.
- **Async Delivery** — ingestion just persists + queues; a separate worker (Redis Streams) handles actual delivery.
- **Retry with Backoff + Jitter** — configurable max attempts, exponential delay.
- **Dead Letter Queue** — exhausted events are inspectable and manually replayable, not lost.
- **Event & Attempt History** — full lifecycle per event (status, retry count, correlation ID) and per delivery attempt (status code, response time/body, errors).
- **Event Intelligence** — maintains a reference payload shape per `user + provider + event type` and flags structural drift (field added/removed, type changes).

## Architecture

```
Webhook Provider → FastAPI (auth, endpoint resolution, signature check, idempotency)
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
           MongoDB            Redis Streams
    (events, attempts,        (queue + DLQ)
         users)                    │
                                   ▼
                                Worker
                         (retry, backoff, analysis)
                                   │
                                   ▼
                           Your Backend
```

## Tech Stack

| Layer | Tech |
|---|---|
| API | FastAPI |
| Queue | Redis Streams |
| Database | MongoDB |
| Auth | JWT + Argon2 password hashing |
| HTTP client | HTTPX |
| Frontend | Vanilla HTML/CSS/JS |
| Containerization | Docker |

## Experiments & Results

Tested against a baseline (no reliability layer) across HTTP 500s, timeouts, duplicate delivery, and backend downtime. Baseline re-delivers duplicates and loses recovery visibility; WebhookPulse dedupes, queues, retries, and recovers via DLQ.

A 30-event acknowledgement benchmark:

| Metric | Baseline | WebhookPulse |
|---|---|---|
| ACK success rate | 100% | 100% |
| Avg ACK latency | 80.22 ms | 263.50 ms |
| Median ACK latency | 78.43 ms | 248.46 ms |

Higher ACK latency is expected — WebhookPulse does signature verification, idempotency checks, and persistence before acknowledging. This project optimizes for **reliability and observability under failure**, not raw ACK speed. A separate recovery test confirmed an event that failed twice (500, 500) was retried and marked `delivered` on the third attempt.

## API Overview

```
POST /auth/register            POST /endpoints
POST /auth/login               GET  /endpoints
GET  /auth/me                  POST /webhooks/{endpoint_id}

GET  /events                   GET  /events/stats
GET  /events/{event_id}        POST /events/{event_id}/replay

GET  /health
```

## Local Development

**Prerequisites:** Python 3.12+, Docker, MongoDB, Redis

```bash
git clone <repository-url>
cd WebhookPulse

# Start Redis
docker run -d --name webhookpulse-redis -p 6379:6379 redis

# Configure webhookpulse/backend/.env
MONGO_URI=<your-mongodb-uri>
MONGO_DATABASE=webhookpulse
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=<your-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Install & run
cd webhookpulse/backend
python -m venv myenv && myenv\Scripts\activate   # Windows
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

API: `http://127.0.0.1:8000` · Docs: `http://127.0.0.1:8000/docs`

Run the worker process separately to consume events from Redis Streams.

## Project Structure

```
WebhookPulse/
├── webhookpulse/
│   ├── backend/src/{routes,controllers,services,repositories,providers,models,core,infrastructure}
│   └── frontend/
├── baseline/
├── experiment.md
└── README.md
```

## Design Decisions

- **Redis Streams** — lightweight persistent queue, decouples HTTP ingestion from background delivery, without Kafka-level infra.
- **MongoDB** — natural fit for semi-structured, provider-varying payloads and event/attempt history.
- **Provider Adapters** — signature schemes, event ID headers, and payload shapes differ per provider, so provider-specific logic is isolated behind adapters while the core pipeline stays provider-agnostic.

## Security

JWT auth, tenant-scoped authorization, Argon2 password hashing, provider signature verification, HTTPS in production, secrets via environment variables, no signature-bypass mode. Hosted deployments should only receive test data, not production payloads.

## Limitations

This is an MVP, not a commercial-platform clone:

- Single-node queue/worker, not load-tested
- In-process retry delay rather than a scheduled retry system
- Redis consumer-group recovery not yet implemented
- Schema intelligence is structural, not semantic
- DLQ replay is manual; no alerting integrations (Slack/PagerDuty)

## Future Work

Redis consumer groups, production-grade scheduled retries, transactional outbox for Mongo→Redis consistency, encrypted secrets, rate limiting, horizontal worker scaling, more provider adapters, semantic payload analysis, alerting integrations, configurable retention.

## License

Add your chosen license here.