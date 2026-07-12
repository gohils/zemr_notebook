"""
ETLBase: the single abstract base class that every pipeline task
(pre-processing, extract, transform, load, post-processing) derives from.

Design:
- Every concrete task is instantiated with (name, parameters) taken straight
  from a block in config.json.
- The framework calls `.run(context)` (not `.execute()` directly). `run()`
  is a template method that adds logging, timing and uniform error handling
  around the subclass-supplied `.execute()`.
- Subclasses only need to implement `execute(context) -> PipelineContext`.

Stage-specific base classes (PreProcessingTask, ExtractTask, TransformTask,
LoadTask, PostProcessingTask) subclass ETLBase purely for readability /
type-clarity in the concrete implementations; they add no new contract.
"""

from __future__ import annotations
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict

from etl_framework.core.context import PipelineContext
from etl_framework.core.exceptions import ETLTaskError


class ETLBase(ABC):
    """Abstract base class for every executable unit in the pipeline."""

    #: overridden by stage-specific subclasses purely for logging clarity
    stage_name: str = "generic"

    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.parameters = parameters or {}
        self.logger = logging.getLogger(f"etl.{self.stage_name}.{self.name}")

    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Perform the task's work and return the (possibly mutated) context.
        Must be implemented by every concrete task.
        """
        raise NotImplementedError

    def run(self, context: PipelineContext) -> PipelineContext:
        """Template method invoked by the PipelineExecutor. Do not override."""
        self.logger.info("START name=%s parameters=%s", self.name, self._safe_params())
        started = time.perf_counter()
        try:
            context = self.execute(context)
        except Exception as exc:  # noqa: BLE001 - intentionally broad, re-raised wrapped
            self.logger.exception("FAILED name=%s", self.name)
            raise ETLTaskError(self.stage_name, self.name, exc) from exc
        elapsed = time.perf_counter() - started
        self.logger.info(
            "COMPLETE name=%s elapsed=%.3fs rows=%s",
            self.name, elapsed, context.row_count(),
        )
        return context

    def _safe_params(self) -> Dict[str, Any]:
        """Redact obviously sensitive keys before logging parameters."""
        redacted = {}
        sensitive_markers = ("secret", "password", "key", "token")
        for k, v in self.parameters.items():
            if any(marker in k.lower() for marker in sensitive_markers):
                redacted[k] = "***REDACTED***"
            else:
                redacted[k] = v
        return redacted


class PreProcessingTask(ETLBase):
    """Base class for Stage 1: unzip, decrypt, validate arrival, rename, move, ..."""
    stage_name = "pre_processing"


class ExtractTask(ETLBase):
    """Base class for Stage 2: pull data from a source system into context.data."""
    stage_name = "extract"


class TransformTask(ETLBase):
    """Base class for Stage 3: technical transformation (flatten, normalize, cast, ...)."""
    stage_name = "technical_transformation"


class LoadTask(ETLBase):
    """Base class for Stage 4: write context.data to a destination (S3, Parquet, ...)."""
    stage_name = "load"


class PostProcessingTask(ETLBase):
    """Base class for Stage 5: archive, cleanup, notify, ..."""
    stage_name = "post_processing"
