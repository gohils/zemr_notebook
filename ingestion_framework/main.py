"""
Entrypoint.

Usage:
    python main.py path/to/config.json
"""

import sys

from etl_framework.core.executor import PipelineExecutor
from etl_framework.core.logging_setup import configure_logging


def main():
    configure_logging()
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/demo_config.json"

    executor = PipelineExecutor(config_path)
    context = executor.run()

    print("\n--- Pipeline finished ---")
    print(f"Rows in final dataset : {context.row_count()}")
    print(f"Metadata              : {context.metadata}")


if __name__ == "__main__":
    main()
