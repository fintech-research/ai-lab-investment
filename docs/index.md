# AI Lab Investment

Analysis code for *Investing in Artificial General Intelligence* — a model of irreversible capacity investment under regime-switching demand uncertainty with duopoly competition, endogenous default risk, and diminishing returns calibrated to AI scaling laws.

## Project structure

```
src/ai_lab_investment/
├── __main__.py              # Entry point (python -m ai_lab_investment)
├── pipeline.py              # Hydra-based pipeline orchestration
├── exceptions.py            # Custom exceptions
├── models/                  # Core economic models
│   ├── parameters.py        # ModelParameters dataclass
│   ├── base_model.py        # SingleFirmModel (regime-switching real options)
│   ├── duopoly.py           # DuopolyModel (preemption equilibrium)
│   ├── nfirm.py             # NFirmModel (N-firm sequential entry)
│   ├── valuation.py         # ValuationAnalysis (decomposition, credit risk)
│   └── symbolic_duopoly.py  # SymPy symbolic derivation and verification
├── calibration/             # Calibration to AI firm archetypes
│   ├── data.py              # FirmData, CalibrationData dataclasses
│   └── revealed_beliefs.py  # RevealedBeliefs inversion algorithm
├── figures/                 # Publication-quality figure generation
│   ├── phase1.py            # Single-firm comparative statics
│   ├── phase2.py            # Duopoly equilibrium and default
│   ├── phase3.py            # N-firm crowding effects
│   ├── phase4.py            # Calibration and revealed beliefs
│   ├── phase5.py            # Valuation and AI investment dilemma
│   └── phi_allocation.py    # Training-inference allocation plots
├── tables/                  # Table generation
├── data/                    # Data loading utilities
└── utils/
    ├── directories.py       # DataDirectories, ResultsDirectories
    └── files.py             # Timestamped file naming
```

## Pipeline

The analysis runs as a Hydra-managed pipeline. Each phase can be toggled independently via `conf/config.yaml`:

| Phase | Config flag | Description |
|-------|-------------|-------------|
| 1 | `tasks.phase1_base_model` | Single-firm investment triggers and comparative statics |
| 2 | `tasks.phase2_duopoly` | Duopoly preemption with default risk |
| 3 | `tasks.phase3_nfirm` | N-firm sequential entry (numerical) |
| 4 | `tasks.phase4_calibration` | Calibration to AI firm archetypes, revealed beliefs |
| 5 | `tasks.phase5_valuation` | Growth option decomposition, credit risk, AI investment dilemma |

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

- **`model_derivation.ipynb`** — Complete SymPy derivation of the core model (characteristic equations, option values, training-inference allocation, default boundary).
