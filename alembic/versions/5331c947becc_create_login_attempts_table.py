"""Create Login Attempts Table

Revision ID: 5331c947becc
Revises: 9a1c0378dccb
Create Date: 2026-01-02 19:31:36.673580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5331c947becc'
down_revision: Union[str, Sequence[str], None] = '9a1c0378dccb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('login_attempts', 
                    sa.Column('user_id', sa.String(100), nullable=False, primary_key=True),
                    sa.Column('attempts', sa.Integer, nullable=False),
                    sa.Column('cooldown', sa.TIMESTAMP(timezone=True), nullable=True),
                    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('login_attempts', if_exists=True)
