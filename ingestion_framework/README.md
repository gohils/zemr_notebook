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

## How it works

```
config.json  ──►  PipelineExecutor  ──►  runs each stage in order:

  pre_processing (list)   -> UnzipFile, PGPDecryptor, ...
  extract (single)        -> CSVDataSource, ...
  technical_transformations (list) -> JSONFlatten, SchemaNormalizer, ...
  load (single)            -> ParquetLoader, ...
  post_processing (list)  -> ArchiveFile, ...
```

Each task block in the config has the same shape:

```json
{
  "name": "task_name",
  "module": "dotted.module.path",
  "class_name": "ClassName",
  "parameters": { "...": "..." }
}
```

The executor does, for every task: `importlib.import_module(module)`,
`getattr(module, class_name)`, instantiate with `(name, parameters)`, call
`.run(context)`. `PipelineContext` (holding a pandas DataFrame in `.data`,
plus `.file_paths` and `.metadata`) is threaded through every stage.

## Class hierarchy

```
ETLBase (ABC)                       -- etl_framework/core/base.py
 ├── PreProcessingTask
 │     ├── UnzipFile                -- preprocessing/unzip_file.py
 │     └── PGPDecryptor             -- preprocessing/pgp.py
 ├── ExtractTask
 │     └── CSVDataSource            -- datasources/csv.py
 ├── TransformTask
 │     ├── JSONFlatten              -- transformers/json_flatten.py
 │     └── SchemaNormalizer         -- transformers/schema.py
 ├── LoadTask
 │     └── ParquetLoader            -- loaders/parquet.py
 └── PostProcessingTask
       └── ArchiveFile              -- postprocessing/archive.py
```

`ETLBase` only requires subclasses to implement:

```python
def execute(self, context: PipelineContext) -> PipelineContext: ...
```

`run()` (called by the executor, not overridden by subclasses) wraps
`execute()` with logging, timing, and uniform error handling
(`ETLTaskError`, which carries the stage + task name + original exception).

## Adding a new task type (e.g. a database extractor, S3 loader, Kafka source)

1. Create a class deriving from the relevant stage base (or `ETLBase` directly).
2. Implement `execute(self, context) -> PipelineContext`.
3. Reference `module` / `class_name` / `parameters` for it in `config.json`.

No executor changes required — this is the whole point of the framework.

## Running

```bash
pip install -r requirements.txt
python main.py config/demo_config.json      # runnable end-to-end demo
python main.py config/config.json           # the CRM pipeline config as originally supplied
```

`config/demo_config.json` uses local sample data (`sample_data/customer_nested.csv`)
and has been run end-to-end (extract -> flatten -> schema normalize -> parquet
load -> archive) to confirm the framework works.

`config/config.json` is the original CRM pipeline config supplied — it
references Windows paths (`C:/temp/...`) that won't exist outside that
environment, but will validate and run identically once those paths are real
(or repointed at your source system).

## Notes on specific tasks

- **PGPDecryptor** needs `python-gnupg` (`pip install python-gnupg`) and the
  system `gpg` binary. Private key material is resolved via
  `resolve_secret(secret_reference)` in `preprocessing/pgp.py` — swap the
  default (env-var based) implementation for a real secrets manager client
  (Vault, AWS Secrets Manager, etc) in production. If `python-gnupg` isn't
  installed, the task logs a warning and passes the file through unchanged,
  so a full pipeline can still be exercised without it.
- **SchemaNormalizer** looks up `target_schema` in
  `transformers/schema_registry.json` (column rename + dtype rules). Add new
  schemas there, or point `parameters.registry_path` at your own file.
- **ParquetLoader** supports `mode: "append"` (reads + concatenates the
  existing file) or `"overwrite"`, and optional `partition_cols`.
- Every pre/post-processing task treats a missing input file as a
  warn-and-continue rather than a hard failure, so partially-available demo
  environments don't need every referenced path to exist. Remove that
  guard (`if not os.path.exists(...)`) if you want strict fail-fast behavior
  in production.

## Extending further

- Add a real secrets-manager client to `resolve_secret()`.
- Add more `DataSource` classes (REST API, Database, SFTP, Kafka) under
  `datasources/`, more `Loader` classes (S3, GCS, ADLS, BigQuery, Delta)
  under `loaders/` — same pattern every time: derive from the stage base
  class, implement `execute()`, reference in config.
- Swap `PipelineContext.data` for a Spark/Polars DataFrame if you outgrow
  pandas — only the concrete task implementations touch `.data` directly, so
  the base classes/executor need no changes.
