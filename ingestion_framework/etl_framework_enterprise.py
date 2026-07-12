"""
================================================================================
 Enterprise Config-Driven ETL Framework  (single-file template)
================================================================================
Combines:
  - the clean, minimal-dependency task/stage shape (ETLBase -> 5 stage base
    classes -> PipelineContext -> PipelineExecutor iterating a fixed stage list)
  - production-readiness fixes needed before this pattern is safe to run at
    enterprise scale:
        1. Dynamic task loading that ACTUALLY imports the module named in
           config (the previous version silently ignored `module` and only
           ever loaded classes from its own file -- ok for a demo, breaks
           the moment two teams want to own their own connector files).
        2. Structured `logging` instead of `print()` (log levels, timestamps,
           routable to Splunk/ELK/Datadog).
        3. A small exception hierarchy (ConfigError / TaskLoadError /
           ETLTaskError) so failures are diagnosable by category, not just a
           bare re-raised exception.
        4. Config validation at startup, not discovered mid-run.
        5. Secret-parameter redaction in logs.
        6. Per-task timing.
        7. get_meta()/set_meta() with default support, not just a setter.

No third-party dependencies -- runs anywhere with a stock Python 3.9+.
(Swap the list-of-dicts `data` payload for pandas/Spark/Polars in your own
 concrete task classes; nothing in ETLBase/PipelineContext/PipelineExecutor
 assumes a particular data engine.)

Run directly:
    python etl_framework_enterprise.py
================================================================================
"""

from __future__ import annotations

import importlib
import json
import logging
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
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
    """Raised when a task fails during execute(). Wraps the original exception
    so callers can branch on `.stage` / `.task_name` without parsing strings."""

    def __init__(self, stage: str, task_name: str, original_exception: Exception):
        self.stage = stage
        self.task_name = task_name
        self.original_exception = original_exception
        super().__init__(
            f"[{stage}] Task '{task_name}' failed: "
            f"{type(original_exception).__name__}: {original_exception}"
        )


# ================================================================================
# 2. SECRETS  (stub resolver -- swap the body for Vault/AWS Secrets Manager/etc.)
# ================================================================================

import os


def resolve_secret(secret_reference: str) -> str:
    """
    Resolve a secret_reference (e.g. 'sftp/partner/password') to an actual value.

    Default implementation: environment variable lookup. Replace with a real
    secrets-manager client in production:

        import boto3
        _client = boto3.client("secretsmanager")
        def resolve_secret(secret_reference):
            return _client.get_secret_value(SecretId=secret_reference)["SecretString"]

    Every task needing credentials should call this rather than reading a raw
    secret out of `parameters` -- it's the one place the secrets backend lives.
    """
    env_var = secret_reference.upper().replace("/", "_").replace("-", "_")
    value = os.environ.get(env_var)
    if value is None:
        raise KeyError(
            f"Could not resolve secret_reference='{secret_reference}' "
            f"(expected env var '{env_var}' to be set)"
        )
    return value


# ================================================================================
# 3. PIPELINE CONTEXT  (state passed between every task, in every stage)
# ================================================================================

@dataclass
class PipelineContext:
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    files: List[str] = field(default_factory=list)
    pipeline_config: Optional[Dict[str, Any]] = None

    def set_data(self, data: Any) -> None:
        self.data = data

    def add_file(self, path: str) -> None:
        self.files.append(path)

    def set_meta(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    # kept as an alias so code written against the "add_metadata" naming still works
    add_metadata = set_meta

    def get_meta(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    def row_count(self) -> Optional[int]:
        try:
            return len(self.data)
        except TypeError:
            return None


# ================================================================================
# 4. ETLBase (ABC) + STAGE BASE CLASSES
# ================================================================================

class ETLBase(ABC):
    """Abstract base class every task in every stage derives from."""

    stage_name: str = "generic"   # overridden per stage below

    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.parameters = parameters or {}
        self.logger = logging.getLogger(f"etl.{self.stage_name}.{self.name}")

    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Implement task logic here. Must return the (possibly mutated) context."""
        raise NotImplementedError

    def run(self, context: PipelineContext) -> PipelineContext:
        """Template method invoked by PipelineExecutor. Do not override."""
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
        """Redact obviously sensitive parameter values before logging them."""
        sensitive_markers = ("secret", "password", "token", "_key", "apikey")
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
    stage_name = "technical_transform"


class LoadTask(ETLBase):
    """Stage 4: write context.data to a destination."""
    stage_name = "load"


class PostProcessingTask(ETLBase):
    """Stage 5: archive, cleanup, notify, ..."""
    stage_name = "post_processing"


# ================================================================================
# 5. EXAMPLE TASK CLASSES  (one small concrete implementation per stage)
#    Swap bodies for real logic (pandas/boto3/requests/DB drivers/etc.) --
#    ETLBase / PipelineContext / PipelineExecutor never need to change.
# ================================================================================

class UnzipFile(PreProcessingTask):
    """
    parameters:
        input_file : path to the source archive (e.g. 'customer.zip')
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        input_file = self.parameters["input_file"]
        self.logger.info("Unzipping: %s", input_file)
        context.add_file(input_file.replace(".zip", ".csv"))
        return context


class CSVExtractor(ExtractTask):
    """
    parameters:
        file_path : path to the CSV to read (stubbed here as an in-memory
                    list[dict]; swap for pandas.read_csv / your real reader)
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        file_path = self.parameters["file_path"]
        self.logger.info("Reading CSV: %s", file_path)

        # Stand-in for a real read (pandas.read_csv, etc.)
        df = [{"id": 1, "name": "John"}, {"id": 2, "name": "Mary"}]

        context.set_data(df)
        context.set_meta("source", file_path)
        context.set_meta("extracted_row_count", len(df))
        return context


class ColumnNormalizer(TransformTask):
    """Uppercases the 'name' key to 'NAME' as a stand-in for real schema work."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        self.logger.info("Normalizing columns")
        for row in context.data:
            row["NAME"] = row.pop("name")
        return context


class AddAuditColumn(TransformTask):
    """
    parameters:
        source_system : value to stamp onto every row (default 'CRM')
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        source_system = self.parameters.get("source_system", "CRM")
        self.logger.info("Adding audit column: source_system=%s", source_system)
        for row in context.data:
            row["source_system"] = source_system
        return context


class CSVLoader(LoadTask):
    """
    parameters:
        target_path : destination path (stubbed -- swap for a real writer)
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        target = self.parameters["target_path"]
        self.logger.info("Writing output: %s (%d rows)", target, len(context.data))
        context.set_meta("target", target)
        context.set_meta("loaded_row_count", len(context.data))
        return context


class ArchiveFile(PostProcessingTask):
    """Archives every file tracked in context.files during this run."""

    def execute(self, context: PipelineContext) -> PipelineContext:
        self.logger.info("Archiving files: %s", context.files)
        context.set_meta("archived_files", list(context.files))
        return context


# ================================================================================
# 6. DYNAMIC TASK LOADER  (the piece that actually has to work correctly)
# ================================================================================

# The name this module is known by. When run as a script this is "__main__";
# when imported elsewhere (e.g. `import etl_framework_enterprise`) it's the
# real dotted path. Either way, config entries using the sentinel "__main__"
# (or omitting "module" entirely) resolve to THIS file's own classes.
_SELF_MODULE_NAME = __name__


def create_task(task_config: Dict[str, Any]) -> ETLBase:
    """
    Resolve `module` + `class_name` from a task config block into an
    instantiated ETLBase subclass.

    Unlike a naive version of this function, `module_name` is actually used
    to import whatever module the config names -- a config pointing at
    "finance_team.connectors.sap_extractor" really does import that module,
    rather than silently falling back to this file. That's what makes the
    framework usable across teams/repos, not just within one script.
    """
    if "class_name" not in task_config:
        raise ConfigError(f"Task config missing 'class_name': {task_config}")

    module_name = task_config.get("module", "__main__")
    class_name = task_config["class_name"]
    name = task_config.get("name", class_name)
    parameters = task_config.get("parameters", {})

    try:
        if module_name in (None, "", "__main__", _SELF_MODULE_NAME):
            module = sys.modules[_SELF_MODULE_NAME]
        else:
            module = importlib.import_module(module_name)
    except ImportError as exc:
        raise TaskLoadError(f"Could not import module '{module_name}': {exc}") from exc

    task_class = getattr(module, class_name, None)
    if task_class is None:
        raise TaskLoadError(f"Module '{module_name}' has no class '{class_name}'")

    if not (isinstance(task_class, type) and issubclass(task_class, ETLBase)):
        raise TaskLoadError(f"{module_name}.{class_name} does not derive from ETLBase")

    return task_class(name=name, parameters=parameters)


# ================================================================================
# 7. PIPELINE EXECUTOR
# ================================================================================

class PipelineExecutor:
    """
    Drives the 5 stages, in this fixed order, entirely from `config`:

        pre_processing (0..N tasks)
            -> extract (exactly 1 task)
                -> technical_transformations (0..N tasks)
                    -> load (exactly 1 task)
                        -> post_processing (0..N tasks)
    """

    STAGE_ORDER = (
        "pre_processing",
        "extract",
        "technical_transformations",
        "load",
        "post_processing",
    )
    SINGLE_TASK_STAGES = {"extract", "load"}

    def __init__(self, config: Union[str, Path, Dict[str, Any]]):
        self.config = self._load_config(config)
        self._validate_config(self.config)
        self.logger = logging.getLogger("etl.executor")

    # -------------------- config loading / validation --------------------

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

    def _validate_config(self, config: Dict[str, Any]) -> None:
        for required in ("extract", "load"):
            if required not in config:
                raise ConfigError(f"config missing required section: '{required}'")

        for stage_name in self.STAGE_ORDER:
            stage = config.get(stage_name)
            if not stage:
                continue
            task_defs = stage["tasks"] if "tasks" in stage else [stage]
            for task_def in task_defs:
                if "class_name" not in task_def:
                    raise ConfigError(
                        f"Stage '{stage_name}' has a task missing 'class_name': {task_def}"
                    )

    # -------------------- stage execution --------------------

    def _execute_stage(self, stage_name: str, context: PipelineContext) -> PipelineContext:
        stage = self.config.get(stage_name)
        if not stage:
            self.logger.info("No config for stage '%s' - skipping", stage_name)
            return context

        if "tasks" in stage:
            for task_def in stage["tasks"]:
                task = create_task(task_def)
                context = task.run(context)
        else:
            task = create_task(stage)
            context = task.run(context)

        return context

    # -------------------- public API --------------------

    def run(self, initial_data: Any = None) -> PipelineContext:
        pipeline_meta = self.config.get("pipeline", {})
        pipeline_name = pipeline_meta.get("name", "unnamed_pipeline")

        self.logger.info("=== PIPELINE START: %s ===", pipeline_name)
        context = PipelineContext(data=initial_data, pipeline_config=self.config)
        context.set_meta("pipeline_name", pipeline_name)

        try:
            for stage_name in self.STAGE_ORDER:
                context = self._execute_stage(stage_name, context)
        except ETLFrameworkError:
            self.logger.exception("=== PIPELINE FAILED: %s ===", pipeline_name)
            raise

        self.logger.info("=== PIPELINE COMPLETE: %s ===", pipeline_name)
        return context


# ================================================================================
# 8. DEMO / ENTRYPOINT
# ================================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)-32s | %(message)s",
        datefmt="%H:%M:%S",
    )

    config = {
        "pipeline": {
            "name": "crm_sales_pipeline"
        },

        "pre_processing": {
            "tasks": [
                {
                    "name": "unzip_customer_file",
                    "module": "__main__",
                    "class_name": "UnzipFile",
                    "parameters": {"input_file": "customer.zip"},
                }
            ]
        },

        "extract": {
            "name": "read_customer_csv",
            "module": "__main__",
            "class_name": "CSVExtractor",
            "parameters": {"file_path": "customer.csv"},
        },

        "technical_transformations": {
            "tasks": [
                {
                    "name": "normalize_columns",
                    "module": "__main__",
                    "class_name": "ColumnNormalizer",
                    "parameters": {},
                },
                {
                    "name": "add_audit",
                    "module": "__main__",
                    "class_name": "AddAuditColumn",
                    "parameters": {"source_system": "CRM"},
                },
            ]
        },

        "load": {
            "name": "load_customer",
            "module": "__main__",
            "class_name": "CSVLoader",
            "parameters": {"target_path": "/output/customer.csv"},
        },

        "post_processing": {
            "tasks": [
                {
                    "name": "archive",
                    "module": "__main__",
                    "class_name": "ArchiveFile",
                    "parameters": {},
                }
            ]
        },
    }

    # Round-trip through disk, the way a real deployment would load it --
    # proves the config is genuinely JSON-serializable, not just a Python dict.
    config_path = "./etl_pipe1_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    with open(config_path, "r") as f:
        loaded_config = json.load(f)

    executor = PipelineExecutor(loaded_config)
    result = executor.run()

    print("\n===================")
    print("FINAL DATA:")
    print(result.data)
    print("\nMETADATA:")
    print(result.metadata)
    print("\nFILES:")
    print(result.files)
