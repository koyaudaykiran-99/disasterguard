"""add sos client_id and telemetry

Revision ID: e3c4d7e89123
Revises: f4591a27b401
Create Date: 2026-09-07 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e3c4d7e89123'
down_revision: Union[str, Sequence[str], None] = 'f4591a27b401'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('sos_reports', sa.Column('client_id', sa.String(length=100), nullable=True))
    op.create_index('ix_sos_reports_client_id', 'sos_reports', ['client_id'], unique=True)
    op.add_column('sos_reports', sa.Column('accuracy', sa.Float(), nullable=True))
    op.add_column('sos_reports', sa.Column('transport', sa.String(length=50), nullable=True, server_default='INTERNET'))
    op.add_column('sos_reports', sa.Column('device_timestamp', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_index('ix_sos_reports_client_id', table_name='sos_reports')
    op.drop_column('sos_reports', 'device_timestamp')
    op.drop_column('sos_reports', 'transport')
    op.drop_column('sos_reports', 'accuracy')
    op.drop_column('sos_reports', 'client_id')
