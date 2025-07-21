"""
Billing logic for different payment methods
"""
from datetime import datetime
from calendar import monthrange

from models import PaymentMethod


class SimpleBillingService:
    def __init__(self, credit_card_billing_day: int = 25):
        self.credit_card_billing_day = credit_card_billing_day

    def calculate_billing_date(
        self, transaction_date, payment_method, card_last_four=None
    ):
        """Calculate when expense affects budget"""
        if payment_method == PaymentMethod.CREDIT_CARD:
            return self._next_billing_cycle(transaction_date)
        else:
            return transaction_date  # Immediate

    def _next_billing_cycle(self, transaction_date):
        """Credit card billing logic - 25th of each month"""
        year = transaction_date.year
        month = transaction_date.month
        day = transaction_date.day

        # Get the billing day for current month (handle month-end edge cases)
        billing_day = min(
            self.credit_card_billing_day, monthrange(year, month)[1]
        )

        if day >= billing_day:
            # Transaction on/after 25th → next month's billing (25th)
            if month == 12:
                next_year = year + 1
                next_month = 1
            else:
                next_year = year
                next_month = month + 1

            # Get billing day for next month (handle February edge case)
            next_billing_day = min(
                self.credit_card_billing_day, 
                monthrange(next_year, next_month)[1]
            )

            return datetime(
                next_year,
                next_month,
                next_billing_day,
                transaction_date.hour,
                transaction_date.minute,
                transaction_date.second,
                transaction_date.microsecond,
                transaction_date.tzinfo,
            )
        else:
            # Transaction before 25th → current month's billing (25th)
            return datetime(
                year,
                month,
                billing_day,
                transaction_date.hour,
                transaction_date.minute,
                transaction_date.second,
                transaction_date.microsecond,
                transaction_date.tzinfo,
            )

    def get_billing_summary(self, expenses, start_date=None, end_date=None):
        """Analytics by payment method"""
        summary = {
            "CREDIT_CARD": {"count": 0, "amount": 0, "pending_billing": 0},
            "DEBIT_CARD": {"count": 0, "amount": 0},
            "BANK_TRANSFER": {"count": 0, "amount": 0},
            "CASH": {"count": 0, "amount": 0},
            "total": {"count": 0, "amount": 0},
        }

        from datetime import timezone
        now = datetime.now(timezone.utc)

        for expense in expenses:
            payment_method = expense.payment_method.value
            amount = expense.amount

            # Update totals
            summary["total"]["count"] += 1
            summary["total"]["amount"] += amount

            # Update payment method specific counts
            if payment_method in summary:
                summary[payment_method]["count"] += 1
                summary[payment_method]["amount"] += amount

                # For credit cards, track pending billing 
                # (charges after next 25th)
                if (
                    payment_method == "CREDIT_CARD"
                    and expense.billing_date > now
                ):
                    summary["CREDIT_CARD"]["pending_billing"] += amount

        return summary


# Global billing service instance with 25th billing cycle
billing_service = SimpleBillingService(credit_card_billing_day=25) 