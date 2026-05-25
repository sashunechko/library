"""create books table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("isbn", sa.String(13), nullable=True, unique=True),
        sa.Column("year", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("books")
