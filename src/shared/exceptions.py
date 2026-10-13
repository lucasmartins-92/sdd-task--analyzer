"""Custom exceptions for the TaskAnalyzer module."""

from datetime import datetime


class TaskValidationError(Exception):
    """Base exception for every task input validation failure."""


class EmptyTaskListError(TaskValidationError):
    """Raised when the list of tasks to analyze is empty."""

    def __init__(self) -> None:
        """Initializes the error with an actionable message."""
        super().__init__(
            "Task list is empty: provide at least one Task to analyze."
        )


class InvalidTaskDateError(TaskValidationError):
    """Raised when a task's completion date precedes its creation date.

    Attributes:
        task_id: Identifier of the offending task.
        data_criacao: Creation date of the task.
        data_conclusao: Completion date of the task.
    """

    def __init__(
        self,
        task_id: str,
        data_criacao: datetime,
        data_conclusao: datetime,
    ) -> None:
        """Initializes the error with the task id and both dates.

        Args:
            task_id: Identifier of the offending task.
            data_criacao: Creation date of the task.
            data_conclusao: Completion date of the task.
        """
        self.task_id = task_id
        self.data_criacao = data_criacao
        self.data_conclusao = data_conclusao
        super().__init__(
            f"Task '{task_id}' has data_conclusao "
            f"({data_conclusao.isoformat()}) earlier than data_criacao "
            f"({data_criacao.isoformat()}): completion date must be on or "
            f"after creation date."
        )
