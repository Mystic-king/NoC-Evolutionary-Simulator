import random
from modules.tsp.cities import generate_cities,distance_matrix

def solve_tsp(cities_count=20,population_size=100,generations=200,crossover_rate=.9,mutation_rate=.15,seed=42,elite_size=2):
    if cities_count<4: raise ValueError("cities_count must be >= 4")
    if population_size<4: raise ValueError("population_size must be >= 4")
    if generations<1: raise ValueError("generations must be >= 1")
    if not 0<=crossover_rate<=1 or not 0<=mutation_rate<=1: raise ValueError("Rates must be in [0,1]")
    if not 1<=elite_size<population_size: raise ValueError("elite_size must be in [1,population_size-1]")
    rng=random.Random(seed); cities=generate_cities(cities_count,seed); d=distance_matrix(cities)
    def length(route): return sum(d[route[i]][route[(i+1)%len(route)]] for i in range(len(route)))
    def select(pop):
        return min(rng.sample(pop,min(4,len(pop))),key=length)[:]
    def ox(a,b):
        if rng.random()>=crossover_rate: return a[:]
        lo,hi=sorted(rng.sample(range(len(a)),2)); child=[None]*len(a)
        child[lo:hi+1]=a[lo:hi+1]
        fill=[x for x in b if x not in child]; j=0
        for i in list(range(hi+1,len(a)))+list(range(0,lo)): child[i]=fill[j]; j+=1
        return child
    pop=[]
    base=list(range(cities_count))
    for _ in range(population_size):
        route=base[:]; rng.shuffle(route); pop.append(route)
    hist=[]
    for gen in range(generations+1):
        ranked=sorted(pop,key=length)
        hist.append({"generation":gen,"best_distance":length(ranked[0]),"average_distance":sum(map(length,pop))/len(pop)})
        if gen==generations: break
        nxt=[x[:] for x in ranked[:elite_size]]
        while len(nxt)<population_size:
            child=ox(select(pop),select(pop))
            if rng.random()<mutation_rate:
                i,j=rng.sample(range(cities_count),2); child[i],child[j]=child[j],child[i]
            nxt.append(child)
        pop=nxt
    best=min(pop,key=length)
    return {"algorithm":"Permutation Genetic Algorithm","objective":"minimize closed-tour Euclidean distance",
            "best_route":best,"best_distance":length(best),"cities":cities,"history":hist,
            "seed":seed,"cities_count":cities_count,"population_size":population_size,"generations":generations}
