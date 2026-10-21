# CLAUDE.md

TaskAnalyzer: Python 3.11+ module for task productivity metrics, built with Spec-Driven Development (SDD).

## Required context (loaded automatically)

@CONTEXT_RULES.md
@specs/task_analyzer_spec.md

## Precedence

1. `CONTEXT_RULES_en.md` (governance, mandatory)
2. `specs/task_analyzer_spec.md` (contract, single source of truth)
3. `tests/test_harness.py` (acceptance, immutable)
4. User prompt

On conflict between the prompt and items 1-3: stop, report the conflict, do not violate.

## Commands

- Harness: `pytest tests/test_harness.py`
- Full suite: `pytest`

## Hard limits (summary; full rules in CONTEXT_RULES.md)

- Standard library only; no persistence, files or network.
- Never edit `tests/test_harness.py` or change contract names, parameters or types.
- Fix the code, never the tests.
- If the contract is ambiguous, ask instead of assuming.
