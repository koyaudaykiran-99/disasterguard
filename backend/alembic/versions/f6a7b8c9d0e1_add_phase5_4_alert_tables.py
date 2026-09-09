"""add phase 5.4 alert intelligence tables

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-08 22:18:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Add new columns to alerts table
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('alerts')]

    new_columns = [
        ("alert_category", sa.Column('alert_category', sa.String(length=60), nullable=True, server_default='FLOOD_WARNING')),
        ("approval_status", sa.Column('approval_status', sa.String(length=30), nullable=True, server_default='APPROVED')),
        ("approved_by", sa.Column('approved_by', sa.String(length=120), nullable=True)),
        ("approved_at", sa.Column('approved_at', sa.DateTime(), nullable=True)),
        ("forecast_horizon", sa.Column('forecast_horizon', sa.String(length=10), nullable=True)),
        ("risk_score", sa.Column('risk_score', sa.Integer(), nullable=True)),
        ("confidence_score", sa.Column('confidence_score', sa.Float(), nullable=True)),
        ("uncertainty_score", sa.Column('uncertainty_score', sa.Float(), nullable=True)),
        ("risk_velocity", sa.Column('risk_velocity', sa.Float(), nullable=True)),
        ("evidence_json", sa.Column('evidence_json', sa.Text(), nullable=True)),
        ("actionable_instructions_json", sa.Column('actionable_instructions_json', sa.Text(), nullable=True)),
        ("is_simulation", sa.Column('is_simulation', sa.Boolean(), nullable=True, server_default='false')),
    ]

    for col_name, col_def in new_columns:
        if col_name not in existing_columns:
            op.add_column('alerts', col_def)

    # 2. Create alert_targets table
    tables = inspector.get_table_names()
    if 'alert_targets' not in tables:
        op.create_table(
            'alert_targets',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('alert_id', sa.Integer(), nullable=False),
            sa.Column('target_type', sa.String(length=30), nullable=True, server_default='GEO_ZONE'),
            sa.Column('location_name', sa.String(length=180), nullable=False),
            sa.Column('geometry_wkt', sa.Text(), nullable=True),
            sa.Column('user_count_estimate', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_alert_targets_id'), 'alert_targets', ['id'], unique=False)
        op.create_index(op.f('ix_alert_targets_alert_id'), 'alert_targets', ['alert_id'], unique=False)
        op.create_index(op.f('ix_alert_targets_target_type'), 'alert_targets', ['target_type'], unique=False)

    # 3. Create alert_deliveries table
    if 'alert_deliveries' not in tables:
        op.create_table(
            'alert_deliveries',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('alert_id', sa.Integer(), nullable=False),
            sa.Column('target_id', sa.Integer(), nullable=True),
            sa.Column('channel', sa.String(length=30), nullable=True, server_default='IN_APP'),
            sa.Column('status', sa.String(length=30), nullable=True, server_default='PENDING'),
            sa.Column('attempt_count', sa.Integer(), nullable=True, server_default='1'),
            sa.Column('sent_at', sa.DateTime(), nullable=True),
            sa.Column('delivered_at', sa.DateTime(), nullable=True),
            sa.Column('failed_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['target_id'], ['alert_targets.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_alert_deliveries_id'), 'alert_deliveries', ['id'], unique=False)
        op.create_index(op.f('ix_alert_deliveries_alert_id'), 'alert_deliveries', ['alert_id'], unique=False)
        op.create_index(op.f('ix_alert_deliveries_channel'), 'alert_deliveries', ['channel'], unique=False)
        op.create_index(op.f('ix_alert_deliveries_status'), 'alert_deliveries', ['status'], unique=False)

    # 4. Create alert_acknowledgements table
    if 'alert_acknowledgements' not in tables:
        op.create_table(
            'alert_acknowledgements',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('alert_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('client_id', sa.String(length=120), nullable=True),
            sa.Column('channel', sa.String(length=30), nullable=True, server_default='IN_APP'),
            sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_alert_acknowledgements_id'), 'alert_acknowledgements', ['id'], unique=False)
        op.create_index(op.f('ix_alert_acknowledgements_alert_id'), 'alert_acknowledgements', ['alert_id'], unique=False)
        op.create_index(op.f('ix_alert_acknowledgements_client_id'), 'alert_acknowledgements', ['client_id'], unique=False)

def downgrade():
    op.drop_table('alert_acknowledgements')
    op.drop_table('alert_deliveries')
    op.drop_table('alert_targets')
    
    cols = [
        'is_simulation', 'actionable_instructions_json', 'evidence_json',
        'risk_velocity', 'uncertainty_score', 'confidence_score', 'risk_score',
        'forecast_horizon', 'approved_at', 'approved_by', 'approval_status', 'alert_category'
    ]
    for c in cols:
        op.drop_column('alerts', c)
