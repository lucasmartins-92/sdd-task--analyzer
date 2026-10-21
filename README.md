# TaskAnalyzer

[![CI](https://github.com/lucasmartins-92/sdd-task--analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/lucasmartins-92/sdd-task--analyzer/actions/workflows/ci.yml)

Módulo em Python 3.11+ (somente biblioteca padrão) que calcula métricas de produtividade de tarefas: taxa de atraso, tempo médio de conclusão e detalhamento por prioridade. Foi construído com Spec-Driven Development (SDD), com código gerado por IA e regido por regras explícitas de governança.

## Estrutura do repositório

```
CONTEXT_RULES.md, CONTEXT_RULES_en.md    regras de governança para IA
CLAUDE.md                                ponto de entrada para o agente
specs/task_analyzer_spec.md              contrato (fonte da verdade)
.github/
  workflows/ci.yml                       pipeline do GitHub Actions
  PULL_REQUEST_TEMPLATE.md
src/
  modules/task_analyzer.py               regras de negócio
  shared/exceptions.py                   exceções personalizadas
tests/test_harness.py                    testes de aceitação (imutáveis)
Dockerfile, docker-compose.yml, .dockerignore
requirements.txt, pytest.ini
```

## Executando localmente

```bash
pip install -r requirements.txt
pytest tests/test_harness.py -v
```

## Executando com Docker

```bash
docker compose run --rm tests
# ou
docker build -t task-analyzer . && docker run --rm task-analyzer
```

## Fases do projeto

1. **Fase 1 – SDD:** o contrato e o `CONTEXT_RULES.md` definem o que a IA pode construir.
2. **Fase 2 – Código por IA + pytest:** o `TaskAnalyzer` é implementado conforme o contrato e validado pelo harness de aceitação.
3. **Fase 3 – CI/CD + Docker + Governança:** o GitHub Actions executa o harness a cada push ou PR para `main`/`develop`; a imagem Docker torna a suíte reproduzível em qualquer ambiente; o relatório de governança documenta o processo.
