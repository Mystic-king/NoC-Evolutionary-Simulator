from pathlib import Path
import json, zipfile, logging
from core.experiment_manager import ExperimentManager
from core.result_manager import ResultManager

class SimulationManager:
    def __init__(self, output_root="outputs/experiments"):
        self.experiments = ExperimentManager(output_root)
        self.results = ResultManager()

    def run(self, experiment, config):
        runners = {
            "basic-ga": self._basic_ga, "tsp": self._tsp, "noc-routing-ga": self._noc_ga,
            "metaheuristics": self._metaheuristics, "neuro-fuzzy": self._neuro_fuzzy,
            "cnn-routing": self._cnn, "gem5-garnet": self._gem5,
        }
        if experiment not in runners:
            raise ValueError(f"Unknown experiment '{experiment}'. Choose: {', '.join(runners)}")
        path = self.experiments.create_run(experiment, config)
        logger = self.experiments.get_logger(path)
        logger.info("Starting experiment %s", experiment)
        try:
            result, artifacts = runners[experiment](config, path, logger)
            descriptions = {
                "basic-ga": ("Binary genetic algorithm using tournament selection, single-point crossover, bit-flip mutation and elitism.",
                             "Maximize f(x)=x^2 over an unsigned binary integer search space."),
                "tsp": ("Permutation genetic algorithm using order crossover, swap mutation and elitism.",
                        "Minimize the Euclidean length of a closed tour visiting every generated city once."),
                "noc-routing-ga": ("Genetic search over valid simple mesh paths. Candidate paths are evaluated using hop count, seeded synthetic intermediate-router congestion and a small turn penalty.",
                                   "Find a low-cost path between source and destination in a 2D mesh. Congestion is synthetic and is not a measured GEM5 counter."),
                "metaheuristics": ("GA, particle swarm optimization, ant colony optimization and simulated annealing are run on the same Rastrigin minimization benchmark.",
                                   "Compare heuristic convergence on a multimodal continuous objective. Lower objective values are better; the known global minimum is zero."),
                "neuro-fuzzy": ("Two-input, four-rule first-order Sugeno ANFIS. Consequent parameters are fitted by least squares and Gaussian premise parameters are updated by finite-difference gradient steps.",
                                "Approximate sin(pi*x)*cos(pi*y) and evaluate RMSE on held-out synthetic samples."),
                "cnn-routing": ("A convolutional neural network is trained on generated 2D mesh examples. Labels are dimension-order XY next-hop directions.",
                                "Classify the next-hop direction (east, west, south, north) from current-router, destination and congestion feature maps. Evaluation uses a held-out generated test split."),
                "gem5-garnet": ("The Python preview builds a 2D mesh, generates synthetic traffic and routes packets using XY dimension-order routing. An optional adapter runs a user-supplied compiled GEM5 binary and Garnet configuration script.",
                                "Explore topology and packet routing. Python preview metrics are not GEM5 statistics; only counters parsed from an actual external GEM5 run are simulator measurements."),
            }
            method, objective = descriptions[experiment]
            result.update({"methodology": method, "objective_description": objective,
                           "experiment": experiment, "run_directory": str(path), "status": "completed"})
            self.results.save_json(path, "results.json", result)
            self.results.save_pdf(path, f"{experiment.title()} Report", result, configuration=config)
            logger.info("Experiment completed")
            self._zip(path)
            return result
        except Exception as exc:
            logger.exception("Experiment failed: %s", exc)
            self.results.save_json(path, "failure.json", {"status":"failed","error":str(exc),"experiment":experiment})
            raise

    def _basic_ga(self,c,p,l):
        from modules.basic_ga.optimizer import BasicGeneticAlgorithm, GAConfig
        cfg=GAConfig(**{k:v for k,v in c.items() if k in GAConfig.__dataclass_fields__})
        r=BasicGeneticAlgorithm(cfg).run()
        self.results.save_csv(p,"fitness_history.csv",r["history"])
        from core.visualizer import save_history_plot
        save_history_plot(r["history"],p/"fitness_convergence.png")
        return ({k:v for k,v in r.items() if k!="history"},["fitness_history.csv","fitness_convergence.png"])

    def _tsp(self,c,p,l):
        from modules.tsp.genetic_algorithm import solve_tsp
        from core.visualizer import save_history_plot, save_tsp_plot
        r=solve_tsp(**c)
        self.results.save_csv(p,"distance_history.csv",r["history"])
        self.results.save_csv(p,"cities.csv",[{"city_id":i,"x":xy[0],"y":xy[1]} for i,xy in enumerate(r["cities"])])
        save_history_plot(r["history"],p/"tsp_convergence.png",series=("best_distance","average_distance"),title="TSP distance convergence")
        save_tsp_plot(r["cities"],r["best_route"],p/"best_route.png")
        r["best_route_coordinates"]=[r["cities"][i] for i in r["best_route"]]
        return ({k:v for k,v in r.items() if k not in ("history","cities")},["distance_history.csv","cities.csv","tsp_convergence.png","best_route.png"])

    def _noc_ga(self,c,p,l):
        from modules.noc_genetic_algorithm.optimizer import optimize_route
        from core.visualizer import save_history_plot, save_mesh_plot
        r=optimize_route(**c)
        self.results.save_csv(p,"routing_fitness.csv",r["history"])
        save_history_plot(r["history"],p/"routing_convergence.png",title="NoC routing optimization")
        save_mesh_plot(r["rows"],r["cols"],p/"optimized_route.png",route=r["best_path"],title="Optimized NoC path")
        r["best_path_names"]=[f"({x},{y})" for x,y in r["best_path"]]
        self.results.save_csv(p,"synthetic_congestion.csv",[
            {"row":rr,"column":cc,"congestion_penalty":value}
            for rrcc,value in r["congestion"].items()
            for rr,cc in [tuple(map(int,rrcc.split(","))) ]])
        return ({k:v for k,v in r.items() if k not in ("history","best_path","congestion")},["routing_fitness.csv","routing_convergence.png","optimized_route.png","synthetic_congestion.csv"])

    def _metaheuristics(self,c,p,l):
        from modules.metaheuristics.benchmarks import compare_algorithms
        from core.visualizer import save_history_plot, save_comparison_plot
        r=compare_algorithms(**c)
        self.results.save_csv(p,"algorithm_comparison.csv",r["comparison"])
        save_comparison_plot(r["comparison"],p/"algorithm_comparison.png")
        artifacts=["algorithm_comparison.csv","algorithm_comparison.png"]
        for name,hist in r["histories"].items():
            self.results.save_csv(p,f"{name}_history.csv",hist)
            save_history_plot(hist,p/f"{name}_convergence.png",series=("best_fitness",),title=f"{name.upper()} convergence")
            artifacts.extend([f"{name}_history.csv",f"{name}_convergence.png"])
        return ({"benchmark":r["benchmark"],"dimension":r["dimension"],"comparison":r["comparison"],
                 "note":"Objective is minimization; lower fitness is better."},artifacts)

    def _neuro_fuzzy(self,c,p,l):
        from modules.neuro_fuzzy.anfis import run_anfis_demo
        from core.visualizer import save_history_plot
        r=run_anfis_demo(**c)
        self.results.save_csv(p,"training_history.csv",r["history"])
        self.results.save_csv(p,"predictions.csv",r["predictions"])
        save_history_plot(r["history"],p/"anfis_training.png",x="epoch",series=("train_mse",),title="ANFIS training error")
        return ({k:v for k,v in r.items() if k not in ("history","predictions")},["training_history.csv","predictions.csv","anfis_training.png"])

    def _cnn(self,c,p,l):
        from modules.cnn_routing.train import run_cnn_demo
        from core.visualizer import save_history_plot
        r=run_cnn_demo(output_dir=p,**c)
        self.results.save_csv(p,"cnn_training_history.csv",r["history"])
        self.results.save_csv(p,"cnn_predictions.csv",r["predictions"])
        save_history_plot(r["history"],p/"cnn_training.png",x="epoch",series=("train_loss","validation_loss"),title="CNN loss")
        save_history_plot(r["history"],p/"cnn_accuracy.png",x="epoch",series=("validation_accuracy",),title="CNN validation accuracy")
        return ({k:v for k,v in r.items() if k not in ("history","predictions")},["cnn_training_history.csv","cnn_predictions.csv","cnn_training.png","cnn_accuracy.png"])


    def _gem5(self,c,p,l):
        from modules.gem5_garnet.topology import validate_mesh
        from modules.gem5_garnet.traffic import generate_traffic
        from modules.gem5_garnet.routing import route_packets
        from core.visualizer import save_mesh_plot
        rows=int(c.get("rows",4)); cols=int(c.get("cols",4))
        validate_mesh(rows,cols)
        packets=generate_traffic(rows,cols,int(c.get("packet_count",30)),int(c.get("seed",42)),c.get("traffic_pattern","uniform"))
        routed=route_packets(packets,rows,cols)
        save_mesh_plot(rows,cols,p/"gem5_mesh_topology.png")
        self.results.save_csv(p,"packet_routes.csv",[
            {"packet_id":x["packet_id"],"source":str(x["source"]),"destination":str(x["destination"]),
             "hops":x["hops"],"path":str(x["path"])} for x in routed["packets"]])
        preview={"backend":"Python educational Garnet-style topology/traffic preview (not GEM5 output)",
                 "rows":rows,"cols":cols,"traffic_pattern":c.get("traffic_pattern","uniform"),
                 "packet_count":len(packets),"total_hops":routed["total_hops"],
                 "average_hops":routed["average_hops"],"seed":int(c.get("seed",42))}
        actual=None
        if bool(c.get("gem5_binary")) != bool(c.get("config_script")):
            raise ValueError("Provide both gem5_binary and config_script for actual GEM5 execution, or leave both blank for the Python preview.")
        if c.get("gem5_binary") and c.get("config_script"):
            from modules.gem5_garnet.gem5_adapter import run_gem5
            actual=run_gem5(c["gem5_binary"],c["config_script"],p,c.get("args",""),int(c.get("timeout_seconds",3600)))
        return ({"python_preview":preview,"actual_gem5":actual,
                 "important_note":"Python preview metrics are educational estimates. Only actual_gem5.parsed_stats are from GEM5."},
                ["gem5_mesh_topology.png","packet_routes.csv"])

    @staticmethod
    def _zip(path):
        zpath=Path(path)/"experiment_artifacts.zip"
        with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
            for f in Path(path).iterdir():
                if f.is_file() and f != zpath: z.write(f,f.name)
