def _seed(st, container):
    return container.number_input("Random seed", 0, 2147483647, 42, help="Use the same seed to make a run reproducible.")


def render_config_form(st, name):
    """Render a clear, module-specific configuration form."""
    ids = {
        "Basic Genetic Algorithm": "basic-ga", "GEM5 / Garnet Full-System Simulation": "gem5-garnet",
        "NoC Routing Optimization using GA": "noc-routing-ga", "CNN Routing Path Prediction": "cnn-routing",
        "Nature-Inspired Algorithm Comparison": "metaheuristics", "Neuro-Fuzzy / ANFIS": "neuro-fuzzy",
        "Traveling Salesman Problem": "tsp",
    }
    st.markdown("### Experiment configuration")
    st.caption("Set the parameters below. Hover over a field's help icon for guidance, then launch the run.")
    with st.form("config_" + ids[name], border=True):
        c = {}
        if name == "Basic Genetic Algorithm":
            st.markdown("**Search space and population**")
            a, b = st.columns(2)
            c["chromosome_length"] = a.slider("Chromosome length", 2, 16, 5, help="Number of bits in each candidate solution.")
            c["population_size"] = b.number_input("Population size", 4, 500, 50)
            c["generations"] = a.number_input("Generations", 1, 2000, 100)
            c["tournament_size"] = b.number_input("Tournament size", 2, int(c["population_size"]), 3)
            st.markdown("**Evolution operators**")
            a, b, d = st.columns(3)
            c["crossover_rate"] = a.slider("Crossover rate", 0.0, 1.0, .8, .01)
            c["mutation_rate"] = b.slider("Mutation rate", 0.0, 1.0, .02, .01)
            c["seed"] = _seed(st, d)

        elif name == "Traveling Salesman Problem":
            st.markdown("**Problem size and search budget**")
            a, b = st.columns(2)
            c["cities_count"] = a.slider("Number of cities", 4, 100, 20)
            c["population_size"] = b.number_input("Population size", 4, 500, 80)
            c["generations"] = a.number_input("Generations", 1, 2000, 150)
            c["seed"] = _seed(st, b)
            st.markdown("**Evolution operators**")
            a, b = st.columns(2)
            c["crossover_rate"] = a.slider("Crossover rate", 0.0, 1.0, .9, .01)
            c["mutation_rate"] = b.slider("Mutation rate", 0.0, 1.0, .15, .01)

        elif name == "NoC Routing Optimization using GA":
            st.markdown("**Network topology**")
            a, b = st.columns(2)
            c["rows"] = a.slider("Mesh rows", 2, 8, 4)
            c["cols"] = b.slider("Mesh columns", 2, 8, 4)
            c["source"] = (0, 0)
            c["destination"] = (int(c["rows"]) - 1, int(c["cols"]) - 1)
            st.caption(f"Source router: {c['source']}  ·  Destination router: {c['destination']}  ·  {int(c['rows']) * int(c['cols'])} routers")
            st.markdown("**Genetic search**")
            a, b = st.columns(2)
            c["population_size"] = a.number_input("Population size", 4, 300, 40)
            c["generations"] = b.number_input("Generations", 1, 500, 60)
            c["mutation_rate"] = a.slider("Mutation rate", 0.0, 1.0, .2, .01)
            c["crossover_rate"] = b.slider("Crossover rate", 0.0, 1.0, .8, .01)
            c["congestion_weight"] = a.slider("Congestion penalty weight", 0.0, 10.0, 2.0, .1)
            c["seed"] = _seed(st, b)
            st.info("Congestion values are generated synthetic inputs. They are not live router measurements.")

        elif name == "CNN Routing Path Prediction":
            st.markdown("**Dataset and model**")
            a, b = st.columns(2)
            c["samples"] = a.number_input("Generated samples", 100, 20000, 1600, 100)
            c["grid_size"] = b.slider("Mesh grid size", 3, 16, 8)
            c["epochs"] = a.slider("Training epochs", 1, 100, 8)
            c["batch_size"] = b.select_slider("Batch size", options=[4, 8, 16, 32, 64, 128, 256, 512], value=64)
            c["learning_rate"] = a.number_input("Learning rate", .00001, .1, .001, format="%.5f")
            c["seed"] = _seed(st, b)
            st.caption("The generated labels follow dimension-order XY routing.")

        elif name == "Nature-Inspired Algorithm Comparison":
            st.markdown("**Benchmark settings**")
            a, b = st.columns(2)
            c["dimension"] = a.slider("Problem dimension", 2, 30, 5)
            c["population_size"] = b.number_input("Population / ant count", 8, 200, 30)
            c["iterations"] = a.number_input("Iterations", 5, 1000, 80)
            c["algorithm"] = b.selectbox("Algorithm selection", ["all", "ga", "pso", "aco", "sa"], format_func=lambda x: "Compare all four" if x == "all" else x.upper())
            c["seed"] = _seed(st, a)
            st.caption("Objective: Rastrigin minimization. Lower objective values are better; global minimum = 0.")

        elif name == "Neuro-Fuzzy / ANFIS":
            st.markdown("**Training settings**")
            a, b = st.columns(2)
            c["samples"] = a.number_input("Training dataset samples", 50, 5000, 350)
            c["epochs"] = b.slider("Training epochs", 1, 200, 25)
            c["learning_rate"] = a.number_input("Premise learning rate", .0001, .2, .035, format="%.4f")
            c["seed"] = _seed(st, b)
            st.caption("The demo approximates a generated two-input nonlinear function.")

        else:
            st.markdown("**Mesh and traffic generation**")
            a, b = st.columns(2)
            c["rows"] = a.slider("Mesh rows", 2, 16, 4)
            c["cols"] = b.slider("Mesh columns", 2, 16, 4)
            c["packet_count"] = a.number_input("Packets to generate", 1, 10000, 30)
            c["traffic_pattern"] = b.selectbox("Traffic pattern", ["uniform", "transpose", "hotspot", "neighbor"])
            c["seed"] = _seed(st, a)
            st.divider()
            with st.expander("Advanced · Optional actual GEM5 execution"):
                c["gem5_binary"] = st.text_input("GEM5 binary path", placeholder="/path/to/gem5.opt")
                c["config_script"] = st.text_input("Garnet config script path", placeholder="/path/to/config.py")
                c["args"] = st.text_input("Additional GEM5 arguments", placeholder="Optional command-line arguments")
                c["timeout_seconds"] = st.number_input("Execution timeout (seconds)", 60, 14400, 3600, step=60)
                st.warning("Provide both the compiled GEM5 binary and compatible config script, or leave both blank to use the Python preview.")

        st.divider()
        submitted = st.form_submit_button("▶  Launch experiment", type="primary", use_container_width=True)
    return submitted, c
