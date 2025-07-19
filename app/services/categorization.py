import re

from fuzzywuzzy import fuzz
from models import MerchantRule
from sqlalchemy.orm import Session


class ExpenseCategorizationService:
    """Service for automatically categorizing expenses using merchant rules."""

    def __init__(self, db: Session, fuzzy_threshold: int = 80):
        self.db = db
        self.fuzzy_threshold = fuzzy_threshold

    def categorize_expense(
        self, merchant: str
    ) -> tuple[int | None, bool, float | None]:
        """
        Categorize an expense based on merchant name.

        Returns:
            Tuple of (category_id, auto_categorized, confidence_score)
        """
        # Get all active merchant rules ordered by priority
        rules = (
            self.db.query(MerchantRule)
            .filter(MerchantRule.is_active == True)  # noqa: E712
            .order_by(MerchantRule.priority.desc())
            .all()
        )

        best_match = None
        best_confidence = 0.0

        for rule in rules:
            confidence = self._calculate_match_confidence(
                merchant, rule.merchant_pattern, rule.is_regex
            )

            if confidence > best_confidence and confidence >= self.fuzzy_threshold:
                best_match = rule
                best_confidence = confidence

                # If it's an exact match or regex match, break early
                if confidence >= 95:
                    break

        if best_match:
            return best_match.category_id, True, best_confidence / 100.0

        return None, False, None

    def _calculate_match_confidence(
        self, merchant: str, pattern: str, is_regex: bool
    ) -> float:
        """Calculate the confidence score for a pattern match."""
        if is_regex:
            try:
                if re.search(pattern, merchant, re.IGNORECASE):
                    return 100.0  # Exact regex match
            except re.error:
                # Invalid regex pattern, skip
                return 0.0
        else:
            # Use fuzzy string matching
            return float(fuzz.ratio(merchant.lower(), pattern.lower()))

        return 0.0

    def suggest_merchant_rules(self, merchant: str, limit: int = 5) -> list[dict]:
        """
        Suggest potential merchant rules for an uncategorized expense.

        Returns list of dictionaries with pattern suggestions and categories.
        """
        # Get existing patterns and find similar ones
        existing_rules = (
            self.db.query(MerchantRule)
            .filter(MerchantRule.is_active == True)  # noqa: E712
            .all()
        )

        suggestions = []
        for rule in existing_rules:
            confidence = fuzz.ratio(merchant.lower(), rule.merchant_pattern.lower())
            if confidence > 60:  # Lower threshold for suggestions
                suggestions.append(
                    {
                        "pattern": rule.merchant_pattern,
                        "category_id": rule.category_id,
                        "confidence": confidence / 100.0,
                        "is_regex": rule.is_regex,
                    }
                )

        # Sort by confidence and return top matches
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:limit]

    def bulk_recategorize(self) -> dict:
        """
        Recategorize all expenses that are currently uncategorized.

        Returns summary of categorization results.
        """
        from models import Expense  # Import here to avoid circular imports

        # Get uncategorized expenses
        uncategorized_expenses = (
            self.db.query(Expense).filter(Expense.category_id.is_(None)).all()
        )

        categorized_count = 0
        total_count = len(uncategorized_expenses)

        for expense in uncategorized_expenses:
            category_id, auto_categorized, confidence = self.categorize_expense(
                expense.merchant
            )

            if category_id:
                expense.category_id = category_id
                expense.auto_categorized = auto_categorized
                expense.confidence_score = confidence
                categorized_count += 1

        self.db.commit()

        return {
            "total_expenses": total_count,
            "categorized": categorized_count,
            "remaining_uncategorized": total_count - categorized_count,
            "success_rate": (categorized_count / total_count * 100)
            if total_count > 0
            else 0,
        }
