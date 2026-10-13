"""TaskAnalyzer: productivity metrics for software development tasks."""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from src.shared.exceptions import EmptyTaskListError, InvalidTaskDateError

logger = logging.getLogger(__name__)

SECONDS_PER_DAY = 86400


class PrioridadeEnum(str, Enum):
    """Priority levels a task can have."""

    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"


@dataclass(frozen=True)
class Task:
    """Represents a single task in the system.

    Attributes:
        id: Unique task identifier.
        titulo: Descriptive task title.
        data_criacao: Date/time the task was registered.
        prazo_estimado: Deadline for delivery.
        prioridade: Task priority level.
        data_conclusao: Effective completion date/time; None if open.
    """

    id: str
    titulo: str
    data_criacao: datetime
    prazo_estimado: datetime
    prioridade: PrioridadeEnum
    data_conclusao: Optional[datetime] = None


@dataclass(frozen=True)
class MetricByPriority:
    """Consolidated metrics for a specific priority level.

    Attributes:
        total_tarefas: Number of tasks with this priority.
        concluidas: Number of completed tasks.
        atrasadas: Number of late tasks.
        tempo_medio_conclusao_dias: Mean completion time in days.
    """

    total_tarefas: int
    concluidas: int
    atrasadas: int
    tempo_medio_conclusao_dias: float


@dataclass(frozen=True)
class MetricsResult:
    """Consolidated result of the productivity metrics analysis.

    Attributes:
        total_tarefas: Total number of tasks analyzed.
        total_concluidas: Number of completed tasks.
        taxa_atraso_percentual: Percentage of late tasks, in [0.0, 100.0].
        tempo_medio_conclusao_dias: Mean completion time in days.
        metricas_por_prioridade: Metrics for every PrioridadeEnum level.
    """

    total_tarefas: int
    total_concluidas: int
    taxa_atraso_percentual: float
    tempo_medio_conclusao_dias: float
    metricas_por_prioridade: Dict[PrioridadeEnum, MetricByPriority]


def _validate_tasks(tasks: List[Task]) -> None:
    """Validates the input before any calculation, stopping at first error.

    Args:
        tasks: Tasks to validate.

    Raises:
        EmptyTaskListError: If the list is empty.
        InvalidTaskDateError: If a task's completion precedes its creation.
    """
    if not tasks:
        logger.error("event=validation_failed reason=empty_task_list")
        raise EmptyTaskListError()
    for task in tasks:
        if (
            task.data_conclusao is not None
            and task.data_conclusao < task.data_criacao
        ):
            logger.error(
                "event=validation_failed reason=invalid_task_date "
                "task_id=%s data_criacao=%s data_conclusao=%s",
                task.id,
                task.data_criacao.isoformat(),
                task.data_conclusao.isoformat(),
            )
            raise InvalidTaskDateError(
                task.id, task.data_criacao, task.data_conclusao
            )


def _is_late(task: Task, data_referencia: datetime) -> bool:
    """Checks whether a task exceeded its deadline.

    Args:
        task: Task to check.
        data_referencia: Reference point used for open tasks.

    Returns:
        True if the task is late, False otherwise.
    """
    effective_end = (
        task.data_conclusao
        if task.data_conclusao is not None
        else data_referencia
    )
    return effective_end > task.prazo_estimado


def _duration_days(data_criacao: datetime, data_conclusao: datetime) -> float:
    """Computes the completion duration of a task in days.

    Args:
        data_criacao: Creation date of the task.
        data_conclusao: Completion date of the task.

    Returns:
        Duration between creation and completion, in days.
    """
    delta = data_conclusao - data_criacao
    return delta.total_seconds() / SECONDS_PER_DAY


def _mean(values: List[float]) -> float:
    """Computes the arithmetic mean, guarding against empty input.

    Args:
        values: Values to average.

    Returns:
        The mean of the values, or 0.0 if there are none.
    """
    return sum(values) / len(values) if values else 0.0


def _summarize(
    tasks: List[Task], data_referencia: datetime
) -> MetricByPriority:
    """Computes the metrics shared by the overall and per-priority scopes.

    Args:
        tasks: Tasks in the scope (may be empty).
        data_referencia: Reference point used for open tasks.

    Returns:
        MetricByPriority with totals, late count and mean duration.
    """
    durations = [
        _duration_days(task.data_criacao, task.data_conclusao)
        for task in tasks
        if task.data_conclusao is not None
    ]
    return MetricByPriority(
        total_tarefas=len(tasks),
        concluidas=len(durations),
        atrasadas=sum(1 for task in tasks if _is_late(task, data_referencia)),
        tempo_medio_conclusao_dias=_mean(durations),
    )


def analyze_tasks(
    tasks: List[Task],
    data_referencia: Optional[datetime] = None,
) -> MetricsResult:
    """Processes the task list and returns the consolidated metrics.

    Args:
        tasks: List of Task objects to analyze.
        data_referencia: Point in time used to check lateness of open
            tasks. If None, datetime.now() is used.

    Returns:
        MetricsResult with overall and per-priority consolidated metrics.

    Raises:
        EmptyTaskListError: If the task list is empty.
        InvalidTaskDateError: If a completion date is earlier than the
            creation date.
    """
    logger.info("event=analysis_started task_count=%d", len(tasks))
    _validate_tasks(tasks)

    reference = data_referencia if data_referencia is not None else (
        datetime.now()
    )
    overall = _summarize(tasks, reference)
    by_priority = {
        prioridade: _summarize(
            [task for task in tasks if task.prioridade == prioridade],
            reference,
        )
        for prioridade in PrioridadeEnum
    }
    result = MetricsResult(
        total_tarefas=overall.total_tarefas,
        total_concluidas=overall.concluidas,
        taxa_atraso_percentual=round(
            overall.atrasadas / overall.total_tarefas * 100, 2
        ),
        tempo_medio_conclusao_dias=overall.tempo_medio_conclusao_dias,
        metricas_por_prioridade=by_priority,
    )
    logger.info(
        "event=analysis_finished task_count=%d completed=%d late=%d",
        overall.total_tarefas,
        overall.concluidas,
        overall.atrasadas,
    )
    return result
