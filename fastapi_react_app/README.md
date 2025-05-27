# Simple Evaluation App

A minimal FastAPI + React + Mantine evaluation app.

## Prerequisites

- Python 3.11+
- `uv` package manager (recommended)
- Node.js and npm

## Setup

### Backend Setup (using uv)

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

### Frontend Setup

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

## Files

**Backend:**

- `backend.py` - FastAPI server with 4 endpoints

**Frontend:**

- `index.html` - Basic HTML page
- `src/main.jsx` - React entry point with Mantine
- `src/App.jsx` - Single file with all components
- `package.json` - Only essential dependencies
- `vite.config.js` - Proxy to backend

## Run

1. Start backend in a terminal window

```bash
uv run backend.py
```

2. Start frontend in a second terminal window:

   ```bash
   cd frontend # if not in there already
   npm run dev
   ```

3. Open http://localhost:5173

## What it does

- Lists inputs with "Evaluate" buttons
- Click to see input and documents
- Add notes and mark Good/Bad
- All data saved to SQLite

## IDE Setup (VSCode/Cursor/etc...)

1. Open the project in VSCode
2. Press `Cmd + Shift + P` (Mac) or `Ctrl + Shift + P` (Windows/Linux)
3. Select "Python: Select Interpreter"
4. Choose the `.venv` environment from the list
5. Reload the window (`Cmd + Shift + P` → "Developer: Reload Window")
