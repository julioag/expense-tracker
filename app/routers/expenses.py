from datetime import datetime

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Expense, PaymentMethod
from schemas import Expense as ExpenseSchema
from schemas import (
    ExpenseCreate,
    ExpenseSummary,
    ExpenseUpdate,
    WebhookExpense,
)
from services.categorization import ExpenseCategorizationService
from services.billing import billing_service
from sqlalchemy import desc
from sqlalchemy.orm import Session

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseSchema)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense with automatic billing date calculation."""
    categorization_service = ExpenseCategorizationService(db)

    # Auto-categorize if no category is provided
    category_id = expense.category_id
    auto_categorized = False
    confidence_score = None

    if not category_id:
        category_id, auto_categorized, confidence_score = (
            categorization_service.categorize_expense(expense.merchant)
        )

    # Calculate billing date if not provided
    billing_date = expense.billing_date
    if not billing_date:
        billing_date = billing_service.calculate_billing_date(
            expense.transaction_date,
            expense.payment_method,
            expense.card_last_four,
        )

    db_expense = Expense(
        amount=expense.amount,
        merchant=expense.merchant,
        description=expense.description,
        transaction_date=expense.transaction_date,
        category_id=category_id,
        payment_method=expense.payment_method,
        billing_date=billing_date,
        card_last_four=expense.card_last_four,
        source_email=expense.source_email,
        raw_data=expense.raw_data,
        auto_categorized=auto_categorized,
        confidence_score=confidence_score,
    )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.get("/", response_model=list[ExpenseSchema])
def get_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    merchant: str | None = None,
    payment_method: PaymentMethod | None = None,
    use_billing_date: bool = Query(
        False, description="Filter by billing date instead of transaction date"
    ),
    db: Session = Depends(get_db),
):
    """Get expenses with optional filtering by payment method and billing dates."""
    query = db.query(Expense)

    if category_id:
        query = query.filter(Expense.category_id == category_id)

    if payment_method:
        query = query.filter(Expense.payment_method == payment_method)

    # Choose between transaction date and billing date for filtering
    date_field = (
        Expense.billing_date if use_billing_date else Expense.transaction_date
    )

    if start_date:
        query = query.filter(date_field >= start_date)

    if end_date:
        query = query.filter(date_field <= end_date)

    if merchant:
        query = query.filter(Expense.merchant.ilike(f"%{merchant}%"))

    expenses = (
        query.order_by(desc(date_field)).offset(skip).limit(limit).all()
    )
    return expenses


@router.get("/{expense_id}", response_model=ExpenseSchema)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get a specific expense."""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseSchema)
def update_expense(
    expense_id: int, expense_update: ExpenseUpdate, db: Session = Depends(get_db)
):
    """Update an expense."""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # Update fields if provided
    for field, value in expense_update.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)

    # Recalculate billing date if payment method or transaction date changed
    if expense_update.payment_method or expense_update.transaction_date:
        expense.billing_date = billing_service.calculate_billing_date(
            expense.transaction_date,
            expense.payment_method,
            expense.card_last_four,
        )

    # If category was manually set, mark as not auto-categorized
    if expense_update.category_id is not None:
        expense.auto_categorized = False
        expense.confidence_score = None

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense."""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}


# Enhanced webhook endpoint for n8n integration
@router.post("/webhook", response_model=ExpenseSchema)
def webhook_create_expense(
    webhook_expense: WebhookExpense, db: Session = Depends(get_db)
):
    """Create expense from webhook with automatic payment method detection."""
    
    # Auto-detect payment method if not provided
    payment_method = webhook_expense.payment_method
    if not payment_method and webhook_expense.raw_data:
        payment_method = billing_service.detect_payment_method(
            webhook_expense.raw_data, webhook_expense.card_last_four
        )
    
    # Extract card last four if not provided
    card_last_four = webhook_expense.card_last_four
    if not card_last_four and webhook_expense.raw_data:
        card_last_four = billing_service.extract_card_last_four(
            webhook_expense.raw_data
        )

    expense_create = ExpenseCreate(
        amount=webhook_expense.amount,
        merchant=webhook_expense.merchant,
        description=webhook_expense.description,
        transaction_date=webhook_expense.transaction_date,
        payment_method=payment_method or PaymentMethod.DEBIT_CARD,
        card_last_four=card_last_four,
        source_email=webhook_expense.source_email,
        raw_data=webhook_expense.raw_data,
    )

    return create_expense(expense_create, db)


@router.post("/recategorize")
def recategorize_expenses(db: Session = Depends(get_db)):
    """Recategorize all uncategorized expenses."""
    categorization_service = ExpenseCategorizationService(db)
    result = categorization_service.bulk_recategorize()
    return result


@router.get("/analytics/summary", response_model=ExpenseSummary)
def get_expense_summary(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    use_billing_date: bool = Query(
        False, description="Use billing date for analysis"
    ),
    payment_method: PaymentMethod | None = None,
    db: Session = Depends(get_db),
):
    """Get expense analytics summary with billing date support."""
    query = db.query(Expense)

    # Choose between transaction date and billing date for analysis
    date_field = (
        Expense.billing_date if use_billing_date else Expense.transaction_date
    )

    if start_date:
        query = query.filter(date_field >= start_date)

    if end_date:
        query = query.filter(date_field <= end_date)

    if payment_method:
        query = query.filter(Expense.payment_method == payment_method)

    expenses = query.all()

    if not expenses:
        return ExpenseSummary(
            total_amount=0.0, transaction_count=0, average_amount=0.0, categories={}
        )

    total_amount = sum(exp.amount for exp in expenses)
    transaction_count = len(expenses)
    average_amount = total_amount / transaction_count

    # Group by categories
    categories = {}
    for expense in expenses:
        if expense.category:
            cat_name = expense.category.name
            categories[cat_name] = categories.get(cat_name, 0) + expense.amount

    return ExpenseSummary(
        total_amount=total_amount,
        transaction_count=transaction_count,
        average_amount=average_amount,
        categories=categories,
    )


@router.get("/analytics/billing-summary")
def get_billing_summary(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
):
    """Get billing summary by payment method."""
    query = db.query(Expense)

    if start_date:
        query = query.filter(Expense.transaction_date >= start_date)

    if end_date:
        query = query.filter(Expense.transaction_date <= end_date)

    expenses = query.all()
    
    return billing_service.get_billing_summary(
        expenses, start_date or datetime.min, end_date or datetime.max
    )
