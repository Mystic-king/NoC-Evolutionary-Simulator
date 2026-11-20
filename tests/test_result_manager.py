import json
from core.experiment_manager import ExperimentManager
from core.result_manager import ResultManager


def test_run_directory_and_json_are_created(tmp_path):
    manager = ExperimentManager(tmp_path)
    run_dir = manager.create_run("basic ga", {"seed": 9})
    assert run_dir.exists()
    assert (run_dir / "configuration.json").exists()
    metadata = json.loads((run_dir / "configuration.json").read_text())
    assert metadata["configuration"]["seed"] == 9


def test_csv_is_saved(tmp_path):
    path = ResultManager.save_csv(tmp_path, "history.csv", [{"epoch": 0, "score": 1.0}])
    assert path.exists()
    assert "score" in path.read_text()
