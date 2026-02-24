# QABuddy: Angular UI + Python Backend

This project now includes:
- **Python backend API** (Flask) for chatbot responses.
- **Angular frontend UI** that calls the Python API.

## 1) Run backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```

Backend runs on `http://localhost:5000`.

## 2) Run Angular UI

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:4200` and sends chat requests to the Python backend.

## API

- `GET /api/health`
- `POST /api/chat`
  - Body: `{ "message": "your prompt", "tools": ["knowledge_base", "answer_enhancer"] }`

## Optional CLI mode

```bash
python chatbot.py --name QABuddy
```
