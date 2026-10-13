# task_analyzer_spec.md

**Módulo:** TaskAnalyzer
**Paradigma:** Spec-Driven Development (SDD)
**Linguagem:** Python 3.11+
**Localização sugerida:** `.context/contracts/task_analyzer_spec.md`
**Status:** Fonte única da verdade (Single Source of Truth) do módulo.

---

## 1. Identificação

| Campo | Valor |
|-------|-------|
| Autor | Lucas Martins de Andrade |
| Curso | Ciência da Computação |
| Turno | Asa Norte / Noturno |
| Contato | lucas.ma@sempreceub.com |

---

## 2. Propósito

O TaskAnalyzer processa uma coleção de tarefas do ciclo de desenvolvimento de software e produz indicadores consolidados de produtividade:

| Indicador | Descrição |
|-----------|-----------|
| Tempo médio de conclusão | Duração média, em dias, das tarefas efetivamente concluídas. |
| Taxa de atraso | Percentual de tarefas que excederam o prazo: concluídas após o prazo ou abertas com prazo já expirado em relação à data de referência. |
| Indicadores por prioridade | Os mesmos indicadores segmentados por `ALTA`, `MEDIA` e `BAIXA`. |

---

## 3. Escopo

**Dentro do escopo:**
- Validação da entrada.
- Cálculo dos indicadores gerais e por prioridade.
- Retorno de um objeto `MetricsResult` imutável.

**Fora do escopo:**
- Persistência de dados (arquivos, banco de dados).
- Comunicação de rede.
- Interface de usuário ou serialização do resultado.
- Uso de bibliotecas de terceiros.

---

## 4. Contrato Executável de Interface

### 4.1 Modelos de dados

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class PrioridadeEnum(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"


@dataclass(frozen=True)
class Task:
    """Representa uma tarefa individual no sistema."""
    id: str
    titulo: str
    data_criacao: datetime
    prazo_estimado: datetime
    prioridade: PrioridadeEnum
    data_conclusao: Optional[datetime] = None


@dataclass(frozen=True)
class MetricByPriority:
    """Métricas consolidadas para um nível de prioridade específico."""
    total_tarefas: int
    concluidas: int
    atrasadas: int
    tempo_medio_conclusao_dias: float


@dataclass(frozen=True)
class MetricsResult:
    """Resultado consolidado da análise de métricas de produtividade."""
    total_tarefas: int
    total_concluidas: int
    taxa_atraso_percentual: float
    tempo_medio_conclusao_dias: float
    metricas_por_prioridade: Dict[PrioridadeEnum, MetricByPriority]
```

### 4.2 Assinatura do módulo principal

```python
def analyze_tasks(
    tasks: List[Task],
    data_referencia: Optional[datetime] = None,
) -> MetricsResult:
    """Processa a lista de tarefas e retorna os indicadores consolidados.

    Args:
        tasks: Lista de objetos Task a serem analisados.
        data_referencia: Ponto no tempo usado para checar atrasos em tarefas
            abertas. Se None, utiliza datetime.now().

    Returns:
        MetricsResult com as métricas consolidadas gerais e por prioridade.

    Raises:
        EmptyTaskListError: Se a lista de tarefas estiver vazia.
        InvalidTaskDateError: Se a data de conclusão for anterior à data
            de criação.
    """
```

### 4.3 Exceções customizadas

| Exceção | Condição | Requisito da mensagem |
|---------|----------|-----------------------|
| `EmptyTaskListError` | `tasks` é uma lista vazia. | Mensagem clara informando que a lista está vazia. |
| `InvalidTaskDateError` | `data_conclusao < data_criacao`. | Deve conter o `id` da tarefa e as duas datas envolvidas. |

---

## 5. Especificação dos Atributos

| Campo | Tipo Python | Obrigatório | Regra de negócio |
|-------|-------------|-------------|------------------|
| `Task.id` | `str` | Sim | Identificador único da tarefa. |
| `Task.titulo` | `str` | Sim | Título descritivo da tarefa. |
| `Task.data_criacao` | `datetime` | Sim | Data/hora de registro da tarefa. |
| `Task.prazo_estimado` | `datetime` | Sim | Data/hora limite estipulada para entrega. |
| `Task.prioridade` | `PrioridadeEnum` | Sim | Nível de prioridade da tarefa. |
| `Task.data_conclusao` | `Optional[datetime]` | Não (`None` se aberta) | Data/hora de encerramento efetivo. Deve ser `>= data_criacao`. |
| `MetricsResult.taxa_atraso_percentual` | `float` | Sim | Valor entre `0.0` e `100.0`. |
| `MetricsResult.tempo_medio_conclusao_dias` | `float` | Sim | Média em dias das tarefas concluídas. `0.0` se nenhuma concluída. |

---

## 6. Regras de Negócio

### 6.1 Ordem de validação

1. Lista vazia → `EmptyTaskListError`.
2. Qualquer tarefa com `data_conclusao < data_criacao` → `InvalidTaskDateError`.
3. A validação ocorre integralmente antes de qualquer cálculo.

### 6.2 Definições de cálculo

| Conceito | Regra |
|----------|-------|
| Tarefa concluída | `data_conclusao is not None`. |
| Atrasada (concluída) | `data_conclusao > prazo_estimado`. |
| Atrasada (aberta) | `data_conclusao is None` e `data_referencia > prazo_estimado`. |
| Data de referência | `data_referencia` se informada; caso contrário `datetime.now()`, resolvida uma única vez por execução. |
| Duração de uma tarefa | `(data_conclusao - data_criacao).total_seconds() / 86400`. |
| `taxa_atraso_percentual` | `(total de atrasadas / total_tarefas) * 100`, arredondada a 2 casas decimais. |
| `tempo_medio_conclusao_dias` | Média das durações das tarefas concluídas; `0.0` se nenhuma. |
| `metricas_por_prioridade` | Contém sempre as três chaves de `PrioridadeEnum`, com valores zerados quando não há tarefas. |

### 6.3 Decisões de projeto a confirmar

Pontos não definidos no documento de origem; os valores abaixo são as premissas adotadas.

| Caso | Premissa |
|------|----------|
| `data_conclusao == prazo_estimado` | Não é atraso (comparação estrita `>`). |
| Tarefa aberta com `data_referencia == prazo_estimado` | Não é atraso. |
| `data_conclusao == data_criacao` | Válido; duração de `0.0` dia. |
| Datetimes naive misturados com aware | Fora do contrato; o chamador deve usar um único padrão. |
| Média por prioridade sem tarefas concluídas | `0.0`. |

---

## 7. Cenários de Aceite (BDD)

Estes cenários são a base inviolável do Test Harness (`tests/test_harness.py`).

### Cenário 1: Caminho feliz, processamento com métricas válidas

**Dado** uma lista com 3 tarefas:

| Tarefa | Prioridade | Situação |
|--------|------------|----------|
| 1 | ALTA | Criada há 5 dias, prazo em 3 dias, concluída em 2 dias. Sem atraso. |
| 2 | ALTA | Criada há 10 dias, prazo há 2 dias, concluída há 1 dia. Atrasada. |
| 3 | MEDIA | Criada há 4 dias, prazo há 1 dia, não concluída. Atraso ativo. |

**Quando** `analyze_tasks` for executada com essa lista,
**Então** deve retornar um `MetricsResult` em que:

- `total_tarefas == 3`
- `total_concluidas == 2`
- `tempo_medio_conclusao_dias == 1.5` (média de 2 dias e 1 dia)
- `taxa_atraso_percentual == 66.67`
- `metricas_por_prioridade[PrioridadeEnum.ALTA].atrasadas == 1`
- `metricas_por_prioridade[PrioridadeEnum.MEDIA].atrasadas == 1`

> **Inconsistência no enunciado original:** "criada há 10 dias" e "concluída há 1 dia" resultam em duração de 9 dias para a Tarefa 2, e a média seria 5,5 dias, não 1,5. Para o harness ser determinístico e coerente com os resultados esperados, use a fixture de referência da seção 7.1.

#### 7.1 Fixture de referência (determinística)

Referência: `data_referencia = datetime(2026, 1, 15, 12, 0)`.

| Tarefa | Prioridade | `data_criacao` | `prazo_estimado` | `data_conclusao` | Duração | Atrasada |
|--------|------------|----------------|------------------|------------------|---------|----------|
| 1 | ALTA | 2026-01-10 12:00 | 2026-01-18 12:00 | 2026-01-12 12:00 | 2,0 | Não |
| 2 | ALTA | 2026-01-13 12:00 | 2026-01-13 18:00 | 2026-01-14 12:00 | 1,0 | Sim |
| 3 | MEDIA | 2026-01-11 12:00 | 2026-01-14 12:00 | `None` | n/a | Sim |

Resultado esperado completo:

| Escopo | total | concluídas | atrasadas | tempo médio (dias) |
|--------|-------|------------|-----------|--------------------|
| Geral | 3 | 2 | 2 (taxa 66.67%) | 1.5 |
| ALTA | 2 | 2 | 1 | 1.5 |
| MEDIA | 1 | 0 | 1 | 0.0 |
| BAIXA | 0 | 0 | 0 | 0.0 |

### Cenário 2: Inconsistência temporal nas datas

**Dado** uma lista contendo uma tarefa com `data_conclusao = 2026-01-01` e `data_criacao = 2026-01-05`,
**Quando** `analyze_tasks` for chamada,
**Então** o sistema deve interromper a execução e disparar `InvalidTaskDateError` com mensagem clara.

### Cenário 3: Lista vazia

**Dado** uma lista de tarefas vazia (`[]`),
**Quando** `analyze_tasks` for executada,
**Então** o sistema deve disparar `EmptyTaskListError`.

---

## 8. Integração com o Test Harness (pytest)

1. **Tradução BDD para pytest:** cada cenário da seção 7 vira uma função de teste em `tests/test_harness.py`.
2. **Ciclo de feedback:** o agente de IA executa `pytest tests/test_harness.py` para verificar a conformidade.
3. **Aprovação rígida:** o código só é considerado pronto com 100% dos cenários aprovados, sem falhas e sem violações de cobertura.
4. **Imutabilidade:** os testes do harness não podem ser alterados, removidos ou simplificados.

Mapeamento sugerido:

| Cenário | Função de teste |
|---------|-----------------|
| 1 | `test_cenario_1_metricas_validas` |
| 2 | `test_cenario_2_inconsistencia_temporal` |
| 3 | `test_cenario_3_lista_vazia` |

---

## 9. Requisitos Não Funcionais

| Requisito | Regra |
|-----------|-------|
| Linguagem | Python 3.11+ |
| Dependências | Apenas biblioteca padrão |
| Tipagem | Type hints em 100% das funções |
| Estilo | PEP 8 e SRP |
| Documentação | Google Style Docstrings em funções públicas e classes |
| Observabilidade | Logs estruturados via módulo `logging` |
| Imutabilidade | Dataclasses `frozen=True`; entrada não é mutada |
| Persistência | Nenhuma (sem arquivos, banco ou rede) |
| Determinismo | Resultado idêntico para mesma entrada quando `data_referencia` é informada |

---

## 10. Estrutura de Arquivos Esperada

```
src/
├── modules/
│   └── task_analyzer.py      # Modelos e analyze_tasks
└── shared/
    └── exceptions.py         # EmptyTaskListError, InvalidTaskDateError
tests/
└── test_harness.py           # Cenários 1 a 3 (imutável)
```

---

## 11. Critérios de Aceite Globais

- [ ] Cenários 1, 2 e 3 aprovados no `test_harness.py`.
- [ ] Contrato (seção 4) implementado sem alteração de nomes, parâmetros ou tipos.
- [ ] Regras da seção 6 implementadas e cobertas por testes.
- [ ] Conformidade integral com `.context/CONTEXT_RULES.md`.
