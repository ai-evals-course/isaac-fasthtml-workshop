# FastHTML Demo Applications

This directory contains two FastHTML demo applications:

- `main_in_memory.py`: A simple in-memory data store demo
- `main_sqlite.py`: A SQLite-backed data store demo

## Prerequisites

- Python 3.11+
- `uv` package manager (recommended)

## Quick Start

### Using `uv` (Recommended)

1. Initialize the project:

```bash
uv init --app
```

2. Create and activate virtual environment:

```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
uv add -r requirements.txt
```

## Running the Applications

Choose one of the following applications to run:

### In-Memory Demo (simplest version)

```bash
uv run main_in_memory.py
```

### SQLite Demo (from the talk)

```bash
uv run main_sqlite.py
```

Both applications will start a local server at http://localhost:5001

## IDE Setup (VSCode/Cursor/etc...)

1. Open the project in VSCode
2. Press `Cmd + Shift + P` (Mac) or `Ctrl + Shift + P` (Windows/Linux)
3. Select "Python: Select Interpreter"
4. Choose the `.venv` environment from the list
5. Reload the window (`Cmd + Shift + P` → "Developer: Reload Window")

## Project Structure

- `main_in_memory.py`: In-memory data store demo
- `main_sqlite.py`: SQLite-backed data store demo
- `db.py`: Database utilities
- `requirements.txt`: Project dependencies
- `ds.csv`: Sample data file
