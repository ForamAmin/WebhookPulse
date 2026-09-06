# WebhookPulse — Final Build Spec

> Status: architecture locked. This supersedes earlier drafts — specifically, treat §4 (feature set) and the auth/multi-tenancy decision below as the source of truth, overriding any earlier note that called multi-tenancy "cut."

---

## 1. Problem Statement

When a webhook event fails, gets delayed, arrives twice, or its payload shape changes unexpectedly, a developer has no single place to see what happened to that event across its lifecycle — they reconstruct it by hand from provider dashboards, app logs, and DB state.

## 2. What WebhookPulse Is

A reliability and observability layer sitting **inline** between a provider and the user's backend:

```
Provider (Stripe/GitHubtc.) → WebhookPulse → User's Backend
```

Inline, not sidecar — deliberate trade-off: simpler to build/demo, and justified because self-hosting (see §5) already answers the trust question a sidecar would otherwise solve. Accepted cost: if WebhookPulse is down, the backend gets nothing, so retry/DLQ logic must be solid — there's no fallback path.

## 3. Access Model (Locked)

Two tiers only. No seedless public showcase, no forked logic.

| Tier | How | Data location |
|---|---|---|
| 1. Self-hosted | `git clone` → `docker-compose up` | User's own infra, never leaves it |
| 2. Hosted | Sign in on your deployed instance | Your infra — explicitly "no sensitive/production traffic" |

**Single-codebase rule:** the app is *always* authenticated and *always* multi-tenant. Self-host just means the user is tenant #1 on their own machine — same code, same schema, same ingestion-per-user-token logic. No `if SELF_HOSTED: skip_auth()` branch, ever. The only difference between tiers is `.env` config (DB/Redis connection strings), never code.

This makes auth + multi-tenant data isolation a **foundational feature**, not optional scope — it gates everything else and is built first.

## 4. Core Feature Set (5 things, each earns its place)

1. **Auth + multi-tenancy** — user accounts, per-user ingestion URL (`/incoming/{user_token}`), every record scoped by `user_id`. *(Foundational — nothing else works without this now.)*
2. **Ingestion + signature verification** — HMAC check against provider secret before accepting anything.
3. **Idempotency** — dedupe on provider event ID / content hash before queueing.
4. **Async queue + retry (exponential backoff + jitter) + DLQ** — sub-second ack to provider, real processing happens off the request path; failures isolated and recoverable, not lost.
5. **Event Intelligence** — schema-drift detection (structural fingerprint per user+provider+event-type), event diff viewer, anomaly scoring. This is the differentiator.

**Explicitly cut:** conditional routing, payload transformation, alerting integrations (Slack/PagerDuty), auto-replay-on-fix. Named as "future work" in the README, not built.

## 5. Security Posture

- Self-hosted data never touches your infra — removes the "why should I trust you with my payload" objection at the root.
- Hosted tier: explicit "test data only" framing, short payload retention (24–72h), metadata kept longer than raw payloads.
- HTTPS only, secrets in env vars, signature verification with no bypass mode (even in tests — use test-mode secrets).

## 6. Event Flow (end to end)

```
1. Provider POSTs → WebhookPulse ingress (/incoming/{user_token})
2. Signature verified → fail: 401, log, do not queue
3. Idempotency check → duplicate: ack 200, skip reprocessing
4. Accepted → correlation ID assigned → written to queue
   → 200 returned to provider HERE (fast ack)
5. Worker pulls event off queue
6. Event Intelligence pass: compare structure to stored fingerprint
   for this user+provider+event-type → flag drift/anomalies
7. Worker forwards to user's configured backend URL
   → success: mark complete
   → failure: retry with backoff+jitter, re-queue
8. Retries exhausted → move to DLQ
9. DLQ events: inspectable, diffable, manually replayable
```

Every event's correlation ID threads through steps 4–9, giving the timeline view for free — it's a state machine with timestamps, not a separate subsystem.

## 7. Data Model

- **users** — id, email, auth credentials, ingestion token
- **events** — id, user_id, correlation_id, provider, event_type, raw_payload, status, retry_count, created_at
- **event_analysis** — event_id, checks (JSON), anomalies (JSON)
- **provider_schemas** — user_id, provider, event_type, reference_shape (field→type map), updated_at

`provider_schemas` is the least-discussed but most important table — it's what schema-diff compares against. **[DECIDE]**: lock the reference shape from the first N events, or maintain a rolling consensus shape as new events arrive. Pick one before building §4.5.

## 8. Stack

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI | Async-native, fits fast-ack requirement, Pydantic aids schema comparison |
| Queue | Redis (Streams) | Real distributed-systems pattern without Kafka-level overhead |
| Store | MongoDB | Semi-structured payloads, natural fit for structural diffing |
| Frontend | Vanilla HTML/CSS/JS | UI surface is small (timeline, DLQ list, diff view) — no framework needed |
| Containerization | Docker / docker-compose | Same compose file for local dev, self-host, and prod deploy |

## 9. Deployment (all free tier)

- Backend (FastAPI + worker): **Render** free web service
- Queue: **Upstash** Redis (no cold-start, unlike Render's free Redis)
- DB: **MongoDB Atlas M0** (free forever, 512MB)
- Frontend: **Vercel/Netlify** static hosting
- Note: free backend spins down after 15 min idle — ping it before a demo/interview

## 10. Build Phases (execute in this order)

**Phase 0 — Foundations**
- Repo scaffold, docker-compose skeleton (FastAPI + Redis + Mongo stubs)
- Decide provider_schemas strategy (§7 [DECIDE])

**Phase 1 — Auth & Multi-tenancy**
- User model, sign-up/login, per-user ingestion token/URL
- This unlocks both access tiers simultaneously — nothing later is tenant-unaware

**Phase 2 — Ingestion**
- `/incoming/{user_token}` endpoint, signature verification, idempotency check, correlation ID assignment, fast-ack

**Phase 3 — Queue + Reliability**
- Redis Streams integration, worker pool, exponential backoff + jitter retry, DLQ collection

**Phase 4 — Event Intelligence**
- Structural fingerprint storage/update logic, diff algorithm (recursive key/type comparison), anomaly scoring, diff viewer data shape

**Phase 5 — Dashboard**
- Vanilla JS frontend: event timeline (per logged-in user), DLQ list with replay button, side-by-side diff view

**Phase 6 — Deploy + Demo**
- Deploy per §9, seed hosted instance with realistic test data
- Record 2–3 min demo: ingestion → simulated failure → backoff → DLQ → schema-drift catch → replay
- Write README: problem, architecture, honest limitations (§11), both access tiers explained

## 11. Limitations (state these explicitly in the README)

- Single-node queue/worker — design could scale (stateless workers, shared queue) but isn't load-tested
- Schema-drift is structural only (type/field presence), not semantic
- DLQ replay is manual-trigger in v1
- No alerting integrations in v1

## 12. Resume Framing

> WebhookPulse — A webhook reliability and observability layer with multi-tenant self-host/hosted deployment, demonstrating async ingestion, signature verification, exponential-backoff retries, dead-letter queues with replay, and schema-drift detection ("Event Intelligence"). Built with FastAPI, Redis, and MongoDB.

Avoid "replaces Hookdeck" — the honest pitch is "built minimal, working versions of the same core distributed-systems patterns those tools rely on, plus one differentiator they don't emphasize."

---

## Open Decisions Before Coding
- [ ] provider_schemas fingerprint strategy: snapshot-first-N vs rolling consensus
- [ ] Exact demo provider(s): Stripe test webhooks recommended first
- [ ] Diff algorithm edge cases: nested objects, arrays — define comparison depth
  
## Related Work

Webhook reliability patterns are well-documented in industry guides and academic literature:

- **arXiv:2607.15529** (2026): Two-Path Status Verification for messaging pipelines [147]
- **arXiv:2608.00783** (2026): Safety invariants for agent orchestration, including duplicate webhook delivery [148]
- **InvokeBot** (2026): Webhook Reliability Patterns — 20+ patterns for production systems [149]
- **HookListener** (2026): State of Webhooks 2025–2026 — best practices for provider abstraction, idempotency, async processing [155]

This project does not claim novelty in the reliability patterns themselves.

The goal is **pedagogical**: to understand these patterns by first experiencing the failure modes through baseline experiments, then implementing the solutions.

This approach follows classic engineering education patterns (e.g., implementing TCP to understand networking, building a database to understand ACID).