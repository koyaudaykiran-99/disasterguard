"""add emergency updates table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-08 19:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'emergency_updates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('client_update_id', sa.String(length=100), nullable=True),
        sa.Column('sos_id', sa.Integer(), sa.ForeignKey('sos_reports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('update_type', sa.String(length=50), nullable=False, server_default='TEXT_UPDATE'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('location_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='CITIZEN_APP'),
        sa.Column('delivery_status', sa.String(length=30), nullable=False, server_default='RECEIVED'),
        sa.Column('original_language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('processing_status', sa.String(length=30), nullable=False, server_default='PROCESSED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_emergency_updates_client_update_id', 'emergency_updates', ['client_update_id'], unique=True)
    op.create_index('ix_emergency_updates_sos_id', 'emergency_updates', ['sos_id'])
    op.create_index('ix_emergency_updates_incident_id', 'emergency_updates', ['incident_id'])
    op.create_index('ix_emergency_updates_update_type', 'emergency_updates', ['update_type'])
    op.create_index('ix_emergency_updates_created_at', 'emergency_updates', ['created_at'])

def downgrade() -> None:
    op.drop_index('ix_emergency_updates_created_at', table_name='emergency_updates')
    op.drop_index('ix_emergency_updates_update_type', table_name='emergency_updates')
    op.drop_index('ix_emergency_updates_incident_id', table_name='emergency_updates')
    op.drop_index('ix_emergency_updates_sos_id', table_name='emergency_updates')
    op.drop_index('ix_emergency_updates_client_update_id', table_name='emergency_updates')
    op.drop_table('emergency_updates')
