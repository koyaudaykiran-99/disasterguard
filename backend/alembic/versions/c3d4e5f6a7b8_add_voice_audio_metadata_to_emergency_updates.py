"""add voice audio metadata to emergency updates

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-08 19:41:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('emergency_updates', sa.Column('audio_id', sa.String(length=100), nullable=True))
    op.add_column('emergency_updates', sa.Column('audio_duration', sa.Float(), nullable=True))
    op.add_column('emergency_updates', sa.Column('audio_mime_type', sa.String(length=60), nullable=True))
    op.add_column('emergency_updates', sa.Column('audio_size', sa.Integer(), nullable=True))
    op.add_column('emergency_updates', sa.Column('audio_storage_reference', sa.String(length=255), nullable=True))
    op.add_column('emergency_updates', sa.Column('transcription_provider', sa.String(length=60), nullable=True))
    op.add_column('emergency_updates', sa.Column('transcription_model', sa.String(length=60), nullable=True))
    op.add_column('emergency_updates', sa.Column('transcription_confidence', sa.Float(), nullable=True))
    op.create_index('ix_emergency_updates_audio_id', 'emergency_updates', ['audio_id'])

def downgrade() -> None:
    op.drop_index('ix_emergency_updates_audio_id', table_name='emergency_updates')
    op.drop_column('emergency_updates', 'transcription_confidence')
    op.drop_column('emergency_updates', 'transcription_model')
    op.drop_column('emergency_updates', 'transcription_provider')
    op.drop_column('emergency_updates', 'audio_storage_reference')
    op.drop_column('emergency_updates', 'audio_size')
    op.drop_column('emergency_updates', 'audio_mime_type')
    op.drop_column('emergency_updates', 'audio_duration')
    op.drop_column('emergency_updates', 'audio_id')
