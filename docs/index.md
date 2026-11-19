# AI Lab Investment

Analysis code for *Investing in Artificial General Intelligence*: a real-options model of irreversible compute investment under regime-switching demand, with a duopoly entry game, endogenous default, a training-inference allocation, and diminishing returns to capacity motivated by AI scaling laws. The model of record is solved in its primitives: the training fraction and the post-switch policy are in closed form, and the pre-switch policy and the entry equilibrium are computed numerically. Parts of the closed-form algebra are machine-checked in Lean 4 (`lean/README.md` in the repository lists what is and is not covered).

## Project structure

```
src/ai_lab_investment/
├── __main__.py              # Entry point (python -m ai_lab_investment)
├── pipeline.py              # Hydra-based pipeline orchestration
├── exceptions.py            # Custom exceptions
├── models/                  # Core economic models
│   ├── parameters.py        # ModelParameters dataclass
│   ├── base_model.py        # SingleFirmModel (regime-switching real options)
│   ├── piecewise_option.py  # Exact piecewise single-firm problem (model of record)
│   ├── duopoly.py           # DuopolyModel (entry game in the exact primitives)
│   ├── preemption_exact.py  # Entry game in the exact primitives, no credit
│   ├── preemption_levered.py # Entry game with shutdown, default and debt (model of record)
│   ├── belief_mismatch.py   # Dario's dilemma at the exact policies
│   ├── capability_stock.py  # Capability-stock research prototype (not in the pipeline)
│   ├── valuation.py         # ValuationAnalysis (decomposition, credit risk)
│   └── symbolic_duopoly.py  # SymPy symbolic derivation and verification
├── calibration/             # Calibration to AI firm archetypes
│   ├── data.py              # FirmData, CalibrationData dataclasses
│   ├── archetypes.py        # Archetype-level outputs at the assigned allocations
│   └── revealed_beliefs.py  # RevealedBeliefs inversion algorithm
├── figures/                 # Publication-quality figure generation
│   ├── paper.py             # All paper figures (source of truth)
│   ├── phase1.py            # Single-firm comparative statics
│   ├── phase2.py            # Duopoly equilibrium and default
│   ├── phase4.py            # Calibration and revealed beliefs
│   └── phase5.py            # Valuation and Dario's dilemma
├── robustness.py            # One-at-a-time and joint robustness sweeps
└── utils/
    ├── directories.py       # DataDirectories, ResultsDirectories
    └── files.py             # Timestamped file naming
```

## Pipeline

The analysis runs as a Hydra-managed pipeline. Each phase can be toggled independently via `conf/config.yaml`:

| Phase | Config flag | Description |
|-------|-------------|-------------|
| 1 | `tasks.phase1_base_model` | Single-firm investment triggers and comparative statics |
| 2 | `tasks.phase2_duopoly` | Duopoly entry game with default risk |
| 4 | `tasks.phase4_calibration` | Calibration to AI firm archetypes, revealed beliefs |
| 5 | `tasks.phase5_valuation` | Growth option decomposition, credit risk, Dario's dilemma |
| - | `tasks.robustness_sweep` | Robustness sweeps of Internet Appendix D and E |

Run the full pipeline:

```bash
just run-pipeline
```

Or individual phases via Hydra overrides:

```bash
uv run python -m ai_lab_investment tasks.phase1_base_model=true
```

## Notebooks

The `notebooks/` directory contains interactive derivations:

- **`model_derivation.ipynb`**: SymPy checks of the identities behind Propositions 1 to 3 (characteristic equations, the piecewise pre-switch solution, the training-inference allocation, the default boundary and its thresholds, the recovery rule), with numerical cross-checks against the model code. It covers symbolic identities only, not the levels of the entry equilibrium.
