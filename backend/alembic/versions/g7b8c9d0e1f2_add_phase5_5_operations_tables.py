"""add phase 5.5 operations tables

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-08 23:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'g7b8c9d0e1f2'
down_revision = 'f6a7b8c9d0e1'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 1. operational_recommendations table
    if 'operational_recommendations' not in existing_tables:
        op.create_table(
            'operational_recommendations',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False),
            sa.Column('resource_type', sa.String(length=40), nullable=False),
            sa.Column('resource_id', sa.Integer(), nullable=False),
            sa.Column('resource_name', sa.String(length=180), nullable=True),
            sa.Column('score', sa.Float(), nullable=False),
            sa.Column('reasoning_json', sa.Text(), nullable=True),
            sa.Column('warnings_json', sa.Text(), nullable=True),
            sa.Column('confidence', sa.String(length=20), server_default='HIGH'),
            sa.Column('data_provenance', sa.String(length=30), server_default='REAL'),
            sa.Column('status', sa.String(length=30), server_default='RECOMMENDED'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index('ix_operational_recommendations_id', 'operational_recommendations', ['id'])
        op.create_index('ix_operational_recommendations_incident_id', 'operational_recommendations', ['incident_id'])
        op.create_index('ix_operational_recommendations_resource_type', 'operational_recommendations', ['resource_type'])
        op.create_index('ix_operational_recommendations_resource_id', 'operational_recommendations', ['resource_id'])
        op.create_index('ix_operational_recommendations_status', 'operational_recommendations', ['status'])
        op.create_index('ix_operational_recommendations_created_at', 'operational_recommendations', ['created_at'])

    # 2. resource_contentions table
    if 'resource_contentions' not in existing_tables:
        op.create_table(
            'resource_contentions',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('resource_id', sa.Integer(), nullable=False),
            sa.Column('resource_name', sa.String(length=180), nullable=True),
            sa.Column('incident_ids_json', sa.Text(), nullable=False),
            sa.Column('preferred_incident_id', sa.Integer(), nullable=True),
            sa.Column('severity', sa.String(length=30), server_default='HIGH'),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('alternatives_json', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('detected_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('resolved_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_resource_contentions_id', 'resource_contentions', ['id'])
        op.create_index('ix_resource_contentions_resource_id', 'resource_contentions', ['resource_id'])
        op.create_index('ix_resource_contentions_preferred_incident_id', 'resource_contentions', ['preferred_incident_id'])
        op.create_index('ix_resource_contentions_severity', 'resource_contentions', ['severity'])
        op.create_index('ix_resource_contentions_is_active', 'resource_contentions', ['is_active'])
        op.create_index('ix_resource_contentions_detected_at', 'resource_contentions', ['detected_at'])

    # 3. operational_bottlenecks table
    if 'operational_bottlenecks' not in existing_tables:
        op.create_table(
            'operational_bottlenecks',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('zone', sa.String(length=120), nullable=False),
            sa.Column('bottleneck_type', sa.String(length=40), nullable=False),
            sa.Column('severity', sa.String(length=30), server_default='HIGH'),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('metrics_json', sa.Text(), nullable=True),
            sa.Column('guidance', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('detected_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('resolved_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_operational_bottlenecks_id', 'operational_bottlenecks', ['id'])
        op.create_index('ix_operational_bottlenecks_zone', 'operational_bottlenecks', ['zone'])
        op.create_index('ix_operational_bottlenecks_bottleneck_type', 'operational_bottlenecks', ['bottleneck_type'])
        op.create_index('ix_operational_bottlenecks_severity', 'operational_bottlenecks', ['severity'])
        op.create_index('ix_operational_bottlenecks_is_active', 'operational_bottlenecks', ['is_active'])
        op.create_index('ix_operational_bottlenecks_detected_at', 'operational_bottlenecks', ['detected_at'])

    # 4. response_plans table
    if 'response_plans' not in existing_tables:
        op.create_table(
            'response_plans',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, unique=True),
            sa.Column('priority', sa.String(length=20), server_default='HIGH'),
            sa.Column('priority_score', sa.Float(), nullable=False),
            sa.Column('recommended_team_id', sa.Integer(), nullable=True),
            sa.Column('recommended_team_name', sa.String(length=180), nullable=True),
            sa.Column('alternative_teams_json', sa.Text(), nullable=True),
            sa.Column('recommended_shelter_id', sa.Integer(), nullable=True),
            sa.Column('recommended_shelter_name', sa.String(length=180), nullable=True),
            sa.Column('recommended_hospital_id', sa.Integer(), nullable=True),
            sa.Column('recommended_hospital_name', sa.String(length=180), nullable=True),
            sa.Column('reasons_json', sa.Text(), nullable=True),
            sa.Column('warnings_json', sa.Text(), nullable=True),
            sa.Column('confidence', sa.String(length=20), server_default='HIGH'),
            sa.Column('data_provenance_json', sa.Text(), nullable=True),
            sa.Column('human_confirmation_required', sa.Boolean(), server_default='true', nullable=False),
            sa.Column('status', sa.String(length=30), server_default='RECOMMENDED'),
            sa.Column('override_reason', sa.Text(), nullable=True),
            sa.Column('reviewed_by', sa.String(length=120), nullable=True),
            sa.Column('reviewed_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        )
        op.create_index('ix_response_plans_id', 'response_plans', ['id'])
        op.create_index('ix_response_plans_incident_id', 'response_plans', ['incident_id'])
        op.create_index('ix_response_plans_priority', 'response_plans', ['priority'])
        op.create_index('ix_response_plans_recommended_team_id', 'response_plans', ['recommended_team_id'])
        op.create_index('ix_response_plans_status', 'response_plans', ['status'])
        op.create_index('ix_response_plans_created_at', 'response_plans', ['created_at'])

def downgrade():
    op.drop_table('response_plans')
    op.drop_table('operational_bottlenecks')
    op.drop_table('resource_contentions')
    op.drop_table('operational_recommendations')
