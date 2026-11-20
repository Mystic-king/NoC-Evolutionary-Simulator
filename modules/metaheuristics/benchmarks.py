"""Comparable continuous optimizers on the same Rastrigin minimization task."""
import math, random
import numpy as np

def rastrigin(x):
    x=np.asarray(x,dtype=float)
    return float(10*len(x)+np.sum(x*x-10*np.cos(2*math.pi*x)))

def _ga(dim,pop_size,iters,seed,bounds):
    rng=random.Random(seed); pop=[[rng.uniform(*bounds) for _ in range(dim)] for _ in range(pop_size)]
    hist=[]
    for t in range(iters+1):
        scores=[rastrigin(x) for x in pop]; bi=min(range(pop_size),key=scores.__getitem__)
        hist.append({"generation":t,"best_fitness":scores[bi]})
        if t==iters: break
        ranked=[x for _,x in sorted(zip(scores,pop),key=lambda z:z[0])]
        nxt=[ranked[0][:]]
        while len(nxt)<pop_size:
            a,b=rng.choice(ranked[:max(2,pop_size//2)]),rng.choice(ranked[:max(2,pop_size//2)])
            child=[(u+v)/2 if rng.random()<.5 else u for u,v in zip(a,b)]
            child=[max(bounds[0],min(bounds[1],v+rng.gauss(0,.35))) for v in child]
            nxt.append(child)
        pop=nxt
    return min(pop,key=rastrigin),hist

def _pso(dim,pop_size,iters,seed,bounds):
    rng=np.random.default_rng(seed); lo,hi=bounds
    pos=rng.uniform(lo,hi,(pop_size,dim)); vel=np.zeros_like(pos)
    pbest=pos.copy(); pscore=np.array([rastrigin(x) for x in pos])
    gi=int(np.argmin(pscore)); gbest=pbest[gi].copy(); hist=[]
    for t in range(iters+1):
        scores=np.array([rastrigin(x) for x in pos]); better=scores<pscore
        pbest[better]=pos[better]; pscore[better]=scores[better]
        gi=int(np.argmin(pscore)); gbest=pbest[gi].copy()
        hist.append({"generation":t,"best_fitness":float(pscore[gi])})
        if t==iters: break
        r1=rng.random((pop_size,dim)); r2=rng.random((pop_size,dim))
        vel=.72*vel+1.45*r1*(pbest-pos)+1.45*r2*(gbest-pos)
        pos=np.clip(pos+vel,lo,hi)
    return gbest.tolist(),hist

def _sa(dim,iters,seed,bounds):
    rng=random.Random(seed); current=[rng.uniform(*bounds) for _ in range(dim)]
    score=rastrigin(current); best=current[:]; best_score=score; hist=[]
    for t in range(iters+1):
        hist.append({"generation":t,"best_fitness":best_score})
        if t==iters: break
        temp=max(.01,1.0*(.015**(t/max(1,iters))))
        candidate=[max(bounds[0],min(bounds[1],v+rng.gauss(0,1.0))) for v in current]
        cs=rastrigin(candidate)
        if cs<score or rng.random()<math.exp(min(0,(score-cs)/temp)):
            current,score=candidate,cs
        if score<best_score: best,best_score=current[:],score
    return best,hist

def _aco(dim,iters,seed,bounds,bins=31,ants=30):
    rng=np.random.default_rng(seed); lo,hi=bounds
    grid=np.linspace(lo,hi,bins); pher=np.ones((dim,bins)); hist=[]; best=None; best_score=float("inf")
    for t in range(iters+1):
        candidates=[]
        for _ in range(ants):
            vec=[]
            for d in range(dim):
                probs=pher[d]**1.2; probs=probs/probs.sum()
                vec.append(float(grid[rng.choice(bins,p=probs)]))
            candidates.append(vec)
        scores=[rastrigin(x) for x in candidates]
        ix=int(np.argmin(scores))
        if scores[ix]<best_score: best,best_score=candidates[ix][:],scores[ix]
        hist.append({"generation":t,"best_fitness":best_score})
        if t==iters: break
        pher*=.88
        for vec,score in zip(candidates,scores):
            reward=1.0/(1.0+score)
            for d,val in enumerate(vec):
                j=int(np.argmin(np.abs(grid-val))); pher[d,j]+=reward*10
        pher=np.maximum(pher,1e-8)
    return best,hist

def compare_algorithms(dimension=5,population_size=30,iterations=80,seed=42,algorithm="all"):
    if not 2<=dimension<=30: raise ValueError("dimension must be between 2 and 30")
    if population_size<8: raise ValueError("population_size must be >= 8")
    if iterations<5: raise ValueError("iterations must be >= 5")
    if algorithm not in ("all","ga","pso","aco","sa"): raise ValueError("algorithm must be all, ga, pso, aco, or sa")
    funcs={"ga":lambda:_ga(dimension,population_size,iterations,seed,(-5.12,5.12)),
           "pso":lambda:_pso(dimension,population_size,iterations,seed,(-5.12,5.12)),
           "aco":lambda:_aco(dimension,iterations,seed,(-5.12,5.12),ants=population_size),
           "sa":lambda:_sa(dimension,iterations,seed,(-5.12,5.12))}
    chosen=list(funcs) if algorithm=="all" else [algorithm]
    comparison=[]; histories={}
    for name in chosen:
        solution,hist=funcs[name](); histories[name]=hist
        comparison.append({"algorithm":name.upper(),"best_fitness":float(rastrigin(solution)),
                           "best_solution":json_safe(solution),"objective":"minimize Rastrigin"})
    comparison.sort(key=lambda x:x["best_fitness"])
    return {"benchmark":"Rastrigin function (global optimum 0 at x=[0,...,0])",
            "dimension":dimension,"comparison":comparison,"histories":histories}

def json_safe(value):
    return [float(x) for x in value]
