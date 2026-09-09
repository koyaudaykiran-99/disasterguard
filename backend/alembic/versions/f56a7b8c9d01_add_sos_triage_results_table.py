"""add sos triage results table

Revision ID: f56a7b8c9d01
Revises: e3c4d7e89123
Create Date: 2026-09-07 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f56a7b8c9d01'
down_revision: Union[str, Sequence[str], None] = 'e3c4d7e89123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'sos_triage_results',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sos_id', sa.Integer(), sa.ForeignKey('sos_reports.id', ondelete='CASCADE'), nullable=False),
        sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id', ondelete='SET NULL'), nullable=True),
        sa.Column('incident_type', sa.String(length=64), nullable=False, server_default='OTHER'),
        sa.Column('severity', sa.String(length=32), nullable=False, server_default='MODERATE'),
        sa.Column('priority_score', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('confidence_type', sa.String(length=32), nullable=False, server_default='HEURISTIC_UNCERTAINTY'),
        sa.Column('people_at_risk', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('medical_emergency', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('trapped_person', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('flooding', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('infrastructure_damage', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('immediate_threat', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('recommended_action', sa.Text(), nullable=False, server_default='Operator review recommended'),
        sa.Column('reasoning', sa.JSON(), nullable=False),
        sa.Column('data_sources', sa.JSON(), nullable=False),
        sa.Column('facts', sa.JSON(), nullable=False),
        sa.Column('predictions', sa.JSON(), nullable=False),
        sa.Column('ai_interpretation', sa.Text(), nullable=False, server_default=''),
        sa.Column('provider', sa.String(length=64), nullable=False, server_default='DeterministicTriageEngine'),
        sa.Column('model', sa.String(length=64), nullable=False, server_default='rule-based-nlp-v2'),
        sa.Column('triage_status', sa.String(length=32), nullable=False, server_default='COMPLETE'),
        sa.Column('stale_data_warning', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('human_confirmation_required', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_sos_triage_results_sos_id', 'sos_triage_results', ['sos_id'], unique=True)
    op.create_index('ix_sos_triage_results_priority_score', 'sos_triage_results', ['priority_score'], unique=False)
    op.create_index('ix_sos_triage_results_incident_type', 'sos_triage_results', ['incident_type'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_sos_triage_results_incident_type', table_name='sos_triage_results')
    op.drop_index('ix_sos_triage_results_priority_score', table_name='sos_triage_results')
    op.drop_index('ix_sos_triage_results_sos_id', table_name='sos_triage_results')
    op.drop_table('sos_triage_results')
