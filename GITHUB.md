# GitHub Setup Guide

Repository: **https://github.com/mayankdahotre/chat-api**

## What is in the repo

| Item | Purpose |
|------|---------|
| `.gitignore` | Excludes `.env`, `venv/`, `node_modules/`, `__pycache__/`, `.db` files |
| `README.md` | Project overview and run instructions |
| `v1/.env.example` | Template for Azure OpenAI keys (no secrets) |
| `v1/` | Simple FastAPI `/chat` API |
| `v2/` | Full copilot stack (backend + frontend) |

**Important:** Real `.env` files with API keys are **not** committed to GitHub.

---

## First-time setup (already done)

These steps were used to publish this project:

### 1. Initialize git locally

```powershell
cd "c:\Users\Mayank Dahotre\Desktop\CogitX\chat api"
git init
```

### 2. Add a `.gitignore`

Make sure secrets and dependencies are never committed:

```
.env
venv/
node_modules/
__pycache__/
```

### 3. Stage and commit

```powershell
git add .
git commit -m "Initial commit"
```

### 4. Create repo on GitHub and push

Using GitHub CLI:

```powershell
git branch -M main
gh repo create chat-api --public --source=. --remote=origin --push
```

Or create the repo manually at [github.com/new](https://github.com/new), then:

```powershell
git remote add origin https://github.com/mayankdahotre/chat-api.git
git push -u origin main
```

---

## Pushing future changes

After you edit files locally:

```powershell
cd "c:\Users\Mayank Dahotre\Desktop\CogitX\chat api"
git add .
git commit -m "Describe your change"
git push
```

---

## Clone on another machine

```powershell
git clone https://github.com/mayankdahotre/chat-api.git
cd chat-api\v1
copy .env.example .env
```

Edit `.env` and add your Azure OpenAI credentials, then:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Test with Postman:

- **URL:** `http://127.0.0.1:8000/chat`
- **Method:** `POST`
- **Body:**

```json
{
  "prompt": "hello"
}
```

---

## Security reminders

- Never commit `.env` files
- Use `.env.example` as a template only
- Rotate API keys if they were ever exposed
