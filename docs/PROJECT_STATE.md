# PROJECT STATE

> This is the exact operational state of the course. Update at the end of every session.

## Identity

Project: **Production AI Incident & Knowledge Copilot**  
Sprint: **14-day AI Engineer capstone**  
Current day: **Day 0 — Setup**  
Current phase: **Final Git checkpoint**  
Overall status: **DAY 0 ENVIRONMENT COMPLETE — initial commit/push pending**

## Permanent local project root

`/Users/yagnesh/Desktop/projects/ai-incident-copilot`

## Machine / environment

- macOS 12.6 Monterey
- Apple Silicon `arm64`
- 8 GB RAM
- PyCharm
- Git 2.33.0
- `uv` 0.12.3
- Python 3.12.13
- Docker Desktop 4.37.2
- Docker Engine 27.4.0
- Docker Compose 2.31.0

## Completed

- [x] Project concept selected
- [x] 14-day learning strategy agreed
- [x] Durable source-of-truth approach agreed
- [x] Starter repository created
- [x] Permanent local project root selected
- [x] Git repository initialized on `main`
- [x] Git identity configured
- [x] GitHub HTTPS remote configured
- [x] PyCharm opened and project interpreter configured
- [x] `uv` installed
- [x] Python 3.12.13 installed through `uv`
- [x] `.venv` created
- [x] baseline pytest passed
- [x] Docker daemon verified
- [x] Docker `hello-world` container executed successfully
- [x] Local Qwen2.5-0.5B-Instruct Q4_K_M GGUF downloaded
- [x] `llama.cpp` server executed through Docker
- [x] local OpenAI-compatible `/v1/chat/completions` request succeeded
- [x] generated first local LLM response
- [x] `docs/START_HERE.md` read

## Local inference decision

Current local model:

`Qwen2.5-0.5B-Instruct Q4_K_M`

Runtime:

`llama.cpp` server inside Docker

Reason Ollama was not used:

Current Ollama releases do not support this machine's macOS 12.6 environment.

First measured local inference sample:

- prompt tokens: 39
- completion tokens: 38
- total tokens: 77
- generation speed: ~31.45 tokens/sec

These are environment-validation numbers only, not a formal benchmark.

## Current blockers

None.

## Remaining Day 0 work

- [ ] Review Git contents
- [ ] Initial checkpoint commit
- [ ] Push `main` to GitHub
- [ ] Verify clean working tree

## GitHub remote

`https://github.com/yagnesh25gehlot/ai-incident-copilot.git`

## Next exact action

Run final verification, commit the repository, and push `main` to GitHub.

## Next learning session

**Day 1 — LLM fundamentals + first Python LLM client**

Before Day 1:

1. Read `docs/START_HERE.md`.
2. Read this file.
3. Start a fresh chat inside the same AI Engineer ChatGPT Project if desired.
4. Provide `MASTER_PLAN.md` and `PROJECT_STATE.md`.
5. Use the continuation prompt from `START_HERE.md`.

Do not start Day 1 implementation during Day 0.
