# 🌾 Rural Survey & FAQ Bot

## 🎯 Overview
A multi-language AI assistant that helps rural citizens access government schemes, health services, agricultural pricing, and representative information. The project includes:

- FastAPI backend with optional database and background services
- Minimalistic Indian-themed frontend
- Consent-first survey workflow with mock data for demos
- Multi-language support (English, Hindi, Telugu)

---

## 🛠️ Prerequisites
- Python 3.10+
- Node.js 18+ (only for serving the frontend)
- (Optional) PostgreSQL 14+ if you want full database functionality

Set up a virtual environment and install Python dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Run Modes
### 1. Quick Demo (no database)
Runs the simplified backend (`app_simple.py`) and frontend with mock survey data.

```bash
# In one terminal (backend)
cd backend
python -m uvicorn app_simple:app --host 0.0.0.0 --port 8000 --reload

# In another terminal (frontend)
cd frontend
npx serve -l 5173
```
Open [http://localhost:5173](http://localhost:5173) to use the demo.

### 2. Full System (database + services)
Uses the comprehensive backend (`app.py`) with database, sentiment analysis, and external integrations.

```bash
cd backend
python start.py
```
This script will:
- Check environment variables / `.env`
- Initialize database (PostgreSQL via `DATABASE_URL`)
- Load mock data
- Run diagnostic tests (`test_comprehensive.py`)
- Start the FastAPI server from `app.py`

If you want to skip tests, set `RUN_TESTS=False` in `.env`.

---

## 🧪 Testing
### Quick smoke test for the simplified backend
```bash
cd backend
python - <<'PY'
from app_simple import app
print('✅ Simplified app imports successfully')
PY
```

### Judge testing script (uses running `app_simple.py`)
```bash
cd backend
python test_for_judges.py
```
This script calls the live backend and prints pass/fail for key scenarios in English and Hindi.

### Comprehensive tests (full system only)
```bash
cd backend
python -m pytest test_comprehensive.py
```
Requires database and service dependencies from `.env`.

---

## ⚙️ Environment Configuration
Copy `.env.example` to `.env` inside `backend/` and update keys:
```bash
cd backend
cp .env.example .env
```

Critical entries:
- `DATABASE_URL` (PostgreSQL DSN) for full system
- API keys (optional—without them, the fallback mock data still works)

For quick demos, you can leave API keys empty and keep `USE_MOCK_DATA=True`.

---

## 🖥️ Frontend Features
Located in `frontend/`:
- `index.html`: consent-first UI and language selector (English, Hindi, Telugu)
- `styles.css`: Indian government-inspired theme
- `script.js`: interactive survey flow + backend FAQ integration

To serve without installing Node.js globally:
```bash
cd frontend
npx serve -l 5173
```

Backend API base defaults to `http://localhost:8000`. Modify `window.__API_BASE_URL__` or `script.js` if backend runs elsewhere.

---

## 📂 Important Files
- `backend/app_simple.py`: Simplified backend (no DB). Judges should use this for quick evaluation.
- `backend/start.py`: Full startup script with service initialization.
- `backend/test_for_judges.py`: Automated smoke checks against the live backend.
- `backend/test_comprehensive.py`: Full integration tests (requires DB/services).
- `frontend/index.html`: Government-styled web interface.

---

## ✅ Judge Checklist
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Start simplified backend: `python -m uvicorn app_simple:app --reload`
3. Serve frontend: `npx serve -l 5173`
4. Open [http://localhost:5173](http://localhost:5173)
5. Choose a language > accept survey > follow mock prompts > continue to FAQ
6. Verify multi-language chatbot answers (English, Hindi, Telugu)
7. Optional: run `python backend/test_for_judges.py`

For full evaluation with database, run `python backend/start.py` after configuring `.env`.

---

## 🙏 Thank You
Built to empower rural communities with accessible, language-friendly government services.
