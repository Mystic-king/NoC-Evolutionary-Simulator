from modules.metaheuristics.benchmarks import _ga, rastrigin

def optimize_rastrigin(dimension=5,population_size=30,iterations=80,seed=42,bounds=(-5.12,5.12)):
    solution,history=_ga(dimension,population_size,iterations,seed,bounds)
    return {"algorithm":"GA","solution":solution,"fitness":rastrigin(solution),"history":history}
