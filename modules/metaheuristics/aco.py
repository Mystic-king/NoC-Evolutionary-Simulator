from modules.metaheuristics.benchmarks import _aco, rastrigin

def optimize_rastrigin(dimension=5,ant_count=30,iterations=80,seed=42,bounds=(-5.12,5.12)):
    solution,history=_aco(dimension,iterations,seed,bounds,ants=ant_count)
    return {"algorithm":"ACO","solution":solution,"fitness":rastrigin(solution),"history":history}
