from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class AssetType(str, enum.Enum):
    STOCK = "stock"
    CRYPTO = "crypto"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)  # BTC, AAPL, etc
    name = Column(String, nullable=False)  # Bitcoin, Apple Inc
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="asset")
    positions = relationship("Position", back_populates="asset")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)  # Price per unit
    fee = Column(Float, default=0.0)
    
    total_amount = Column(Float, nullable=False)  # quantity * price + fee
    realized_pnl = Column(Float, default=0.0)  # For sell transactions
    
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    quantity = Column(Float, nullable=False)  # Current holdings
    average_buy_price = Column(Float, nullable=False)  # Average cost basis
    total_invested = Column(Float, nullable=False)  # Total amount invested
    
    current_price = Column(Float, default=0.0)  # Last updated price
    current_value = Column(Float, default=0.0)  # quantity * current_price
    unrealized_pnl = Column(Float, default=0.0)  # current_value - total_invested
    unrealized_pnl_percentage = Column(Float, default=0.0)
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="positions")
    asset = relationship("Asset", back_populates="positions")