import json
from pathlib import Path
import pytest
import main

def test_cli_list(capsys):
    assert main.main(["list"])==0
    output=capsys.readouterr().out
    assert "basic-ga" in output
    assert "gem5-garnet" in output

def test_cli_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main.main(["run","--help"])
    assert exc.value.code==0
    assert "--config" in capsys.readouterr().out

def test_cli_run_creates_experiment(tmp_path,capsys):
    config=json.dumps({"population_size":8,"generations":2,"seed":17})
    assert main.main(["run","basic-ga","--config",config,"--output",str(tmp_path)])==0
    output=capsys.readouterr().out
    assert "Experiment completed" in output
    assert list(tmp_path.glob("basic_ga_*"))

def test_cli_rejects_non_object_config(tmp_path):
    with pytest.raises(SystemExit):
        main.main(["run","basic-ga","--config","[]","--output",str(tmp_path)])
