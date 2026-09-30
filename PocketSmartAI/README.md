# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application based on the supplied project document. It provides three budget planners: Home Interior, Party, and Jewelry, with account authentication, saved recommendation history, optional outfit-image understanding, Gemini integration, and deterministic fallback recommendations.

## Architecture

- FastAPI: API + server-rendered pages
- Jinja2 + CSS + JavaScript: frontend
- SQLite + SQLAlchemy: users and recommendation history
- JWT in an HttpOnly cookie: browser authentication; Bearer tokens also work for API clients
- Google GenAI SDK: Gemini multimodal recommendations
- Fallback engine: app remains usable when `GEMINI_API_KEY` is missing or an AI request fails

The original document mentions Gemini 1.5 Flash Pro. The implementation uses the current stable Gemini 3.8 Flash model by default; change `GEMINI_MODEL` in `.env` if your account uses another supported model.

## VS Code setup (Windows)

1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Open Terminal.
4. Create a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

5. Install packages:

```powershell
python -m pip install -r requirements.txt
```

6. Copy `.env.example` to `.env`.
7. Set a long random `SECRET_KEY`.
8. Add your Gemini API key to `GEMINI_API_KEY` if you want live AI. If it is empty, the fallback recommendation engine works.

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs
Health check: http://127.0.0.1:8000/health

## Test

```powershell
python -m pytest -q
```

## Gemini key

Create a Gemini API key in Google AI Studio, then put it in `.env`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Never commit `.env` or expose the key in browser JavaScript.

## Main routes

Pages:
- `/`
- `/login`
- `/register`
- `/dashboard`
- `/planner/home`
- `/planner/party`
- `/planner/jewelry`
- `/history-page`

API:
- `POST /api/register`
- `POST /api/login`
- `POST /token`
- `GET /api/logout`
- `GET /session-info`
- `GET /session-data`
- `POST /generate-home`
- `POST /generate-party`
- `POST /generate-jewelry` (multipart form with JSON `payload` and optional `outfit_image`)
- `GET /history`
- `GET /recommendations-details/{id}`

## Important product-data limitation

The supplied project document describes Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO sourcing, but does not provide API credentials, API contracts, or legal scraping specifications. This implementation therefore generates platform search links instead of scraping or pretending to have live inventory. Replace the provider layer with official partner APIs when credentials/contracts are available.
