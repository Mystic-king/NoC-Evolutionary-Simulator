from pathlib import Path
import streamlit as st

from core.simulation_manager import SimulationManager
from interface.dashboard import render_dashboard, render_history
from interface.experiment_page import PRACTICALS, render_experiment_intro
from interface.configuration import render_config_form
from interface.results_page import render_results

st.set_page_config(
    page_title="NoC Studio | Evolutionary Simulator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# A small, dependency-free design system. The application remains fully usable
# with Streamlit's standard components and does not require custom components.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#e8eef8; --muted:#91a2bb; --panel:#111d30; --line:rgba(148,163,184,.16); --accent:#45d6c5; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 12% 0%, rgba(31,91,117,.22), transparent 35%), #081321; color:var(--ink); }
.block-container { max-width: 1440px; padding-top: 2rem; padding-bottom: 3rem; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }
h1 { font-size:2.35rem !important; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0c192a,#0a1422); border-right:1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#aab9cc; }
[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(20,37,58,.96),rgba(13,27,44,.96)); border:1px solid var(--line); padding:17px 18px; border-radius:16px; }
[data-testid="stMetricLabel"] { color:#9eb0c6; }
[data-testid="stMetricValue"] { color:#f4f8ff; font-family:'Space Grotesk',sans-serif; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line) !important; border-radius:16px; }
.stButton > button, .stDownloadButton > button, button[kind="primary"] { border-radius:10px; font-weight:700; min-height:2.7rem; }
button[kind="primary"] { background:linear-gradient(100deg,#20bcae,#48d6c5); color:#06202a; border:0; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:var(--accent); color:var(--accent); }
[data-testid="stForm"] { background:rgba(17,29,48,.72); border:1px solid var(--line); padding:1.25rem; border-radius:18px; }
[data-testid="stTabs"] button { font-weight:600; }
hr { border-color:var(--line); }
.small-muted { color:#91a2bb; font-size:.88rem; }
.hero { padding:1.7rem 1.8rem; border:1px solid rgba(69,214,197,.2); border-radius:22px; background:linear-gradient(115deg,rgba(18,49,67,.96),rgba(15,29,49,.95) 60%,rgba(24,44,65,.9)); margin-bottom:1.3rem; }
.hero-kicker { color:#58decf; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; }
.hero h1 { margin:.35rem 0 .35rem 0; }
.hero p { color:#b7c6d9; max-width:780px; margin:0; }
.section-label { color:#54d9ca; text-transform:uppercase; font-size:.72rem; letter-spacing:.14em; font-weight:700; margin-bottom:.25rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='padding:10px 4px 18px'><div style='font-size:2rem'>🧬</div><div style='font-family:Space Grotesk;font-size:1.28rem;font-weight:700;color:#f2f7ff'>NoC <span style='color:#45d6c5'>STUDIO</span></div><div class='small-muted'>Evolutionary simulation workspace</div></div>", unsafe_allow_html=True)
    page = st.radio("WORKSPACE", ["Overview", "Experiment Lab", "Run History"],
                    index=["Overview", "Experiment Lab", "Run History"].index(st.session_state.get("page", "Overview")),
                    label_visibility="visible")
    st.session_state["page"] = page
    st.divider()
    if page == "Experiment Lab":
        st.markdown("**SELECT PRACTICAL**")
        selected = st.selectbox("Practical module", list(PRACTICALS), label_visibility="collapsed")
    else:
        selected = None
    st.divider()
    st.caption("VERSION 1.1 · LOCAL WORKSPACE")
    st.caption("Runs and artifacts are saved in `outputs/experiments`. ")

if page == "Overview":
    render_dashboard(st)
elif page == "Run History":
    render_history(st)
else:
    render_experiment_intro(st, selected)
    submitted, config = render_config_form(st, selected)
    if submitted:
        status = st.status("Preparing experiment…", expanded=True)
        try:
            status.write("Validating configuration and initializing the experiment workspace.")
            status.write("Executing the selected practical and generating report artifacts.")
            result = SimulationManager().run(PRACTICALS[selected], config)
            st.session_state["last_result"] = result
            st.session_state["last_result_for"] = selected
            status.update(label="Experiment completed", state="complete", expanded=False)
            st.toast("Experiment completed and artifacts saved.", icon="✅")
        except Exception as exc:
            status.update(label="Experiment failed", state="error", expanded=True)
            st.exception(exc)
            st.info("Open Run History and inspect the run folder's `simulation.log` or `failure.json` for diagnostics.")
    previous = st.session_state.get("last_result") if st.session_state.get("last_result_for") == selected else None
    render_results(st, previous)
