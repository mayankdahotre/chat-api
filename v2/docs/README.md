# Documentation Index

Welcome to the **Multi-Domain Conversational Analytics Copilot Backend (v2)** documentation.

| Document | Description |
|----------|-------------|
| [Setup Guide](./SETUP.md) | Installation, environment variables, and running the server |
| [Architecture](./ARCHITECTURE.md) | 4-node DAG topology, **LangGraph flow charts**, state machine, routing, and conversation flows |
| [API Reference](./API.md) | Endpoints, request/response formats, and SSE event protocol |
| [Database Schema](./DATABASE.md) | Three isolated databases, tables, and seed data |

## Quick Links

- **Swagger UI:** http://localhost:8000/docs
- **Health check:** `GET /api/v1/health`
- **Main endpoint:** `POST /api/v1/chat/stream`
- **Demo script:** `python demo.py` (from `backend/`)

## What This System Does

This backend is a production-grade conversational AI copilot that:

1. Accepts multi-turn chat messages over a **single SSE streaming endpoint**
2. Routes user intent through a **LangGraph 4-node DAG** (Intent → Finance / Marketing → Terminal)
3. Maintains **session state** across server restarts via SQLite
4. Enforces **strict data isolation** between Finance and Marketing domain databases

## Supported Conversation Domains

| Domain | Example Queries | Data Source |
|--------|-----------------|-------------|
| **Finance** | Financial statements, COGS, revenue, balance sheet | `finance_data.db` |
| **Marketing** | Campaign performance, CAC, LTV, ROAS, CTR | `marketing_data.db` |
