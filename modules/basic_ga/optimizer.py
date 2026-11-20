from dataclasses import asdict, dataclass
import random

@dataclass(frozen=True)
class GAConfig:
    chromosome_length:int=5
    population_size:int=50
    generations:int=100
    crossover_rate:float=.8
    mutation_rate:float=.02
    tournament_size:int=3
    seed:int=42
    def __post_init__(self):
        if self.chromosome_length<2: raise ValueError("chromosome_length must be >= 2")
        if self.population_size<4: raise ValueError("population_size must be >= 4")
        if self.generations<1: raise ValueError("generations must be >= 1")
        if not 0<=self.crossover_rate<=1: raise ValueError("crossover_rate must be in [0,1]")
        if not 0<=self.mutation_rate<=1: raise ValueError("mutation_rate must be in [0,1]")
        if not 2<=self.tournament_size<=self.population_size: raise ValueError("tournament_size must be in [2,population_size]")
    def to_dict(self): return asdict(self)

class BasicGeneticAlgorithm:
    """Binary GA maximizing f(x)=x^2 for x in [0, 2^bits-1]."""
    def __init__(self,config): self.config=config; self.rng=random.Random(config.seed)
    @staticmethod
    def decode(ch): return int("".join(map(str,ch)),2)
    def fitness(self,ch): return float(self.decode(ch)**2)
    def _select(self,pop):
        return max(self.rng.sample(pop,self.config.tournament_size),key=self.fitness)[:]
    def _cross(self,a,b):
        if self.rng.random()>=self.config.crossover_rate: return a[:],b[:]
        k=self.rng.randrange(1,len(a)); return a[:k]+b[k:],b[:k]+a[k:]
    def _mutate(self,ch):
        out=ch[:]
        for i in range(len(out)):
            if self.rng.random()<self.config.mutation_rate: out[i]^=1
        return out
    def run(self):
        pop=[[self.rng.randint(0,1) for _ in range(self.config.chromosome_length)] for _ in range(self.config.population_size)]
        history=[]
        for gen in range(self.config.generations+1):
            scores=[self.fitness(x) for x in pop]; bi=max(range(len(pop)),key=scores.__getitem__)
            history.append({"generation":gen,"best_fitness":scores[bi],"average_fitness":sum(scores)/len(scores),"best_solution":self.decode(pop[bi])})
            if gen==self.config.generations: break
            nxt=[pop[bi][:]]
            while len(nxt)<self.config.population_size:
                a,b=self._cross(self._select(pop),self._select(pop))
                nxt.append(self._mutate(a))
                if len(nxt)<self.config.population_size: nxt.append(self._mutate(b))
            pop=nxt
        best=max(pop,key=self.fitness); x=self.decode(best)
        return {"algorithm":"Binary Genetic Algorithm","objective":"maximize f(x)=x^2",
          "best_solution":x,"best_chromosome":"".join(map(str,best)),"best_fitness":self.fitness(best),
          "theoretical_optimum":((1<<self.config.chromosome_length)-1)**2,
          "generations_executed":self.config.generations,"seed":self.config.seed,
          "configuration":self.config.to_dict(),"history":history}
