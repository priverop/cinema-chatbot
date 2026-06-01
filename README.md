# Cinema-chatbot

Customer support AI agent for a Cinema app, built with FastAPI and LLM orchestration.

Users ask questions in natural language to get information about theaters, movies, and showtimes.

The goal of this project is to learn about AI harnessing, tooling, embeddings, RAG, evals, and guardrails.

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) (Python) — hexagonal architecture.
- [React](https://react.dev/) — frontend chat.
- [SQLModel](https://sqlmodel.tiangolo.com/) — ORM + SQLite 3.
- [Pydantic](https://docs.pydantic.dev/).
- [Gemini API](https://ai.google.dev/) — LLM and embeddings.
- [Comet Opik](https://www.comet.com/opik) — evals and observability.
- [ChromaDB](https://www.trychroma.com/) — vector database for RAG.

## Usage

```bash
# 1. Configure environment
cp .env.example .env  # fill GEMINI_API_KEY, OPIK_API_KEY, OPIK_WORKSPACE

# 2. Backend
pip install -r requirements.txt
fastapi dev

# 3. Index the knowledge base (RAG)
python -m app.scripts.index_knowledge

# 4. Frontend
cd frontend && pnpm install && pnpm run dev
```

Open http://localhost:5173 and start chatting.

**Evals (optional)**

```bash
# Upload dataset to Opik (required before running evals)
python -m evals.build_dataset

# Run evals
python -m evals.run_evals

# With optional suites
RUN_AB=1 RUN_RAG=1 RUN_MODERATION=1 python -m evals.run_evals
```

## How it works

The agent receives a user message and sends it to the Gemini API with a system prompt and the available tools. The LLM can respond directly or request one or more tool calls. Tool results are appended to the conversation and the loop continues until a plain reply is produced (max 5 iterations).

```
user message
      │
      ▼
GuardedChat  ← input guardrail check
      │ blocked → return refusal
      │ ok ↓
      ▼
Chat.__call__()
      │
      ▼
LLM (Gemini) ← system prompt + history + tool specs
      │
      ├── plain reply ────────────────────► ChatResponse
      │
      └── tool_calls ──► run tool(s)
                              │
                              ▼
                   append result to history
                              │
                              ▼
                       loop (max 5 iters)
      │
      ▼
output guardrail check
      │ blocked → return refusal
      │ ok ↓
      ▼
      response
```

## Tooling

The LLM selects from these tools to retrieve cinema data: `get_movies`, `get_theaters`, `get_showtimes`, `get_cheapest_session`, and `search_knowledge`.

## RAG

Knowledge base lives in `/db/knowledge`. Files are split into chunks, embedded with the Gemini API, and inserted into ChromaDB.

```bash
python -m app.scripts.index_knowledge
```

The model retrieves that info using the `search_knowledge` tool.

## Opik

Fully integrated with [Comet Opik](https://www.comet.com/opik) for metrics, evaluations, and A/B testing.

- **Metrics**: traces on the Gemini client, Chat, and tools — latency, cost, and interaction debugging.
- **A/B testing**: compare different base prompts to improve quality and reduce token usage.

### Evaluations

- **Tool selection**: compares actual vs. expected tool calls.
- **Hallucinations**: LLM judge.
- **Correctness**: GEval score for answer accuracy.
- **RAG**: ContextPrecision (are the chunks relevant?) and ContextRecall (do the chunks cover the question?).
- **Moderation**: score for harmful content.

The more evals you run, the longer it takes. Sleeps are added in code to avoid API rate limiting.

## Guardrails

Two guardrails protect the `/chat` endpoint:

- `RegexPromptInjection` — blocks prompt injection attempts on input.
- `TitleLeakGuardrail` — blocks hallucinated or leaked movie titles on output.

## Decisions

### Opik Hallucinations

The judge LLM has some false positives on hallucinations:

```
"input": "¿Hay sesiones este fin de semana?",
"context": ["[]"],  # tool returned empty
"output": "No he encontrado ninguna sesión para este fin de semana (del 29 al 31 de mayo).",
"score": 0.5,
"reason": ['The output correctly identifies that there are no showtimes available based on the empty context.', 'The output introduces specific dates (May 29-31) that were not present in the provided context.']
```

`few_shot_examples` could be added to the Hallucination constructor to clarify this to the judge, but that risks biasing it to pass wrong answers. Further testing needed.
