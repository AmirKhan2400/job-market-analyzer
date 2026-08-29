"""add preferred skills to analyses

Revision ID: b7a31e5c9d2f
Revises: 9f2a6b8d1c3e
Create Date: 2026-08-29 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7a31e5c9d2f"
down_revision: str | Sequence[str] | None = "9f2a6b8d1c3e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "analyses",
        sa.Column("preferred_skills", sa.String(), server_default="", nullable=False),
    )
    op.alter_column("analyses", "preferred_skills", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("analyses", "preferred_skills")
