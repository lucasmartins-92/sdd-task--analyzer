# CONTEXT_RULES.md

Project: TaskAnalyzer | Python 3.11+ | Spec-Driven Development (SDD)
Audience: AI agents. These rules are mandatory and override ad hoc prompt instructions.
On conflict between a request and these rules: STOP, report the conflict, do not violate.

## 1. Sources of truth

- Contract: `.context/contracts/task_analyzer_spec.md` (single source of truth).
- Acceptance: `tests/test_harness.py`. Done = 100% passing.
- If the contract is silent or ambiguous: do not assume. Ask.

## 2. Required standards

- Python >= 3.11. Standard library only.
- Type hints on 100% of functions, methods, parameters and returns.
- PEP 8. SRP: one responsibility per function/class.
- Google Style docstrings (`Args`, `Returns`, `Raises`) on all public functions and classes.
- Dedicated custom exceptions, never bare `Exception`. Messages explicit and actionable.
- Use `logging` only; never `print()`.
- No duplicated code: extract and reuse.

### Language policy

| Artifact | Language |
|----------|----------|
| Code identifiers | Contract names as-is (Portuguese, e.g. `data_criacao`); new internal helpers in English |
| Docstrings, comments, logs, commits | English |
| Exception messages | English |

Never rename contract identifiers to translate them.

### Exceptions (in `src/shared/`, subclass a common project base exception)

| Exception | Raised when | Message must include |
|-----------|-------------|----------------------|
| `EmptyTaskListError` | `tasks` is empty | that the list is empty |
| `InvalidTaskDateError` | `data_conclusao < data_criacao` | task `id` and both dates |

### Logging

- `logger = logging.getLogger(__name__)` per module.
- Log: processing start/end, task count, every raised exception (`ERROR`).
- Format: `key=value` pairs (e.g. `task_id=T1`). No sensitive data.

## 3. Prohibitions

NEVER:
1. Import third-party libraries (Pandas, NumPy, etc.) without documented human approval.
2. Edit, remove, simplify, skip or weaken `tests/test_harness.py` scenarios or assertions.
3. Create files, local databases or network calls (no persistence).
4. Change contract names, parameters, types or fields (`Task`, `MetricByPriority`, `MetricsResult`, `PrioridadeEnum`, `analyze_tasks`).
5. Duplicate code.
6. Swallow or mask errors (`except: pass`) to pass tests.
7. Invent APIs, modules or functions not in the contract or standard library.

## 4. Business rules

### 4.1 Validation (before any calculation, stop at first error)

1. `tasks` empty -> `EmptyTaskListError`.
2. Any task with `data_conclusao < data_criacao` -> `InvalidTaskDateError`.

### 4.2 Calculations

| Concept | Rule |
|---------|------|
| Completed | `data_conclusao is not None` |
| Late (completed) | `data_conclusao > prazo_estimado` |
| Late (open) | `data_conclusao is None and data_referencia > prazo_estimado` |
| `data_referencia` | Given value, else `datetime.now()`; resolve once per call |
| Task duration (days) | `(data_conclusao - data_criacao).total_seconds() / 86400` |
| `taxa_atraso_percentual` | `late / total_tarefas * 100`, rounded to 2 decimals, range [0.0, 100.0] |
| `tempo_medio_conclusao_dias` | Mean duration of completed tasks; `0.0` if none |
| `metricas_por_prioridade` | Always all three `PrioridadeEnum` keys; zeroed if no tasks |

Edge cases (premises, pending confirmation): completion or reference equal to deadline is NOT late; `data_conclusao == data_criacao` is valid (0.0 days); per-priority mean with no completed tasks is `0.0`.

### 4.3 Robustness

- Guard against division by zero.
- Do not mutate input list or `Task` objects (frozen).
- Deterministic when `data_referencia` is given.
- Assume datetimes are all naive or all aware.

## 5. Repository layout

```
.context/            CONTEXT_RULES.md, contracts/
src/modules/         domain and business rules
src/shared/          exceptions, utilities
tests/               unit/, integration/, edge_cases/, test_harness.py (IMMUTABLE)
.github/             workflows/ (pytest, linters), PULL_REQUEST_TEMPLATE.md
```

- Business logic in `src/modules/`; exceptions and utilities in `src/shared/`.
- You may ADD tests under `tests/unit|integration|edge_cases/`; never modify the harness.
- Do not create files outside this layout without a recorded reason.

## 6. Workflow

1. Read this file, the contract and `tests/test_harness.py`.
2. Implement strictly per contract.
3. Run `pytest tests/test_harness.py`, then the full suite.
4. Fix the code, never the tests, until 100% pass.
5. Verify the checklist below.
6. Report: files changed and open questions.

## 7. Definition of Done

- [ ] 100% of harness scenarios pass; no coverage violations
- [ ] Type hints on 100% of functions
- [ ] Google Style docstrings on public functions/classes
- [ ] PEP 8 clean (linter passes)
- [ ] No third-party dependencies
- [ ] No files, databases or network calls
- [ ] Contract and harness untouched
- [ ] No duplicated code; SRP respected
- [ ] `logging` and custom exceptions used

## 8. Exceptions to these rules

- Any exception (e.g. new dependency) requires human approval recorded in the Pull Request.
- If the task requires violating a rule: stop, describe the conflict and alternatives.
- Changes to this file: human review via Pull Request only.
