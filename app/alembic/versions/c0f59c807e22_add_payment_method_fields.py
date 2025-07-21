"""add_payment_method_fields

Revision ID: c0f59c807e22
Revises: 
Create Date: 2025-07-21 00:20:23.028269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0f59c807e22'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add payment method, billing date, and card fields to expenses table."""
    
    # Create the PaymentMethod enum type (skip if exists)
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT 1 FROM pg_type WHERE typname = 'paymentmethod'"
    ))
    if not result.fetchone():
        payment_method_enum = sa.Enum(
            'CREDIT_CARD', 
            'DEBIT_CARD', 
            'BANK_TRANSFER', 
            'CASH',
            name='paymentmethod'
        )
        payment_method_enum.create(op.get_bind())
    
    # Add new columns to expenses table (skip if exist)
    inspector = sa.inspect(op.get_bind())
    columns = [col['name'] for col in inspector.get_columns('expenses')]
    
    if 'payment_method' not in columns:
        op.add_column(
            'expenses', 
            sa.Column(
                'payment_method', 
                sa.Enum(
                    'CREDIT_CARD', 'DEBIT_CARD', 'BANK_TRANSFER', 'CASH',
                    name='paymentmethod'
                ), 
                nullable=False, 
                server_default='DEBIT_CARD'
            )
        )
    
    if 'billing_date' not in columns:
        # Add billing_date column without default first
        op.add_column(
            'expenses', 
            sa.Column(
                'billing_date', 
                sa.DateTime(timezone=True), 
                nullable=True
            )
        )
        
        # Update existing records
        op.execute("""
            UPDATE expenses 
            SET billing_date = transaction_date 
            WHERE billing_date IS NULL
        """)
        
        # Make it NOT NULL
        op.alter_column('expenses', 'billing_date', nullable=False)
    
    if 'card_last_four' not in columns:
        op.add_column(
            'expenses', 
            sa.Column('card_last_four', sa.String(length=4), nullable=True)
        )
    
    # Create indexes for performance (skip if exist)
    existing_indexes = [
        idx['name'] for idx in inspector.get_indexes('expenses')
    ]
    
    if 'ix_expenses_payment_method' not in existing_indexes:
        op.create_index(
            'ix_expenses_payment_method', 'expenses', ['payment_method']
        )
    
    if 'ix_expenses_billing_date' not in existing_indexes:
        op.create_index(
            'ix_expenses_billing_date', 'expenses', ['billing_date']
        )


def downgrade() -> None:
    """Remove payment method and billing fields from expenses table."""
    
    # Drop indexes
    op.drop_index('ix_expenses_billing_date', table_name='expenses')
    op.drop_index('ix_expenses_payment_method', table_name='expenses')
    
    # Drop columns
    op.drop_column('expenses', 'card_last_four')
    op.drop_column('expenses', 'billing_date')
    op.drop_column('expenses', 'payment_method')
    
    # Drop the enum type
    sa.Enum(name='paymentmethod').drop(op.get_bind())
