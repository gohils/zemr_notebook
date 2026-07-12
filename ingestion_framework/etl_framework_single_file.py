"""
================================================================================
 Single-File Configuration-Driven ETL Framework
================================================================================
Everything lives in one script:
  - ETLBase (abstract) + 5 stage base classes
  - PipelineContext (state passed between every task)
  - Concrete demo task classes for all 5 stages
  - PipelineExecutor (reads a config dict/JSON, dynamically resolves + runs tasks)
  - A runnable demo at the bottom, in the same spirit as:
        result = Extract(input_dataframe=input_df, ...).run()
    but driven entirely by config (module/class_name/parameters), matching the
    architecture: pre_processing -> extract -> technical_transformations ->
    load -> post_processing.

Run directly:
    python etl_framework_single_file.py
================================================================================
"""

from __future__ import annotations

import importlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


# ================================================================================
# 1. EXCEPTIONS
# ================================================================================

class ETLFrameworkError(Exception):
    """Base exception for all framework-level errors."""


class ConfigError(ETLFrameworkError):
    """Raised when the config is missing, malformed, or missing required keys."""


class TaskLoadError(ETLFrameworkError):
    """Raised when a module/class referenced in the config cannot be resolved."""


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


# ================================================================================
# 2. PIPELINE CONTEXT  (the object passed between every task, in every stage)
# ================================================================================

@dataclass
class PipelineContext:
    data: Any = None                                    # working dataset
    file_paths: List[str] = field(default_factory=list)  # files touched so far
    metadata: Dict[str, Any] = field(default_factory=dict)  # cross-task info
    pipeline_config: Optional[Dict[str, Any]] = None     # full parsed config

    def set_data(self, data: Any) -> None:
        self.data = data

    def add_file_path(self, path: str) -> None:
        self.file_paths.append(path)

    def set_meta(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def get_meta(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    def row_count(self) -> Optional[int]:
        try:
            return len(self.data)
        except TypeError:
            return None


# ================================================================================
# 3. ETLBase (ABC) + STAGE BASE CLASSES
# ================================================================================

class ETLBase(ABC):
    """Abstract base class every task in every stage derives from."""

    stage_name: str = "generic"   # overridden by each stage base class below

    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.parameters = parameters or {}
        self.logger = logging.getLogger(f"etl.{self.stage_name}.{self.name}")

    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Implement task logic here. Must return the (possibly mutated) context."""
        raise NotImplementedError

    def run(self, context: PipelineContext) -> PipelineContext:
        """Template method called by PipelineExecutor. Do not override."""
        self.logger.info("START name=%s parameters=%s", self.name, self._safe_params())
        started = time.perf_counter()
        try:
            context = self.execute(context)
        except Exception as exc:  # noqa: BLE001 - intentionally broad, re-raised wrapped
            self.logger.exception("FAILED name=%s", self.name)
            raise ETLTaskError(self.stage_name, self.name, exc) from exc
        elapsed = time.perf_counter() - started
        self.logger.info(
            "COMPLETE name=%s elapsed=%.4fs rows=%s",
            self.name, elapsed, context.row_count(),
        )
        return context

    def _safe_params(self) -> Dict[str, Any]:
        """Redact obviously sensitive keys before logging parameters."""
        sensitive_markers = ("secret", "password", "key", "token")
        return {
            k: ("***REDACTED***" if any(m in k.lower() for m in sensitive_markers) else v)
            for k, v in self.parameters.items()
        }


class PreProcessingTask(ETLBase):
    """Stage 1: unzip, decrypt, validate arrival, rename, move, ..."""
    stage_name = "pre_processing"


class ExtractTask(ETLBase):
    """Stage 2: pull data from a source system into context.data."""
    stage_name = "extract"


class TransformTask(ETLBase):
    """Stage 3: technical transformation (flatten, normalize, cast, ...)."""
    stage_name = "technical_transformation"


class LoadTask(ETLBase):
    """Stage 4: write context.data to a destination."""
    stage_name = "load"


class PostProcessingTask(ETLBase):
    """Stage 5: archive, cleanup, notify, ..."""
    stage_name = "post_processing"


# ================================================================================
# 4. CONCRETE TASK CLASSES  (one small demo implementation per stage)
#    Each derives from its stage base class and implements execute() only.
#    Swap these bodies for real logic (pandas/boto3/requests/etc.) as needed --
#    the base classes and executor never need to change.
# ================================================================================

# ---- Stage 1: Pre-Processing --------------------------------------------------

class UnzipFile(PreProcessingTask):
    """Demo pre-processing step: pretend to unzip an input file."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        suffix = self.parameters.get("suffix", "_UnzipFile")
        context.set_data(str(context.data) + suffix)
        context.add_file_path(f"unzipped::{context.data}")
        return context


class PGPDecryptor(PreProcessingTask):
    """Demo pre-processing step: pretend to decrypt a PGP file."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        suffix = self.parameters.get("suffix", "_PGPDecrypt")
        context.set_data(str(context.data) + suffix)
        context.add_file_path(f"decrypted::{context.data}")
        return context


# ---- Stage 2: Extract ----------------------------------------------------------

class CSVDataSource(ExtractTask):
    """Demo extract step: pretend to read a CSV into a dataset."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        # `input_value` lets the config seed the starting dataset, same role
        # `input_dataframe` played in the plain-class version of this script.
        starting_value = self.parameters.get("input_value", context.data)
        context.set_data(str(starting_value) + "_Extract")
        context.set_meta("source_system", "CSV")
        context.set_meta("extracted_row_count", 1)
        return context


# ---- Stage 3: Technical Transformation -----------------------------------------

class Transform1(TransformTask):
    """Demo transform step (e.g. stands in for JSON flattening)."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        context.set_data(str(context.data) + "_Transform1")
        return context


class Transform2(TransformTask):
    """Demo transform step (e.g. stands in for schema normalization)."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        context.set_data(str(context.data) + "_Transform2")
        context.set_meta("applied_schema", self.parameters.get("target_schema", "n/a"))
        return context


# ---- Stage 4: Load --------------------------------------------------------------

class Load(LoadTask):
    """Demo load step: pretend to write the dataset to a destination."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        context.set_data(str(context.data) + "_Load")
        context.set_meta("load_destination", self.parameters.get("destination_path", "n/a"))
        context.set_meta("loaded_row_count", context.get_meta("extracted_row_count", 1))
        return context


# ---- Stage 5: Post-Processing ---------------------------------------------------

class ArchiveFile(PostProcessingTask):
    """Demo post-processing step: pretend to archive the source file."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        context.set_data(str(context.data) + "_ArchiveFile")
        context.set_meta("archived", True)
        return context


# ================================================================================
# 5. PIPELINE EXECUTOR  (reads config, dynamically resolves + runs tasks)
# ================================================================================

class PipelineExecutor:
    """
    Drives the 5 stages in a fixed order, reading which classes to run (and with
    what parameters) entirely from `config`:

        pre_processing (list of tasks)
            -> extract (single task)
                -> technical_transformations (list of tasks)
                    -> load (single task)
                        -> post_processing (list of tasks)

    Task resolution:
        - If a task's "module" is omitted or "__main__", the class is looked up
          in THIS script's globals() -- everything needed for this demo lives
          in one file.
        - Otherwise, "module" is imported normally via importlib and the class
          is read off it -- this is how the framework scales back out to a
          real multi-file package (etl_framework.datasources.csv, etc.)
          without any change to this executor.
    """

    def __init__(self, config: Union[str, Dict[str, Any]]):
        self.config = self._load_config(config)
        self._validate_config(self.config)
        self.pipeline_meta = self.config.get("data_pipeline", {})

    # -------------------- config loading / validation --------------------

    @staticmethod
    def _load_config(config: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(config, dict):
            return config
        with open(config, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as exc:
                raise ConfigError(f"Invalid JSON in {config}: {exc}") from exc

    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        for key in ("extract", "load"):
            if key not in config:
                raise ConfigError(f"config missing required section: '{key}'")
            for req in ("class_name",):
                if req not in config[key]:
                    raise ConfigError(f"'{key}' block missing '{req}'")

    # -------------------- dynamic task resolution --------------------

    @staticmethod
    def _instantiate_task(task_def: Dict[str, Any]) -> ETLBase:
        module_path = task_def.get("module", "__main__")
        class_name = task_def["class_name"]
        name = task_def.get("name", class_name)
        parameters = task_def.get("parameters", {})

        if module_path in (None, "__main__"):
            task_class = globals().get(class_name)
            if task_class is None:
                raise TaskLoadError(f"Class '{class_name}' not found in this script")
        else:
            try:
                module = importlib.import_module(module_path)
            except ImportError as exc:
                raise TaskLoadError(f"Could not import module '{module_path}': {exc}") from exc
            task_class = getattr(module, class_name, None)
            if task_class is None:
                raise TaskLoadError(f"Module '{module_path}' has no class '{class_name}'")

        if not issubclass(task_class, ETLBase):
            raise TaskLoadError(f"{class_name} does not derive from ETLBase")

        return task_class(name=name, parameters=parameters)

    def _run_task_list(self, section_name: str, context: PipelineContext) -> PipelineContext:
        section = self.config.get(section_name)
        if not section or "tasks" not in section:
            logging.getLogger("etl.executor").info("No tasks for stage '%s' - skipping", section_name)
            return context
        for task_def in section["tasks"]:
            task = self._instantiate_task(task_def)
            context = task.run(context)
        return context

    def _run_single_task(self, section_name: str, context: PipelineContext) -> PipelineContext:
        section = self.config.get(section_name)
        if not section:
            logging.getLogger("etl.executor").info("No config for stage '%s' - skipping", section_name)
            return context
        task = self._instantiate_task({**section, "name": section.get("name", section_name)})
        return task.run(context)

    # -------------------- public API --------------------

    def run(self, initial_data: Any = None) -> PipelineContext:
        logger = logging.getLogger("etl.executor")
        pipeline_name = self.pipeline_meta.get("pipeline_name", "unnamed_pipeline")
        pipeline_id = self.pipeline_meta.get("pipeline_id", "unknown_id")
        logger.info("=== PIPELINE START: %s (%s) ===", pipeline_name, pipeline_id)

        context = PipelineContext(data=initial_data, pipeline_config=self.config)
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


# ================================================================================
# 6. DEMO / ENTRYPOINT
# ================================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)-38s | %(message)s",
        datefmt="%H:%M:%S",
    )

    input_df = "df1"
    app_input_param = "zparams1"

    # ---------------------------------------------------------------------
    # 6a. Direct instantiation (no config) -- same pattern as calling
    #     Extract(...).run() directly, just now going through ETLBase.run()
    #     instead of execute() so logging/error-handling apply automatically.
    # ---------------------------------------------------------------------
    print("--- direct call (no config) ---")
    result = CSVDataSource(
        name="extract_direct",
        parameters={"input_value": input_df, "app_input_param": app_input_param},
    ).run(PipelineContext())
    print(result.data)

    # ---------------------------------------------------------------------
    # 6b. Build the 5-stage config, matching the pipeline diagram exactly:
    #     pre_processing -> extract -> technical_transformations -> load -> post_processing
    # ---------------------------------------------------------------------
    config_dict = {
        "data_pipeline": {
            "pipeline_name": "demo_single_file_pipeline",
            "pipeline_id": "dp001",
        },
        "pre_processing": {
            "tasks": [
                {
                    "name": "unzip_input_file",
                    "module": "__main__",
                    "class_name": "UnzipFile",
                    "parameters": {"suffix": "_UnzipFile"},
                },
                {
                    "name": "decrypt_file",
                    "module": "__main__",
                    "class_name": "PGPDecryptor",
                    "parameters": {"suffix": "_PGPDecrypt"},
                },
            ]
        },
        "extract": {
            "name": "extract_csv",
            "module": "__main__",
            "class_name": "CSVDataSource",
            "parameters": {"input_value": input_df, "app_input_param": app_input_param},
        },
        "technical_transformations": {
            "tasks": [
                {
                    "name": "transform1",
                    "module": "__main__",
                    "class_name": "Transform1",
                    "parameters": {"app_input_param": app_input_param},
                },
                {
                    "name": "transform2",
                    "module": "__main__",
                    "class_name": "Transform2",
                    "parameters": {"target_schema": "customer_v1"},
                },
            ]
        },
        "load": {
            "name": "load_output",
            "module": "__main__",
            "class_name": "Load",
            "parameters": {"destination_path": "/tmp/output/customer"},
        },
        "post_processing": {
            "tasks": [
                {
                    "name": "archive_source_file",
                    "module": "__main__",
                    "class_name": "ArchiveFile",
                    "parameters": {},
                }
            ]
        },
    }

    file_path = "./etl_pipe1_config.json"
    with open(file_path, "w") as f:
        json.dump(config_dict, f, indent=2)

    # ---------------------------------------------------------------------
    # 6c. Read config.json back from disk (as it would be in a real deploy)
    #     and run the full 5-stage pipeline through PipelineExecutor.
    # ---------------------------------------------------------------------
    with open(file_path, "r") as f:
        loaded_config = json.load(f)

    print("\nstart of ETL json workflow ===========> ", input_df)
    executor = PipelineExecutor(loaded_config)
    final_context = executor.run(initial_data=input_df)
    print("End of ETL json workflow ===========> ", final_context.data)
    print("Metadata:", final_context.metadata)
    print("Files touched:", final_context.file_paths)
