"""
Technical transformation: standardize column names and data types against a
named target schema.

Schemas are defined in a small JSON registry (schema_registry.json, colocated
with this module by default) shaped like:

    {
      "customer_v1": {
        "columns": {
          "cust_id":   {"rename": "customer_id", "dtype": "string"},
          "cust_name": {"rename": "customer_name", "dtype": "string"},
          "signup_dt": {"rename": "signup_date", "dtype": "datetime"}
        },
        "add_missing_as_null": true
      }
    }

dtype supports: string, int, float, bool, datetime.
"""

from __future__ import annotations
import json
import os
import pandas as pd

from etl_framework.core.base import TransformTask
from etl_framework.core.context import PipelineContext

_DTYPE_CASTERS = {
    "string": lambda s: s.astype("string"),
    "int": lambda s: pd.to_numeric(s, errors="coerce").astype("Int64"),
    "float": lambda s: pd.to_numeric(s, errors="coerce").astype("float64"),
    "bool": lambda s: s.astype("bool"),
    "datetime": lambda s: pd.to_datetime(s, errors="coerce"),
}

DEFAULT_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "schema_registry.json")


class SchemaNormalizer(TransformTask):
    """
    parameters:
        target_schema : name of the schema entry to apply, e.g. "customer_v1"
        registry_path : (optional) path to the schema registry JSON file
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        df: pd.DataFrame = context.data
        target_schema = self.parameters["target_schema"]
        registry_path = self.parameters.get("registry_path", DEFAULT_REGISTRY_PATH)

        registry = self._load_registry(registry_path)
        if target_schema not in registry:
            raise KeyError(f"Schema '{target_schema}' not found in {registry_path}")

        schema_def = registry[target_schema]
        columns_def = schema_def.get("columns", {})

        rename_map = {
            src: rule["rename"]
            for src, rule in columns_def.items()
            if "rename" in rule and src in df.columns
        }
        df = df.rename(columns=rename_map)

        for src, rule in columns_def.items():
            target_col = rule.get("rename", src)
            dtype = rule.get("dtype")
            if dtype and target_col in df.columns:
                caster = _DTYPE_CASTERS.get(dtype)
                if caster is None:
                    self.logger.warning("Unknown dtype '%s' for column '%s' - skipping cast", dtype, target_col)
                    continue
                df[target_col] = caster(df[target_col])

        if schema_def.get("add_missing_as_null", True):
            for src, rule in columns_def.items():
                target_col = rule.get("rename", src)
                if target_col not in df.columns:
                    df[target_col] = pd.NA

        context.set_data(df)
        context.set_meta("applied_schema", target_schema)
        self.logger.info("Applied schema '%s' (%d column rules)", target_schema, len(columns_def))
        return context

    @staticmethod
    def _load_registry(path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Schema registry not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
