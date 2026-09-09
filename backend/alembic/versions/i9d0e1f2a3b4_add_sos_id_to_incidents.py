"""add sos_id to incidents table

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2a3
Create Date: 2026-09-09 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'i9d0e1f2a3b4'
down_revision = 'h8c9d0e1f2a3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [c['name'] for c in inspector.get_columns('incidents')]
    if 'sos_id' not in existing_columns:
        op.add_column(
            'incidents',
            sa.Column('sos_id', sa.Integer(), sa.ForeignKey('sos_reports.id', ondelete='SET NULL'), nullable=True)
        )
        op.create_index('ix_incidents_sos_id', 'incidents', ['sos_id'], unique=False)


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [c['name'] for c in inspector.get_columns('incidents')]
    if 'sos_id' in existing_columns:
        op.drop_index('ix_incidents_sos_id', table_name='incidents')
        op.drop_column('incidents', 'sos_id')
