"""Add content column

Revision ID: 923dd98321d1
Revises: 5f489a3d47d7
Create Date: 2025-12-25 14:25:15.256629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '923dd98321d1'
down_revision: Union[str, Sequence[str], None] = '5f489a3d47d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(100), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
