"""add phase 6 situational awareness tables

Revision ID: h8c9d0e1f2a3
Revises: g7b8c9d0e1f2
Create Date: 2026-09-09 13:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'h8c9d0e1f2a3'
down_revision = 'g7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 1. situational_snapshots
    if 'situational_snapshots' not in existing_tables:
        op.create_table(
            'situational_snapshots',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('overall_status', sa.String(length=30), nullable=False, server_default='NORMAL'),
            sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('risk_direction', sa.String(length=30), nullable=False, server_default='STABLE'),
            sa.Column('critical_areas_json', sa.Text(), nullable=True),
            sa.Column('active_incidents', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('critical_incidents', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('active_alerts', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('resource_contentions', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('operational_bottlenecks', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('recommended_operator_attention_json', sa.Text(), nullable=True),
            sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
            sa.Column('data_freshness_json', sa.Text(), nullable=True),
            sa.Column('data_provenance', sa.String(length=30), nullable=False, server_default='REAL'),
            sa.Column('generated_at', sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index('ix_situational_snapshots_id', 'situational_snapshots', ['id'])
        op.create_index('ix_situational_snapshots_overall_status', 'situational_snapshots', ['overall_status'])
        op.create_index('ix_situational_snapshots_risk_direction', 'situational_snapshots', ['risk_direction'])
        op.create_index('ix_situational_snapshots_generated_at', 'situational_snapshots', ['generated_at'])

    # 2. operational_events
    if 'operational_events' not in existing_tables:
        op.create_table(
            'operational_events',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('event_type', sa.String(length=60), nullable=False),
            sa.Column('entity_type', sa.String(length=40), nullable=True),
            sa.Column('entity_id', sa.String(length=64), nullable=True),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('severity', sa.String(length=30), nullable=False, server_default='INFO'),
            sa.Column('confidence', sa.Float(), nullable=False, server_default='0.9'),
            sa.Column('source', sa.String(length=50), nullable=False, server_default='SYSTEM'),
            sa.Column('data_provenance', sa.String(length=30), nullable=False, server_default='REAL'),
            sa.Column('metadata_json', sa.Text(), nullable=True),
            sa.Column('event_timestamp', sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index('ix_operational_events_id', 'operational_events', ['id'])
        op.create_index('ix_operational_events_event_type', 'operational_events', ['event_type'])
        op.create_index('ix_operational_events_entity_type', 'operational_events', ['entity_type'])
        op.create_index('ix_operational_events_entity_id', 'operational_events', ['entity_id'])
        op.create_index('ix_operational_events_severity', 'operational_events', ['severity'])
        op.create_index('ix_operational_events_source', 'operational_events', ['source'])
        op.create_index('ix_operational_events_event_timestamp', 'operational_events', ['event_timestamp'])

    # 3. incident_clusters
    if 'incident_clusters' not in existing_tables:
        op.create_table(
            'incident_clusters',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('cluster_code', sa.String(length=60), nullable=False, unique=True),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('dominant_hazard', sa.String(length=50), nullable=False, server_default='FLOOD'),
            sa.Column('risk_level', sa.String(length=30), nullable=False, server_default='HIGH'),
            sa.Column('latitude', sa.Float(), nullable=False),
            sa.Column('longitude', sa.Float(), nullable=False),
            sa.Column('radius_km', sa.Float(), nullable=False, server_default='1.5'),
            sa.Column('incident_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('incident_ids_json', sa.Text(), nullable=False),
            sa.Column('severity_distribution_json', sa.Text(), nullable=True),
            sa.Column('estimated_affected_population', sa.Integer(), nullable=True),
            sa.Column('resource_demand_json', sa.Text(), nullable=True),
            sa.Column('recommended_attention', sa.Text(), nullable=True),
            sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('detected_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index('ix_incident_clusters_id', 'incident_clusters', ['id'])
        op.create_index('ix_incident_clusters_cluster_code', 'incident_clusters', ['cluster_code'])
        op.create_index('ix_incident_clusters_dominant_hazard', 'incident_clusters', ['dominant_hazard'])
        op.create_index('ix_incident_clusters_risk_level', 'incident_clusters', ['risk_level'])
        op.create_index('ix_incident_clusters_is_active', 'incident_clusters', ['is_active'])
        op.create_index('ix_incident_clusters_detected_at', 'incident_clusters', ['detected_at'])

    # 4. risk_hotspots
    if 'risk_hotspots' not in existing_tables:
        op.create_table(
            'risk_hotspots',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('hotspot_code', sa.String(length=60), nullable=False, unique=True),
            sa.Column('name', sa.String(length=180), nullable=False),
            sa.Column('hazard_type', sa.String(length=50), nullable=False, server_default='FLASH_FLOOD'),
            sa.Column('latitude', sa.Float(), nullable=False),
            sa.Column('longitude', sa.Float(), nullable=False),
            sa.Column('radius_km', sa.Float(), nullable=False, server_default='1.0'),
            sa.Column('hotspot_score', sa.Float(), nullable=False, server_default='75.0'),
            sa.Column('severity', sa.String(length=30), nullable=False, server_default='HIGH'),
            sa.Column('confidence', sa.Float(), nullable=False, server_default='0.88'),
            sa.Column('sos_density', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('rainfall_intensity_mm', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('flood_susceptibility_score', sa.Float(), nullable=False, server_default='0.0'),
            sa.Column('forecast_trajectory', sa.String(length=40), nullable=False, server_default='INCREASING'),
            sa.Column('supporting_evidence_json', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('detected_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index('ix_risk_hotspots_id', 'risk_hotspots', ['id'])
        op.create_index('ix_risk_hotspots_hotspot_code', 'risk_hotspots', ['hotspot_code'])
        op.create_index('ix_risk_hotspots_hazard_type', 'risk_hotspots', ['hazard_type'])
        op.create_index('ix_risk_hotspots_severity', 'risk_hotspots', ['severity'])
        op.create_index('ix_risk_hotspots_is_active', 'risk_hotspots', ['is_active'])
        op.create_index('ix_risk_hotspots_detected_at', 'risk_hotspots', ['detected_at'])

    # 5. operator_attention_items
    if 'operator_attention_items' not in existing_tables:
        op.create_table(
            'operator_attention_items',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('urgency', sa.String(length=30), nullable=False, server_default='HIGH'),
            sa.Column('category', sa.String(length=50), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id', ondelete='SET NULL'), nullable=True),
            sa.Column('related_entity_type', sa.String(length=40), nullable=True),
            sa.Column('related_entity_id', sa.String(length=64), nullable=True),
            sa.Column('recommended_action', sa.Text(), nullable=False),
            sa.Column('is_acknowledged', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('acknowledged_by', sa.String(length=120), nullable=True),
            sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
            sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index('ix_operator_attention_items_id', 'operator_attention_items', ['id'])
        op.create_index('ix_operator_attention_items_urgency', 'operator_attention_items', ['urgency'])
        op.create_index('ix_operator_attention_items_category', 'operator_attention_items', ['category'])
        op.create_index('ix_operator_attention_items_incident_id', 'operator_attention_items', ['incident_id'])
        op.create_index('ix_operator_attention_items_is_acknowledged', 'operator_attention_items', ['is_acknowledged'])
        op.create_index('ix_operator_attention_items_is_resolved', 'operator_attention_items', ['is_resolved'])
        op.create_index('ix_operator_attention_items_created_at', 'operator_attention_items', ['created_at'])

    # 6. correlation_records
    if 'correlation_records' not in existing_tables:
        op.create_table(
            'correlation_records',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('correlation_id', sa.String(length=80), nullable=False, unique=True),
            sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('incident_clusters.id', ondelete='CASCADE'), nullable=True),
            sa.Column('incident_ids_json', sa.Text(), nullable=False),
            sa.Column('correlation_type', sa.String(length=50), nullable=False),
            sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
            sa.Column('correlation_reason', sa.Text(), nullable=False),
            sa.Column('detected_at', sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index('ix_correlation_records_id', 'correlation_records', ['id'])
        op.create_index('ix_correlation_records_correlation_id', 'correlation_records', ['correlation_id'])
        op.create_index('ix_correlation_records_cluster_id', 'correlation_records', ['cluster_id'])
        op.create_index('ix_correlation_records_correlation_type', 'correlation_records', ['correlation_type'])
        op.create_index('ix_correlation_records_detected_at', 'correlation_records', ['detected_at'])


def downgrade():
    op.drop_table('correlation_records')
    op.drop_table('operator_attention_items')
    op.drop_table('risk_hotspots')
    op.drop_table('incident_clusters')
    op.drop_table('operational_events')
    op.drop_table('situational_snapshots')
