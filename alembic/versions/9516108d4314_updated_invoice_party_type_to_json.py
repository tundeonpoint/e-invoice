"""updated invoice party type to JSON

Revision ID: 9516108d4314
Revises: e59b13033e66
Create Date: 2025-11-12 07:10:03.103996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import json

# revision identifiers, used by Alembic.
revision: str = '9516108d4314'
down_revision: Union[str, Sequence[str], None] = 'e59b13033e66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# blank JSON structure to populate new column with (all fields blank)
BLANK_JSON = {
  "party_name": "",
  "tin": "",
  "email": "",
  "telephone": "",
  "business_description": "",
  "postal_address": {
    "street_name": "",
    "city_name": "",
    "postal_zone": "",
    "lga": "",
    "state": "",
    "country": ""
  }
}


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    blank_json_text = json.dumps(BLANK_JSON)

    if dialect == "postgresql":
        # Drop old column if exists
        with op.batch_alter_table("invoices") as batch_op:
            try:
                batch_op.drop_column("accounting_supplier_party")
            except Exception:
                pass

        # Step 1: Add new JSON column (nullable=True first)
        op.add_column(
            "invoices",
            sa.Column("accounting_supplier_party", sa.JSON(), nullable=True)
        )

        # Step 2: Populate all rows with blank JSON
        op.execute(
            text("UPDATE invoices SET accounting_supplier_party = :j").bindparams(j=blank_json_text)
        )

        # Step 3: Set column to NOT NULL
        op.alter_column(
            "invoices",
            "accounting_supplier_party",
            nullable=False
        )

    elif dialect == "mysql":
        with op.batch_alter_table("invoices") as batch_op:
            try:
                batch_op.drop_column("accounting_supplier_party")
            except Exception:
                pass

        op.add_column(
            "invoices",
            sa.Column("accounting_supplier_party", sa.JSON(), nullable=True)
        )

        op.execute(
            text("UPDATE invoices SET accounting_supplier_party = :j").bindparams(j=blank_json_text)
        )

        op.alter_column(
            "invoices",
            "accounting_supplier_party",
            nullable=False
        )

    elif dialect == "sqlite":
        op.add_column(
            "invoices",
            sa.Column("accounting_supplier_party_new", sa.Text(), nullable=True)
        )
        op.execute(
            text("UPDATE invoices SET accounting_supplier_party_new = :j").bindparams(j=blank_json_text)
        )
        try:
            op.alter_column("invoices", "accounting_supplier_party_new", new_column_name="accounting_supplier_party")
        except Exception:
            print("SQLite: rename failed, manual adjustment may be required.")

    else:
        # Fallback
        with op.batch_alter_table("invoices") as batch_op:
            try:
                batch_op.drop_column("accounting_supplier_party")
            except Exception:
                pass
        op.add_column("invoices", sa.Column("accounting_supplier_party", sa.JSON(), nullable=True))
        op.execute(text("UPDATE invoices SET accounting_supplier_party = :j").bindparams(j=blank_json_text))
        op.alter_column("invoices", "accounting_supplier_party", nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect in ("postgresql", "mysql"):
        with op.batch_alter_table("invoices") as batch_op:
            try:
                batch_op.drop_column("accounting_supplier_party")
            except Exception:
                pass

        op.add_column(
            "invoices",
            sa.Column("accounting_supplier_party", sa.Text(), nullable=True)
        )
        op.execute(text("UPDATE invoices SET accounting_supplier_party = ''"))

    elif dialect == "sqlite":
        op.add_column(
            "invoices",
            sa.Column("accounting_supplier_party_old", sa.Text(), nullable=True)
        )
        op.execute(text("UPDATE invoices SET accounting_supplier_party_old = ''"))
        try:
            op.alter_column("invoices", "accounting_supplier_party_old", new_column_name="accounting_supplier_party")
        except Exception:
            print("SQLite: rename failed, manual adjustment may be required.")