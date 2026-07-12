"""Extract task: read a CSV file into a pandas DataFrame."""

from __future__ import annotations
import pandas as pd

from etl_framework.core.base import ExtractTask
from etl_framework.core.context import PipelineContext


class CSVDataSource(ExtractTask):
    """
    parameters:
        input_path : path to the .csv file
        header     : whether the first row is a header (default True)
        delimiter  : field delimiter (default ',')
        encoding   : file encoding (default 'utf-8')
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        input_path = self.parameters["input_path"]
        header = 0 if self.parameters.get("header", True) else None
        delimiter = self.parameters.get("delimiter", ",")
        encoding = self.parameters.get("encoding", "utf-8")

        df = pd.read_csv(input_path, header=header, delimiter=delimiter, encoding=encoding)

        context.set_data(df)
        context.add_file_path(input_path)
        context.set_meta("source_system", "CSV")
        context.set_meta("extracted_row_count", len(df))
        self.logger.info("Extracted %d rows, %d columns from %s", len(df), len(df.columns), input_path)
        return context
