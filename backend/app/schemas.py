from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models import TransactionType, AssetType

# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ============ Asset Schemas ============
class AssetBase(BaseModel):
    symbol: str = Field(..., description="Asset symbol (e.g., BTC, AAPL)")
    name: str = Field(..., description="Asset name (e.g., Bitcoin, Apple Inc)")
    asset_type: AssetType

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ Transaction Schemas ============
class TransactionBase(BaseModel):
    asset_id: int
    transaction_type: TransactionType
    quantity: float = Field(..., gt=0, description="Quantity must be positive")
    price: float = Field(..., gt=0, description="Price must be positive")
    fee: float = Field(default=0.0, ge=0, description="Fee must be non-negative")
    transaction_date: datetime
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    user_id: int
    total_amount: float
    realized_pnl: float
    created_at: datetime
    
    # Nested objects
    asset: Asset
    
    class Config:
        from_attributes = True

# ============ Position Schemas ============
class PositionBase(BaseModel):
    asset_id: int
    quantity: float
    average_buy_price: float
    total_invested: float

class Position(PositionBase):
    id: int
    user_id: int
    current_price: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_percentage: float
    last_updated: datetime
    
    # Nested objects
    asset: Asset
    
    class Config:
        from_attributes = True

# ============ Dashboard/Analytics Schemas ============
class PnLAnalytics(BaseModel):
    period: str  # "7d", "30d", "1y", "all"
    total_pnl: float
    total_pnl_percentage: float
    realized_pnl: float
    unrealized_pnl: float

class PortfolioSummary(BaseModel):
    total_invested: float
    current_value: float
    total_pnl: float
    total_pnl_percentage: float
    total_positions: int
    total_transactions: int
    pnl_7d: PnLAnalytics
    pnl_30d: PnLAnalytics
    pnl_1y: PnLAnalytics
    pnl_all: PnLAnalytics