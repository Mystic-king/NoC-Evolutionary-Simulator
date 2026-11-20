PRACTICALS = {
    "Basic Genetic Algorithm": "basic-ga",
    "GEM5 / Garnet Full-System Simulation": "gem5-garnet",
    "NoC Routing Optimization using GA": "noc-routing-ga",
    "CNN Routing Path Prediction": "cnn-routing",
    "Nature-Inspired Algorithm Comparison": "metaheuristics",
    "Neuro-Fuzzy / ANFIS": "neuro-fuzzy",
    "Traveling Salesman Problem": "tsp",
}
DESCRIPTIONS = {
    "Basic Genetic Algorithm": "Optimize a binary-encoded integer objective using tournament selection, crossover, mutation and elitism.",
    "GEM5 / Garnet Full-System Simulation": "Explore a 2D mesh, generate traffic patterns and inspect XY routing. Optionally run a real external GEM5/Garnet configuration.",
    "NoC Routing Optimization using GA": "Optimize a path through a 2D mesh using evolutionary search and a seeded synthetic congestion cost model.",
    "CNN Routing Path Prediction": "Generate labeled routing examples, train a convolutional classifier and evaluate held-out predictions.",
    "Nature-Inspired Algorithm Comparison": "Compare GA, PSO, ACO and simulated annealing on the same Rastrigin minimization benchmark.",
    "Neuro-Fuzzy / ANFIS": "Train a two-input Sugeno ANFIS with Gaussian membership functions and hybrid premise/consequent learning.",
    "Traveling Salesman Problem": "Find a short closed tour using a permutation genetic algorithm.",
}


def render_experiment_intro(st, name):
    st.markdown("<div class='section-label'>Experiment lab · Practical module</div>", unsafe_allow_html=True)
    st.title(name)
    st.write(DESCRIPTIONS[name])
    notes = {
        "GEM5 / Garnet Full-System Simulation": "Python preview is educational. Actual GEM5 statistics require a compatible compiled binary and Garnet configuration.",
        "NoC Routing Optimization using GA": "The congestion penalty is seeded synthetic input, not measured GEM5 traffic.",
        "CNN Routing Path Prediction": "Training labels are generated from XY routing rules; this is not a hardware-trained model.",
        "Neuro-Fuzzy / ANFIS": "The demonstration uses a generated synthetic target function.",
    }
    if name in notes:
        st.info(notes[name])
