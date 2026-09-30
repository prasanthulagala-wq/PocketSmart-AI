from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import COOKIE_NAME, create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, RegisterRequest, SessionInfo, TokenResponse

router = APIRouter()

def _login_response(user: User, request: Request, as_json: bool = False):
    token = create_access_token(user)
    if as_json:
        response = Response(content=TokenResponse(access_token=token).model_dump_json(), media_type="application/json")
    else:
        response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", secure=request.url.scheme == "https", max_age=86400)
    return response

@router.post("/api/register")
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        from fastapi import HTTPException
        raise HTTPException(409, "Email is already registered")
    user = User(name=payload.name.strip(), email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return _login_response(user, request, True)

@router.post("/api/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return _login_response(user, request, True)

@router.post("/token")
def token(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    return login(payload, request, db)

@router.get("/api/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response

@router.get("/session-info", response_model=SessionInfo)
def session_info(request: Request, db: Session = Depends(get_db)):
    from ..auth import get_optional_user
    user = get_optional_user(request, db)
    return SessionInfo(logged_in=bool(user), user_id=user.id if user else None, name=user.name if user else None, email=user.email if user else None)

@router.get("/session-data")
def session_data(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "name": user.name, "email": user.email}
