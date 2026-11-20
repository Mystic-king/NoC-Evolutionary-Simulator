from modules.gem5_garnet.topology import xy_route

def route_packets(packets,rows,cols):
    routed=[]
    for packet in packets:
        path=xy_route(tuple(packet["source"]),tuple(packet["destination"]))
        routed.append({**packet,"path":path,"hops":len(path)-1})
    total_hops=sum(x["hops"] for x in routed)
    return {"packets":routed,"total_hops":total_hops,
            "average_hops":total_hops/len(routed) if routed else 0}
