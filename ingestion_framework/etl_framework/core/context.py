"""
PipelineContext is the object passed between every stage of the pipeline.

It carries:
  - `data`        : the working dataset (pandas.DataFrame by convention, but any
                     object is allowed so datasources can hand back whatever is
                     natural, e.g. a list[dict] before the first transform).
  - `file_paths`   : list of file paths currently relevant to the run
                     (populated/updated by pre-processing tasks such as unzip/decrypt).
  - `metadata`     : free-form dict for anything tasks want to stash and read later
                     (row counts, schema info, source system name, etc).
  - `pipeline_config`: the full parsed config.json, in case a task needs
                     cross-cutting info (e.g. pipeline_id for logging/lineage).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PipelineContext:
    data: Any = None
    file_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    pipeline_config: Optional[Dict[str, Any]] = None

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
