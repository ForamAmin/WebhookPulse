# WebhookPulse — Baseline

The `baseline` application is a simple direct webhook integration built before implementing WebhookPulse.

Its purpose is to provide a realistic control implementation that allows us to understand how a normal application behaves when it receives webhooks directly from an external provider.

The baseline intentionally keeps the architecture simple. It does not contain the reliability and observability mechanisms that WebhookPulse will later introduce.

---

## 1. Purpose

The baseline is designed to answer a fundamental question:

> What actually happens when an application receives webhooks directly from an external provider?

Instead of assuming that features such as queues, retries, deduplication, dead-letter queues, replay, and observability are necessary, the baseline first implements the simplest realistic direct integration.

The system can then be subjected to different webhook scenarios, and the resulting behavior can be observed and documented.

All experiment setups, observations, results, and conclusions are documented separately in the repository-level `experiment.md`.

---

## 2. Architecture

The baseline follows a simple direct integration model:

```text
┌─────────────────┐
│    Frontend     │
│    Mini Shop    │
└────────┬────────┘
         │
         │ Payment Request
         ▼
┌─────────────────┐
│    FastAPI      │
│     Backend     │
└────────┬────────┘
         │
         │ Payment Request
         ▼
┌──────────────────┐
│   MockGateway    │
│ Payment Simulator│
└────────┬─────────┘
         │
         │ Webhook
         ▼
┌─────────────────┐
│    FastAPI      │
│   /webhook      │
└─────────────────┘
```

The important characteristic of this architecture is that the payment gateway communicates directly with the backend.

There is no intermediate webhook reliability layer.

---

## 3. Project Structure

```text
baseline/
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── assets/
│       ├── images/
│       └── icons/
│
├── backend/
│   └── ...
│
└── README.md
```

---

## 4. Frontend

The frontend is a small shopping application used to generate realistic payment transactions.

It provides basic functionality such as:

- Product listing
- Add to cart
- Quantity modification
- Remove items
- Cart total
- Pay Now
- Payment processing state
- Payment success/failure state
- Order/payment status

The frontend is intentionally simple because its primary purpose is to generate payment activity that results in webhook events.

The frontend does not process WebhookPulse functionality and does not contain any retry, queue, dead-letter queue, replay, or webhook observability logic.

---

## 5. Frontend Technology

The frontend uses:

- HTML
- CSS
- Vanilla JavaScript

No frontend framework is required for the baseline.

---

## 6. Backend

The backend is implemented using FastAPI.

Its responsibilities include:

- Providing APIs for the frontend
- Initiating payment requests
- Communicating with the payment simulator
- Receiving webhook requests
- Verifying webhook authenticity where applicable
- Processing webhook events
- Recording or logging received events
- Updating the relevant payment or order state

The backend represents the type of application that would normally receive webhooks directly from an external provider.

---

## 7. Webhook Endpoint

The backend exposes a webhook endpoint:

```text
POST /webhook
```

The payment gateway sends webhook requests directly to this endpoint.

The basic webhook flow is:

```text
Payment Event Occurs
        ↓
Payment Gateway
        ↓
POST /webhook
        ↓
FastAPI Backend
        ↓
Verify / Process Event
        ↓
Update Application State
```

The webhook delivery is separate from the browser-based payment flow.

The frontend initiates the payment, but the webhook is delivered directly from the payment gateway to the backend.

---

## 8. Payment Flow

The complete baseline flow is:

```text
1. User opens the shopping frontend
        ↓
2. User adds products to the cart
        ↓
3. User clicks "Pay Now"
        ↓
4. Frontend communicates with the backend
        ↓
5. Backend initiates the payment
        ↓
6. MockGateway simulates the payment
        ↓
7. MockGateway sends a webhook to the backend
        ↓
8. Backend receives the webhook
        ↓
9. Backend verifies and processes the event
        ↓
10. Application state is updated
```

A key distinction is:

```text
Browser Payment Flow
        ≠
Server-to-Server Webhook Flow
```

The browser does not directly receive or process the server-to-server webhook.

---

## 9. MockGateway

The baseline uses MockGateway as a payment gateway simulator.

The simulator provides a controlled environment for generating payment events and delivering webhook requests to the backend without involving real financial transactions.

This allows the baseline to focus on webhook behavior rather than the complexity of integrating with a real payment provider from the beginning.

MockGateway is used only as the external event source. The webhook handling itself remains part of the baseline backend.

---

## 10. Why Use a Mock Gateway?

Using a payment simulator provides several advantages during the baseline stage:

- No real payments are involved
- Payment scenarios can be reproduced
- Webhook behavior can be tested safely
- Failure conditions can be intentionally triggered
- Development does not depend entirely on a real payment provider
- The focus remains on webhook delivery and processing

Once the baseline behavior is understood, the same reliability problems can be addressed by WebhookPulse.

---

## 11. What the Baseline Does Not Have

The baseline intentionally does not implement the features that WebhookPulse is designed to provide.

It does not contain:

- Redis Streams
- Message queues
- Asynchronous webhook processing
- Background workers
- Automatic retry mechanisms
- Exponential backoff
- Jitter
- Dead-letter queues
- Manual replay
- Webhook dashboard
- Event inspection
- Schema drift detection
- Anomaly detection
- Advanced idempotency handling
- Provider abstraction
- Distributed event-processing infrastructure

These capabilities belong to the WebhookPulse implementation.

Keeping them out of the baseline is important because the baseline acts as the control implementation for the project.

---

## 12. Webhook Scenarios

The baseline will be used to observe how a direct webhook integration behaves under different conditions.

The scenarios include:

### Successful Delivery

The backend is available and successfully processes the webhook.

This establishes the normal behavior of the system.

### Backend Returns 5xx

The webhook reaches the backend, but the backend intentionally returns an error.

This allows us to observe what happens when webhook processing fails.

### Slow Backend

The webhook endpoint intentionally takes longer to respond.

This allows us to observe the behavior of delayed responses and timeouts.

### Backend Unavailable

The backend is stopped or made unreachable.

This allows us to observe what happens when the provider cannot deliver the webhook.

### Duplicate Webhook

The same event is delivered more than once.

This allows us to observe the consequences of duplicate event delivery.

### Out-of-Order Events

Multiple events are delivered in an order different from the order in which they occurred.

This allows us to examine assumptions about webhook event ordering.

### Signature Verification

Webhook authenticity is tested using the provider's signing mechanism where applicable.

This demonstrates why webhook requests should not simply be trusted because they reached the endpoint.

### Payload Changes

The webhook payload structure is modified to simulate changes in the provider's event format.

This helps identify problems caused by tightly coupled webhook consumers.

---

## 13. Experiment Documentation

The baseline experiments are documented in a single file at the repository root:

```text
../experiment.md
```

The experiment document contains the actual:

- Experiment objectives
- Test setup
- Scenarios
- Expected behavior
- Observed behavior
- Results
- Evidence
- Problems discovered
- Engineering implications
- Mapping of observed problems to WebhookPulse features

The results are intentionally kept separate from this README so that this document describes the baseline system itself, while `experiment.md` records what was actually observed during testing.

---

## 14. Baseline to WebhookPulse

The baseline establishes the direct integration that WebhookPulse will improve upon.

Conceptually:

```text
                 BASELINE

Provider
   │
   │ Webhook
   ▼
Backend
   │
   └── Direct Processing
```

The experiments performed on this architecture are expected to expose reliability and observability problems such as:

- Delivery failures
- Slow processing
- Duplicate events
- Temporary backend unavailability
- Retry uncertainty
- Lack of replay capability
- Limited visibility into webhook processing
- Payload changes

WebhookPulse introduces an intermediate reliability layer:

```text
                WEBHOOKPULSE

Provider
   │
   ▼
WebhookPulse
   │
   ├── Verify
   ├── Deduplicate
   ├── Correlate
   ├── Enqueue
   └── Acknowledge
          │
          ▼
       Worker
          │
          ├── Retry
          ├── Backoff
          ├── DLQ
          └── Replay
          │
          ▼
   Customer Backend
```

The baseline therefore provides the practical foundation for deciding which WebhookPulse features are actually necessary.

---

## 15. Provider-Agnostic Goal

Although the baseline may initially use a Razorpay-like payment simulation, WebhookPulse is not intended to be tied to a single provider.

The final system should be capable of supporting webhook-producing providers such as:

- GitHub
- Razorpay
- Stripe
- PayPal
- Other webhook providers

Different providers may use different webhook formats and authentication or signature-verification mechanisms.

Therefore, provider-specific verification belongs at the edge of WebhookPulse.

After verification, the incoming event can be converted into a common event representation that is processed by the same downstream pipeline.

Conceptually:

```text
GitHub ────────┐
Razorpay ──────┤
Stripe ────────┤
PayPal ────────┤
Other ─────────┘
       │
       ▼
Provider-Specific
Verification / Adapter
       │
       ▼
Common Event Envelope
       │
       ▼
Same WebhookPulse Pipeline
```

The goal is to keep the core processing pipeline provider-agnostic.

Adding support for a new provider should primarily require a provider-specific adapter or configuration at the edge rather than rewriting the core webhook-processing system.

---

## 16. Engineering Philosophy

The baseline follows a simple engineering principle:

> Understand the problem before building the solution.

Rather than immediately introducing queues, retries, distributed workers, and observability mechanisms, the project first implements the simplest direct integration.

The system is then tested under different webhook conditions.

Each WebhookPulse feature should have a clear engineering reason behind it.

The baseline therefore serves as the control system from which the reliability requirements of WebhookPulse can be derived.

---

## 17. Running the Baseline

The exact setup and run instructions will be added as the implementation is completed.

At a high level, the process is:

```text
1. Start the FastAPI backend
2. Start the frontend
3. Start/configure MockGateway
4. Configure the webhook destination
5. Perform a test payment
6. Verify that the webhook reaches the backend
7. Record the result
8. Repeat using the defined failure scenarios
```

---

## 18. Definition of Done

The baseline is considered complete when:

- [ ] The frontend shopping flow works
- [ ] Products can be added to the cart
- [ ] Cart quantities can be modified
- [ ] Products can be removed
- [ ] A payment can be initiated
- [ ] The backend communicates with MockGateway
- [ ] Payment events can be generated
- [ ] The webhook endpoint is available
- [ ] The backend can receive webhook events
- [ ] Webhook authenticity can be verified where applicable
- [ ] Webhook events can be recorded or logged
- [ ] Successful webhook delivery can be demonstrated
- [ ] Failure scenarios can be reproduced
- [ ] Results are documented in `../experiment.md`

---

## 19. Relationship to the Main Project

The baseline is not the final WebhookPulse product.

It is the first stage of the project:

```text
Stage 1
   │
   ▼
Build Direct Integration
   │
   ▼
Observe Webhook Behavior
   │
   ▼
Document Failures
   │
   ▼
Identify Reliability Problems
   │
   ▼
Stage 2
   │
   ▼
Build WebhookPulse
   │
   ▼
Introduce Reliability Mechanisms
   │
   ▼
Repeat Relevant Scenarios
   │
   ▼
Compare Results
```

This approach ensures that WebhookPulse is designed around observed engineering problems rather than being a collection of distributed-systems features added without a concrete purpose.

---

## Final Principle

> Do not build the solution before understanding the problem.

The baseline exists to establish what happens when webhooks are delivered directly to a backend.

The observations from this system form the foundation for the architecture and feature decisions of WebhookPulse.
