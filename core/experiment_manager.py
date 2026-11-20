from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json, logging, re

class ExperimentManager:
    def __init__(self, output_root="outputs/experiments"):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def create_run(self, experiment_name, configuration):
        slug = re.sub(r"[^a-z0-9]+", "_", experiment_name.lower()).strip("_") or "experiment"
        stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
        run_id = uuid4().hex[:8]
        path = self.output_root / f"{slug}_{stamp}_{run_id}"
        path.mkdir(parents=True, exist_ok=False)
        metadata = {
            "experiment_name": experiment_name, "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "configuration": configuration,
        }
        (path / "configuration.json").write_text(json.dumps(metadata, indent=2, default=str))
        logger = self.get_logger(path)
        logger.info("Created run for %s", experiment_name)
        return path

    @staticmethod
    def get_logger(path):
        path = Path(path)
        run_id = path.name.rsplit("_", 1)[-1]
        logger = logging.getLogger(f"nocsim.{run_id}")
        if not logger.handlers:
            logger.setLevel(logging.INFO); logger.propagate = False
            handler = logging.FileHandler(path / "simulation.log", encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(handler)
        return logger
