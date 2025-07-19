from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import Category
from schemas import Category as CategorySchema
from schemas import CategoryCreate, CategoryUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategorySchema)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new expense category."""
    # Check if category name already exists
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Category with this name already exists"
        )

    db_category = Category(
        name=category.name, description=category.description, color=category.color
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/", response_model=list[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    """Get all expense categories."""
    categories = db.query(Category).order_by(Category.name).all()
    return categories


@router.get("/{category_id}", response_model=CategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int, category_update: CategoryUpdate, db: Session = Depends(get_db)
):
    """Update a category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check if new name conflicts with existing category
    if category_update.name and category_update.name != category.name:
        existing = (
            db.query(Category).filter(Category.name == category_update.name).first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Category with this name already exists"
            )

    # Update fields if provided
    for field, value in category_update.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check if category has associated expenses
    from models import Expense

    expense_count = db.query(Expense).filter(Expense.category_id == category_id).count()
    if expense_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {expense_count} associated expenses",
        )

    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}
