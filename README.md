# Chat API

Azure OpenAI chat APIs for CogitX.

## Versions

| Folder | Description |
|--------|-------------|
| [`v1/`](./v1/) | Simple FastAPI `/chat` endpoint (Azure OpenAI) |
| [`v2/`](./v2/) | Full copilot: FastAPI + LangGraph backend, React frontend |

## v1 — Quick start

```powershell
cd v1
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your Azure OpenAI credentials
uvicorn main:app --reload --port 8000
```

**POST** `http://127.0.0.1:8000/chat`

```json
{
  "prompt": "hello"
}
```

Response:

```json
{
  "answer": "..."
}
```

API docs: `http://127.0.0.1:8000/docs`

## v2 — Quick start

See [v2/README.md](./v2/README.md) for backend, frontend, and architecture docs.

## Security

Never commit `.env` files. Use `.env.example` as a template.
