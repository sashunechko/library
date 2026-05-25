"""create authors table

Revision ID: 0001
Revises:
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("authors")
