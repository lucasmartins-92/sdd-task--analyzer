# CONTEXT_RULES.md

**Projeto:** TaskAnalyzer
**Paradigma:** Spec-Driven Development (SDD) & AI Harness
**Linguagem:** Python 3.11+
**Escopo:** Regras de governança obrigatórias para qualquer Agente de IA que gere, altere ou revise código neste repositório.

> Este documento tem precedência sobre qualquer instrução ad hoc do prompt. Em caso de conflito entre uma solicitação e estas regras, o agente deve interromper e sinalizar o conflito, sem violar as regras.

---

## 1. Fonte da Verdade

1. O contrato técnico em `specs/` é a **Single Source of Truth**.
2. O arquivo `tests/test_harness.py` é o **homologador automático**. O código só é considerado pronto quando 100% dos cenários passarem.
3. O agente não deve inferir comportamento não especificado. Se o contrato for omisso ou ambíguo, o agente deve registrar a dúvida e solicitar esclarecimento, sem assumir.

---

## 2. Diretrizes Arquiteturais Obrigatórias

| # | Diretriz | Regra |
|---|----------|-------|
| 2.1 | Versão mínima | Python **3.11+**. |
| 2.2 | Tipagem estrita | Type hints em **100%** das funções, métodos e assinaturas (parâmetros e retorno). |
| 2.3 | Código limpo | Aderência rigorosa ao **PEP 8** e ao princípio **SRP** (uma responsabilidade por função/classe). |
| 2.4 | Documentação | **Google Style Docstrings** em todas as funções públicas e classes (`Args`, `Returns`, `Raises`). |
| 2.5 | Exceções customizadas | Exceções dedicadas, com mensagens explícitas e acionáveis. Proibido usar `Exception` genérica. |
| 2.6 | Logs estruturados | Usar exclusivamente o módulo nativo `logging`. Proibido `print()` para rastreabilidade. |
| 2.7 | Dependências | Apenas biblioteca padrão do Python. |

### 2.1 Exceções do domínio

| Exceção | Condição de disparo |
|---------|---------------------|
| `EmptyTaskListError` | Lista de tarefas vazia. |
| `InvalidTaskDateError` | `data_conclusao` anterior a `data_criacao`. |

Ambas devem residir em `src/shared/` e herdar de uma exceção base do projeto.

### 2.2 Logging

- Usar `logging.getLogger(__name__)` em cada módulo.
- Registrar: início e fim do processamento, quantidade de tarefas, e toda exceção disparada (nível `ERROR`).
- Mensagens devem incluir contexto (ex.: `task_id`) em formato chave=valor.
- Proibido registrar dados sensíveis.

---

## 3. Proibições Explícitas (Guardrails)

O agente **NÃO PODE**:

1. **Importar bibliotecas de terceiros** (Pandas, NumPy etc.) sem aprovação humana explícita e documentada.
2. **Alterar, remover, simplificar ou comentar** cenários de `tests/test_harness.py`, nem enfraquecer asserções para fazê-los passar.
3. **Persistir dados**: criar arquivos, bancos locais ou realizar comunicação de rede.
4. **Alterar o contrato**: nomes, parâmetros, tipos de retorno ou campos de `Task`, `MetricByPriority`, `MetricsResult`, `PrioridadeEnum` e `analyze_tasks`.
5. **Duplicar código**: lógica repetida deve ser extraída para funções reutilizáveis.
6. **Silenciar erros** (`except: pass`) ou mascarar falhas para obter aprovação nos testes.
7. **Inventar** APIs, módulos ou funções inexistentes (alucinação). Em caso de dúvida, consultar o contrato.

---

## 4. Regras de Negócio (derivadas do contrato)

### 4.1 Validações (ordem obrigatória)

1. Se `tasks` estiver vazia → `EmptyTaskListError`.
2. Se alguma tarefa tiver `data_conclusao < data_criacao` → `InvalidTaskDateError` (mensagem deve conter o `id` da tarefa e as datas envolvidas).
3. A validação ocorre **antes** de qualquer cálculo; a execução é interrompida no primeiro erro.

### 4.2 Definições de cálculo

| Indicador | Regra |
|-----------|-------|
| Tarefa concluída | `data_conclusao is not None`. |
| Tarefa atrasada (concluída) | `data_conclusao > prazo_estimado`. |
| Tarefa atrasada (aberta) | `data_conclusao is None` e `data_referencia > prazo_estimado`. |
| `data_referencia` | Se `None`, usar `datetime.now()`. Deve ser resolvida uma única vez por execução. |
| `taxa_atraso_percentual` | `(atrasadas / total_tarefas) * 100`, arredondada a 2 casas, no intervalo `[0.0, 100.0]`. |
| `tempo_medio_conclusao_dias` | Média da duração (`data_conclusao - data_criacao`) em dias, das tarefas concluídas. Retorna `0.0` se nenhuma concluída. |
| `metricas_por_prioridade` | Deve conter **todas** as chaves de `PrioridadeEnum` (ALTA, MEDIA, BAIXA), inclusive com valores zerados. |

### 4.3 Robustez

- Divisões devem ser protegidas contra divisão por zero.
- A função não deve mutar a lista de entrada nem os objetos `Task` (são `frozen`).
- A função deve ser determinística quando `data_referencia` for fornecida.
- Comparações entre datas devem assumir datetimes consistentes (todos *naive* ou todos *aware*).

---

## 5. Estrutura do Repositório

```
root/
├── CONTEXT_RULES.md
├── specs/              # Contrato técnico
├── src/
│   ├── modules/        # Domínio e regras de negócio (ex.: task_analyzer)
│   └── shared/         # Utilitários, exceções e componentes comuns
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── edge_cases/
│   └── test_harness.py # IMUTÁVEL
└── .github/
    ├── workflows/      # CI: pytest e linters
    └── PULL_REQUEST_TEMPLATE.md
```

**Regras de localização:**
- Regras de negócio em `src/modules/`; exceções e utilitários em `src/shared/`.
- Novos testes vão em `tests/unit/`, `tests/integration/` ou `tests/edge_cases/`. O agente pode **adicionar** testes, nunca alterar os do harness.
- Não criar arquivos fora desta estrutura sem justificativa registrada.

---

## 6. Ciclo de Trabalho do Agente

1. **Ler** este arquivo, o contrato em `specs/` e `tests/test_harness.py`.
2. **Implementar** estritamente conforme o contrato.
3. **Executar** `pytest tests/test_harness.py` e a suíte completa.
4. **Corrigir o código** (nunca os testes) até 100% de aprovação.
5. **Verificar conformidade** com o checklist da seção 7.
6. **Reportar** o resultado, listando arquivos alterados e eventuais dúvidas.

---

## 7. Checklist de Conformidade (Definition of Done)

- [ ] 100% dos cenários do `test_harness.py` passam, sem falhas.
- [ ] Nenhuma violação de cobertura.
- [ ] Type hints em 100% das funções.
- [ ] Docstrings Google Style em todas as funções públicas e classes.
- [ ] PEP 8 respeitado (linter sem erros).
- [ ] Nenhuma dependência de terceiros adicionada.
- [ ] Nenhum arquivo, banco ou chamada de rede criado.
- [ ] Contrato intacto (nomes, parâmetros e tipos).
- [ ] Testes do harness intactos.
- [ ] Sem código duplicado; cada função com responsabilidade única.
- [ ] Uso de `logging` e exceções customizadas com mensagens claras.

---

## 8. Tratamento de Conflitos e Exceções às Regras

- Qualquer necessidade de exceção a estas regras (ex.: nova dependência) exige **aprovação humana registrada** no Pull Request.
- Se cumprir a tarefa exigir violar uma regra, o agente deve **parar e reportar**, descrevendo o conflito e as alternativas.
- Mudanças neste arquivo só podem ser feitas por revisão humana via Pull Request, usando o `PULL_REQUEST_TEMPLATE.md`.
