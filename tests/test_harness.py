"""Acceptance harness for TaskAnalyzer (contract section 7 scenarios)."""

from datetime import datetime
from typing import List

import pytest

from src.modules.task_analyzer import (
    MetricByPriority,
    MetricsResult,
    PrioridadeEnum,
    Task,
    analyze_tasks,
)
from src.shared.exceptions import EmptyTaskListError, InvalidTaskDateError

DATA_REFERENCIA = datetime(2026, 1, 15, 12, 0)


@pytest.fixture
def reference_tasks() -> List[Task]:
    """Builds the deterministic reference fixture from contract section 7.1.

    Returns:
        The three tasks of scenario 1.
    """
    return [
        Task(
            id="1",
            titulo="Task 1",
            data_criacao=datetime(2026, 1, 10, 12, 0),
            prazo_estimado=datetime(2026, 1, 18, 12, 0),
            prioridade=PrioridadeEnum.ALTA,
            data_conclusao=datetime(2026, 1, 12, 12, 0),
        ),
        Task(
            id="2",
            titulo="Task 2",
            data_criacao=datetime(2026, 1, 13, 12, 0),
            prazo_estimado=datetime(2026, 1, 13, 18, 0),
            prioridade=PrioridadeEnum.ALTA,
            data_conclusao=datetime(2026, 1, 14, 12, 0),
        ),
        Task(
            id="3",
            titulo="Task 3",
            data_criacao=datetime(2026, 1, 11, 12, 0),
            prazo_estimado=datetime(2026, 1, 14, 12, 0),
            prioridade=PrioridadeEnum.MEDIA,
        ),
    ]


def test_cenario_1_metricas_validas(reference_tasks: List[Task]) -> None:
    """Scenario 1: happy path produces the expected metrics."""
    result = analyze_tasks(reference_tasks, data_referencia=DATA_REFERENCIA)

    assert isinstance(result, MetricsResult)
    assert result.total_tarefas == 3
    assert result.total_concluidas == 2
    assert result.tempo_medio_conclusao_dias == pytest.approx(1.5)
    assert result.taxa_atraso_percentual == 66.67
    assert result.metricas_por_prioridade == {
        PrioridadeEnum.ALTA: MetricByPriority(
            total_tarefas=2,
            concluidas=2,
            atrasadas=1,
            tempo_medio_conclusao_dias=1.5,
        ),
        PrioridadeEnum.MEDIA: MetricByPriority(
            total_tarefas=1,
            concluidas=0,
            atrasadas=1,
            tempo_medio_conclusao_dias=0.0,
        ),
        PrioridadeEnum.BAIXA: MetricByPriority(
            total_tarefas=0,
            concluidas=0,
            atrasadas=0,
            tempo_medio_conclusao_dias=0.0,
        ),
    }


def test_cenario_2_inconsistencia_temporal() -> None:
    """Scenario 2: completion before creation raises InvalidTaskDateError."""
    task = Task(
        id="T-INVALID",
        titulo="Inconsistent dates",
        data_criacao=datetime(2026, 1, 5),
        prazo_estimado=datetime(2026, 1, 10),
        prioridade=PrioridadeEnum.BAIXA,
        data_conclusao=datetime(2026, 1, 1),
    )

    with pytest.raises(InvalidTaskDateError) as exc_info:
        analyze_tasks([task], data_referencia=DATA_REFERENCIA)

    message = str(exc_info.value)
    assert "T-INVALID" in message
    assert "2026-01-05" in message
    assert "2026-01-01" in message


def test_cenario_3_lista_vazia() -> None:
    """Scenario 3: an empty task list raises EmptyTaskListError."""
    with pytest.raises(EmptyTaskListError, match="(?i)empty"):
        analyze_tasks([], data_referencia=DATA_REFERENCIA)
