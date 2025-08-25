"""Merge heads for reports table

Revision ID: d92e3f8b4c01
Revises: 99219061f7b0, c4d8e9f12345
Create Date: 2025-08-23 16:17:20.907720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd92e3f8b4c01'
down_revision: Union[str, Sequence[str], None] = ('99219061f7b0', 'c4d8e9f12345')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
