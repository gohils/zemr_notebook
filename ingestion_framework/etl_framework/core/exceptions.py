"""
Custom exceptions for the ETL framework.
"""


class ETLFrameworkError(Exception):
    """Base exception for all framework-level errors."""


class ConfigError(ETLFrameworkError):
    """Raised when config.json is missing, malformed, or missing required keys."""


class TaskLoadError(ETLFrameworkError):
    """Raised when a module/class referenced in the config cannot be imported/instantiated."""


class ETLTaskError(ETLFrameworkError):
    """Raised when a task fails during execute(). Wraps the original exception."""

    def __init__(self, stage: str, task_name: str, original_exception: Exception):
        self.stage = stage
        self.task_name = task_name
        self.original_exception = original_exception
        super().__init__(
            f"[{stage}] Task '{task_name}' failed: "
            f"{type(original_exception).__name__}: {original_exception}"
        )
