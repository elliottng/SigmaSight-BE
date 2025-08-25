"""Add portfolio reports tables

Revision ID: c4d8e9f12345
Revises: b5cd2cea0507
Create Date: 2025-08-23 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c4d8e9f12345'
down_revision = 'b5cd2cea0507'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create portfolio_reports table
    op.create_table('portfolio_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('version', sa.String(length=10), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('anchor_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('calculation_engines_status', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('content_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('content_markdown', sa.Text(), nullable=True),
        sa.Column('content_csv', sa.Text(), nullable=True),
        sa.Column('portfolio_name', sa.String(length=255), nullable=True),
        sa.Column('position_count', sa.Integer(), nullable=True),
        sa.Column('total_value', sa.String(length=50), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False),
        sa.Column('generation_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for portfolio_reports
    op.create_index('idx_portfolio_reports_portfolio_current', 'portfolio_reports', ['portfolio_id', 'is_current'])
    op.create_index('idx_portfolio_reports_generated_at', 'portfolio_reports', ['generated_at'])
    op.create_index('idx_portfolio_reports_anchor_date', 'portfolio_reports', ['anchor_date'])

    # Create report_generation_jobs table
    op.create_table('report_generation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('progress_percentage', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.String(length=100), nullable=True),
        sa.Column('total_steps', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_completion_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('max_retries', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.ForeignKeyConstraint(['report_id'], ['portfolio_reports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for report_generation_jobs
    op.create_index('idx_report_jobs_portfolio_status', 'report_generation_jobs', ['portfolio_id', 'status'])
    op.create_index('idx_report_jobs_status', 'report_generation_jobs', ['status'])
    op.create_index('idx_report_jobs_created_at', 'report_generation_jobs', ['created_at'])

    # Set default values for existing columns
    op.alter_column('portfolio_reports', 'report_type',
                   existing_type=sa.VARCHAR(length=50),
                   server_default='comprehensive')
    op.alter_column('portfolio_reports', 'version',
                   existing_type=sa.VARCHAR(length=10),
                   server_default='2.0')
    op.alter_column('portfolio_reports', 'is_current',
                   existing_type=sa.BOOLEAN(),
                   server_default='true')
    op.alter_column('portfolio_reports', 'generated_at',
                   existing_type=sa.DateTime(timezone=True),
                   server_default=sa.text('now()'))
    op.alter_column('portfolio_reports', 'created_at',
                   existing_type=sa.DateTime(timezone=True),
                   server_default=sa.text('now()'))
    op.alter_column('portfolio_reports', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   server_default=sa.text('now()'))

    op.alter_column('report_generation_jobs', 'job_type',
                   existing_type=sa.VARCHAR(length=50),
                   server_default='comprehensive')
    op.alter_column('report_generation_jobs', 'status',
                   existing_type=sa.VARCHAR(length=20),
                   server_default='pending')
    op.alter_column('report_generation_jobs', 'progress_percentage',
                   existing_type=sa.INTEGER(),
                   server_default='0')
    op.alter_column('report_generation_jobs', 'total_steps',
                   existing_type=sa.INTEGER(),
                   server_default='8')
    op.alter_column('report_generation_jobs', 'retry_count',
                   existing_type=sa.INTEGER(),
                   server_default='0')
    op.alter_column('report_generation_jobs', 'max_retries',
                   existing_type=sa.INTEGER(),
                   server_default='3')
    op.alter_column('report_generation_jobs', 'created_at',
                   existing_type=sa.DateTime(timezone=True),
                   server_default=sa.text('now()'))
    op.alter_column('report_generation_jobs', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   server_default=sa.text('now()'))


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_report_jobs_created_at', table_name='report_generation_jobs')
    op.drop_index('idx_report_jobs_status', table_name='report_generation_jobs')
    op.drop_index('idx_report_jobs_portfolio_status', table_name='report_generation_jobs')
    op.drop_index('idx_portfolio_reports_anchor_date', table_name='portfolio_reports')
    op.drop_index('idx_portfolio_reports_generated_at', table_name='portfolio_reports')
    op.drop_index('idx_portfolio_reports_portfolio_current', table_name='portfolio_reports')
    
    # Drop tables
    op.drop_table('report_generation_jobs')
    op.drop_table('portfolio_reports')