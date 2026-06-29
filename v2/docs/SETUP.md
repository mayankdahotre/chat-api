# Setup Guide

## Prerequisites

- **Python 3.11+** (tested on 3.12)
- **pip** package manager
- **PowerShell** or any terminal (Windows/macOS/Linux)

Optional:
- Azure OpenAI credentials (routing works without LLM using keyword classification)

---

## Installation

### 1. Navigate to the backend

```powershell
cd "c:\Users\Mayank Dahotre\Desktop\CogitX\chat api\v2\backend"
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

```powershell
copy .env.example .env
```

Edit `.env` with your values:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_API_KEY` | No | — | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | No | — | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | No | `gpt-4.1` | Model deployment name |
| `AZURE_OPENAI_API_VERSION` | No | `2025-04-01-preview` | API version |
| `APP_HOST` | No | `0.0.0.0` | Server bind host |
| `APP_PORT` | No | `8000` | Server port |
| `DEBUG` | No | `true` | Enable auto-reload |

> **Note:** The system works fully without Azure OpenAI. Intent routing and domain responses use keyword-based classification and CRUD-backed templates.

---

## Running the Server

### Development (with auto-reload)

```powershell
python -m uvicorn app.main:app --reload
```

### Production

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Verify it is running

```powershell
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{ "status": "ok", "version": "2.0.0" }
```

---

## Database Initialization

Databases are created automatically on first startup inside the `backend/data/` folder:

```
backend/data/
├── app_storage.db      # Sessions and message history
├── finance_data.db     # Financial statements and balance sheet
└── marketing_data.db   # Campaign metrics
```

No manual migration step is required. Seed data is inserted on first run.

To reset all data, stop the server and delete the `backend/data/` folder, then restart.

---

## Running the Demo

A built-in demo script exercises all conversation flows:

```powershell
python demo.py
```

This runs:
1. Health check
2. Finance statement request
3. Finance follow-up (self-loop)
4. Domain shift to marketing
5. Session history retrieval
6. Session termination

---

## Interactive API Docs

Once the server is running, open:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Fatal error in launcher: Unable to create process` | Use `python -m uvicorn ...` instead of `uvicorn`, or recreate the venv in `backend/` |
| `ModuleNotFoundError: No module named 'app'` | Run uvicorn from the `backend/` folder, not from inside `app/` |
| Port 8000 already in use | Change `APP_PORT` in `.env` or kill the existing process |
| `&&` not working in PowerShell | Use `;` as command separator instead of `&&` |
| Empty responses | Check that `backend/data/*.db` files exist; delete `backend/data/` and restart to re-seed |
| Session says "ended" | Click **New chat** in the UI or call `POST /api/v1/chat/reset` |

---

## Project Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | HTTP API framework |
| `uvicorn` | ASGI server |
| `langgraph` | Multi-agent DAG state machine |
| `langchain-core` | Message types and graph primitives |
| `aiosqlite` | Async SQLite database access |
| `pydantic-settings` | Environment configuration |
| `python-dotenv` | `.env` file loading |
