# Backend — Multi-Domain Conversational Analytics Copilot

FastAPI + LangGraph backend with SSE streaming and isolated Finance/Marketing SQLite databases.

## Quick Start

```powershell
cd backend

python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **API docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/v1/health
- **Demo:** `python demo.py`
- **Terminal chat:** `python chat_cli.py`

## Layout

```
backend/
├── app/               # FastAPI + LangGraph application
├── data/              # SQLite databases (auto-created)
├── chat_cli.py        # Interactive terminal client
├── demo.py            # End-to-end demo script
├── requirements.txt
└── .env.example
```
