# NoC Evolutionary Simulator — Release 1.1

A modular educational laboratory for Network-on-Chip concepts, evolutionary optimization,
CNN-based routing prediction, and neuro-fuzzy learning. The Streamlit GUI and Typer CLI
call the same Python simulation services.

## Practical modules

| Practical | Implementation | Notes |
|---|---|---|
| Introduction to GEM5/Garnet | Mesh topology, traffic generation, XY routing preview, optional external GEM5 adapter | Python preview is explicitly not GEM5 output |
| Discrete NoC routing optimization using GA | Genetic search over valid mesh paths | Uses a seeded synthetic congestion model |
| CNN routing path prediction | PyTorch CNN classifier | Learns generated XY next-hop labels |
| Nature-inspired/metaheuristic algorithms | GA, PSO, ACO and simulated annealing | Comparable Rastrigin minimization benchmark |
| Basic genetic algorithm | Binary chromosome GA | Maximizes `f(x)=x²` over a bounded integer domain |
| Neuro-fuzzy system | Two-input, four-rule Sugeno ANFIS | Hybrid least-squares and premise-parameter learning |
| GA for TSP | Permutation GA with order crossover and swap mutation | Generated Euclidean city coordinates |

## GUI experience (Release 1.1)

The Streamlit interface includes a redesigned dark research-workspace theme, a practical
module overview, recent-run activity, searchable experiment history, dedicated experiment
configuration panels, execution status, interactive result tabs, convergence charts, artifact
previews and one-click downloads for PDF/ZIP/JSON/log files. The interface is responsive
and uses standard Streamlit components; no separate frontend build is required.

## Platform capabilities

- Shared simulation engine for GUI and CLI
- Per-run configuration, JSON results, logs, CSV histories, figures and PDF report
- ZIP bundle for each experiment
- Seeded, reproducible stochastic algorithms
- Input validation and error artifacts
- Unit and smoke tests
- Optional actual GEM5 execution through an external binary and user-supplied config script

## System requirements

- Python 3.10 or newer (Python 3.11 recommended)
- macOS, Linux or Windows
- 4 GB RAM minimum; 8 GB recommended for CNN training
- A modern CPU; CUDA is optional (the current CNN training implementation runs on CPU)
- Actual GEM5 practical: separately compiled GEM5 with a compatible Garnet configuration script

## Installation

```bash
git clone <your-repository-url>
cd NoC-Evolutionary-Simulator

python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e .
pip install -e ".[dev]"
```

PyTorch is a core dependency because the CNN practical is part of the platform. If pip
cannot find a suitable PyTorch wheel for your operating system/Python version, install
the appropriate CPU or accelerator build from the official PyTorch installation selector,
then rerun `pip install -e .`.

## Start the GUI

```bash
streamlit run app.py
```

## CLI

```bash
python main.py list
python main.py --help
python main.py run --help
```

Examples:

```bash
# Basic GA
python main.py run basic-ga --config '{"population_size":50,"generations":100,"seed":42}'

# TSP
python main.py run tsp --config '{"cities_count":20,"population_size":80,"generations":150,"seed":42}'

# NoC routing GA
python main.py run noc-routing-ga --config '{"rows":4,"cols":4,"source":[0,0],"destination":[3,3],"population_size":40,"generations":60,"seed":42}'

# Compare GA, PSO, ACO and SA
python main.py run metaheuristics --config '{"dimension":5,"population_size":30,"iterations":80,"algorithm":"all","seed":42}'

# ANFIS
python main.py run neuro-fuzzy --config '{"samples":350,"epochs":25,"learning_rate":0.035,"seed":42}'

# CNN
python main.py run cnn-routing --config '{"samples":1600,"epochs":8,"batch_size":64,"grid_size":8,"seed":42}'

# GEM5/Garnet Python learning preview (not actual GEM5)
python main.py run gem5-garnet --config '{"rows":4,"cols":4,"packet_count":30,"traffic_pattern":"uniform","seed":42}'

# Actual GEM5 requires an installed binary and a compatible config script
python main.py run gem5-garnet --config '{"rows":4,"cols":4,"packet_count":30,"gem5_binary":"build/ALL/gem5.opt","config_script":"path/to/garnet_config.py","args":"--help","timeout_seconds":3600}'
```

List previous runs:

```bash
python main.py show-results
```

## Output structure

Each experiment creates a unique directory:

```text
outputs/experiments/<experiment>_<timestamp>_<run-id>/
├── configuration.json
├── results.json
├── simulation.log
├── report.pdf
├── experiment_artifacts.zip
└── experiment-specific CSV, PNG, model and simulator files
```

The `experiment_artifacts.zip` contains the run's output files except itself. The parent
folder remains the canonical, unpacked record of the run.

## Practical correctness and interpretation

1. A stochastic optimizer should be run with multiple seeds when comparing methods.
2. A single best result does not prove an algorithm is globally optimal.
3. CNN labels in this release are generated from XY dimension-order routing; accuracy
   measures agreement with that synthetic labeling rule.
4. ANFIS is evaluated on a synthetic mathematical target function.
5. NoC GA congestion values are seeded synthetic penalties, not measured network counters.
6. The GEM5 Python preview is for teaching topology, packet generation and routing.
   Only a successful external GEM5 run produces actual GEM5 statistics.
7. GEM5 configuration options vary by version. Use a Garnet config script compatible
   with the GEM5 build installed on the machine.

## Run tests

```bash
pytest -q
```

## Development note

This is a functional educational release, not a replacement for hardware validation or
the official GEM5 documentation. Before institutional deployment, pin dependency versions,
run tests on the target lab machines, review security and accessibility, and maintain a
known-good GEM5 build/configuration pair.
