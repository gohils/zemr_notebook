# Developer Guide: Configuration-Driven ETL Framework

**Audience:** Engineers building or extending data ingestion pipelines on this framework
**Scope:** Architecture, extension points, and end-to-end examples for all five pipeline stages
**Framework version:** 1.0

---

## Table of Contents

1. [Purpose and Design Philosophy](#1-purpose-and-design-philosophy)
2. [Architecture Overview](#2-architecture-overview)
3. [Core Concepts](#3-core-concepts)
4. [Repository Layout](#4-repository-layout)
5. [Installation and Local Setup](#5-installation-and-local-setup)
6. [Running a Pipeline](#6-running-a-pipeline)
7. [The config.json Contract](#7-the-configjson-contract)
8. [Extension Guide: Stage 1 — Pre-Processing](#8-extension-guide-stage-1--pre-processing)
9. [Extension Guide: Stage 2 — Extract](#9-extension-guide-stage-2--extract)
10. [Extension Guide: Stage 3 — Technical Transformation](#10-extension-guide-stage-3--technical-transformation)
11. [Extension Guide: Stage 4 — Load](#11-extension-guide-stage-4--load)
12. [Extension Guide: Stage 5 — Post-Processing](#12-extension-guide-stage-5--post-processing)
13. [Unit Testing New Tasks](#13-unit-testing-new-tasks)
14. [Secrets Management](#14-secrets-management)
15. [Logging, Observability, and Lineage](#15-logging-observability-and-lineage)
16. [Error Handling and Retry Strategy](#16-error-handling-and-retry-strategy)
17. [Enterprise Considerations](#17-enterprise-considerations)
18. [New-Task Checklist (Definition of Done)](#18-new-task-checklist-definition-of-done)
19. [Appendix A: Full Class Reference](#19-appendix-a-full-class-reference)
20. [Appendix B: FAQ](#20-appendix-b-faq)

---

## 1. Purpose and Design Philosophy

This framework exists so that **adding a new data source, transformation, or destination
never requires touching the pipeline engine**. A pipeline is fully described by a
`config.json` file; the engine (`PipelineExecutor`) only knows how to read that file and
call `.run()` on whatever classes it points to.

Three design rules fall out of that goal, and every contribution should be checked
against them:

| Rule | Why it matters |
|---|---|
| **One contract, five stages.** Every task — regardless of stage — derives from `ETLBase` and implements exactly one method: `execute(context) -> context`. | Keeps the executor's code stage-agnostic and trivially small. |
| **State flows through `PipelineContext`, never through instance attributes.** | Makes tasks stateless, reusable across runs, and safe to unit test in isolation. |
| **Configuration, not code, controls what runs.** New sources/sinks are *registered by writing a class*, not by editing an if/else chain anywhere. | Enables non-engineers (config owners) to compose pipelines from an existing catalog of tasks. |

If a change you're making requires editing `PipelineExecutor` to special-case your new
class, stop — that's a signal the class should conform to the existing contract instead.

---

## 2. Architecture Overview
# ETL Framework

A config-driven ETL framework. Every task in every stage derives from a single
abstract base class, `ETLBase`, and is wired together purely through
`config.json` — no code changes needed to add, remove, or reorder tasks.

```
                  Data Source
                      |
                      v
=================================================
Stage 1: PRE-PROCESSING
=================================================
- unzip files
- decrypt files
- validate file arrival
- rename files
- move files
                      |
                      v
=================================================
Stage 2: EXTRACT
=================================================
- REST API
- Database
- CSV
- JSON
- SFTP
- Kafka
                      |
                      v
=================================================
Stage 3: TECHNICAL TRANSFORMATION
=================================================
- JSON flattening
- schema normalization
- datatype standardization
- encoding conversion
- technical cleansing
                      |
                      v
=================================================
Stage 4: LOAD
=================================================
- GCS
- ADLS
- S3
- BigQuery
- Delta
- Parquet
                      |
                      v
=================================================
Stage 5: POST-PROCESSING
=================================================
- archive source files
- move processed files
- cleanup temporary files
- notification
```

```
                         config.json
                              │
                              ▼
                     ┌─────────────────┐
                     │ PipelineExecutor │
                     └─────────────────┘
                              │
   ┌──────────────────────────────────────────────────────────┐
   │                                                            │
   ▼                                                            ▼
Stage 1: PRE-PROCESSING (0..N tasks)          Stage 4: LOAD (exactly 1 task)
  UnzipFile, PGPDecryptor, ...                  ParquetLoader, S3Loader, ...
   │                                                            ▲
   ▼                                                            │
Stage 2: EXTRACT (exactly 1 task)             Stage 3: TECHNICAL TRANSFORMATION (0..N)
  CSVDataSource, RestApiDataSource, ...  ───►    JSONFlatten, SchemaNormalizer, ...
                                                            │
                                                            ▼
                                          Stage 5: POST-PROCESSING (0..N tasks)
                                            ArchiveFile, NotifierTask, ...
```

Every arrow above is a `PipelineContext` object being handed from one task's `run()`
return value into the next task's `run()` call. The executor does not know or care what
a task does internally — only that it accepts and returns a `PipelineContext`.

**Execution order is fixed and non-configurable:** pre_processing → extract →
technical_transformations → load → post_processing. What *is* configurable is which
classes run inside each stage, and in what order within `pre_processing`,
`technical_transformations`, and `post_processing` (the executor iterates the `tasks`
list in the order it's declared).

---

## 3. Core Concepts

### 3.1 `ETLBase` — the single abstract contract

```python
# etl_framework/core/base.py
class ETLBase(ABC):
    stage_name: str = "generic"

    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.parameters = parameters or {}
        self.logger = logging.getLogger(f"etl.{self.stage_name}.{self.name}")

    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError

    def run(self, context: PipelineContext) -> PipelineContext:
        # logging + timing + exception wrapping around execute() — do not override
        ...
```

Two methods matter, and they matter for different people:

- **`execute()`** is what *you* write when adding a new task. This is where your logic lives.
- **`run()`** is what the *executor* calls. It is a template method — logging, timing, and
  uniform error translation into `ETLTaskError` happen here, automatically, for every task
  in the framework. **Never override `run()`.**

### 3.2 Stage base classes

`PreProcessingTask`, `ExtractTask`, `TransformTask`, `LoadTask`, `PostProcessingTask` all
subclass `ETLBase` and add nothing except a `stage_name` value used in log lines
(`etl.<stage_name>.<task_name>`). Always derive from the stage-specific base rather than
`ETLBase` directly — it's what makes log output and stack traces immediately tell you
which stage failed.

### 3.3 `PipelineContext` — the state object

```python
# etl_framework/core/context.py
@dataclass
class PipelineContext:
    data: Any = None                          # working dataset (pandas.DataFrame by convention)
    file_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    pipeline_config: Optional[Dict[str, Any]] = None
```

| Field | Convention |
|---|---|
| `data` | The dataset in flight. `ExtractTask`s populate it; `TransformTask`s reassign it; `LoadTask`s read it. Pandas `DataFrame` by convention — see §17.3 if you need to swap engines. |
| `file_paths` | Running list of files touched by the run (unzipped files, decrypted files, extracted files). Append via `context.add_file_path(path)`; never used by the executor itself — purely for downstream tasks/lineage/debugging. |
| `metadata` | Free-form dict for cross-task communication (row counts, applied schema name, source system, etc). Use `context.set_meta(key, value)` / `context.get_meta(key, default)`. |
| `pipeline_config` | The full parsed `config.json`. Available if a task needs cross-cutting info (e.g. `pipeline_id` for lineage tagging) — use sparingly; prefer `parameters` for anything task-specific. |

**Rule of thumb:** if two tasks need to communicate something that isn't the dataset
itself, put it in `metadata`, not in an instance attribute on either task. Tasks are
instantiated fresh per run and should hold no state between `execute()` calls.

### 3.4 `PipelineExecutor` — the engine

```python
# etl_framework/core/executor.py
class PipelineExecutor:
    def __init__(self, config: Union[str, Path, Dict[str, Any]]): ...
    def run(self) -> PipelineContext: ...
```

On `run()`, for every task block in the config it does, in essence:

```python
module = importlib.import_module(task_def["module"])
task_class = getattr(module, task_def["class_name"])
task = task_class(name=task_def["name"], parameters=task_def["parameters"])
context = task.run(context)
```

This is the entire extension mechanism. There is no plugin registry to update, no
factory function to edit, no enum to extend — `module` + `class_name` in JSON *is* the
registration.

---

## 4. Repository Layout

```
etl_project/
├── main.py                              # CLI entrypoint
├── requirements.txt
├── config/
│   ├── config.json                      # production pipeline definitions
│   └── demo_config.json
├── sample_data/
└── etl_framework/
    ├── core/
    │   ├── base.py                      # ETLBase + 5 stage base classes
    │   ├── context.py                   # PipelineContext
    │   ├── executor.py                  # PipelineExecutor
    │   ├── exceptions.py                # ConfigError, TaskLoadError, ETLTaskError
    │   └── logging_setup.py
    ├── preprocessing/                   # Stage 1 — derive from PreProcessingTask
    │   ├── unzip_file.py    (UnzipFile)
    │   └── pgp.py            (PGPDecryptor)
    ├── datasources/                     # Stage 2 — derive from ExtractTask
    │   └── csv.py            (CSVDataSource)
    ├── transformers/                    # Stage 3 — derive from TransformTask
    │   ├── json_flatten.py   (JSONFlatten)
    │   ├── schema.py         (SchemaNormalizer)
    │   └── schema_registry.json
    ├── loaders/                         # Stage 4 — derive from LoadTask
    │   └── parquet.py        (ParquetLoader)
    └── postprocessing/                  # Stage 5 — derive from PostProcessingTask
        └── archive.py        (ArchiveFile)
```

**Convention:** new task modules live in the package matching their stage
(`preprocessing/`, `datasources/`, `transformers/`, `loaders/`, `postprocessing/`), one
class per file, filename in `snake_case` matching the class in `PascalCase`
(`s3_loader.py` → `S3Loader`). This isn't enforced by the executor — `module` in the
config can point anywhere importable — but breaking it makes the codebase harder to
navigate and should be flagged in review.

---

## 5. Installation and Local Setup

```bash
git clone <repo-url>
cd etl_project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt`:

```
pandas>=2.0
pyarrow>=14.0
python-gnupg>=0.5.2   # optional, only needed for PGPDecryptor
```

Stage-specific extensions (S3, REST APIs, databases, Slack, etc.) will add their own
dependencies — see each section below. Pin versions in `requirements.txt` and note the
task(s) that need them with a comment, as done for `python-gnupg`.

---

## 6. Running a Pipeline

```bash
python main.py config/demo_config.json
python main.py config/config.json
```

`main.py`:

```python
from etl_framework.core.executor import PipelineExecutor
from etl_framework.core.logging_setup import configure_logging

configure_logging()
context = PipelineExecutor("config/demo_config.json").run()
print(f"Rows in final dataset: {context.row_count()}")
```

In an orchestrator (Airflow, Dagster, cron, a CI job) this is a two-line integration:

```python
from etl_framework.core.executor import PipelineExecutor

def run_pipeline_task(config_path: str):
    context = PipelineExecutor(config_path).run()
    return context.metadata  # e.g. push row counts / lineage into your metastore
```

`PipelineExecutor.run()` raises on failure (wrapping the original exception in
`ETLTaskError`), so orchestrator retry/alerting policies attach the same way they would
to any other Python task.

---

## 7. The config.json Contract

Every task block, in every stage, has the identical shape:

```json
{
  "name": "human_readable_task_name",
  "module": "etl_framework.<package>.<file>",
  "class_name": "YourTaskClass",
  "parameters": { "...": "task-specific kwargs, passed straight through" }
}
```

| Top-level key | Shape | Required | Notes |
|---|---|---|---|
| `data_pipeline` | object | Yes | Metadata only (`pipeline_name`, `pipeline_id`, etc). Not executed; injected into `context.metadata`. |
| `pre_processing` | `{ "tasks": [ ... ] }` | No | List of task blocks, run in declared order. Empty/absent = skipped. |
| `extract` | single task block | **Yes** | Exactly one task. Must produce `context.data`. |
| `technical_transformations` | `{ "tasks": [ ... ] }` | No | List of task blocks, run in declared order. |
| `load` | single task block | **Yes** | Exactly one task. Reads `context.data`. |
| `post_processing` | `{ "tasks": [ ... ] }` | No | List of task blocks, run in declared order. |

`parameters` is intentionally untyped at the config-parsing layer — validation of
required/optional keys is the responsibility of each task's `execute()` (see the
`self.parameters["required_key"]` vs. `self.parameters.get("optional_key", default)`
pattern used throughout every example below). This keeps `PipelineExecutor` decoupled
from the growing set of parameter shapes as new tasks are added.

> **Enterprise tip:** for teams with many pipelines, consider validating `config.json`
> against a JSON Schema in CI before deployment (structure only — required top-level
> keys, `module`/`class_name`/`parameters` present on every task block). This catches
> typos in `module` paths at merge time instead of at 2am in production. See §17.5.

---

## 8. Extension Guide: Stage 1 — Pre-Processing

**When to add a task here:** anything that needs to happen to raw files *before* they're
readable as structured data — arrival validation, decompression, decryption, renaming,
moving between filesystems/buckets, checksum verification.

**Contract:** `PreProcessingTask.execute(context) -> context`. Typically reads/writes
files on disk (or remote storage) and updates `context.file_paths`; does **not** touch
`context.data` (that doesn't exist yet — extract hasn't run).

### Example: `SFTPFileFetcher`

A common enterprise need: pull the day's file down from a partner's SFTP server before
any local processing can begin.

```python
# etl_framework/preprocessing/sftp_fetch.py
"""Pre-processing task: fetch a file from a remote SFTP server to local disk."""

from __future__ import annotations
import os
import paramiko  # pip install paramiko

from etl_framework.core.base import PreProcessingTask
from etl_framework.core.context import PipelineContext
from etl_framework.preprocessing.pgp import resolve_secret  # reuse existing secret resolver


class SFTPFileFetcher(PreProcessingTask):
    """
    parameters:
        host            : SFTP server hostname
        port            : SFTP port (default 22)
        username        : SFTP username
        password_secret_ref : secret_reference resolved via resolve_secret()
        remote_path     : path to the file on the SFTP server
        local_path      : where to save it locally
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        host = self.parameters["host"]
        port = self.parameters.get("port", 22)
        username = self.parameters["username"]
        password = resolve_secret(self.parameters["password_secret_ref"])
        remote_path = self.parameters["remote_path"]
        local_path = self.parameters["local_path"]

        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)

        transport = paramiko.Transport((host, port))
        try:
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(remote_path, local_path)
        finally:
            transport.close()

        context.add_file_path(local_path)
        context.set_meta("sftp_source_host", host)
        self.logger.info("Fetched %s from %s -> %s", remote_path, host, local_path)
        return context
```

Wire it into `config.json`:

```json
{
  "pre_processing": {
    "tasks": [
      {
        "name": "fetch_partner_file",
        "module": "etl_framework.preprocessing.sftp_fetch",
        "class_name": "SFTPFileFetcher",
        "parameters": {
          "host": "sftp.partner.example.com",
          "username": "svc_ingestion",
          "password_secret_ref": "sftp/partner/password",
          "remote_path": "/outbound/sales_20260712.csv",
          "local_path": "/data/inbound/sales_20260712.csv"
        }
      }
    ]
  }
}
```

**Design notes:**
- Secrets are resolved by reference (`password_secret_ref`), never embedded in
  `config.json` — see §14.
- The task raises on connection/auth failure (no try/except swallowing it) — a missing
  source file is often a hard stop for the pipeline, unlike optional-file scenarios.
  Contrast with `UnzipFile`'s existing warn-and-skip behavior for missing local files;
  choose the failure mode deliberately per task and document it in the docstring.

---

## 9. Extension Guide: Stage 2 — Extract

**When to add a task here:** a new source system type. Exactly one extract task runs
per pipeline, and its job is singular: populate `context.data` with the dataset for this
run.

**Contract:** `ExtractTask.execute(context) -> context`, must call `context.set_data(...)`.

### Example: `RestApiDataSource`

Pulls paginated JSON from a REST API into a DataFrame — a very common enterprise
extract pattern (Salesforce, Workday, internal microservices, etc).

```python
# etl_framework/datasources/rest_api.py
"""Extract task: pull paginated JSON from a REST API into a pandas DataFrame."""

from __future__ import annotations
import pandas as pd
import requests  # pip install requests

from etl_framework.core.base import ExtractTask
from etl_framework.core.context import PipelineContext
from etl_framework.preprocessing.pgp import resolve_secret


class RestApiDataSource(ExtractTask):
    """
    parameters:
        base_url          : API endpoint, e.g. "https://api.crm.example.com/v2/accounts"
        auth_token_secret_ref : secret_reference for a bearer token
        page_param        : query param name for page number (default "page")
        page_size_param    : query param name for page size (default "page_size")
        page_size          : records per page (default 200)
        records_key        : key in the JSON response holding the record list
        max_pages          : safety cap on pagination (default 1000)
        timeout_seconds    : per-request timeout (default 30)
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        base_url = self.parameters["base_url"]
        token = resolve_secret(self.parameters["auth_token_secret_ref"])
        page_param = self.parameters.get("page_param", "page")
        page_size_param = self.parameters.get("page_size_param", "page_size")
        page_size = self.parameters.get("page_size", 200)
        records_key = self.parameters["records_key"]
        max_pages = self.parameters.get("max_pages", 1000)
        timeout = self.parameters.get("timeout_seconds", 30)

        headers = {"Authorization": f"Bearer {token}"}
        all_records = []
        page = 1

        while page <= max_pages:
            response = requests.get(
                base_url,
                headers=headers,
                params={page_param: page, page_size_param: page_size},
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
            records = payload.get(records_key, [])

            if not records:
                break

            all_records.extend(records)
            self.logger.info("Fetched page %d (%d records, %d total)", page, len(records), len(all_records))

            if len(records) < page_size:
                break  # last page
            page += 1

        df = pd.DataFrame(all_records)
        context.set_data(df)
        context.set_meta("source_system", "REST_API")
        context.set_meta("extracted_row_count", len(df))
        context.set_meta("api_pages_fetched", page)
        return context
```

Wire it into `config.json`:

```json
{
  "extract": {
    "module": "etl_framework.datasources.rest_api",
    "class_name": "RestApiDataSource",
    "parameters": {
      "base_url": "https://api.crm.example.com/v2/accounts",
      "auth_token_secret_ref": "crm_api/token",
      "records_key": "data",
      "page_size": 500
    }
  }
}
```

**Design notes:**
- `raise_for_status()` — extract failures should fail the pipeline loudly, not
  silently produce an empty/partial dataset. Compare this to §8's file-not-found
  warn-and-skip pattern: extract is the one stage where a missing/broken source should
  almost always be a hard failure.
- `max_pages` is a deliberate safety cap — enterprise APIs with bugs or unbounded
  pagination have caused real production incidents; don't skip this kind of guard rail
  when writing a new extractor.
- For a **Database** extractor, follow the same shape but replace the `requests` loop
  with SQLAlchemy/`pd.read_sql(query, engine)`; for **Kafka**, consume for a bounded
  window or offset range and build the DataFrame from the consumed batch. The contract
  (`execute()` populates `context.data`) doesn't change.

---

## 10. Extension Guide: Stage 3 — Technical Transformation

**When to add a task here:** structural/technical changes to the dataset — flattening,
type casting, schema mapping, deduplication, encoding fixes, technical cleansing. This
stage is explicitly **not** for business logic (that belongs in a downstream
business-transformation layer, if your platform has one) — keep these tasks source- and
target-agnostic where possible.

**Contract:** `TransformTask.execute(context) -> context`, reads and reassigns
`context.data`.

### Example: `DeduplicationTransformer`

Removes duplicate records based on a business key, keeping the most recently updated row
— a near-universal need before loading to an analytical store.

```python
# etl_framework/transformers/deduplication.py
"""Technical transformation: drop duplicate rows on a business key, keeping the most
recent record according to a tiebreaker column."""

from __future__ import annotations
import pandas as pd

from etl_framework.core.base import TransformTask
from etl_framework.core.context import PipelineContext


class DeduplicationTransformer(TransformTask):
    """
    parameters:
        key_columns       : list of column(s) that define a unique business record
        tiebreaker_column  : column to sort by when resolving duplicates (e.g. an
                              updated_at timestamp or a version number)
        keep               : "last" or "first" after sorting by tiebreaker_column
                              ascending (default "last" = most recent wins)
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        df: pd.DataFrame = context.data
        key_columns = self.parameters["key_columns"]
        tiebreaker_column = self.parameters["tiebreaker_column"]
        keep = self.parameters.get("keep", "last")

        before = len(df)
        df = df.sort_values(by=tiebreaker_column).drop_duplicates(
            subset=key_columns, keep=keep
        )
        after = len(df)

        context.set_data(df)
        context.set_meta("duplicates_dropped", before - after)
        self.logger.info(
            "Deduplicated on %s: %d rows -> %d rows (%d dropped)",
            key_columns, before, after, before - after,
        )
        return context
```

Wire it into `config.json`:

```json
{
  "technical_transformations": {
    "tasks": [
      {
        "name": "dedupe_on_customer_id",
        "module": "etl_framework.transformers.deduplication",
        "class_name": "DeduplicationTransformer",
        "parameters": {
          "key_columns": ["customer_id"],
          "tiebreaker_column": "updated_at",
          "keep": "last"
        }
      }
    ]
  }
}
```

**Design notes:**
- This task composes naturally after `SchemaNormalizer` in the task list (dedupe on the
  *standardized* column name, not the raw source name) — task **ordering within a stage
  matters** and is entirely controlled by the order of entries in `config.json`.
  Document expected ordering dependencies in the docstring, as done here.
- `context.set_meta("duplicates_dropped", ...)` is cheap and valuable: dashboards or
  data-quality alerts can be built directly off `context.metadata` without any extra
  instrumentation work.

---

## 11. Extension Guide: Stage 4 — Load

**When to add a task here:** a new destination system. Exactly one load task runs per
pipeline; it reads `context.data` and writes it to the destination.

**Contract:** `LoadTask.execute(context) -> context`, reads `context.data`.

### Example: `S3Loader`

```python
# etl_framework/loaders/s3.py
"""Load task: write context.data to S3 as Parquet."""

from __future__ import annotations
import io
import boto3  # pip install boto3
import pandas as pd

from etl_framework.core.base import LoadTask
from etl_framework.core.context import PipelineContext


class S3Loader(LoadTask):
    """
    parameters:
        bucket        : S3 bucket name
        key            : S3 object key, e.g. "raw/customer/2026/07/12/customer.parquet"
        aws_region     : (optional) AWS region for the client
        storage_class  : (optional) S3 storage class, e.g. "STANDARD_IA"
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        df: pd.DataFrame = context.data
        bucket = self.parameters["bucket"]
        key = self.parameters["key"]
        region = self.parameters.get("aws_region")
        storage_class = self.parameters.get("storage_class", "STANDARD")

        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)

        s3 = boto3.client("s3", region_name=region)
        s3.upload_fileobj(
            buffer, bucket, key,
            ExtraArgs={"StorageClass": storage_class},
        )

        context.set_meta("loaded_row_count", len(df))
        context.set_meta("load_destination", f"s3://{bucket}/{key}")
        self.logger.info("Wrote %d rows to s3://%s/%s", len(df), bucket, key)
        return context
```

Wire it into `config.json`:

```json
{
  "load": {
    "module": "etl_framework.loaders.s3",
    "class_name": "S3Loader",
    "parameters": {
      "bucket": "enterprise-data-lake-raw",
      "key": "crm/customer/2026/07/12/customer.parquet",
      "aws_region": "ap-southeast-2"
    }
  }
}
```

**Design notes:**
- Writing to an in-memory buffer (`io.BytesIO`) rather than a temp file avoids local
  disk I/O and cleanup concerns — a good default pattern for any cloud-object-store
  loader (same approach applies to GCS/ADLS with their respective SDKs).
- AWS credentials are resolved by `boto3`'s standard credential chain (env vars,
  instance role, `~/.aws/credentials`) — no `secret_reference` needed here, unlike the
  SFTP/API examples, because this is the idiomatic pattern for AWS SDKs in enterprise
  environments (IAM roles, not long-lived keys). Follow the credential convention native
  to whatever platform SDK you're wrapping, rather than forcing every loader through
  `resolve_secret()`.
- For **BigQuery** or **Delta**, follow the same shape: read `context.data`, use the
  platform SDK/client (`google-cloud-bigquery`, `delta-spark`) to write it, record
  `loaded_row_count` and `load_destination` in metadata. Mirror the `mode` parameter
  pattern from `ParquetLoader` (`append`/`overwrite`) if the destination supports it.

---

## 12. Extension Guide: Stage 5 — Post-Processing

**When to add a task here:** anything that happens after a successful load — archiving,
cleanup, notifications, triggering downstream jobs, updating a control table.

**Contract:** `PostProcessingTask.execute(context) -> context`.

### Example: `SlackNotifier`

```python
# etl_framework/postprocessing/slack_notify.py
"""Post-processing task: post a pipeline completion summary to Slack."""

from __future__ import annotations
import requests

from etl_framework.core.base import PostProcessingTask
from etl_framework.core.context import PipelineContext
from etl_framework.preprocessing.pgp import resolve_secret


class SlackNotifier(PostProcessingTask):
    """
    parameters:
        webhook_secret_ref : secret_reference for the Slack incoming webhook URL
        channel_override    : (optional) channel to post to
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        webhook_url = resolve_secret(self.parameters["webhook_secret_ref"])
        pipeline_name = context.get_meta("pipeline_name", "unknown_pipeline")
        pipeline_id = context.get_meta("pipeline_id", "unknown_id")
        row_count = context.row_count()

        message = {
            "text": (
                f":white_check_mark: *{pipeline_name}* (`{pipeline_id}`) completed. "
                f"Rows loaded: {context.get_meta('loaded_row_count', row_count)}. "
                f"Destination: {context.get_meta('load_destination', 'n/a')}"
            )
        }
        if "channel_override" in self.parameters:
            message["channel"] = self.parameters["channel_override"]

        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()

        self.logger.info("Posted completion notification to Slack")
        return context
```

Wire it into `config.json`:

```json
{
  "post_processing": {
    "tasks": [
      {
        "name": "notify_slack",
        "module": "etl_framework.postprocessing.slack_notify",
        "class_name": "SlackNotifier",
        "parameters": {
          "webhook_secret_ref": "slack/data-eng-alerts/webhook"
        }
      }
    ]
  }
}
```

**Design notes:**
- This task reads entirely from `context.metadata` populated by earlier stages
  (`pipeline_name`, `loaded_row_count`, `load_destination`) — a good illustration of why
  every task should be generous about writing to `metadata`, even when it seems
  unnecessary at the time. You don't know which later task will want it.
- Post-processing tasks only run if everything upstream succeeded (the executor raises
  and stops the pipeline on any earlier failure). If you need a notification *on
  failure* too, that's an orchestrator-level concern (catch `ETLTaskError` around
  `PipelineExecutor.run()` in your Airflow/Dagster task and notify from there), not
  something to build into `post_processing`.

---

## 13. Unit Testing New Tasks

Because every task is stateless and takes a `PipelineContext` in, returns one out,
testing never requires spinning up the executor or a real config.json.

```python
# tests/test_deduplication.py
import pandas as pd
import pytest

from etl_framework.core.context import PipelineContext
from etl_framework.transformers.deduplication import DeduplicationTransformer


@pytest.fixture
def sample_context():
    df = pd.DataFrame({
        "customer_id": [1, 1, 2],
        "updated_at": ["2026-01-01", "2026-02-01", "2026-01-01"],
        "email": ["old@x.com", "new@x.com", "b@x.com"],
    })
    return PipelineContext(data=df)


def test_dedup_keeps_most_recent(sample_context):
    task = DeduplicationTransformer(
        name="test_dedup",
        parameters={"key_columns": ["customer_id"], "tiebreaker_column": "updated_at"},
    )

    result = task.run(sample_context)

    assert len(result.data) == 2
    kept_row = result.data[result.data["customer_id"] == 1].iloc[0]
    assert kept_row["email"] == "new@x.com"
    assert result.metadata["duplicates_dropped"] == 1


def test_dedup_raises_wrapped_error_on_missing_key(sample_context):
    from etl_framework.core.exceptions import ETLTaskError

    task = DeduplicationTransformer(
        name="test_dedup",
        parameters={"key_columns": ["does_not_exist"], "tiebreaker_column": "updated_at"},
    )

    with pytest.raises(ETLTaskError) as exc_info:
        task.run(sample_context)

    assert exc_info.value.stage == "technical_transformation"
    assert exc_info.value.task_name == "test_dedup"
```

**Testing conventions:**
- Call `task.run(context)`, not `task.execute(context)`, in tests — this exercises the
  same logging/error-wrapping path production traffic goes through, and confirms your
  task raises `ETLTaskError` (not a raw exception) on failure, which downstream
  orchestrator error handling relies on.
- Build `PipelineContext` fixtures directly — no need to run extract/prior stages to
  test a stage 3+ task in isolation.
- For tasks that call external services (`RestApiDataSource`, `S3Loader`,
  `SlackNotifier`), mock the client/library call (`requests_mock`, `moto` for AWS,
  `responses`) rather than hitting real endpoints in unit tests. Reserve real endpoint
  calls for a separate integration test suite gated behind credentials in CI.

---

## 14. Secrets Management

No task in this framework should ever read a password, API key, or private key
material directly out of `config.json`. The convention, established in
`etl_framework/preprocessing/pgp.py`, is a `secret_reference` string in `parameters`
resolved at runtime:

```python
def resolve_secret(secret_reference: str) -> str:
    """Default: env var lookup. Replace with a real secrets manager client in prod."""
    env_var = secret_reference.upper().replace("/", "_").replace("-", "_")
    value = os.environ.get(env_var)
    if value is None:
        raise KeyError(f"Could not resolve secret_reference='{secret_reference}'")
    return value
```

**For production, replace the body — not the interface — with your real secrets
backend:**

```python
# Example: AWS Secrets Manager
import boto3

_client = boto3.client("secretsmanager")

def resolve_secret(secret_reference: str) -> str:
    return _client.get_secret_value(SecretId=secret_reference)["SecretString"]
```

```python
# Example: HashiCorp Vault
import hvac

_vault = hvac.Client(url=os.environ["VAULT_ADDR"])

def resolve_secret(secret_reference: str) -> str:
    path, _, field = secret_reference.rpartition("#")
    secret = _vault.secrets.kv.v2.read_secret_version(path=path)
    return secret["data"]["data"][field]
```

Every new task that needs credentials should import and call this same
`resolve_secret()` function (see `SFTPFileFetcher`, `RestApiDataSource`, and
`SlackNotifier` above) rather than inventing a per-task secrets mechanism. This keeps
the secrets backend a one-place swap regardless of how many task types exist.

`ETLBase._safe_params()` also redacts any parameter key containing `secret`,
`password`, `key`, or `token` before it's written to logs — name your parameters
accordingly (`password_secret_ref`, `auth_token_secret_ref`, `webhook_secret_ref`, as
used above) so this redaction fires automatically.

---

## 15. Logging, Observability, and Lineage

Every task gets a pre-configured logger at `self.logger`, namespaced as
`etl.<stage_name>.<task_name>`. `run()` automatically logs:

```
START name=<task> parameters=<redacted params>
COMPLETE name=<task> elapsed=<seconds> rows=<context.row_count()>
```

or, on failure:

```
FAILED name=<task>
```
followed by the full traceback, before re-raising as `ETLTaskError`.

**Your `execute()` implementations should log at `INFO` for anything a pipeline
operator would want in a run summary** (row counts, files touched, records
deduplicated) and at `WARNING` for recoverable/skip conditions (as `UnzipFile` and
`PGPDecryptor` do for missing input files). Avoid `DEBUG`-level noise in the default
path; use it for verbose diagnostic detail only.

**Lineage / run metadata:** `context.metadata` accumulates through the whole run and is
returned from `PipelineExecutor.run()`. Orchestrator integration code (§6) should push
this into whatever metastore/lineage system your platform uses — every example task
above contributes to it (`extracted_row_count`, `applied_schema`, `loaded_row_count`,
`archived_file`, etc.) precisely so this is possible without extra instrumentation.

---

## 16. Error Handling and Retry Strategy

- **Within a task:** let exceptions propagate. `ETLBase.run()` catches everything,
  logs it, and re-raises as `ETLTaskError(stage, task_name, original_exception)`. Do
  not catch-and-swallow inside `execute()` unless the failure is genuinely
  recoverable and expected (see the file-not-found warn-and-skip pattern in
  `UnzipFile`/`PGPDecryptor` — a deliberate, documented exception to this rule, not the
  default).
- **Across the pipeline:** `PipelineExecutor.run()` does not catch exceptions from
  individual tasks beyond logging the pipeline-level failure; a failure in any task
  stops the pipeline immediately. There is no partial-continue mode by design — a
  transformation or load task should never run against a dataset a prior stage failed
  to fully produce.
- **Retries:** the framework does not implement retries itself — that's intentionally
  left to the orchestration layer (Airflow retries, Dagster retry policies, etc.),
  which already has visibility into whether a failure is transient. Individual tasks
  calling flaky external services (APIs, SFTP) may implement their own bounded retry
  around just that call (e.g. `tenacity`) if idempotent, but should not retry the whole
  `execute()` method internally.
- **Idempotency:** design new `LoadTask`s and `PostProcessingTask`s to be safely
  re-runnable — a retried pipeline run should not double-load data or double-send
  notifications where avoidable. `ParquetLoader`'s `mode` parameter
  (`overwrite`/`append`) and `ArchiveFile`'s timestamp-suffixed filenames are both
  examples of idempotency-supporting design choices; carry the same thinking into new
  tasks (e.g., an `S3Loader` writing to a deterministic, date-partitioned key is safer
  under retry than one appending a random UUID).

---

## 17. Enterprise Considerations

### 17.1 Config validation in CI

Add a CI step that instantiates `PipelineExecutor(config_path)` for every
`config/*.json` in the repo (constructor-only — don't call `.run()`) to catch structural
errors (missing `module`/`class_name`, bad JSON, unimportable modules) before deploy:

```python
# tests/test_config_validity.py
import glob
import pytest
from etl_framework.core.executor import PipelineExecutor

@pytest.mark.parametrize("config_path", glob.glob("config/*.json"))
def test_config_loads(config_path):
    PipelineExecutor(config_path)  # raises ConfigError/TaskLoadError on problems
```

### 17.2 Task catalog / governance

As the number of concrete tasks grows across teams, maintain a lightweight catalog
(a table in this doc, a wiki page, or a generated listing from docstrings) of every
available `module`/`class_name` combination and its `parameters`, so config authors
don't need to read source code to compose a new pipeline. Treat new task PRs like any
shared-library API change — review parameter naming for consistency with existing tasks
(`destination_path`, `mode`, `*_secret_ref` are established conventions; match them).

### 17.3 Swapping the data engine

`PipelineContext.data` is typed as `Any` specifically so a team can move from pandas to
Polars, Spark, or Dask without changing `ETLBase`, `PipelineContext`, or
`PipelineExecutor` — only the concrete task implementations that touch `.data` need to
change, and they can be migrated incrementally (a Spark `ExtractTask` handing a Spark
DataFrame to a Spark-aware `TransformTask` is fine as long as every task in that
pipeline agrees on the type it's passing along).

### 17.4 Multi-environment configs

Keep environment-specific values (bucket names, hostnames, secret references) out of
a single `config.json` checked into source control for prod; either template it
(Jinja2/environment substitution at deploy time) or maintain
`config/dev.config.json`, `config/prod.config.json`, etc., and select by deploy
pipeline. The framework itself is environment-agnostic — this is a deployment-tooling
decision, not a framework one.

### 17.5 JSON Schema for config.json

For stricter structural guarantees than the runtime checks in
`PipelineExecutor._validate_config`, maintain a JSON Schema and validate in CI:

```python
import json, jsonschema

schema = json.load(open("config/config.schema.json"))
config = json.load(open("config/config.json"))
jsonschema.validate(config, schema)
```

This catches things like "a task block missing `parameters`" at PR time rather than at
pipeline-run time.

---

## 18. New-Task Checklist (Definition of Done)

Use this checklist for every new task class PR:

- [ ] Class derives from the correct stage base (`PreProcessingTask` / `ExtractTask` /
      `TransformTask` / `LoadTask` / `PostProcessingTask`), not `ETLBase` directly.
- [ ] Only `execute()` is implemented; `run()` is untouched.
- [ ] Docstring lists every `parameters` key, required vs. optional, with defaults.
- [ ] Required parameters accessed via `self.parameters["key"]` (fails loudly if
      missing); optional ones via `self.parameters.get("key", default)`.
- [ ] Any credential is resolved via `resolve_secret(secret_reference)` — nothing
      sensitive is read directly from `parameters`.
- [ ] Parameter names containing secrets end in `_secret_ref` (or similar) so
      `ETLBase._safe_params()` redacts them in logs.
- [ ] `context.set_meta(...)` calls for anything a later stage or an orchestrator might
      reasonably want (row counts, destination paths, applied config names).
- [ ] Logs at `INFO` for normal operation, `WARNING` only for a deliberate,
      documented skip/degrade path (not as a substitute for raising).
- [ ] Unit test(s) using a hand-built `PipelineContext` fixture, calling `.run()` (not
      `.execute()`), covering both a success case and a failure case
      (asserting `ETLTaskError`).
- [ ] External service calls are mocked in unit tests.
- [ ] New third-party dependency added to `requirements.txt` with a comment noting
      which task needs it.
- [ ] Example `config.json` block added to this guide's relevant section (or the team's
      task catalog per §17.2).

---

## 19. Appendix A: Full Class Reference

```
ETLBase (ABC)                          etl_framework/core/base.py
 │   execute(context) -> context        [abstract — implement this]
 │   run(context) -> context            [template method — never override]
 │
 ├── PreProcessingTask                  stage_name = "pre_processing"
 │     ├── UnzipFile                    preprocessing/unzip_file.py
 │     ├── PGPDecryptor                 preprocessing/pgp.py
 │     └── SFTPFileFetcher              preprocessing/sftp_fetch.py        [§8]
 │
 ├── ExtractTask                        stage_name = "extract"
 │     ├── CSVDataSource                datasources/csv.py
 │     └── RestApiDataSource            datasources/rest_api.py            [§9]
 │
 ├── TransformTask                      stage_name = "technical_transformation"
 │     ├── JSONFlatten                  transformers/json_flatten.py
 │     ├── SchemaNormalizer             transformers/schema.py
 │     └── DeduplicationTransformer     transformers/deduplication.py      [§10]
 │
 ├── LoadTask                           stage_name = "load"
 │     ├── ParquetLoader                loaders/parquet.py
 │     └── S3Loader                     loaders/s3.py                      [§11]
 │
 └── PostProcessingTask                 stage_name = "post_processing"
       ├── ArchiveFile                  postprocessing/archive.py
       └── SlackNotifier                postprocessing/slack_notify.py     [§12]
```

Supporting modules:

| Module | Purpose |
|---|---|
| `etl_framework/core/context.py` | `PipelineContext` dataclass |
| `etl_framework/core/executor.py` | `PipelineExecutor` — config parsing, dynamic loading, stage orchestration |
| `etl_framework/core/exceptions.py` | `ConfigError`, `TaskLoadError`, `ETLTaskError` |
| `etl_framework/core/logging_setup.py` | `configure_logging()` |
| `etl_framework/preprocessing/pgp.py` | Also houses `resolve_secret()`, the shared secrets-resolution entry point |
| `etl_framework/transformers/schema_registry.json` | Named schema definitions consumed by `SchemaNormalizer` |

---

## 20. Appendix B: FAQ

**Q: Can a pipeline have zero pre-processing or post-processing tasks?**
Yes — `pre_processing` and `post_processing` are optional; an absent or empty `tasks`
list is skipped (`PipelineExecutor._run_task_list` logs and continues).

**Q: Can I have more than one extract or load task?**
Not within this framework's current contract — `extract` and `load` are single task
blocks by design, keeping "where does the data come from" and "where does it go"
unambiguous for any given pipeline. If you need to combine multiple sources, write a
single `ExtractTask` that internally fans out to multiple sources and concatenates the
result into one `context.data` — the multi-source logic lives inside your task, not in
the executor.

**Q: How do I control the order of tasks within a stage?**
By the order you list them in the `tasks` array in `config.json`. The executor iterates
in list order; there is no separate priority/weight field.

**Q: What happens if a class doesn't derive from `ETLBase`?**
`PipelineExecutor._instantiate_task` explicitly checks
`issubclass(task_class, ETLBase)` and raises `TaskLoadError` if it doesn't — this is
caught at pipeline-start, not buried inside stage execution.

**Q: My task needs to read a value another task computed. How?**
`context.metadata`. Write it with `context.set_meta(key, value)` in the upstream task,
read it with `context.get_meta(key, default)` downstream — see `SlackNotifier` (§12)
reading `pipeline_name`/`loaded_row_count` written by earlier stages.

**Q: Where do I put a task that doesn't cleanly fit "extract" vs. "transform" (e.g. a
data-quality gate that should abort the pipeline if validation fails)?**
Typically as the last `technical_transformations` task: implement `execute()` to raise
if validation fails (this will propagate as `ETLTaskError` and stop the pipeline before
`load` runs), or to attach a `context.set_meta("validation_passed", False)` flag your
load task checks and short-circuits on, depending on whether you want a hard stop or a
soft skip.
