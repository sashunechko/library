"""create copies table

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "copies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.Enum("available", "borrowed", name="copystatus"), nullable=False, server_default="available"),
    )


def downgrade() -> None:
    op.drop_table("copies")
    op.execute("DROP TYPE IF EXISTS copystatus")
