from pathlib import Path
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .auth import get_optional_user
from .routers import auth, planners, history

BASE_DIR = Path(__file__).resolve().parent
Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="1.0.0", description="Budget-aware GenAI recommendation assistant")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(history.router)

@app.get("/health")
def health(): return {"status": "ok", "ai_configured": bool(settings.gemini_api_key), "model": settings.gemini_model}

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request): return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request): return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    if not user: return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/planner/{planner}", response_class=HTMLResponse)
def planner_page(planner: str, request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    if not user: return RedirectResponse("/login", status_code=303)
    if planner not in {"home", "party", "jewelry"}: return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(f"{planner}.html", {"request": request, "user": user, "planner": planner})

@app.get("/history-page", response_class=HTMLResponse)
def history_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    if not user: return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("history.html", {"request": request, "user": user})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
