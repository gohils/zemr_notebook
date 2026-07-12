"""
Technical transformation: flatten nested JSON-like columns (dict / list-of-dict
values, or JSON-encoded strings) into separate top-level columns using
dotted-path naming, e.g. `customer.address` -> `customer.address.city`,
`customer.address.zip`.
"""

from __future__ import annotations
import json
import pandas as pd

from etl_framework.core.base import TransformTask
from etl_framework.core.context import PipelineContext


class JSONFlatten(TransformTask):
    """
    parameters:
        flatten_columns : list of column names to flatten. Each column may
                           contain dicts, JSON strings, or lists of dicts.
        drop_original    : drop the original nested column after flattening
                           (default True)
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        df: pd.DataFrame = context.data
        flatten_columns = self.parameters.get("flatten_columns", [])
        drop_original = self.parameters.get("drop_original", True)

        for col in flatten_columns:
            if col not in df.columns:
                self.logger.warning("Column '%s' not present - skipping", col)
                continue

            parsed = df[col].apply(self._coerce_to_dict)

            # list-of-dict values (e.g. customer.orders) get exploded into rows first
            if parsed.apply(lambda v: isinstance(v, list)).any():
                df = df.assign(**{col: parsed}).explode(col, ignore_index=True)
                parsed = df[col].apply(self._coerce_to_dict)

            flattened = pd.json_normalize(parsed).add_prefix(f"{col}.")
            flattened.index = df.index
            df = pd.concat([df, flattened], axis=1)

            if drop_original:
                df = df.drop(columns=[col])

            self.logger.info("Flattened column '%s' into %d field(s)", col, len(flattened.columns))

        context.set_data(df)
        return context

    @staticmethod
    def _coerce_to_dict(value):
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
