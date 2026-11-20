import numpy as np

DIRECTIONS={"E":0,"W":1,"S":2,"N":3}
def generate_routing_dataset(samples=1600,grid_size=8,seed=42):
    """Create labeled samples: [current-router map, destination map, congestion map]."""
    if grid_size<3: raise ValueError("grid_size must be >= 3")
    rng=np.random.default_rng(seed); x=np.zeros((samples,3,grid_size,grid_size),dtype=np.float32)
    y=np.zeros(samples,dtype=np.int64)
    for i in range(samples):
        src=(int(rng.integers(grid_size)),int(rng.integers(grid_size)))
        dst=(int(rng.integers(grid_size)),int(rng.integers(grid_size)))
        while dst==src: dst=(int(rng.integers(grid_size)),int(rng.integers(grid_size)))
        x[i,0,src[0],src[1]]=1.0; x[i,1,dst[0],dst[1]]=1.0
        x[i,2]=rng.random((grid_size,grid_size),dtype=np.float32)
        # Ground-truth dimension-order XY next hop: horizontal first, then vertical.
        if src[1]!=dst[1]: y[i]=DIRECTIONS["E"] if dst[1]>src[1] else DIRECTIONS["W"]
        else: y[i]=DIRECTIONS["S"] if dst[0]>src[0] else DIRECTIONS["N"]
    return x,y
