import json
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import RecommendationHistory, User

router = APIRouter()

@router.get("/history")
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(RecommendationHistory).where(RecommendationHistory.user_id == user.id).order_by(RecommendationHistory.created_at.desc())).all()
    return [{"id": r.id, "planner": r.planner_type, "budget": r.budget, "created_at": r.created_at.isoformat(), "input": json.loads(r.input_summary), "result": json.loads(r.result_json)} for r in rows]

@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = db.scalar(select(RecommendationHistory).where(RecommendationHistory.id == recommendation_id, RecommendationHistory.user_id == user.id))
    from fastapi import HTTPException
    if not row: raise HTTPException(404, "Recommendation not found")
    return {"id": row.id, "planner": row.planner_type, "budget": row.budget, "input": json.loads(row.input_summary), "result": json.loads(row.result_json), "created_at": row.created_at.isoformat()}
