import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import RecommendationHistory, User
from ..schemas import HomeRequest, PartyRequest, JewelryRequest, RecommendationResponse
from ..services.gemini_service import gemini_service

router = APIRouter()
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

async def _image(upload: UploadFile | None, max_bytes: int):
    if not upload: return None, None
    if upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, "Outfit image must be JPG, PNG, or WebP")
    data = await upload.read()
    if len(data) > max_bytes: raise HTTPException(413, "Image is too large")
    return data, upload.content_type

def _save(db: Session, user: User, planner: str, budget: int, data: dict, result: dict):
    db.add(RecommendationHistory(user_id=user.id, planner_type=planner, budget=budget, input_summary=json.dumps(data, ensure_ascii=False), result_json=json.dumps(result, ensure_ascii=False)))
    db.commit()
    return result

@router.post("/generate-home", response_model=RecommendationResponse)
def generate_home(payload: HomeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump(); result = gemini_service.generate("home", data)
    return _save(db, user, "home", payload.budget, data, result)

@router.post("/generate-party", response_model=RecommendationResponse)
def generate_party(payload: PartyRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump(); result = gemini_service.generate("party", data)
    return _save(db, user, "party", payload.budget, data, result)

@router.post("/generate-jewelry", response_model=RecommendationResponse)
async def generate_jewelry(payload: str = Form(...), outfit_image: UploadFile | None = File(default=None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        data = JewelryRequest.model_validate_json(payload).model_dump()
    except Exception as exc:
        raise HTTPException(422, f"Invalid jewelry data: {exc}")
    image_bytes, mime = await _image(outfit_image, 5 * 1024 * 1024)
    result = gemini_service.generate("jewelry", data, image_bytes, mime)
    return _save(db, user, "jewelry", data["budget"], data, result)
