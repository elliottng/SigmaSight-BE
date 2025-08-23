"""Initial schema with all models

Revision ID: 001
Revises: 
Create Date: 2025-07-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # Create portfolios table
    op.create_table('portfolios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_portfolios_user_id')
    )
    op.create_index('ix_portfolios_deleted_at', 'portfolios', ['deleted_at'], unique=False)

    # Create tags table
    op.create_table('tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('tag_type', sa.Enum('REGULAR', 'STRATEGY', name='tagtype'), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tags_user_id_name', 'tags', ['user_id', 'name'], unique=True)
    op.create_index('ix_tags_tag_type', 'tags', ['tag_type'], unique=False)

    # Create positions table
    op.create_table('positions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('position_type', sa.Enum('LC', 'LP', 'SC', 'SP', 'LONG', 'SHORT', name='positiontype'), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column('entry_price', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('exit_price', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('exit_date', sa.Date(), nullable=True),
        sa.Column('underlying_symbol', sa.String(length=10), nullable=True),
        sa.Column('strike_price', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('last_price', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('market_value', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('unrealized_pnl', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('realized_pnl', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_positions_portfolio_id', 'positions', ['portfolio_id'], unique=False)
    op.create_index('ix_positions_symbol', 'positions', ['symbol'], unique=False)
    op.create_index('ix_positions_deleted_at', 'positions', ['deleted_at'], unique=False)
    op.create_index('ix_positions_exit_date', 'positions', ['exit_date'], unique=False)

    # Create position_tags junction table
    op.create_table('position_tags',
        sa.Column('position_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('position_id', 'tag_id')
    )
    op.create_index('ix_position_tags_position_id_tag_id', 'position_tags', ['position_id', 'tag_id'], unique=False)

    # Create market_data_cache table
    op.create_table('market_data_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('high', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('low', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('close', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('data_source', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol', 'date', name='uq_market_data_cache_symbol_date')
    )
    op.create_index('ix_market_data_cache_symbol', 'market_data_cache', ['symbol'], unique=False)
    op.create_index('ix_market_data_cache_date', 'market_data_cache', ['date'], unique=False)

    # Create position_greeks table
    op.create_table('position_greeks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('calculation_date', sa.Date(), nullable=False),
        sa.Column('delta', sa.Numeric(precision=8, scale=6), nullable=True),
        sa.Column('gamma', sa.Numeric(precision=8, scale=6), nullable=True),
        sa.Column('theta', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('vega', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('rho', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('delta_dollars', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('gamma_dollars', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('position_id')
    )
    op.create_index('ix_position_greeks_position_id', 'position_greeks', ['position_id'], unique=False)
    op.create_index('ix_position_greeks_calculation_date', 'position_greeks', ['calculation_date'], unique=False)

    # Create factor_definitions table
    op.create_table('factor_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('factor_type', sa.String(length=20), nullable=False),
        sa.Column('calculation_method', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create factor_exposures table
    op.create_table('factor_exposures',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('factor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('calculation_date', sa.Date(), nullable=False),
        sa.Column('exposure_value', sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column('exposure_dollar', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['factor_id'], ['factor_definitions.id'], ),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('portfolio_id', 'factor_id', 'calculation_date', name='uq_factor_exposures_portfolio_factor_date')
    )
    op.create_index('ix_factor_exposures_portfolio_id_factor_id', 'factor_exposures', ['portfolio_id', 'factor_id'], unique=False)
    op.create_index('ix_factor_exposures_calculation_date', 'factor_exposures', ['calculation_date'], unique=False)

    # Create portfolio_snapshots table
    op.create_table('portfolio_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('total_value', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('cash_value', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('long_value', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('short_value', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('gross_exposure', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('net_exposure', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('daily_pnl', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('daily_return', sa.Numeric(precision=8, scale=6), nullable=True),
        sa.Column('cumulative_pnl', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('portfolio_delta', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('portfolio_gamma', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('portfolio_theta', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('portfolio_vega', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('num_positions', sa.Integer(), nullable=False),
        sa.Column('num_long_positions', sa.Integer(), nullable=False),
        sa.Column('num_short_positions', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('portfolio_id', 'snapshot_date', name='uq_portfolio_snapshots_portfolio_date')
    )
    op.create_index('ix_portfolio_snapshots_portfolio_id', 'portfolio_snapshots', ['portfolio_id'], unique=False)
    op.create_index('ix_portfolio_snapshots_snapshot_date', 'portfolio_snapshots', ['snapshot_date'], unique=False)

    # Create batch_jobs table
    op.create_table('batch_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_name', sa.String(length=100), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('job_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_batch_jobs_job_type', 'batch_jobs', ['job_type'], unique=False)
    op.create_index('ix_batch_jobs_status', 'batch_jobs', ['status'], unique=False)
    op.create_index('ix_batch_jobs_started_at', 'batch_jobs', ['started_at'], unique=False)

    # Create batch_job_schedules table
    op.create_table('batch_job_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_name', sa.String(length=100), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('cron_expression', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('retry_delay_seconds', sa.Integer(), nullable=False),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_name')
    )
    op.create_index('ix_batch_job_schedules_is_active', 'batch_job_schedules', ['is_active'], unique=False)
    op.create_index('ix_batch_job_schedules_next_run_at', 'batch_job_schedules', ['next_run_at'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('batch_job_schedules')
    op.drop_table('batch_jobs')
    op.drop_table('portfolio_snapshots')
    op.drop_table('factor_exposures')
    op.drop_table('factor_definitions')
    op.drop_table('position_greeks')
    op.drop_table('market_data_cache')
    op.drop_table('position_tags')
    op.drop_table('positions')
    op.drop_table('tags')
    op.drop_table('portfolios')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS positiontype')
    op.execute('DROP TYPE IF EXISTS tagtype')
