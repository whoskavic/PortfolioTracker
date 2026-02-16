from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext

from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============ User CRUD ============
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# ============ Asset CRUD ============
def get_asset_by_symbol(db: Session, symbol: str) -> Optional[models.Asset]:
    return db.query(models.Asset).filter(models.Asset.symbol == symbol.upper()).first()

def get_asset(db: Session, asset_id: int) -> Optional[models.Asset]:
    return db.query(models.Asset).filter(models.Asset.id == asset_id).first()

def get_assets(db: Session, skip: int = 0, limit: int = 100) -> List[models.Asset]:
    return db.query(models.Asset).offset(skip).limit(limit).all()

def create_asset(db: Session, asset: schemas.AssetCreate) -> models.Asset:
    db_asset = models.Asset(
        symbol=asset.symbol.upper(),
        name=asset.name,
        asset_type=asset.asset_type
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

# ============ Transaction CRUD ============
def get_transactions(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.Transaction]:
    return db.query(models.Transaction)\
        .filter(models.Transaction.user_id == user_id)\
        .order_by(models.Transaction.transaction_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_transaction(db: Session, transaction_id: int, user_id: int) -> Optional[models.Transaction]:
    return db.query(models.Transaction)\
        .filter(
            and_(
                models.Transaction.id == transaction_id,
                models.Transaction.user_id == user_id
            )
        ).first()

def create_transaction(
    db: Session, 
    transaction: schemas.TransactionCreate, 
    user_id: int
) -> models.Transaction:
    # Calculate total amount
    total_amount = (transaction.quantity * transaction.price) + transaction.fee
    
    # Create transaction
    db_transaction = models.Transaction(
        user_id=user_id,
        asset_id=transaction.asset_id,
        transaction_type=transaction.transaction_type,
        quantity=transaction.quantity,
        price=transaction.price,
        fee=transaction.fee,
        total_amount=total_amount,
        transaction_date=transaction.transaction_date,
        notes=transaction.notes
    )
    
    db.add(db_transaction)
    db.commit()
    
    # Update or create position
    update_position_after_transaction(db, db_transaction)
    
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
    transaction = get_transaction(db, transaction_id, user_id)
    if transaction:
        db.delete(transaction)
        db.commit()
        # Recalculate positions after deletion
        recalculate_position(db, user_id, transaction.asset_id)
        return True
    return False

# ============ Position CRUD ============
def get_positions(db: Session, user_id: int) -> List[models.Position]:
    return db.query(models.Position)\
        .filter(models.Position.user_id == user_id)\
        .all()

def get_position_by_asset(
    db: Session, 
    user_id: int, 
    asset_id: int
) -> Optional[models.Position]:
    return db.query(models.Position)\
        .filter(
            and_(
                models.Position.user_id == user_id,
                models.Position.asset_id == asset_id
            )
        ).first()

def update_position_after_transaction(db: Session, transaction: models.Transaction):
    """
    Update atau create position setelah transaction
    """
    position = get_position_by_asset(db, transaction.user_id, transaction.asset_id)
    
    if transaction.transaction_type == models.TransactionType.BUY:
        if position:
            # Update existing position
            new_quantity = position.quantity + transaction.quantity
            new_invested = position.total_invested + transaction.total_amount
            position.quantity = new_quantity
            position.total_invested = new_invested
            position.average_buy_price = new_invested / new_quantity
        else:
            # Create new position
            position = models.Position(
                user_id=transaction.user_id,
                asset_id=transaction.asset_id,
                quantity=transaction.quantity,
                total_invested=transaction.total_amount,
                average_buy_price=transaction.price
            )
            db.add(position)
    
    elif transaction.transaction_type == models.TransactionType.SELL:
        if position:
            # Calculate realized PnL
            realized_pnl = (transaction.price - position.average_buy_price) * transaction.quantity
            transaction.realized_pnl = realized_pnl
            
            # Update position
            position.quantity -= transaction.quantity
            position.total_invested -= (position.average_buy_price * transaction.quantity)
            
            # Delete position if quantity is 0
            if position.quantity <= 0:
                db.delete(position)
    
    db.commit()

def recalculate_position(db: Session, user_id: int, asset_id: int):
    """
    Recalculate position dari semua transactions
    """
    # Delete existing position
    position = get_position_by_asset(db, user_id, asset_id)
    if position:
        db.delete(position)
        db.commit()
    
    # Get all transactions untuk asset ini
    transactions = db.query(models.Transaction)\
        .filter(
            and_(
                models.Transaction.user_id == user_id,
                models.Transaction.asset_id == asset_id
            )
        )\
        .order_by(models.Transaction.transaction_date)\
        .all()
    
    # Recalculate dari awal
    for trans in transactions:
        update_position_after_transaction(db, trans)

# ============ Analytics ============
def get_portfolio_summary(db: Session, user_id: int) -> dict:
    """
    Get portfolio summary dengan PnL analytics
    """
    positions = get_positions(db, user_id)
    transactions = get_transactions(db, user_id, limit=10000)
    
    total_invested = sum(p.total_invested for p in positions)
    current_value = sum(p.current_value for p in positions)
    unrealized_pnl = sum(p.unrealized_pnl for p in positions)
    realized_pnl = sum(t.realized_pnl for t in transactions if t.transaction_type == models.TransactionType.SELL)
    
    total_pnl = realized_pnl + unrealized_pnl
    total_pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    # Calculate PnL for different periods
    now = datetime.utcnow()
    
    def calculate_period_pnl(days: int):
        start_date = now - timedelta(days=days)
        period_transactions = [t for t in transactions if t.transaction_date >= start_date]
        period_realized = sum(t.realized_pnl for t in period_transactions if t.transaction_type == models.TransactionType.SELL)
        period_total = period_realized + unrealized_pnl
        period_invested = sum(t.total_amount for t in period_transactions if t.transaction_type == models.TransactionType.BUY)
        period_percentage = (period_total / period_invested * 100) if period_invested > 0 else 0
        
        return {
            "period": f"{days}d",
            "total_pnl": period_total,
            "total_pnl_percentage": period_percentage,
            "realized_pnl": period_realized,
            "unrealized_pnl": unrealized_pnl
        }
    
    return {
        "total_invested": total_invested,
        "current_value": current_value,
        "total_pnl": total_pnl,
        "total_pnl_percentage": total_pnl_percentage,
        "total_positions": len(positions),
        "total_transactions": len(transactions),
        "pnl_7d": calculate_period_pnl(7),
        "pnl_30d": calculate_period_pnl(30),
        "pnl_1y": calculate_period_pnl(365),
        "pnl_all": {
            "period": "all",
            "total_pnl": total_pnl,
            "total_pnl_percentage": total_pnl_percentage,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl
        }
    }