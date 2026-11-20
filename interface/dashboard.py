from pathlib import Path
import json
from datetime import datetime

OUTPUT_DIR = Path("outputs/experiments")


def _load_runs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    runs = []
    for folder in sorted((p for p in OUTPUT_DIR.iterdir() if p.is_dir()), key=lambda p: p.name, reverse=True):
        result_file = folder / "results.json"
        if not result_file.exists():
            continue
        try:
            data = json.loads(result_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        runs.append({"folder": folder, "data": data})
    return runs


def render_dashboard(st):
    runs = _load_runs()
    st.markdown("<div class='hero'><div class='hero-kicker'>Network-on-Chip · Research & learning</div><h1>Simulation workspace</h1><p>Design experiments, explore routing strategies and compare evolutionary intelligence methods — all from one place.</p></div>", unsafe_allow_html=True)

    total = len(runs)
    completed = sum(1 for r in runs if r["data"].get("status") == "completed")
    latest = runs[0]["folder"].name if runs else "—"
    a, b, c, d = st.columns(4)
    a.metric("Practical modules", "07", help="Seven practical modules are available in the experiment lab.")
    b.metric("Experiments saved", total)
    c.metric("Completed runs", completed)
    d.metric("Latest run", latest[-8:] if latest != "—" else "—")

    st.markdown("<div class='section-label'>Explore the workspace</div>", unsafe_allow_html=True)
    cards = [
        ("01", "GEM5 / Garnet", "Mesh topology, traffic patterns and XY routing preview."),
        ("02", "NoC routing GA", "Search for low-cost paths through a mesh network."),
        ("03", "CNN routing", "Train a CNN to predict dimension-order next hops."),
        ("04", "Metaheuristics", "Compare GA, PSO, ACO and simulated annealing."),
        ("05", "Basic GA", "Explore selection, crossover, mutation and elitism."),
        ("06", "ANFIS", "Train a Sugeno neuro-fuzzy approximation model."),
        ("07", "Traveling Salesperson", "Optimize a closed tour with a permutation GA."),
    ]
    cols = st.columns(3)
    for i, (num, title, desc) in enumerate(cards):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"<div style='color:#4bd8c8;font-weight:700;font-size:.75rem;letter-spacing:.12em'>PRACTICAL {num}</div><div style='font-family:Space Grotesk;font-size:1.08rem;font-weight:700;margin:.35rem 0'>{title}</div><div class='small-muted'>{desc}</div>", unsafe_allow_html=True)

    left, right = st.columns([1.25, .75], gap="large")
    with left:
        st.subheader("Recent activity")
        if not runs:
            st.info("Your experiment timeline is empty. Open **Experiment Lab** to run your first practical.")
        else:
            rows = []
            for item in runs[:8]:
                data = item["data"]
                rows.append({"Experiment": data.get("experiment", "—").replace("-", " ").title(),
                             "Run ID": item["folder"].name,
                             "Status": data.get("status", "saved"),
                             "Artifacts": len(list(item["folder"].iterdir()))})
            st.dataframe(rows, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Quick guide")
        with st.container(border=True):
            st.markdown("**01 · Choose a practical**")
            st.caption("Select one of the seven modules in Experiment Lab.")
            st.markdown("**02 · Configure parameters**")
            st.caption("Adjust population, generations, topology or model settings.")
            st.markdown("**03 · Run and inspect**")
            st.caption("Review charts, metrics, configuration and generated reports.")
            st.markdown("**04 · Export your work**")
            st.caption("Download the PDF report or complete experiment ZIP.")

    st.caption("Tip: compare multiple runs with different random seeds to understand how stochastic algorithms behave.")


def render_history(st):
    st.markdown("<div class='hero'><div class='hero-kicker'>Experiment archive</div><h1>Run history</h1><p>Browse previous executions and retrieve the reports, raw results and complete artifact bundles.</p></div>", unsafe_allow_html=True)
    runs = _load_runs()
    if not runs:
        st.info("No experiments have been run yet. Your completed runs will appear here.")
        return
    search = st.text_input("Search experiments", placeholder="Filter by practical name or run ID…")
    filtered = [r for r in runs if search.lower() in (r["folder"].name + " " + str(r["data"].get("experiment", ""))).lower()]
    st.caption(f"Showing {len(filtered)} of {len(runs)} saved runs")
    for item in filtered:
        folder, data = item["folder"], item["data"]
        title = data.get("experiment", "Experiment").replace("-", " ").title()
        with st.expander(f"{title}  ·  {folder.name}", expanded=False):
            m1, m2, m3 = st.columns(3)
            m1.metric("Status", data.get("status", "saved"))
            m2.metric("Artifacts", len(list(folder.iterdir())))
            m3.metric("Run ID", folder.name[-12:])
            files = [("PDF report", "report.pdf", "application/pdf"),
                     ("Complete ZIP bundle", "experiment_artifacts.zip", "application/zip"),
                     ("Results JSON", "results.json", "application/json"),
                     ("Simulation log", "simulation.log", "text/plain")]
            buttons = st.columns(len(files))
            for col, (label, filename, mime) in zip(buttons, files):
                path = folder / filename
                if path.exists():
                    col.download_button(label, path.read_bytes(), file_name=f"{folder.name}_{filename}", mime=mime,
                                        key=f"hist_{folder.name}_{filename}", use_container_width=True)
            if data:
                with st.popover("View result summary"):
                    st.json(data)
