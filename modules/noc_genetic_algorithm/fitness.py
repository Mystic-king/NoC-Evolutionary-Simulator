def path_cost(path,congestion=None,congestion_weight=2.0):
    congestion=congestion or {}
    hops=len(path)-1
    load=sum(float(congestion.get(node,0.0)) for node in path[1:-1])
    turns=sum(1 for i in range(2,len(path)) if
        (path[i-1][0]-path[i-2][0],path[i-1][1]-path[i-2][1]) !=
        (path[i][0]-path[i-1][0],path[i][1]-path[i-1][1]))
    return float(hops + congestion_weight*load + .05*turns)
