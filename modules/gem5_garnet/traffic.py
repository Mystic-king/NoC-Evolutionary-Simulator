import random

def generate_traffic(rows,cols,packet_count=30,seed=42,pattern="uniform"):
    if rows<2 or cols<2: raise ValueError("Traffic generation requires a mesh of at least 2x2.")
    if packet_count<1: raise ValueError("packet_count must be positive")
    if pattern not in ("uniform","transpose","hotspot","neighbor"):
        raise ValueError("pattern must be uniform, transpose, hotspot, or neighbor.")
    rng=random.Random(seed); nodes=[(r,c) for r in range(rows) for c in range(cols)]
    packets=[]
    for pid in range(packet_count):
        src=rng.choice(nodes)
        if pattern=="transpose": dst=(src[1]%rows,src[0]%cols)
        elif pattern=="hotspot": dst=(rows//2,cols//2)
        elif pattern=="neighbor": dst=rng.choice([n for n in nodes if abs(n[0]-src[0])+abs(n[1]-src[1])==1] or nodes)
        else: dst=rng.choice(nodes)
        if dst==src and len(nodes)>1: dst=nodes[(nodes.index(src)+1)%len(nodes)]
        packets.append({"packet_id":pid,"source":src,"destination":dst})
    return packets
