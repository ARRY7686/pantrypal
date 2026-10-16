"""create items table

Revision ID: 0001_create_items
Revises:
Create Date: 2026-10-16
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_create_items"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False, server_default="other"),
        sa.Column("location", sa.String(length=20), nullable=False, server_default="pantry"),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="1"),
        sa.Column("unit", sa.String(length=20), nullable=False, server_default="pcs"),
        sa.Column("expires_on", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_items_name", "items", ["name"])
    op.create_index("ix_items_location", "items", ["location"])
    op.create_index("ix_items_expires_on", "items", ["expires_on"])


def downgrade() -> None:
    op.drop_index("ix_items_expires_on", table_name="items")
    op.drop_index("ix_items_location", table_name="items")
    op.drop_index("ix_items_name", table_name="items")
    op.drop_table("items")
