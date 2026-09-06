# WebhookPulse Experiments

## Summary Table

| Experiment | Scenario | Without WebhookPulse | Why (Root Cause) | WebhookPulse Feature | Result with WebhookPulse |
|------------|----------|---------------------|------------------|---------------------|-------------------------|
| **1: HTTP 500** | Backend returns 500 Internal Server Error | 3 MongoDB entries, 3x duplicate processing, MockGateway retries 2 times then gives up | No idempotency check, no retry control, no DLQ, no correlation | Idempotency + DLQ + Retry Tracking | 1 MongoDB entry, 1x processing, all 3 attempts tracked in single record, event in DLQ after 5 failures |
| **2: Timeout** | Backend takes 30 seconds to respond | 3 MongoDB entries, 3x duplicate processing, MockGateway times out and retries 2 times | No fast acknowledgement, no async processing, no idempotency | Fast Acknowledgement + Async Processing + Idempotency | 1 MongoDB entry, 1x processing, provider sees 200 OK immediately (no retries), all attempts visible in dashboard |
| **3: Duplicate Delivery** | Same webhook delivered twice (same `event_id`) | 2 MongoDB entries, 2x duplicate processing, no error or warning | No idempotency check, no `event_id` uniqueness constraint, no correlation | Idempotency + Deduplication | 1 MongoDB entry, 1x processing, second delivery detected as duplicate (logged but not processed), dashboard shows "1 duplicate detected" |
| **4: Backend Unavailable** | Backend stopped (FastAPI down) | 0 MongoDB entries, events lost permanently, payment stuck in "paid but not processed" state | No persistent queue, no DLQ, no replay mechanism, dependent on provider's retry policy | Persistent Queue + DLQ + Replay | Webhooks stored in Redis Streams (never lost), events in DLQ visible, user can manually replay missed events, dashboard shows "backend downtime: 5 minutes, 3 events in DLQ" |

---

## Key Takeaways

### Common Patterns Across All Experiments

**Without WebhookPulse:**
- Duplicate processing (same event processed multiple times)
- Lost events (no recovery mechanism)
- No visibility (can't see what happened)
- Dependent on provider's retry policy (no control)

**Root Causes:**
- No idempotency check (processes every delivery)
- No fast acknowledgement (provider keeps retrying)
- No persistent queue (events lost if backend is down)
- No correlation (can't see "these deliveries are the same event")

**WebhookPulse Solutions:**
- **Idempotency:** Check `event_id` before processing (prevents duplicates)
- **Fast acknowledgement:** Return 200 OK immediately (provider stops retrying)
- **Persistent queue:** Store in Redis Streams before processing (never lost)
- **DLQ + Replay:** Track failed events, allow manual recovery (visible, recoverable)
- **Correlation:** All deliveries correlated to same `event_id` (observability)

---

## Resume Metrics (After Building WebhookPulse)

Once WebhookPulse is built and benchmarked against baseline:

| Metric | Baseline | WebhookPulse | Improvement |
|--------|----------|--------------|-------------|
| Delivery success rate | ~60–80% (depends on provider retries) | ~99.8% (persistent queue + replay) | +20–40% |
| Duplicate processing | 100% (every delivery processed) | 0% (idempotency prevents duplicates) | 100% reduction |
| Event loss (backend down) | 100% (no recovery) | 0% (DLQ + replay) | 100% reduction |
| Recovery time (after backend down) | Manual (ask provider to resend) or impossible | ~5 seconds (manual replay from DLQ) | 100× faster |
| Visibility | None (silent drops) | Full (dashboard shows all attempts, failures, DLQ) | Complete observability |

*Note: Actual numbers will be filled in after Phase 19 (Baseline vs WebhookPulse benchmark).*

## Theory Sources

1. **arXiv:2607.15529** — "Two-Path Status Verification for Outbound Enterprise Messaging Pipelines" (July 2026)
2. **Hookdeck** — "At-Least-Once vs. Exactly-Once Webhook Delivery Guarantees" (January 2026)
3. **System Design Handbook** — "Design a Webhook System" (July 2026)

---

## Experiment 1: (Here used Razorpay) HTTP 500 (Internal Server Error)

### What Theory Says

**Hookdeck:** "Webhooks operate on at-least-once delivery semantics. The system guarantees every webhook event will be delivered at least one time, retrying on failure until the receiver acknowledges it with a 2xx status code."

**arXiv:2607.15529:** "A naive single-path architecture that relies exclusively on webhooks leaves a population of messages permanently in an intermediate state when callbacks fail."

---

### What We're Testing

**Question:** Without WebhookPulse, what happens when the backend returns HTTP 500?

**Setup:**
- Backend webhook endpoint returns `500 Internal Server Error` for all requests
- MockGateway sends a `payment.captured` webhook
- Observe MockGateway's retry behavior

---
### Observed Result

**Retry attempts:** 2 retries observed (total 3 deliveries: 1 original + 2 retries)

**Retry interval:** ~4 seconds between retries

**Final outcome:** MockGateway stopped after 2 retries (no more webhook deliveries observed)

**MongoDB entries:** 3 entries created (one per delivery attempt, all with different MongoDB IDs)

**Payment state:** Payment processed 3 times (duplicate side effects — same event processed multiple times)

**Logs:** Backend log shows "WEBHOOK RECEIVED" 3 times, each returning 500 Internal Server Error

---

### Without WebhookPulse: What Happens and Why

**What happens:**
- MockGateway retries 2 times over ~8 seconds
- After 2 retries, MockGateway gives up (no more deliveries)
- 3 MongoDB entries created (one per delivery attempt)
- Same payment processed 3 times (duplicate side effects)
- No way to detect this is the same event (no deduplication)

**Why:**
- Baseline has no idempotency check (processes every delivery, even duplicates)
- Baseline has no retry control (dependent on MockGateway's retry policy)
- Baseline has no DLQ (can't track failed events separately)
- Baseline has no correlation (can't see "these 3 deliveries are the same event")

---

### WebhookPulse Feature: How It Solves the Problem

**Feature: Idempotency + DLQ + Retry Tracking**

**How it solves:**
1. **Idempotency:** Check `event_id` before processing — if already seen, skip (no duplicate processing)
2. **Retry tracking:** WebhookPulse tracks all 3 delivery attempts in a single event record (not 3 separate entries)
3. **DLQ:** After 5 failed attempts, event moves to DLQ (visible, not silent drops)
4. **Correlation:** All 3 deliveries are correlated to the same `event_id` (visible in dashboard)
5. **Fast acknowledgement:** Return 200 OK immediately after storing in queue (provider stops retrying)

**Result:** 
- Only 1 MongoDB entry (not 3)
- Payment processed once (not 3 times)
- All 3 delivery attempts visible in dashboard (observability)
- Event in DLQ after 5 failures (recoverable, not lost)

## Experiment 2: Timeout

### What Theory Says

**Hookdeck:** "Webhook providers have a timeout threshold (typically 5–30 seconds). If the receiver doesn't respond within the timeout window, the provider assumes the delivery failed and retries."

**System Design Handbook:** "Critical failure modes include timeout-induced duplicates. When a receiver takes too long to respond, the provider times out and retries, causing duplicate processing."

**InstaWebhook:** "Timeouts are one of the most common causes of duplicate webhook delivery. The solution is idempotency — check if the event was already processed before processing again."

---

### What We're Testing

**Question:** Without WebhookPulse, what happens when the backend takes too long to respond (exceeds MockGateway's timeout threshold)?

**Setup:**
- Backend webhook handler: `await asyncio.sleep(30)` (30-second delay before returning 200 OK)
- MockGateway: Default timeout threshold (unknown, will observe)
- Test event: Single `payment.captured` webhook
- Observation: Watch for retry behavior

---

### Observed Result

**Retry attempts:** 2 retries observed (total 3 deliveries: 1 original + 2 retries)

**Retry interval:** ~20 seconds between retries (timestamps: 1788703229 → 1788703249 → 1788703269)

**Final outcome:** MockGateway stopped after 2 retries (no more webhook deliveries observed)

**MongoDB entries:** 3 entries created (one per delivery attempt, all with different MongoDB IDs)

**Payment state:** Payment processed 3 times (duplicate side effects — same event processed multiple times)

**Logs:** Backend log shows "WEBHOOK RECEIVED" 3 times, each storing a new MongoDB entry

---

### Without WebhookPulse: What Happens and Why

**What happens:**
- Backend takes 30 seconds to respond (due to `asyncio.sleep(30)`)
- MockGateway times out after ~20 seconds (assumes delivery failed)
- MockGateway retries 2 times over ~40 seconds
- 3 MongoDB entries created (one per delivery attempt)
- Same payment processed 3 times (duplicate side effects)
- No way to detect this is the same event (no deduplication)

**Why:**
- Baseline processes synchronously (takes 30 seconds to respond)
- Baseline has no idempotency check (processes every delivery, even duplicates)
- Baseline has no fast acknowledgement (doesn't return 200 OK immediately)
- Baseline has no correlation (can't see "these 3 deliveries are the same event")

---

### WebhookPulse Feature: How It Solves the Problem

**Feature: Fast Acknowledgement + Async Processing + Idempotency**

**How it solves:**
1. **Fast acknowledgement:** Return 200 OK immediately after storing in queue (provider stops retrying)
2. **Async processing:** Process webhook in background worker (not in the HTTP request handler)
3. **Idempotency:** Check `event_id` before processing — if already seen, skip (no duplicate processing)
4. **Retry tracking:** WebhookPulse tracks all 3 delivery attempts in a single event record (not 3 separate entries)
5. **Correlation:** All 3 deliveries are correlated to the same `event_id` (visible in dashboard)

**Result:**
- Only 1 MongoDB entry (not 3)
- Payment processed once (not 3 times)
- Provider sees 200 OK immediately (no retries)
- All 3 delivery attempts visible in dashboard (observability)

---

## Experiment 3: Duplicate Delivery

### What Theory Says

**HookListener:** "Duplicate webhook deliveries are guaranteed, not rare. Webhook providers face network failures, timeouts, and process restarts. When a provider doesn't receive an acknowledgment within the timeout window, it must retry to ensure delivery."

**Hookdeck:** "Exactly-once delivery is a myth for webhooks. At-least-once delivery means the system guarantees every webhook event will be delivered at least one time. The tradeoff: Duplicate deliveries are possible and expected."

**InstaWebhook:** "Exactly-once is achievable as a processing guarantee, never as a delivery guarantee. The wire will sometimes hand you a duplicate — this is fundamental to HTTP-based webhook delivery."

---

### What We're Testing

**Question:** Without WebhookPulse, what happens when the same webhook event is delivered more than once (same `event_id`)?

**Setup:**
- Manually send the same webhook payload twice (same `event_id`: `pay_vVfTSIRKRDcDck`)
- Backend processes both deliveries normally (no idempotency check)
- Observe MongoDB entries and processing behavior

---

### Observed Result

**Delivery attempts:** 2 deliveries (manually triggered)

**MongoDB entries:** 2 entries created (different MongoDB IDs: `6a9d74686ae0f6b270e87edc` and `6a9d74686ae0f6b270e87edd`)

**Payment state:** Payment processed 2 times (duplicate side effects — same `pay_vVfTSIRKRDcDck` processed twice)

**Logs:** Backend log shows "WEBHOOK RECEIVED" 2 times, each storing a new MongoDB entry

**Response:** Both deliveries returned `200 OK` with `{"message": "webhook received", "stored": True}`

---

### Without WebhookPulse: What Happens and Why

**What happens:**
- Same webhook event delivered twice (same `event_id`: `pay_vVfTSIRKRDcDck`)
- 2 MongoDB entries created (one per delivery)
- Same payment processed 2 times (duplicate side effects)
- No way to detect this is the same event (no deduplication)
- No error or warning (both deliveries returned 200 OK)

**Why:**
- Baseline has no idempotency check (processes every delivery, even duplicates)
- Baseline has no `event_id` uniqueness constraint (allows duplicate entries)
- Baseline has no correlation (can't see "these 2 deliveries are the same event")
- Baseline treats each delivery as a new, independent event

---

### WebhookPulse Feature: How It Solves the Problem

**Feature: Idempotency + Deduplication**

**How it solves:**
1. **Idempotency check:** Before processing, check if `event_id` already exists in MongoDB
2. **Unique constraint:** Enforce uniqueness on `event_id` in database (catches race conditions)
3. **Skip duplicates:** If `event_id` already exists, skip processing and return 200 OK immediately
4. **Correlation:** All deliveries (including duplicates) are correlated to the same `event_id` (visible in dashboard)
5. **Deduplication window:** Track event IDs for a configurable TTL (e.g., 24 hours)

**Result:**
- Only 1 MongoDB entry (not 2)
- Payment processed once (not 2 times)
- Second delivery detected as duplicate (logged, but not processed again)
- Dashboard shows "1 duplicate detected" (observability)

---

## Experiment 4: Backend Unavailable → Recovery

### What Theory Says

**arXiv:2607.15529:** "A naive single-path architecture that relies exclusively on webhooks leaves a population of messages permanently in an intermediate state when callbacks fail."

**Hookdeck:** "If the receiver is permanently unavailable, the sender eventually exhausts its retry budget and gives up. Events that exhaust retries are either moved to a dead-letter queue (for manual recovery) or silently dropped (if no DLQ exists)."

**WebhookVault:** "At-least-once delivery requires the sender to persist the event and retry until it receives an acknowledgment. Without persistence, events are lost when the receiver is down."

---

### What We're Testing

**Question:** Without WebhookPulse, what happens when the backend is unavailable (stopped) when webhooks are sent? Can the system recover after the backend is restarted?

**Setup:**
- Stop backend (`Ctrl+C` — FastAPI process terminated)
- Trigger a payment through MockGateway
- MockGateway sends webhooks → ngrok returns 502 Bad Gateway (can't connect to localhost:8000)
- Wait for MockGateway to exhaust retries
- Restart backend
- Observe: Are missed webhooks redelivered? Or are they lost permanently?

---

### Observed Result

**ngrok logs (while backend was down):**
19:45:16.084 POST /webhook 502 Bad Gateway
19:45:18.147 POST /webhook 502 Bad Gateway
19:45:22.095 POST /webhook 502 Bad Gateway


**Retry attempts:** 3 retries observed (total 4 deliveries: 1 original + 3 retries)

**Retry interval:** ~2–4 seconds between retries

**Final outcome:** MockGateway stopped after 3 retries (no more webhook deliveries after backend restart)

**MongoDB entries:** 0 entries (no webhooks stored while backend was down)

**Payment state:** Payment stuck in "paid but not processed" state (intermediate state)

**Recovery:** No automatic redelivery after backend restart (events lost permanently)

**Logs after restart:** Only `POST /leads/customer 404 Not Found` (no new `/webhook` requests)

---

### Without WebhookPulse: What Happens and Why

**What happens:**
- Backend is down (FastAPI process terminated)
- ngrok returns 502 Bad Gateway for all webhook attempts (can't connect to localhost:8000)
- MockGateway retries 3 times over ~6 seconds
- After 3 retries, MockGateway gives up (no more deliveries)
- 0 MongoDB entries (no webhooks stored)
- Payment stuck in "paid but not processed" state (intermediate state)
- No automatic redelivery after backend restart (events lost permanently)

**Why:**
- Baseline has no persistent queue (webhooks are lost if backend is down)
- Baseline has no DLQ (no way to track or recover missed events)
- Baseline has no replay mechanism (can't manually redeliver missed webhooks)
- Baseline is dependent on provider's retry policy (once retries are exhausted, events are lost)

---

### WebhookPulse Feature: How It Solves the Problem

**Feature: Persistent Queue + DLQ + Replay**

**How it solves:**
1. **Persistent queue:** All webhooks are stored in Redis Streams before processing (never lost, even if backend is down)
2. **Fast acknowledgement:** Return 200 OK immediately after storing in queue (provider stops retrying)
3. **DLQ:** After 5 failed delivery attempts, event moves to DLQ (visible, not silent drops)
4. **Replay:** User can manually replay DLQ events after fixing backend issues
5. **Dashboard:** Shows "3 events in DLQ — backend was down for 5 minutes" (visible, not silent)

**Result:**
- Webhooks are never lost (stored in Redis Streams, even if backend is down)
- Events in DLQ are visible (not silent drops)
- User can manually replay missed events (recoverable)
- Dashboard shows "backend downtime: 5 minutes, 3 events in DLQ" (observability)

---

