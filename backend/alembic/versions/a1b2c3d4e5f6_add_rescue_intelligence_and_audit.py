"""add rescue intelligence fields and dispatch audit logs

Revision ID: a1b2c3d4e5f6
Revises: f56a7b8c9d01
Create Date: 2026-09-07 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f56a7b8c9d01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Add columns to rescue_teams
    op.add_column('rescue_teams', sa.Column('capabilities', sa.String(length=255), nullable=True, server_default='FLOOD_RESCUE,BOAT_RESCUE,FIRST_AID'))
    op.add_column('rescue_teams', sa.Column('capacity', sa.Integer(), nullable=True, server_default='10'))
    op.add_column('rescue_teams', sa.Column('last_updated', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()))

    # 2. Create rescue_dispatch_audit_logs table
    op.create_table(
        'rescue_dispatch_audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('operator_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('operator_name', sa.String(length=120), nullable=False, server_default='Dispatch Officer'),
        sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rescue_team_id', sa.Integer(), sa.ForeignKey('rescue_teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False, server_default='RESCUE_DISPATCH_CONFIRMED'),
        sa.Column('is_override', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )

    op.create_index('ix_rescue_audit_incident_id', 'rescue_dispatch_audit_logs', ['incident_id'])
    op.create_index('ix_rescue_audit_team_id', 'rescue_dispatch_audit_logs', ['rescue_team_id'])
    op.create_index('ix_rescue_audit_timestamp', 'rescue_dispatch_audit_logs', ['timestamp'])

def downgrade() -> None:
    op.drop_index('ix_rescue_audit_timestamp', table_name='rescue_dispatch_audit_logs')
    op.drop_index('ix_rescue_audit_team_id', table_name='rescue_dispatch_audit_logs')
    op.drop_index('ix_rescue_audit_incident_id', table_name='rescue_dispatch_audit_logs')
    op.drop_table('rescue_dispatch_audit_logs')

    op.drop_column('rescue_teams', 'last_updated')
    op.drop_column('rescue_teams', 'capacity')
    op.drop_column('rescue_teams', 'capabilities')
