"""add forecast predictions table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-08 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'forecast_predictions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('location', sa.String(length=100), default='Chennai Metro', index=True),
        sa.Column('latitude', sa.Float(), nullable=False, index=True),
        sa.Column('longitude', sa.Float(), nullable=False, index=True),
        sa.Column('horizon', sa.String(length=10), nullable=False, index=True),
        sa.Column('forecast_timestamp', sa.DateTime(), nullable=False, index=True),
        sa.Column('risk_score', sa.Integer(), nullable=False, default=0, index=True),
        sa.Column('risk_level', sa.String(length=30), nullable=False, default='LOW', index=True),
        sa.Column('rainfall_estimate_mm', sa.Float(), default=0.0),
        sa.Column('flood_susceptibility', sa.Integer(), default=0),
        sa.Column('proxy_depth_estimate_m', sa.Float(), default=0.0),
        sa.Column('depth_type', sa.String(length=30), default='PROXY_ESTIMATE'),
        sa.Column('confidence', sa.Float(), default=0.70),
        sa.Column('uncertainty', sa.Float(), default=0.30),
        sa.Column('trajectory', sa.String(length=30), default='STABLE'),
        sa.Column('warning_state', sa.String(length=30), default='NORMAL'),
        sa.Column('model_version', sa.String(length=50), default='forecast_v1'),
        sa.Column('data_source', sa.String(length=255), default='REAL_WEATHER + REAL_HISTORICAL_ML + GEOSPATIAL_DERIVATION'),
        sa.Column('data_source_type', sa.String(length=50), default='EXPLAINABLE_FORECAST_ENGINE'),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('valid_until', sa.DateTime(), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('forecast_predictions')
