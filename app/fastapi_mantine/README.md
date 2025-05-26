# Simple Evaluation App

A minimal FastAPI + React + Mantine evaluation app.

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

1. Start backend: `python backend.py`
2. Start frontend: `npm run dev`
3. Open http://localhost:5173

## What it does

- Lists inputs with "Evaluate" buttons
- Click to see input and documents
- Add notes and mark Good/Bad
- All data saved to SQLite 