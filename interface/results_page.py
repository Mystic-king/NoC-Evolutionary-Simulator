from pathlib import Path
import json
import pandas as pd

METRICS = [
    ("best_solution", "Best solution", lambda v: str(v)),
    ("best_fitness", "Best fitness", lambda v: f"{float(v):.5f}"),
    ("best_distance", "Best tour distance", lambda v: f"{float(v):.3f}"),
    ("best_cost", "Optimized path cost", lambda v: f"{float(v):.3f}"),
    ("hop_count", "Route hops", lambda v: str(v)),
    ("validation_accuracy", "Validation accuracy", lambda v: f"{float(v):.1%}"),
    ("validation_rmse", "Validation RMSE", lambda v: f"{float(v):.5f}"),
    ("average_hops", "Average packet hops", lambda v: f"{float(v):.2f}"),
    ("total_hops", "Total packet hops", lambda v: str(v)),
]


def _chart_from_csv(st, path, title):
    if not path.exists():
        return
    try:
        frame = pd.read_csv(path)
    except Exception:
        return
    numeric = [c for c in frame.select_dtypes(include="number").columns if c.lower() not in ("epoch", "generation", "iteration", "step")]
    x = next((c for c in ("generation", "epoch", "iteration", "step") if c in frame.columns), None)
    if numeric:
        st.markdown(f"**{title}**")
        chart_data = frame.set_index(x)[numeric] if x else frame[numeric]
        st.line_chart(chart_data, use_container_width=True)


def render_results(st, result):
    if not result:
        st.markdown("### Results preview")
        st.info("Run a practical to see its metrics, charts, configuration and downloadable artifacts here.")
        return
    run_dir = Path(result.get("run_directory", "outputs"))
    st.divider()
    st.markdown("<div class='section-label'>Execution output</div>", unsafe_allow_html=True)
    st.subheader("Experiment results")
    st.caption(f"Run ID: {run_dir.name}  ·  Status: {result.get('status', 'completed')}")

    available = [(label, fmt(result[key])) for key, label, fmt in METRICS if key in result and result[key] is not None]
    if available:
        cols = st.columns(min(4, len(available)))
        for i, (label, value) in enumerate(available):
            cols[i % len(cols)].metric(label, value)

    overview, charts, artifacts, details = st.tabs(["Overview", "Visual analytics", "Downloads", "Configuration & raw data"])
    with overview:
        if result.get("methodology"):
            st.markdown("**Methodology**")
            st.write(result["methodology"])
        if result.get("objective_description"):
            st.markdown("**Objective**")
            st.write(result["objective_description"])
        if isinstance(result.get("comparison"), list) and result["comparison"]:
            st.markdown("**Algorithm comparison**")
            frame = pd.DataFrame(result["comparison"])
            st.dataframe(frame, use_container_width=True, hide_index=True)
            if "best_fitness" in frame.columns:
                st.bar_chart(frame.set_index("algorithm")[["best_fitness"]])
        if result.get("important_note"):
            st.info(result["important_note"])

    with charts:
        chart_files = [
            ("fitness_history.csv", "Fitness convergence"), ("distance_history.csv", "Tour distance convergence"),
            ("routing_fitness.csv", "Routing optimization convergence"), ("training_history.csv", "ANFIS training"),
            ("cnn_training_history.csv", "CNN training"),
        ]
        found = False
        for filename, title in chart_files:
            if (run_dir / filename).exists():
                _chart_from_csv(st, run_dir / filename, title)
                found = True
        images = [
            ("optimized_route.png", "Optimized NoC route"), ("best_route.png", "Best TSP route"),
            ("algorithm_comparison.png", "Algorithm comparison"), ("cnn_accuracy.png", "CNN validation accuracy"),
            ("gem5_mesh_topology.png", "GEM5 / Garnet mesh preview"), ("anfis_training.png", "ANFIS training error"),
        ]
        for filename, title in images:
            path = run_dir / filename
            if path.exists():
                st.markdown(f"**{title}**")
                st.image(str(path), use_container_width=True)
                found = True
        if not found:
            st.caption("No chart artifacts were generated for this practical.")

    with artifacts:
        file_specs = [
            ("PDF practical report", "report.pdf", "application/pdf"),
            ("Complete experiment bundle", "experiment_artifacts.zip", "application/zip"),
            ("Structured results", "results.json", "application/json"),
            ("Simulation log", "simulation.log", "text/plain"),
        ]
        cols = st.columns(2)
        for i, (label, filename, mime) in enumerate(file_specs):
            path = run_dir / filename
            if path.exists():
                cols[i % 2].download_button(label, path.read_bytes(), file_name=filename, mime=mime,
                                            key=f"result_{run_dir.name}_{filename}", use_container_width=True)
        st.markdown("**Files generated for this run**")
        if run_dir.exists():
            st.dataframe([{"Artifact": p.name, "Size": f"{p.stat().st_size / 1024:.1f} KB"} for p in sorted(run_dir.iterdir()) if p.is_file()],
                         use_container_width=True, hide_index=True)

    with details:
        config_path = run_dir / "configuration.json"
        if config_path.exists():
            st.markdown("**Experiment configuration**")
            st.json(json.loads(config_path.read_text(encoding="utf-8")))
        st.markdown("**Complete result payload**")
        st.json(result)
