from __future__ import annotations
import argparse
import json
from pathlib import Path
from core.simulation_manager import SimulationManager

EXPERIMENTS = (
    "basic-ga", "tsp", "noc-routing-ga", "cnn-routing",
    "metaheuristics", "neuro-fuzzy", "gem5-garnet",
)

def build_parser():
    parser=argparse.ArgumentParser(
        prog="nocsim",
        description="NoC Evolutionary Simulator — execute practical experiments from the terminal."
    )
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("list",help="List available practical modules")
    run=sub.add_parser("run",help="Run one practical using a JSON configuration")
    run.add_argument("experiment",choices=EXPERIMENTS)
    run.add_argument("--config",default="{}",help="Experiment configuration as a JSON object")
    run.add_argument("--output",type=Path,default=Path("outputs/experiments"))
    show=sub.add_parser("show-results",help="List previously saved experiment runs")
    show.add_argument("--output",type=Path,default=Path("outputs/experiments"))
    return parser

def main(argv=None):
    parser=build_parser()
    args=parser.parse_args(argv)
    if args.command=="list":
        print(f"{'PRACTICAL':48}STATUS")
        print("-"*100)
        statuses=[
          ("basic-ga","Implemented"),
          ("tsp","Implemented"),
          ("noc-routing-ga","Implemented educational mesh path optimization"),
          ("cnn-routing","Implemented; PyTorch required"),
          ("metaheuristics","Implemented: GA, PSO, ACO, SA"),
          ("neuro-fuzzy","Implemented: Sugeno ANFIS"),
          ("gem5-garnet","Python learning preview + optional external GEM5"),
        ]
        for name,status in statuses: print(f"{name:48}{status}")
        return 0
    if args.command=="run":
        try: config=json.loads(args.config)
        except json.JSONDecodeError as exc: parser.error(f"--config must be valid JSON: {exc}")
        if not isinstance(config,dict): parser.error("--config must decode to a JSON object.")
        result=SimulationManager(args.output).run(args.experiment,config)
        print("Experiment completed.")
        print(f"Run folder: {result['run_directory']}")
        for key in ("best_solution","best_fitness","best_distance","best_cost","validation_accuracy","validation_rmse"):
            if key in result: print(f"{key}: {result[key]}")
        return 0
    if args.command=="show-results":
        if not args.output.exists():
            print("No experiment output directory.")
            return 0
        folders=sorted((p for p in args.output.iterdir() if p.is_dir()),reverse=True)
        if not folders:
            print("No experiment runs found.")
            return 0
        print(f"{'RUN':48}{'EXPERIMENT':24}STATUS")
        print("-"*100)
        for folder in folders:
            result_file=folder/"results.json"; failure_file=folder/"failure.json"
            if result_file.exists():
                data=json.loads(result_file.read_text(encoding="utf-8"))
                print(f"{folder.name:48}{str(data.get('experiment','-')):24}{data.get('status','-')}")
            elif failure_file.exists():
                print(f"{folder.name:48}{'-':24}failed")
        return 0
    return 1

if __name__=="__main__":
    raise SystemExit(main())
