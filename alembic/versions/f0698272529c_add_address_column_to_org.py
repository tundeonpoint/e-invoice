"""add address column to org

Revision ID: f0698272529c
Revises: 9516108d4314
Create Date: 2025-11-12 19:12:34.834687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0698272529c'
down_revision: Union[str, Sequence[str], None] = '9516108d4314'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema safely."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Safe conversion only if we're on PostgreSQL (native JSON supported)
    if dialect == "postgresql":
        # 1️⃣ Add temporary column for JSON data
        op.add_column('invoices', sa.Column('accounting_customer_party_tmp', sa.JSON(), nullable=True))

        # 2️⃣ Copy and cast existing data to JSON where possible
        op.execute("""
            UPDATE invoices
            SET accounting_customer_party_tmp = 
                CASE
                    WHEN accounting_customer_party ~ '^{.*}$' THEN accounting_customer_party::json
                    ELSE NULL
                END;
        """)

        # 3️⃣ Drop old column and rename new one
        op.drop_column('invoices', 'accounting_customer_party')
        op.alter_column('invoices', 'accounting_customer_party_tmp', new_column_name='accounting_customer_party')
    else:
        # Fallback (e.g. SQLite, MySQL): just replace the column — no casting
        op.drop_column('invoices', 'accounting_customer_party')
        op.add_column('invoices', sa.Column('accounting_customer_party', sa.JSON(), nullable=True))

    # Add new fields to other tables
    op.add_column('organisations', sa.Column('address', sa.JSON(), nullable=True))
    op.add_column('zoho_invoices', sa.Column('customer', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema safely."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Drop new fields first
    op.drop_column('zoho_invoices', 'customer')
    op.drop_column('organisations', 'address')

    if dialect == "postgresql":
        # 1️⃣ Add a temp VARCHAR column
        op.add_column('invoices', sa.Column('accounting_customer_party_tmp', sa.VARCHAR(), nullable=True))

        # 2️⃣ Convert JSON back to text
        op.execute("""
            UPDATE invoices
            SET accounting_customer_party_tmp = accounting_customer_party::text;
        """)

        # 3️⃣ Replace and rename back
        op.drop_column('invoices', 'accounting_customer_party')
        op.alter_column('invoices', 'accounting_customer_party_tmp', new_column_name='accounting_customer_party')
    else:
        # Fallback for other DBs
        op.drop_column('invoices', 'accounting_customer_party')
        op.add_column('invoices', sa.Column('accounting_customer_party', sa.VARCHAR(), nullable=True))