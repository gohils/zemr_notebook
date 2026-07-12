"""Load task: write context.data (pandas DataFrame) to a Parquet destination."""

from __future__ import annotations
import os
import pandas as pd

from etl_framework.core.base import LoadTask
from etl_framework.core.context import PipelineContext


class ParquetLoader(LoadTask):
    """
    parameters:
        destination_path : file or directory path to write to. If it doesn't
                            end in '.parquet' it's treated as a directory and
                            a timestamped file is written inside it.
        mode              : 'append' | 'overwrite' (default 'overwrite')
        partition_cols    : (optional) list of columns to partition by
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        df: pd.DataFrame = context.data
        destination_path = self.parameters["destination_path"]
        mode = self.parameters.get("mode", "overwrite")
        partition_cols = self.parameters.get("partition_cols")

        target_file = self._resolve_target_file(destination_path)
        os.makedirs(os.path.dirname(target_file) or ".", exist_ok=True)

        if mode == "append" and os.path.exists(target_file):
            existing = pd.read_parquet(target_file)
            df = pd.concat([existing, df], ignore_index=True)
            self.logger.info("Appending to existing parquet (%d existing rows)", len(existing))

        if partition_cols:
            df.to_parquet(destination_path, partition_cols=partition_cols, index=False)
            self.logger.info("Wrote %d rows to partitioned parquet at %s", len(df), destination_path)
        else:
            df.to_parquet(target_file, index=False)
            self.logger.info("Wrote %d rows to %s", len(df), target_file)

        context.set_meta("loaded_row_count", len(df))
        context.set_meta("load_destination", target_file)
        return context

    @staticmethod
    def _resolve_target_file(destination_path: str) -> str:
        if destination_path.endswith(".parquet"):
            return destination_path
        return os.path.join(destination_path, "data.parquet")
