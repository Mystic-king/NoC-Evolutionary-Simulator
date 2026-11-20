from pathlib import Path
import json
from core.simulation_manager import SimulationManager
from modules.tsp.genetic_algorithm import solve_tsp
from modules.noc_genetic_algorithm.optimizer import optimize_route
from modules.metaheuristics.benchmarks import compare_algorithms
from modules.neuro_fuzzy.anfis import run_anfis_demo
from modules.gem5_garnet.gem5_adapter import parse_gem5_stats
from modules.gem5_garnet.topology import xy_route

def test_tsp_returns_valid_permutation():
    r=solve_tsp(cities_count=8,population_size=12,generations=5,seed=3)
    assert sorted(r["best_route"])==list(range(8))
    assert r["best_distance"]>0
    assert len(r["history"])==6

def test_xy_route_is_dimension_order():
    assert xy_route((0,0),(2,3))==[(0,0),(0,1),(0,2),(0,3),(1,3),(2,3)]

def test_noc_ga_returns_valid_connected_path():
    r=optimize_route(rows=3,cols=3,source=(0,0),destination=(2,2),population_size=10,generations=4,seed=1)
    path=r["best_path"]
    assert path[0]==(0,0) and path[-1]==(2,2)
    assert all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(path,path[1:]))

def test_metaheuristic_comparison_has_all_four():
    r=compare_algorithms(dimension=2,population_size=8,iterations=5,seed=4)
    assert {x["algorithm"] for x in r["comparison"]}=={"GA","PSO","ACO","SA"}
    assert all(x["best_fitness"]>=0 for x in r["comparison"])

def test_anfis_runs_and_returns_finite_error():
    r=run_anfis_demo(samples=60,epochs=2,seed=5)
    assert r["validation_rmse"]>=0
    assert len(r["rules"])==4
    assert len(r["history"])==2

def test_gem5_stats_parser():
    stats=parse_gem5_stats("system.ruby.network.packets_injected::total 123\nsystem.cpu.numCycles 5.5\n")
    assert stats["system.ruby.network.packets_injected::total"]==123
    assert stats["system.cpu.numCycles"]==5.5

def test_gem5_intro_preview_creates_artifacts(tmp_path):
    r=SimulationManager(tmp_path).run("gem5-garnet",{"rows":3,"cols":3,"packet_count":8,"seed":9})
    assert r["status"]=="completed"
    assert r["actual_gem5"] is None
    folder=Path(r["run_directory"])
    assert (folder/"gem5_mesh_topology.png").exists()
    assert (folder/"packet_routes.csv").exists()
    assert (folder/"report.pdf").exists()
    assert (folder/"experiment_artifacts.zip").exists()

def test_manager_tsp_creates_complete_artifacts(tmp_path):
    r=SimulationManager(tmp_path).run("tsp",{"cities_count":6,"population_size":8,"generations":3,"seed":2})
    folder=Path(r["run_directory"])
    assert r["status"]=="completed"
    for name in ("results.json","configuration.json","distance_history.csv","best_route.png","report.pdf","experiment_artifacts.zip"):
        assert (folder/name).exists()
    saved=json.loads((folder/"results.json").read_text())
    assert saved["best_distance"]>0
