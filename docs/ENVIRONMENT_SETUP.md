# Environment Setup Guide

This project uses **uv** for fast, modern Python package management. This guide explains both traditional Python setup and uv approach.

---

## What is uv?

**uv** is an extremely fast Python package installer and resolver written in Rust. It's designed to be a drop-in replacement for pip and pip-tools.

**Key advantages:**
- ⚡ **10-100x faster** than pip
- 🔒 **Lockfile** for reproducible environments (`uv.lock`)
- 🎯 **Single command** for virtual env + install
- 🔄 **Compatible** with existing pip/requirements.txt workflows
- 📦 **Zero config** - works with standard `pyproject.toml`

**Official docs:** https://github.com/astral-sh/uv

---

## Setup Comparison

### Traditional Python Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest training_specialist/test_training.py -v

# Deactivate when done
deactivate
```

**Pros:**
- ✅ Familiar workflow
- ✅ Standard Python tools
- ✅ No new tool to learn

**Cons:**
- ❌ Slow dependency resolution
- ❌ Manual virtual env management
- ❌ No automatic lockfile

---

### uv Setup (This Project)

```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh
# OR
pip install uv

# Install all dependencies
# (automatically creates .venv if needed)
cd ai_agents
uv sync

# Run commands in virtual environment
uv run pytest training_specialist/test_training.py -v

# Add new dependencies
uv add package_name

# Add dev dependencies
uv add --dev pytest

# Run Python scripts
uv run python script.py

# Update dependencies
uv sync --upgrade
```

**Pros:**
- ✅ 10-100x faster installs
- ✅ Automatic virtual env management
- ✅ Lockfile for reproducibility (`uv.lock`)
- ✅ Single command (`uv run`) - no activation needed
- ✅ Cross-platform consistent behavior

**Cons:**
- ❌ New tool to learn
- ❌ Requires uv installation

---

## Project Structure

```
ai_agents/
├── pyproject.toml        # Dependencies and project config
├── uv.lock               # Lockfile for exact versions
├── .venv/                # Virtual environment (auto-created)
├── nutrition_specialist/ # Nutrition agent
├── training_specialist/  # Training agent
└── shared/               # Shared models and utilities
```

---

## Running Tests

### With uv (Recommended)

```bash
cd ai_agents

# Run all tests
uv run --extra dev pytest -v

# Run specific test file
uv run --extra dev pytest training_specialist/test_training.py -v

# Run specific test
uv run --extra dev pytest training_specialist/test_training.py::test_linear_progressive_hit_target -v

# Run with coverage
uv run --extra dev pytest --cov=. --cov-report=html
```

### With traditional Python

```bash
cd ai_agents

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Deactivate
deactivate
```

---

## Managing Dependencies

### With uv

```bash
# Add a new dependency
uv add pydantic

# Add a dev dependency
uv add --dev pytest mypy black

# Remove a dependency
uv remove package_name

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package_name@latest

# Show installed packages
uv pip list
```

### With traditional Python

```bash
# Add to pyproject.toml dependencies list manually
# Then reinstall
pip install -e .

# Or use pip directly (not recommended for this project)
pip install package_name

# Update
pip install --upgrade package_name

# Show installed packages
pip list
```

---

## pyproject.toml Configuration

This project uses `pyproject.toml` for Python package configuration (PEP 518):

```toml
[project]
name = "fitness-ai-agents"
version = "0.1.0"
description = "Multi-agent fitness coaching system"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0.0",  # Core dependency
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",    # Testing framework
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**How it works:**
- `dependencies`: Required for the package to run
- `dev`: Only needed for development (tests, linting, etc.)
- Both uv and pip can read this file

---

## Common Tasks

### Running Training Specialist Tests

```bash
cd ai_agents

# Run all training tests
uv run --extra dev pytest training_specialist/test_training.py -v

# Run specific test
uv run --extra dev pytest training_specialist/test_training.py::test_linear_progressive_hit_target -v
```

### Running Nutrition Specialist Tests

```bash
cd ai_agents

# Run all nutrition tests
uv run --extra dev pytest nutrition_specialist/test_nutrition.py -v
```

### Interactive Python Shell

```bash
# With uv
uv run python

# With traditional venv
source .venv/bin/activate
python
```

### Import Modules in Python

```python
# Example: Test algorithm interactively
from ai_agents.training_specialist.algorithm import apply_linear_progressive_rules
from ai_agents.shared.models import Set, Session

first_set = Set(weight=100, reps=11)
result = apply_linear_progressive_rules(
    first_set=first_set,
    rep_target=11,
    increment=2.5,
    last_session=None,
    last_successful_weight=97.5,
)
print(result.message)  # "Hit rep target! Next session: 102.5kg x 11 reps"
```

---

## Troubleshooting

### uv not found

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Verify installation
uv --version
```

### Tests not found

```bash
# Make sure you're in ai_agents directory
cd ai_agents

# Include dev dependencies
uv run --extra dev pytest -v
```

### Import errors

```bash
# Sync dependencies
uv sync

# Or reinstall
rm -rf .venv
uv sync
```

### Virtual environment issues

```bash
# Delete virtual environment
rm -rf .venv

# Recreate with uv
uv sync

# With traditional Python
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Migration Path

If you prefer traditional Python tools:

1. **Generate requirements.txt** from pyproject.toml:
   ```bash
   uv pip compile pyproject.toml -o requirements.txt
   uv pip compile pyproject.toml --extra dev -o requirements-dev.txt
   ```

2. **Use pip with generated files**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **But keep uv.lock** in git for reproducibility

---

## Best Practices

### For Development

1. **Always use uv run** for commands:
   ```bash
   uv run pytest -v
   uv run python script.py
   ```

2. **Don't activate .venv manually** - uv handles it

3. **Commit uv.lock** to git for reproducible builds

4. **Use --extra dev** for testing:
   ```bash
   uv run --extra dev pytest
   ```

### For CI/CD

```bash
# Fast, reproducible CI builds
uv sync --frozen  # Uses exact uv.lock versions
uv run --extra dev pytest
```

### For Production

```bash
# Install only production dependencies
uv sync --no-dev

# Run application
uv run python -m app
```

---

## Summary

| Feature | Traditional Python | uv |
|---------|-------------------|-----|
| **Speed** | Slow (pip) | 10-100x faster |
| **Virtual env** | Manual activation | Automatic (uv run) |
| **Lockfile** | requirements.txt | uv.lock |
| **Reproducibility** | Version ranges | Exact versions |
| **Learning curve** | Familiar | Minimal (similar to pip) |
| **Recommendation** | ❌ Use for compatibility | ✅ **Use for this project** |

**Bottom line:** uv is faster, simpler, and more reliable. Use `uv run` for everything!

---

## Quick Reference

```bash
# Setup
uv sync                          # Install all dependencies

# Development
uv run pytest -v                 # Run tests
uv run python script.py          # Run Python script

# Dependencies
uv add package                   # Add dependency
uv add --dev pytest             # Add dev dependency
uv remove package               # Remove dependency

# Updates
uv sync --upgrade               # Update all dependencies

# Help
uv --help                       # Show all commands
```
