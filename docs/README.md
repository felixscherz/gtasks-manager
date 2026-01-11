# Development Documentation

This directory contains additional documentation for developers working on gtasks-manager.

## Quick Start for Developers

### Using uv for Development

We recommend using `uv` for fast dependency management and command execution:

```bash
# Install dependencies and run any command
uv run <command>

# Examples:
uv run gtasks list
uv run pytest
uv run ruff check .
```

### Dependency Management

The project uses `uv.lock` for reproducible dependency resolution:

```bash
# Update dependencies and lock file
uv lock --upgrade

# Install dependencies from lock file
uv sync
```

**Important**: After adding or updating dependencies in `pyproject.toml`, always run `uv lock --upgrade` to update the lock file.

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=gtasks_manager

# Run specific test
uv run pytest tests/unit/test_task_cache.py::test_function_name
```

### Code Quality

```bash
# Lint code
uv run ruff check .

# Format code
uv run ruff format .
```

## Documentation Files

- `textual-framework-guide.md`: Comprehensive guide for working with Textual TUI framework
