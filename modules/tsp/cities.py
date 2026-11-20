import random, math

def generate_cities(count=20,seed=42,scale=100):
    if count<4: raise ValueError("TSP requires at least 4 cities.")
    rng=random.Random(seed)
    return [(round(rng.uniform(0,scale),3),round(rng.uniform(0,scale),3)) for _ in range(count)]

def distance_matrix(cities):
    n=len(cities)
    return [[math.dist(cities[i],cities[j]) for j in range(n)] for i in range(n)]
