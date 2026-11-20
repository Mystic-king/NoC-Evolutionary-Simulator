import random
from collections import deque
from modules.gem5_garnet.topology import mesh_neighbors,validate_mesh
from modules.noc_genetic_algorithm.fitness import path_cost

def _all_simple_paths(src,dst,rows,cols,max_paths=300):
    q=deque([[src]]); found=[]
    while q and len(found)<max_paths:
        path=q.popleft(); node=path[-1]
        if node==dst: found.append(path); continue
        for nxt in mesh_neighbors(node,rows,cols):
            if nxt not in path and len(path)<rows*cols: q.append(path+[nxt])
    return found

def optimize_route(rows=4,cols=4,source=(0,0),destination=(3,3),population_size=40,generations=60,mutation_rate=.2,crossover_rate=.8,seed=42,congestion_weight=2.0):
    validate_mesh(rows,cols)
    if rows>8 or cols>8:
        raise ValueError("NoC routing GA supports meshes up to 8x8 in this release; larger topologies need a bounded path-search backend.")
    source=tuple(source); destination=tuple(destination)
    for node in (source,destination):
        if not (0<=node[0]<rows and 0<=node[1]<cols): raise ValueError(f"Endpoint {node} is outside mesh.")
    if source==destination: raise ValueError("Source and destination must differ.")
    if population_size<4 or generations<1: raise ValueError("population_size >= 4 and generations >= 1 required.")
    if not 0<=mutation_rate<=1 or not 0<=crossover_rate<=1: raise ValueError("mutation_rate and crossover_rate must be in [0,1]")
    rng=random.Random(seed); paths=_all_simple_paths(source,destination,rows,cols)
    if not paths: raise RuntimeError("No route exists between endpoints.")
    # Synthetic congestion is explicitly a model input, not measured GEM5 data.
    congestion={(r,c):rng.random()*.35 for r in range(rows) for c in range(cols)}
    def cost(path): return path_cost(path,congestion,congestion_weight)
    def crossover(a,b):
        common=[node for node in a[1:-1] if node in b[1:-1]]
        if not common or rng.random()>=crossover_rate: return a[:]
        pivot=rng.choice(common); candidate=a[:a.index(pivot)+1]+b[b.index(pivot)+1:]
        if len(set(candidate))!=len(candidate): return a[:]
        if any(abs(x[0]-y[0])+abs(x[1]-y[1])!=1 for x,y in zip(candidate,candidate[1:])): return a[:]
        return candidate
    pop=[rng.choice(paths)[:] for _ in range(population_size)]
    history=[]
    for gen in range(generations+1):
        ranked=sorted(pop,key=cost)
        history.append({"generation":gen,"best_fitness":cost(ranked[0]),"average_fitness":sum(map(cost,pop))/len(pop)})
        if gen==generations: break
        nxt=[ranked[0][:]]
        while len(nxt)<population_size:
            pool=ranked[:max(2,population_size//2)]
            parent_a,parent_b=rng.choice(pool),rng.choice(pool)
            child=crossover(parent_a,parent_b)
            if rng.random()<mutation_rate:
                child=rng.choice(paths)[:]
            nxt.append(child)
        pop=nxt
    best=min(pop,key=cost)
    return {"rows":rows,"cols":cols,"source":source,"destination":destination,"best_path":best,
            "best_cost":cost(best),"hop_count":len(best)-1,"congestion_model":"seeded synthetic node congestion",
            "seed":seed,"history":history,"candidate_simple_paths":len(paths),"crossover_rate":crossover_rate,
            "mutation_rate":mutation_rate,"congestion":{f"{r},{c}":v for (r,c),v in congestion.items()}}
