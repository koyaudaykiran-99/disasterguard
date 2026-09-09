"""add weather source and coordinates

Revision ID: f4591a27b401
Revises: 10a2c26bb145
Create Date: 2026-09-06 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f4591a27b401'
down_revision: Union[str, Sequence[str], None] = '10a2c26bb145'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('weather_observations', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('weather_observations', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('weather_observations', sa.Column('condition', sa.String(length=60), nullable=True, server_default='Clear'))
    op.add_column('weather_observations', sa.Column('source', sa.String(length=30), nullable=False, server_default='real'))
    op.add_column('weather_observations', sa.Column('precipitation_probability', sa.Float(), nullable=True))
    op.create_index('ix_weather_observations_source', 'weather_observations', ['source'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_weather_observations_source', table_name='weather_observations')
    op.drop_column('weather_observations', 'precipitation_probability')
    op.drop_column('weather_observations', 'source')
    op.drop_column('weather_observations', 'condition')
    op.drop_column('weather_observations', 'longitude')
    op.drop_column('weather_observations', 'latitude')
