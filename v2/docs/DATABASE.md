# Database Schema

The system uses **three isolated SQLite databases** stored in the `backend/data/` directory. Each database is accessed only by its designated layer — no cross-domain queries exist.

```
backend/data/
├── app_storage.db      # Application session layer
├── finance_data.db     # Finance domain (Node 2 only)
└── marketing_data.db   # Marketing domain (Node 3 only)
```

Databases are auto-created and seeded on application startup via `app/database/init_db.py`.

---

## 1. Application Storage (`app_storage.db`)

**Access:** Session CRUD layer (`app/crud/app_session.py`) — used by all nodes for persistence.

### Table: `sessions`

Tracks conversation threads and active domain state.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `thread_id` | TEXT | PRIMARY KEY | UUID conversation identifier |
| `active_domain` | TEXT | NULLABLE | `"finance"`, `"marketing"`, or `NULL` |
| `is_active` | INTEGER | NOT NULL, DEFAULT 1 | `1` = open, `0` = terminated |
| `created_at` | TEXT | NOT NULL | ISO timestamp |
| `updated_at` | TEXT | NOT NULL | Last activity timestamp |

### Table: `messages`

Stores full conversation history per thread.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Message ID |
| `thread_id` | TEXT | NOT NULL, FK → sessions | Parent thread |
| `role` | TEXT | NOT NULL | `"user"` or `"assistant"` |
| `content` | TEXT | NOT NULL | Message body |
| `created_at` | TEXT | NOT NULL | ISO timestamp |

**Index:** `idx_messages_thread_id` on `messages(thread_id)`

---

## 2. Finance Domain (`finance_data.db`)

**Access:** Finance CRUD only (`app/crud/finance.py`) — Node 2 exclusive.

### Table: `financial_statements`

Quarterly income statement data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `period` | TEXT | e.g. `"Q1 2025"` |
| `revenue` | REAL | Total revenue ($) |
| `cogs` | REAL | Cost of goods sold ($) |
| `gross_profit` | REAL | Revenue − COGS ($) |
| `operating_expenses` | REAL | OpEx ($) |
| `net_income` | REAL | Net income ($) |

### Table: `balance_sheet`

Quarterly balance sheet snapshots.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `period` | TEXT | e.g. `"Q1 2025"` |
| `total_assets` | REAL | Total assets ($) |
| `total_liabilities` | REAL | Total liabilities ($) |
| `shareholders_equity` | REAL | Equity ($) |

### Seed Data (Financial Statements)

| Period | Revenue | COGS | Gross Profit | OpEx | Net Income |
|--------|---------|------|--------------|------|------------|
| Q1 2025 | $2,450,000 | $980,000 | $1,470,000 | $620,000 | $850,000 |
| Q2 2025 | $2,680,000 | $1,180,000 | $1,500,000 | $640,000 | $860,000 |
| Q3 2025 | $2,910,000 | $1,020,000 | $1,890,000 | $680,000 | $1,210,000 |
| Q4 2025 | $3,150,000 | $1,100,000 | $2,050,000 | $710,000 | $1,340,000 |

---

## 3. Marketing Domain (`marketing_data.db`)

**Access:** Marketing CRUD only (`app/crud/marketing.py`) — Node 3 exclusive.

### Table: `campaign_metrics`

Quarterly campaign performance data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `period` | TEXT | e.g. `"Q1 2025"` |
| `campaign_name` | TEXT | Campaign identifier |
| `spend` | REAL | Ad spend ($) |
| `impressions` | INTEGER | Total impressions |
| `clicks` | INTEGER | Total clicks |
| `conversions` | INTEGER | Total conversions |
| `cac` | REAL | Customer acquisition cost ($) |
| `ltv` | REAL | Lifetime value ($) |
| `roas` | REAL | Return on ad spend (multiplier) |
| `ctr` | REAL | Click-through rate (%) |

### Seed Data (Campaign Metrics)

| Period | Campaign | Spend | CAC | LTV | ROAS | CTR |
|--------|----------|-------|-----|-----|------|-----|
| Q1 2025 | Brand Awareness | $120,000 | $44 | $320 | 3.2x | 3.00% |
| Q2 2025 | Performance Max | $185,000 | $47 | $380 | 4.1x | 3.19% |
| Q3 2025 | Retargeting | $95,000 | $34 | $410 | 5.6x | 4.00% |
| Q4 2025 | Holiday Push | $210,000 | $37 | $450 | 4.8x | 3.80% |

---

## Connection Management

**File:** `app/database/connections.py`

Each database has its own async connection factory:

```python
get_app_storage_connection()  # → app_storage.db
get_finance_connection()      # → finance_data.db
get_marketing_connection()    # → marketing_data.db
```

Connections use `aiosqlite` with `row_factory = aiosqlite.Row` for dict-like row access. Connections are opened per-operation and closed in `finally` blocks — no shared connection pool.

---

## CRUD Operations

### App Session (`app/crud/app_session.py`)

| Function | Description |
|----------|-------------|
| `ensure_session(thread_id)` | Create session if not exists |
| `update_session_domain(thread_id, domain)` | Set active domain |
| `deactivate_session(thread_id)` | Mark session as ended |
| `get_session(thread_id)` | Fetch session metadata |
| `save_message(thread_id, role, content)` | Persist a message |
| `get_messages(thread_id, limit=20)` | Fetch message history |

### Finance (`app/crud/finance.py`)

| Function | Description |
|----------|-------------|
| `get_financial_statements()` | All quarterly statements |
| `get_balance_sheet()` | All balance sheet rows |
| `build_financial_statement_markdown()` | Formatted markdown table |
| `answer_finance_question(question)` | Context-aware finance answers |

### Marketing (`app/crud/marketing.py`)

| Function | Description |
|----------|-------------|
| `get_campaign_metrics()` | All campaign rows |
| `build_marketing_statement_markdown()` | Formatted markdown table |
| `answer_marketing_question(question)` | Context-aware marketing answers |

---

## Resetting Data

To wipe and re-seed all databases:

```powershell
# Stop the server first (from backend/)
Remove-Item -Recurse -Force data/
# Restart — databases are recreated on startup
uvicorn app.main:app --reload
```

Seed data is only inserted when tables are empty (idempotent seeding).
