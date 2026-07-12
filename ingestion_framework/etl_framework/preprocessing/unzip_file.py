"""Pre-processing task: unzip an archive to an output directory."""

from __future__ import annotations
import os
import zipfile

from etl_framework.core.base import PreProcessingTask
from etl_framework.core.context import PipelineContext


class UnzipFile(PreProcessingTask):
    """
    parameters:
        input_path    : path to the .zip archive
        output_path   : directory to extract into
        delete_source : if true, remove the zip file after successful extraction
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        input_path = self.parameters["input_path"]
        output_path = self.parameters["output_path"]
        delete_source = self.parameters.get("delete_source", False)

        os.makedirs(output_path, exist_ok=True)

        if not os.path.exists(input_path):
            # In real deployments this should fail; kept as a warning here so the
            # rest of the demo pipeline can still be exercised without real files.
            self.logger.warning("Input archive not found: %s (skipping unzip)", input_path)
            return context

        extracted_files = []
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(output_path)
            extracted_files = [os.path.join(output_path, n) for n in zf.namelist()]

        for f in extracted_files:
            context.add_file_path(f)

        self.logger.info("Extracted %d file(s) to %s", len(extracted_files), output_path)

        if delete_source:
            os.remove(input_path)
            self.logger.info("Deleted source archive %s", input_path)

        context.set_meta("last_unzip_output", output_path)
        return context
