from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, crud
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=List[schemas.Asset])
def get_assets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_assets(db, skip=skip, limit=limit)


@router.post("", response_model=schemas.Asset)
def create_asset(
    asset: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if crud.get_asset_by_symbol(db, symbol=asset.symbol):
        raise HTTPException(status_code=400, detail="Asset already exists")
    return crud.create_asset(db=db, asset=asset)
