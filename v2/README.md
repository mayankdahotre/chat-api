# Multi-Domain Conversational Analytics Copilot (v2)

Production-grade conversational AI copilot with a **FastAPI + LangGraph** backend and **React + TypeScript** frontend. Routes users between isolated **Finance** and **Marketing** domain workers via a 4-node DAG.

## Documentation

| Guide | Description |
|-------|-------------|
| [docs/README.md](./docs/README.md) | Documentation index |
| [docs/SETUP.md](./docs/SETUP.md) | Installation, configuration, and troubleshooting |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | 4-node DAG, state machine, routing, and flows |
| [docs/API.md](./docs/API.md) | Full API reference with SSE protocol and code examples |
| [docs/DATABASE.md](./docs/DATABASE.md) | Database schemas, seed data, and CRUD operations |
| [backend/README.md](./backend/README.md) | Backend quick start |

## Quick Start

### Backend

```powershell
cd "c:\Users\Mayank Dahotre\Desktop\CogitX\chat api\v2\backend"

python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

- **API docs:** http://localhost:8000/docs
- **Web UI:** http://localhost:5173
- **Run demo:** `python demo.py` (from `backend/`)
- **Terminal chat:** `python chat_cli.py` (from `backend/`)

## Architecture at a Glance

See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for full LangGraph flow charts.

```mermaid
flowchart TD
    START([START]) --> ENTRY{Entry Router}
    ENTRY --> INTENT[Node 1: Intent]
    ENTRY --> FIN[Node 2: Finance]
    ENTRY --> MKT[Node 3: Marketing]
    INTENT -->|"clarify"| END1([END])
    INTENT --> FIN
    INTENT --> MKT
    INTENT --> TERM[Node 4: Terminal]
    FIN --> END2([END])
    FIN --> INTENT
    FIN --> TERM
    MKT --> END3([END])
    MKT --> INTENT
    MKT --> TERM
    TERM --> END4([END])
```

| Node | Role | Database |
|------|------|----------|
| **Node 1 — Intent** | Classifies and routes user intent | `app_storage.db` |
| **Node 2 — Finance** | Financial statements, COGS, revenue | `finance_data.db` |
| **Node 3 — Marketing** | Campaign metrics, CAC, LTV, ROAS | `marketing_data.db` |
| **Node 4 — Terminal** | Session wrap-up | `app_storage.db` |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/chat/stream` | SSE streaming chat |
| `POST` | `/api/v1/chat/reset` | Reset conversation |
| `GET` | `/api/v1/chat/sessions` | Session history |
| `GET` | `/api/v1/health` | Health check |

## Example

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me a financial statement table."}'
```

## Project Layout

```
v2/
├── backend/           # Python FastAPI + LangGraph API
│   ├── app/
│   │   ├── api/       # FastAPI routers
│   │   ├── chat/      # LangGraph DAG, nodes, SSE streaming
│   │   ├── crud/      # Domain-specific data access
│   │   ├── database/  # 3 isolated SQLite connections + seed data
│   │   ├── config.py
│   │   └── main.py
│   ├── data/          # SQLite databases (auto-created)
│   ├── chat_cli.py    # Interactive terminal chat client
│   ├── demo.py        # End-to-end demo script
│   └── requirements.txt
├── frontend/          # React + TypeScript chat UI (Vite)
│   └── src/
├── docs/              # Full documentation (incl. LangGraph flow charts)
└── README.md
```

## Tech Stack

**Backend:** FastAPI · LangGraph · LangChain Core · aiosqlite · Pydantic · SSE  
**Frontend:** React · TypeScript · Vite

<img width="1907" height="867" alt="image" src="https://github.com/user-attachments/assets/bcd820d0-bee3-4f12-9d4a-25222b8be426" />
<img width="1912" height="836" alt="image" src="https://github.com/user-attachments/assets/398c8687-0847-4936-b05b-0c3d22ebb8e8" />
<img width="1918" height="821" alt="image" src="https://github.com/user-attachments/assets/18984f2d-2a91-452b-ad1d-b0116d2e7624" />
<img width="1913" height="857" alt="image" src="https://github.com/user-attachments/assets/21656370-ad1c-4b1f-8860-9f27675f4868" />
<img width="1918" height="862" alt="image" src="https://github.com/user-attachments/assets/b235008f-5898-428e-bb6c-79f389964024" />

