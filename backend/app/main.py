from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv

from app import models, schemas, crud
from app.database import engine, get_db

load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Portfolio Tracker API",
    description="API for tracking investment portfolio",
    version="1.0.0"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# ============ Routes ============

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Portfolio Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ============ Auth Routes ============

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ============ Asset Routes ============

@app.get("/assets", response_model=List[schemas.Asset])
def get_assets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    assets = crud.get_assets(db, skip=skip, limit=limit)
    return assets

@app.post("/assets", response_model=schemas.Asset)
def create_asset(
    asset: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if asset already exists
    db_asset = crud.get_asset_by_symbol(db, symbol=asset.symbol)
    if db_asset:
        raise HTTPException(status_code=400, detail="Asset already exists")
    
    return crud.create_asset(db=db, asset=asset)

# ============ Transaction Routes ============

@app.get("/transactions", response_model=List[schemas.Transaction])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = crud.get_transactions(db, user_id=current_user.id, skip=skip, limit=limit)
    return transactions

@app.post("/transactions", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify asset exists
    asset = crud.get_asset(db, asset_id=transaction.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)

@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    success = crud.delete_transaction(db, transaction_id=transaction_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

# ============ Position Routes ============

@app.get("/positions", response_model=List[schemas.Position])
def get_positions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    positions = crud.get_positions(db, user_id=current_user.id)
    return positions

# ============ Analytics Routes ============

@app.get("/portfolio/summary", response_model=schemas.PortfolioSummary)
def get_portfolio_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    summary = crud.get_portfolio_summary(db, user_id=current_user.id)
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)