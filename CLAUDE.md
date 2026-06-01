# CLAUDE.md

## Project Overview

This project is an AI-powered cinema assistant built with FastAPI and LLM orchestration.

The goal is to learn and experiment with modern AI engineering concepts in a realistic but small-scale product, inspired by real-world customer support AI systems.

Users interact with the system using natural language:

- "What movies are playing tonight?"
- "How much is the IMAX ticket for Dune?"
- "Is the movie in English?"
- "What are tomorrow's sessions for Interstellar?"

The assistant can:

- answer questions
- retrieve cinema information
- use tools/functions
- query internal knowledge
- eventually use RAG and evals

---

# Main Goals

The project is focused on learning:

- FastAPI
- Python backend architecture
- LLM orchestration
- Tool/function calling
- Structured outputs
- RAG pipelines
- AI evals and observability

This is NOT a production-grade app.

The priority is:
1. clarity
2. iteration speed
3. understanding AI engineering primitives

---

# Architecture Philosophy

Keep the project:
- small
- explicit
- understandable
- modular

Avoid unnecessary abstractions and frameworks early on.

Do NOT introduce:
- LangChain
- multi-agent systems
- microservices
- complex infra
- premature optimization

The purpose is learning core concepts first.

## Hexagonal architecture

Another goal for this project is to learn about Hexagonal architecture using FastApi.

Use this architecture, and explain every decision.

The user has to learn about hexagonal architecture concepts (domain, application, infrastructure, etc).

---

# Planned Iterations

## V1 — Basic Chat

- FastAPI setup
- `/chat` endpoint
- LLM API integration
- simple conversational responses

Example flow:

User → FastAPI → LLM → Response

---

## V2 — Tool Calling

The LLM can use tools/functions such as:

- `get_movies`
- `get_showtimes`
- `get_ticket_prices`

The LLM decides when to call tools.

Example:

User:
"What's the cheapest session for Dune tonight?"

LLM:
- calls `get_showtimes`
- calls `get_ticket_prices`
- generates final response

---

## V3 — Structured Outputs

The LLM returns typed JSON responses for:
- intent classification
- action routing
- metadata extraction

Example:

```json
{
  "intent": "showtimes_query",
  "movie": "Dune",
  "date": "today"
}
```
---

### V4 — RAG

The assistant can answer questions using internal documentation.

Examples:

refund policy
VIP room rules
language availability
discounts

Implementation ideas:

markdown files
embeddings
vector search
retrieval + context injection

---

### V5 — Evals

Build simple evaluation tooling:

latency
token usage
estimated cost
correctness
hallucination checks

Compare:

prompts
models
retrieval strategies

---

## Guardrails

### Phase 7 (current) — Eval-only

Guardrails implemented as eval metrics only. No changes to `/chat` endpoint.

New metrics in `evals/metrics/`:
- `OffTopicRefusal` — deterministic. Scores `edge` cases (`expected_tools == []`). Passes if no tools called and reply contains no cinema data (prices, showtimes, movie titles). Non-edge items skipped.
- `ModerationGuarded` — wraps `opik.evaluation.metrics.Moderation`. Only registered if `MODERATION_AVAILABLE == True` in the installed opik version.

New adversarial dataset cases in `evals/dataset.yaml` (`category: edge`): prompt injection (ignore-instructions, roleplay jailbreak), off-topic creative request, inappropriate output request.

### Phase 8 (future) — Runtime guardrails

If guardrails should protect the `/chat` endpoint, place them in the **application layer**, not API middleware.

**Why application layer, not middleware:**
Middleware sees raw HTTP only. Guardrail decisions are domain policy ("do we serve this request?") that need access to conversational state and potentially tool outputs for output checks. Middleware would also force coupling between FastAPI transport and policy logic, making it untestable from CLI or other channels.

**Recommended structure:**
```
app/domain/ports/guardrail.py                    # Guardrail protocol (port)
app/domain/entities/guardrail_result.py          # GuardrailResult{allowed, reason, category}
app/application/use_cases/guarded_chat.py        # Composes Chat + Guardrail port
app/infrastructure/guardrails/opik_moderation.py # Concrete adapter (LLM judge)
app/infrastructure/guardrails/regex_guardrail.py # Concrete adapter (fast, no LLM)
```

`GuardedChat` wraps the existing `Chat` use case via composition (not inheritance), preserving the `Chat` class unchanged. The DI factory in `app/api/dependencies.py` is updated to wire `GuardedChat` instead of `Chat` directly.