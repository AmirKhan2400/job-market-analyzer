"""add visitor id to analyses

Revision ID: 9f2a6b8d1c3e
Revises: 354c00c9339b
Create Date: 2026-08-26 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f2a6b8d1c3e"
down_revision: str | Sequence[str] | None = "354c00c9339b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "analyses",
        sa.Column("visitor_id", sa.String(), server_default="legacy", nullable=False),
    )
    op.create_index("ix_analyses_visitor_id", "analyses", ["visitor_id"])
    op.alter_column("analyses", "visitor_id", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_analyses_visitor_id", table_name="analyses")
    op.drop_column("analyses", "visitor_id")
