from core.visualizer import save_tsp_plot

def render_tour(cities,route,output_path):
    """Save a labeled closed-tour visualization for a TSP solution."""
    return save_tsp_plot(cities,route,output_path,title="Optimized Traveling Salesman Tour")
