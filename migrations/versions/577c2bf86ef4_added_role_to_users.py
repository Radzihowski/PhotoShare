"""Added role to users

Revision ID: 577c2bf86ef4
Revises: e173db7e5825
Create Date: 2026-07-04 08:41:53.926631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '577c2bf86ef4'
down_revision: Union[str, None] = 'e173db7e5825'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# create_type=False so the ENUM is managed explicitly below rather than
# being auto-created/dropped as a side effect of the column operations.
role_enum = postgresql.ENUM('ADMIN', 'MODERATOR', 'USER', name='role', create_type=False)


def upgrade() -> None:
    """Upgrade schema."""
    role_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('role', role_enum, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    role_enum.drop(op.get_bind(), checkfirst=True)
