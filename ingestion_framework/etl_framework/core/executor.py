"""
PipelineExecutor

Reads config.json and drives the 5 stages in order:

    pre_processing (list of tasks)
        -> extract (single task)
            -> technical_transformations (list of tasks)
                -> load (single task)
                    -> post_processing (list of tasks)

Every task, regardless of stage, is defined in the config as:
    {
        "name": "...",
        "module": "dotted.module.path",
        "class_name": "ClassName",
        "parameters": { ... }
    }

The executor dynamically imports `module`, resolves `class_name` from it,
instantiates it with (name, parameters), and calls `.run(context)`. This
means adding a new task type is just: write a class deriving from ETLBase
(or one of the stage-specific subclasses) and reference it in config.json --
no changes to the executor are ever required.
"""

from __future__ import annotations
import importlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

from etl_framework.core.base import ETLBase
from etl_framework.core.context import PipelineContext
from etl_framework.core.exceptions import ConfigError, TaskLoadError

logger = logging.getLogger("etl.executor")


class PipelineExecutor:
    def __init__(self, config: Union[str, Path, Dict[str, Any]]):
        self.config = self._load_config(config)
        self._validate_config(self.config)
        self.pipeline_meta = self.config["data_pipeline"]

    # ------------------------------------------------------------------ #
    # Config loading / validation
    # ------------------------------------------------------------------ #
    @staticmethod
    def _load_config(config: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(config, dict):
            return config
        path = Path(config)
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc

    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        required_top_level = ["data_pipeline", "extract", "load"]
        missing = [k for k in required_top_level if k not in config]
        if missing:
            raise ConfigError(f"config.json missing required section(s): {missing}")
        for key in ("module", "class_name"):
            if key not in config["extract"]:
                raise ConfigError(f"'extract' block missing '{key}'")
            if key not in config["load"]:
                raise ConfigError(f"'load' block missing '{key}'")

    # ------------------------------------------------------------------ #
    # Dynamic class loading / instantiation
    # ------------------------------------------------------------------ #
    @staticmethod
    def _instantiate_task(task_def: Dict[str, Any]) -> ETLBase:
        module_path = task_def["module"]
        class_name = task_def["class_name"]
        name = task_def.get("name", class_name)
        parameters = task_def.get("parameters", {})

        try:
            module = importlib.import_module(module_path)
        except ImportError as exc:
            raise TaskLoadError(f"Could not import module '{module_path}': {exc}") from exc

        try:
            task_class = getattr(module, class_name)
        except AttributeError as exc:
            raise TaskLoadError(
                f"Module '{module_path}' has no class '{class_name}'"
            ) from exc

        if not issubclass(task_class, ETLBase):
            raise TaskLoadError(
                f"{module_path}.{class_name} does not derive from ETLBase"
            )

        return task_class(name=name, parameters=parameters)

    def _run_task_list(self, section_name: str, context: PipelineContext) -> PipelineContext:
        section = self.config.get(section_name)
        if not section or "tasks" not in section:
            logger.info("No tasks configured for stage '%s' - skipping", section_name)
            return context
        for task_def in section["tasks"]:
            task = self._instantiate_task(task_def)
            context = task.run(context)
        return context

    def _run_single_task(self, section_name: str, context: PipelineContext) -> PipelineContext:
        section = self.config.get(section_name)
        if not section:
            logger.info("No config for stage '%s' - skipping", section_name)
            return context
        task = self._instantiate_task({**section, "name": section.get("name", section_name)})
        return task.run(context)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(self) -> PipelineContext:
        pipeline_name = self.pipeline_meta.get("pipeline_name", "unnamed_pipeline")
        pipeline_id = self.pipeline_meta.get("pipeline_id", "unknown_id")
        logger.info("=== PIPELINE START: %s (%s) ===", pipeline_name, pipeline_id)

        context = PipelineContext(pipeline_config=self.config)
        context.set_meta("pipeline_name", pipeline_name)
        context.set_meta("pipeline_id", pipeline_id)

        try:
            context = self._run_task_list("pre_processing", context)
            context = self._run_single_task("extract", context)
            context = self._run_task_list("technical_transformations", context)
            context = self._run_single_task("load", context)
            context = self._run_task_list("post_processing", context)
        except Exception:
            logger.exception("=== PIPELINE FAILED: %s (%s) ===", pipeline_name, pipeline_id)
            raise

        logger.info("=== PIPELINE COMPLETE: %s (%s) ===", pipeline_name, pipeline_id)
        return context
