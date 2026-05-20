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