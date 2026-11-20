from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

def save_history_plot(rows, path, x="generation", series=("best_fitness","average_fitness"), title="Convergence"):
    fig, ax = plt.subplots(figsize=(8,4.5))
    for key in series:
        if rows and key in rows[0]:
            ax.plot([r[x] for r in rows], [r[key] for r in rows], label=key.replace("_"," ").title())
    ax.set_title(title); ax.set_xlabel(x.replace("_"," ").title()); ax.set_ylabel("Value")
    ax.grid(alpha=.25); ax.legend(); fig.tight_layout()
    fig.savefig(path, dpi=150); plt.close(fig)
    return Path(path)

def save_mesh_plot(rows, cols, path, route=None, title="2D Mesh NoC"):
    g = nx.grid_2d_graph(rows, cols)
    pos = {(r,c):(c,-r) for r,c in g.nodes}
    fig, ax = plt.subplots(figsize=(7,6))
    nx.draw_networkx_edges(g,pos,ax=ax,width=1.5,edge_color="#9aa4b2")
    nx.draw_networkx_nodes(g,pos,ax=ax,node_size=650,node_color="#cfe8ff",edgecolors="#245b88")
    labels = {n:f"R{n[0]*cols+n[1]}" for n in g.nodes}
    nx.draw_networkx_labels(g,pos,labels=labels,ax=ax,font_size=8)
    if route:
        edges=list(zip(route,route[1:]))
        nx.draw_networkx_edges(g,pos,edgelist=edges,ax=ax,width=3,edge_color="#e4572e")
        nx.draw_networkx_nodes(g,pos,nodelist=route,ax=ax,node_size=700,node_color="#ffd6a5",edgecolors="#e4572e")
    ax.set_title(title); ax.axis("off"); fig.tight_layout(); fig.savefig(path,dpi=160); plt.close(fig)
    return Path(path)

def save_tsp_plot(cities, route, path, title="TSP route"):
    fig, ax = plt.subplots(figsize=(7,6))
    xs=[cities[i][0] for i in route]+[cities[route[0]][0]]
    ys=[cities[i][1] for i in route]+[cities[route[0]][1]]
    ax.plot(xs,ys,"o-",linewidth=1.8); ax.scatter(xs[0],ys[0],s=100,marker="s",label="Start")
    for i,(x,y) in enumerate(cities): ax.annotate(str(i),(x,y),xytext=(4,4),textcoords="offset points")
    ax.set_title(title); ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.grid(alpha=.25); ax.legend()
    fig.tight_layout(); fig.savefig(path,dpi=160); plt.close(fig); return Path(path)


def save_comparison_plot(rows, path):
    fig, ax = plt.subplots(figsize=(7,4.5))
    labels=[r["algorithm"] for r in rows]
    values=[r["best_fitness"] for r in rows]
    ax.bar(labels,values)
    ax.set_title("Metaheuristic benchmark comparison (lower is better)")
    ax.set_ylabel("Best Rastrigin objective")
    ax.grid(axis="y",alpha=.25)
    fig.tight_layout(); fig.savefig(path,dpi=150); plt.close(fig)
    return Path(path)
