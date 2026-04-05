from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary", response_model=schemas.PortfolioSummary)
def get_portfolio_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_portfolio_summary(db, user_id=current_user.id)
