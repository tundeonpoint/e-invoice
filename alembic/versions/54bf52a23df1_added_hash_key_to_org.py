"""added hash key to org

Revision ID: 54bf52a23df1
Revises: 276201451902
Create Date: 2025-12-15 17:00:37.830160
"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54bf52a23df1'
down_revision: Union[str, Sequence[str], None] = '276201451902'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add column as nullable first
    op.add_column(
        'organisations',
        sa.Column('hash_key', sa.String(length=64), nullable=True)
    )

    # 2. Backfill existing rows with random values
    organisations = sa.table(
        'organisations',
        sa.column('id', sa.Integer),
        sa.column('hash_key', sa.String),
    )

    conn = op.get_bind()
    rows = conn.execute(sa.select(organisations.c.id)).fetchall()

    for row in rows:
        conn.execute(
            organisations.update()
            .where(organisations.c.id == row.id)
            .values(hash_key=uuid.uuid4().hex)
        )

    # 3. Enforce NOT NULL
    op.alter_column(
        'organisations',
        'hash_key',
        nullable=False
    )


def downgrade() -> None:
    op.drop_column('organisations', 'hash_key')
