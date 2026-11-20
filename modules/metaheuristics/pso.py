from modules.metaheuristics.benchmarks import _pso, rastrigin

def optimize_rastrigin(dimension=5,swarm_size=30,iterations=80,seed=42,bounds=(-5.12,5.12)):
    solution,history=_pso(dimension,swarm_size,iterations,seed,bounds)
    return {"algorithm":"PSO","solution":solution,"fitness":rastrigin(solution),"history":history}
