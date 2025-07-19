from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class MerchantRuleBase(BaseModel):
    merchant_pattern: str = Field(..., max_length=255)
    category_id: int
    is_regex: bool = False
    priority: int = Field(default=1, ge=1)
    is_active: bool = True


class MerchantRuleCreate(MerchantRuleBase):
    pass


class MerchantRuleUpdate(BaseModel):
    merchant_pattern: str | None = Field(None, max_length=255)
    category_id: int | None = None
    is_regex: bool | None = None
    priority: int | None = Field(None, ge=1)
    is_active: bool | None = None


class MerchantRule(MerchantRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime | None
    category: Category

    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    merchant: str = Field(..., max_length=255)
    description: str | None = None
    transaction_date: datetime
    category_id: int | None = None


class ExpenseCreate(ExpenseBase):
    source_email: str | None = Field(None, max_length=255)
    raw_data: str | None = None


class ExpenseUpdate(BaseModel):
    amount: float | None = Field(None, gt=0)
    merchant: str | None = Field(None, max_length=255)
    description: str | None = None
    transaction_date: datetime | None = None
    category_id: int | None = None


class Expense(ExpenseBase):
    id: int
    source_email: str | None
    raw_data: str | None
    auto_categorized: bool
    confidence_score: float | None
    created_at: datetime
    updated_at: datetime | None
    category: Category | None

    class Config:
        from_attributes = True


# Webhook schema for n8n integration
class WebhookExpense(BaseModel):
    amount: float = Field(..., gt=0)
    merchant: str = Field(..., max_length=255)
    description: str | None = None
    transaction_date: datetime
    source_email: str | None = Field(None, max_length=255)
    raw_data: str | None = None


# Analytics schemas
class ExpenseSummary(BaseModel):
    total_amount: float
    transaction_count: int
    average_amount: float
    categories: dict[str, float]  # category_name: total_amount


class CategoryExpenseSummary(BaseModel):
    category: Category
    total_amount: float
    transaction_count: int
    percentage_of_total: float
