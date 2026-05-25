"""create loans table

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("copy_id", sa.Integer(), sa.ForeignKey("copies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reader_id", sa.Integer(), sa.ForeignKey("readers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("loan_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("return_date", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("loans")
