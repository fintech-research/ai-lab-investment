# ai-lab-investment

A real-options model of irreversible compute investment by AI laboratories, with regime-switching demand, a duopoly entry game, endogenous default, and a training-inference allocation. Delivers a closed-form training fraction and post-switch policy, the entry equilibrium (competition brings investment forward of the switch), faith-based survival, and Dario's dilemma (the cost of a mistaken belief about the switch). See the [paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300) for details.

- **Blog post** on the use of AI tools to write the paper: <https://vincent.codes.finance/posts/vibe-research-paper/>
- **Github repository**: <https://github.com/fintech-research/ai-lab-investment/>

## Getting started

### Requirements

The project assumes you have a Unix-like operating system (Linux or macOS). Windows users should consider using the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/) or a [devcontainer](#devcontainer).

The project requires the following software to be installed on your machine:

- [uv](https://docs.astral.sh/uv/): A modern Python environment and package manager.
- [Git](https://git-scm.com/): For version control.
- [just](https://github.com/casey/just): A modern command runner.
- [Quarto](https://quarto.org/docs/get-started/): For rendering documents.
- [TeX Live](https://www.tug.org/texlive/): For PDF generation from Quarto.

If you are using [Homebrew](https://brew.sh/), you can install most of these dependencies with the following command:

```bash
brew install uv git just quarto texlive
```

### Devcontainer

If you are using VSCode, you can also use the provided devcontainer configuration to set up a consistent development environment. This requires the [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) and a local installation of [Docker](https://www.docker.com/) or [Podman](https://podman.io/). Note that if you are using Podman, you will need to adjust some settings `devcontainer/devcontainer.json`, see the comments in that file for more details. The container includes all necessary dependencies. Once the container is built and running, you can move on to the "Installation" step below.

### Installation

To get started with this project, clone the repository to your local machine, then navigate into the project directory and type:

```bash
just install
```

This will create a virtual environment, install the required dependencies, set up pre-commit hooks, and create a local `.env` file from the example provided.

Make sure to edit the `.env` file to set your environment variables.

## Useful commands

The project includes a `justfile` with several useful commands. You can see the list of available commands by running:

```bash
just --list
```

Some commonly used commands include:

- `just test`: Run the test suite.
- `just check`: Run code linters, type checkers, and formatters.
- `just docs`: Build the project documentation.
- `just run-pipeline`: Run the analysis pipeline.
- `just render-paper`: Render the research paper.
- `just render-slides`: Render the presentation slides.
- `just preview-slides`: Preview the presentation slides in a web browser.

## Proof verification

Parts of the paper's closed-form algebra are machine-checked in [Lean 4](https://lean-lang.org/) against [Mathlib](https://github.com/leanprover-community/mathlib4). The Lean package lives in [`lean/`](lean/README.md) and proves, with kernel-checked, `sorry`-free proofs, identities and inequalities under stated hypotheses, conditional on the value functions and boundary conditions the paper derives:

- **The Euler ODE and characteristic roots**: `X^β` solves the homogeneous HJB equation iff `Q(β) = 0`; `β_H > 1`, `β_L⁺ > β_H`, `β_L⁻ < 0`; the Leland markup in `(0,1)`.
- **Proposition 1**: the closed-form training fraction `φ*` as the unique interior critical point, with its comparative statics; the post-switch trigger and NPV; the closed-form post-switch capacity `K_H*`, positive under (A2) and the unique global maximiser of its reduced objective; the particular solutions and first-order conditions of the pre-switch problem.
- **Proposition 2 and credit**: smooth pasting equivalent to the closed-form default boundary, the shutdown boundary, the faith-based survival threshold `φ̲` and its comparative statics, the boundary's monotonicity in leverage and rival capacity, and identities of the recovery rule at `φ*`.
- **Corollary 1**: installed value increasing and strictly concave in `λ` iff `φ > φ̲`, and the news identity.
- **Proposition 3**: the contest algebra behind the critical-point statement on the allocation, the fact that the follower's capacity condition has at most one root, and the algebra of the values before the first investment.

No theorem proves optimality of a stopping rule, existence or uniqueness of an equilibrium, or any number; `lean/README.md` lists what is not formalized. Each theorem holds for all admissible parameter values (not just the baseline calibration) and depends only on Lean's standard axioms. To reproduce:

```bash
cd lean
lake exe cache get   # download prebuilt Mathlib (first time only)
lake build           # kernel-checks every proof
```

See [`lean/README.md`](lean/README.md) for the full list of verified results, scope, and limitations.

## License

Code is licensed under the [MIT License](LICENSE). The paper and slides (everything under `paper/` and `slides/`) are licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).

---

Repository initiated with [fintech-research/cookiecutter-py-quarto](https://github.com/fintech-research/cookiecutter-py-quarto).
