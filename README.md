# ai-lab-investment

A unified model of irreversible capacity investment with regime-switching demand, duopoly competition, endogenous default, and AI scaling laws. Delivers analytical triggers and Dario's dilemma (overinvestment asymmetry). See the [paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6305300) for details.

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

## License

Code is licensed under the [MIT License](LICENSE). The paper and slides (everything under `paper/` and `slides/`) are licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).

---

Repository initiated with [fintech-research/cookiecutter-py-quarto](https://github.com/fintech-research/cookiecutter-py-quarto).
