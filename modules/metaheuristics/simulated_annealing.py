from modules.metaheuristics.benchmarks import _sa, rastrigin

def optimize_rastrigin(dimension=5,iterations=80,seed=42,bounds=(-5.12,5.12)):
    solution,history=_sa(dimension,iterations,seed,bounds)
    return {"algorithm":"SA","solution":solution,"fitness":rastrigin(solution),"history":history}
