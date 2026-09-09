"""add historical flood and inundation tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-08 20:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Historical Flood Events Table
    op.create_table(
        'historical_flood_events',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('event_name', sa.String(length=150), nullable=False, index=True),
        sa.Column('event_date', sa.String(length=30), nullable=False, index=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(length=30), default='HIGH', index=True),
        sa.Column('rainfall_total_mm', sa.Float(), nullable=False),
        sa.Column('duration_hours', sa.Integer(), default=24),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=50), default='HISTORICAL_EVENT'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('geometry_wkt', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # 2. Flood Intelligence Predictions Table
    op.create_table(
        'flood_intelligence_predictions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True, index=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=30), default='MODERATE', index=True),
        sa.Column('susceptibility_score', sa.Integer(), default=50, index=True),
        sa.Column('estimated_depth_m', sa.Float(), default=0.5),
        sa.Column('depth_confidence', sa.Float(), default=0.75),
        sa.Column('depth_type', sa.String(length=30), default='PROXY_ESTIMATE'),
        sa.Column('affected_area_km2', sa.Float(), default=1.0),
        sa.Column('data_source_type', sa.String(length=50), default='DERIVED'),
        sa.Column('model_version', sa.String(length=50), default='v2.1-geospatial'),
        sa.Column('explanation', sa.Text(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('flood_intelligence_predictions')
    op.drop_table('historical_flood_events')
