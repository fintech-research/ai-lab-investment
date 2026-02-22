set dotenv-load
data_dir := env('DATA_DIR', 'data')
results_dir := env('RESULTS_DIR', 'results')

# Show available recipes and their short descriptions
help:
    just --list

# Install the virtual environment and install the pre-commit hooks
install:
    @echo "🚀 Creating virtual environment using uv"
    uv sync
    @echo "🚀 Initializing git repo if it does not exist"
    [ -d .git ] || git init -b main
    @echo "🚀 Installing git pre-commit hooks"
    uv run pre-commit install
    @echo "🚀 Creating local .env file"
    cp .env-sample .env
    @echo "Done. ‼️ Edit the .env file to set your environment variables. ‼️"


# Initialize the data directory structure
init-data-dir:
    @echo "🚀 Initializing data directory in {{data_dir}}"
    mkdir -p {{data_dir}}/clean
    mkdir -p {{data_dir}}/preprocessing-cache
    mkdir -p {{data_dir}}/raw/download-cache
    mkdir -p {{data_dir}}/raw/open
    mkdir -p {{data_dir}}/raw/restricted
    mkdir -p {{data_dir}}/results

# Initialize the results directory structure
init-results-dir:
    @echo "🚀 Initializing results directory in {{results_dir}}/"
    mkdir -p {{results_dir}}/figures
    mkdir -p {{results_dir}}/tables
    mkdir -p {{results_dir}}/text


# Initialize both data and results directory structures
init-dirs: init-data-dir init-results-dir

# Run code quality tools.
check:
    @echo "🚀 Checking lock file consistency with 'pyproject.toml'"
    uv lock --locked
    @echo "🚀 Linting code: Running pre-commit"
    uv run pre-commit run -a
    @echo "🚀 Static type checking: Running ty"
    uv run ty check


# Test the code with pytest
test:
    @echo "🚀 Testing code: Running pytest"
    uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

# Test if documentation can be built without warnings or errors
docs-test:
    @echo "🚀 Testing docs build"
    uv run mkdocs build -s

# Build and serve the documentation
docs:
    @echo "🚀 Building and serving the documentation"
    uv run mkdocs serve

# Build the paper (touch index.qmd to ensure code is re-run)
render-paper:
    @echo "🚀 Building paper"
    touch paper/index.qmd
    uv run quarto render paper

# Build the slides
render-slides:
    @echo "🚀 Building long-form slides"
    touch slides/long-form/index.qmd
    uv run quarto render slides/long-form

# Preview the slides
preview-slides:
    @echo "🚀 Previewing long-form slides"
    touch slides/long-form/index.qmd
    uv run quarto preview slides/long-form

# Update dependencies to latest version that satisfy constraints in pyproject.toml
update-deps:
    @echo "🚀 Updating dependencies"
    uv lock --upgrade

# Run the analysis pipeline
run-pipeline:
    @echo "🚀 Running analysis pipeline"
    uv run python -m ai_lab_investment
