"""Post-processing task: move a processed source file into an archive location."""

from __future__ import annotations
import os
import shutil
from datetime import datetime, timezone

from etl_framework.core.base import PostProcessingTask
from etl_framework.core.context import PipelineContext


class ArchiveFile(PostProcessingTask):
    """
    parameters:
        source            : path to the file to archive
        archive_location  : directory to move the file into
        timestamp_suffix  : if true (default), append a UTC timestamp to the
                             archived filename to avoid collisions
    """

    def execute(self, context: PipelineContext) -> PipelineContext:
        source = self.parameters["source"]
        archive_location = self.parameters["archive_location"]
        timestamp_suffix = self.parameters.get("timestamp_suffix", True)

        if not os.path.exists(source):
            self.logger.warning("Source file not found: %s (skipping archive)", source)
            return context

        os.makedirs(archive_location, exist_ok=True)

        filename = os.path.basename(source)
        if timestamp_suffix:
            stem, ext = os.path.splitext(filename)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            filename = f"{stem}_{stamp}{ext}"

        destination = os.path.join(archive_location, filename)
        shutil.move(source, destination)

        context.set_meta("archived_file", destination)
        self.logger.info("Archived %s -> %s", source, destination)
        return context
