from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import MerchantRule
from schemas import MerchantRule as MerchantRuleSchema
from schemas import MerchantRuleCreate, MerchantRuleUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/merchant-rules", tags=["merchant-rules"])


@router.post("/", response_model=MerchantRuleSchema)
def create_merchant_rule(rule: MerchantRuleCreate, db: Session = Depends(get_db)):
    """Create a new merchant rule for expense categorization."""
    db_rule = MerchantRule(
        merchant_pattern=rule.merchant_pattern,
        category_id=rule.category_id,
        is_regex=rule.is_regex,
        priority=rule.priority,
        is_active=rule.is_active,
    )

    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("/", response_model=list[MerchantRuleSchema])
def get_merchant_rules(active_only: bool = Query(False), db: Session = Depends(get_db)):
    """Get all merchant rules."""
    query = db.query(MerchantRule)

    if active_only:
        query = query.filter(MerchantRule.is_active == True)  # noqa: E712

    rules = query.order_by(MerchantRule.priority.desc()).all()
    return rules


@router.get("/{rule_id}", response_model=MerchantRuleSchema)
def get_merchant_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific merchant rule by ID."""
    rule = db.query(MerchantRule).filter(MerchantRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Merchant rule not found")
    return rule


@router.put("/{rule_id}", response_model=MerchantRuleSchema)
def update_merchant_rule(
    rule_id: int, rule_update: MerchantRuleUpdate, db: Session = Depends(get_db)
):
    """Update a merchant rule."""
    rule = db.query(MerchantRule).filter(MerchantRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Merchant rule not found")

    # Update fields if provided
    for field, value in rule_update.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}")
def delete_merchant_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a merchant rule."""
    rule = db.query(MerchantRule).filter(MerchantRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Merchant rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Merchant rule deleted successfully"}


@router.post("/test-rule")
def test_merchant_rule(
    merchant: str, pattern: str, is_regex: bool = False, db: Session = Depends(get_db)
):
    """Test a merchant rule pattern against a merchant name."""
    from services.categorization import ExpenseCategorizationService

    service = ExpenseCategorizationService(db)
    confidence = service._calculate_match_confidence(merchant, pattern, is_regex)

    return {
        "merchant": merchant,
        "pattern": pattern,
        "is_regex": is_regex,
        "confidence": confidence / 100.0,
        "matches": confidence >= service.fuzzy_threshold,
    }
