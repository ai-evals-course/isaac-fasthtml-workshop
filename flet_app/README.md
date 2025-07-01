# Flet Annotation App

This directory contains a [Flet](https://flet.dev) and sqlite based annotation app. 

## Why Flet?

Just to try things out:

I find Flet interesting, as it enables building desktop, mobile, and web apps with Python. Flet uses Flutter and Dart under the hood, and web apps can run as client-server apps with websockets based communcation, or as client (browser) only apps, with the help of [Pyodide](https://pyodide.org/).

I was curious how well Claude Sonnet 4 can write a Flet app and how easy it is to check the generated code and turn it into a workable app.

To sum up my experience: I found that Claude can code Flet apps quite well. Injecting relevant documentation articles into the context helps, but the documentation as a whole does not fit. I found adding a tutorial, like the [Todo App Tutorial](https://flet.dev/docs/tutorials/python-todo) works ok. I also needed to add certain symbols to the context, for example, `ft.Colors` and `ft.Icons` (capital I and C), as Claude often got it wrong. 

With vibe coding, I prefer concise code, as this helps me quickly check and correct generated code. Nothing I know beats FastHTML in that regard, but Flet is doing quite well.

(written by [mitja](https://mitja.dev))

## Prerequisites

- Python 3.12+
- `uv` package manager (recommended)

## Quick Start with uv

## Syncing the environment

```bash
uv sync
```

### Running the Application

As a desktop app:

```bash
uv run main.py
```

As a web app on port `8000`:

```bash
uv run flet run --web main.py
```

As a web app on a different port:

```bash
uv run flet run --web --port 1234 main.py
```

## IDE Setup (VSCode/Cursor/etc...)

1. Open the project in VSCode
2. Press `Cmd + Shift + P` (Mac) or `Ctrl + Shift + P` (Windows/Linux)
3. Select "Python: Select Interpreter"
4. Choose the `.venv` environment from the list
5. Reload the window (`Cmd + Shift + P` → "Developer: Reload Window")

## Project Structure

- `main.py`: The app
- `requirements.txt`: Project dependencies

By default, the sample data is loaded from `../fasthtml_app/ds.csv`.
