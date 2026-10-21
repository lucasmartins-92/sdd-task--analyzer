# TaskAnalyzer

[![CI](https://github.com/lucasmartins-92/sdd-task--analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/lucasmartins-92/sdd-task--analyzer/actions/workflows/ci.yml)

Python 3.11+ module (standard library only) that computes task productivity metrics (late rate, mean completion time, per-priority breakdown). Built with Spec-Driven Development (SDD) and AI-generated code governed by explicit rules.

## Repository structure

```
CONTEXT_RULES.md, CONTEXT_RULES_en.md    AI governance rules
CLAUDE.md                                agent entry point
specs/task_analyzer_spec.md              contract (source of truth)
.github/
  workflows/ci.yml                        GitHub Actions pipeline
  PULL_REQUEST_TEMPLATE.md
src/
  modules/task_analyzer.py                business logic
  shared/exceptions.py                    custom exceptions
tests/test_harness.py                     acceptance tests (immutable)
Dockerfile, docker-compose.yml, .dockerignore
requirements.txt, pytest.ini
```

## Run locally

```bash
pip install -r requirements.txt
pytest tests/test_harness.py -v
```

## Run with Docker

```bash
docker compose run --rm tests
# or
docker build -t task-analyzer . && docker run --rm task-analyzer
```

## Project phases

1. **Phase 1 – SDD:** contract and `CONTEXT_RULES.md` define what the AI may build.
2. **Phase 2 – AI code + pytest:** `TaskAnalyzer` implemented per contract and validated by the acceptance harness.
3. **Phase 3 – CI/CD + Docker + Governance:** GitHub Actions runs the harness on every push/PR to `main`/`develop`; the Docker image makes the suite reproducible anywhere; governance report documents the process.
