"""remove_historical_backfill_progress_table

Revision ID: a4bf86e9a003
Revises: 40680fc5a516
Create Date: 2025-08-05 16:18:47.447299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4bf86e9a003'
down_revision: Union[str, Sequence[str], None] = '40680fc5a516'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove historical_backfill_progress table as it's no longer needed."""
    # Drop the historical_backfill_progress table
    op.drop_table('historical_backfill_progress')


def downgrade() -> None:
    """Recreate historical_backfill_progress table."""
    # Recreate the historical_backfill_progress table if we need to rollback
    op.create_table('historical_backfill_progress',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('portfolio_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False, comment='Status: pending, processing, completed, failed'),
    sa.Column('total_symbols', sa.Integer(), nullable=False, comment='Total number of unique symbols to fetch'),
    sa.Column('processed_symbols', sa.Integer(), nullable=False, comment='Number of symbols successfully processed'),
    sa.Column('failed_symbols', sa.Integer(), nullable=False, comment='Number of symbols that failed to fetch'),
    sa.Column('last_error', sa.Text(), nullable=True, comment='Last error message if any'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='When backfill completed (success or failure)'),
    sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", name=op.f('ck_historical_backfill_progress_backfill_status_check')),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], name=op.f('fk_historical_backfill_progress_portfolio_id_portfolios'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_historical_backfill_progress')),
    sa.UniqueConstraint('portfolio_id', name=op.f('uq_historical_backfill_progress_portfolio_id'))
    )
