from database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class PaymentMethod(enum.Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    CASH = "CASH"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    expenses = relationship("Expense", back_populates="category")
    merchant_rules = relationship("MerchantRule", back_populates="category")


class MerchantRule(Base):
    __tablename__ = "merchant_rules"

    id = Column(Integer, primary_key=True, index=True)
    merchant_pattern = Column(String(255), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_regex = Column(Boolean, default=False)
    # Higher priority rules are applied first
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="merchant_rules")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    merchant = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    transaction_date = Column(
        DateTime(timezone=True), nullable=False, index=True
    )
    category_id = Column(Integer, ForeignKey("categories.id"))

    # Payment method and billing logic
    payment_method = Column(
        Enum(PaymentMethod), nullable=False, default=PaymentMethod.DEBIT_CARD
    )
    billing_date = Column(
        DateTime(timezone=True), nullable=False, index=True
    )  # When expense affects budget
    card_last_four = Column(String(4))  # Last 4 digits for identification

    # Source information (for n8n integration)
    source_email = Column(String(255))  # Which email this came from
    raw_data = Column(Text)  # Store original email content if needed

    # Categorization metadata
    auto_categorized = Column(Boolean, default=False)
    confidence_score = Column(Float)  # Confidence in the categorization

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="expenses")
