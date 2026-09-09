"""initial_disasterguard_schema

Revision ID: 10a2c26bb145
Revises: 
Create Date: 2026-09-06 11:33:59.075382

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '10a2c26bb145'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=140), nullable=False),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'OPERATOR', 'RESCUE_TEAM', 'CITIZEN', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. Weather Observations
    op.create_table(
        'weather_observations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('location', sa.String(length=140), nullable=False),
        sa.Column('rainfall_1h', sa.Float(), nullable=False),
        sa.Column('rainfall_3h', sa.Float(), nullable=False),
        sa.Column('rainfall_6h', sa.Float(), nullable=False),
        sa.Column('rainfall_24h', sa.Float(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('humidity', sa.Float(), nullable=False),
        sa.Column('wind_speed', sa.Float(), nullable=False),
        sa.Column('pressure', sa.Float(), nullable=False),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_weather_observations_id', 'weather_observations', ['id'], unique=False)
    op.create_index('ix_weather_observations_location', 'weather_observations', ['location'], unique=False)

    # 3. Rainfall Predictions
    op.create_table(
        'rainfall_predictions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('location', sa.String(length=140), nullable=False),
        sa.Column('predicted_rainfall', sa.Float(), nullable=False),
        sa.Column('forecast_horizon', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=30), nullable=False),
        sa.Column('prediction_time', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_rainfall_predictions_id', 'rainfall_predictions', ['id'], unique=False)

    # 4. Flood Predictions
    op.create_table(
        'flood_predictions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('location', sa.String(length=140), nullable=False),
        sa.Column('flood_probability', sa.Float(), nullable=False),
        sa.Column('water_depth', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=30), nullable=False),
        sa.Column('prediction_time', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_flood_predictions_id', 'flood_predictions', ['id'], unique=False)

    # 5. Risk Zones
    op.create_table(
        'risk_zones',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=140), nullable=False),
        sa.Column('geometry_wkt', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=30), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('population_estimate', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_risk_zones_id', 'risk_zones', ['id'], unique=False)
    op.create_index('ix_risk_zones_spatial', 'risk_zones', ['latitude', 'longitude'], unique=False)

    # 6. Incidents
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=140), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('incident_type', sa.String(length=50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(length=30), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column('source', sa.String(length=50), nullable=False, server_default=sa.text("'CITIZEN_SOS'")),
        sa.Column('priority_score', sa.Integer(), nullable=False, server_default=sa.text('50')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_incidents_id', 'incidents', ['id'], unique=False)
    op.create_index('ix_incidents_spatial', 'incidents', ['latitude', 'longitude'], unique=False)
    op.create_index('ix_incidents_status', 'incidents', ['status'], unique=False)

    # 7. SOS Reports
    op.create_table(
        'sos_reports',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=30), nullable=False, server_default=sa.text("'CRITICAL'")),
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_sos_reports_id', 'sos_reports', ['id'], unique=False)
    op.create_index('ix_sos_reports_spatial', 'sos_reports', ['latitude', 'longitude'], unique=False)
    op.create_index('ix_sos_reports_status', 'sos_reports', ['status'], unique=False)

    # 8. Alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=140), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False, server_default=sa.text("'FLOOD'")),
        sa.Column('severity', sa.String(length=30), nullable=False, server_default=sa.text("'HIGH'")),
        sa.Column('target_area', sa.String(length=140), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'ACTIVE'")),
    )
    op.create_index('ix_alerts_id', 'alerts', ['id'], unique=False)
    op.create_index('ix_alerts_status', 'alerts', ['status'], unique=False)

    # 9. Shelters
    op.create_table(
        'shelters',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=140), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default=sa.text('1000')),
        sa.Column('current_occupancy', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('contact', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'OPEN'")),
    )
    op.create_index('ix_shelters_id', 'shelters', ['id'], unique=False)
    op.create_index('ix_shelters_spatial', 'shelters', ['latitude', 'longitude'], unique=False)

    # 10. Hospitals
    op.create_table(
        'hospitals',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=140), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('emergency_capacity', sa.Integer(), nullable=False, server_default=sa.text('200')),
        sa.Column('available_beds', sa.Integer(), nullable=False, server_default=sa.text('50')),
        sa.Column('contact', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'AVAILABLE'")),
    )
    op.create_index('ix_hospitals_id', 'hospitals', ['id'], unique=False)
    op.create_index('ix_hospitals_spatial', 'hospitals', ['latitude', 'longitude'], unique=False)

    # 11. Rescue Teams
    op.create_table(
        'rescue_teams',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=140), nullable=False),
        sa.Column('team_size', sa.Integer(), nullable=False, server_default=sa.text('8')),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('vehicle_type', sa.String(length=50), nullable=False, server_default=sa.text("'BOAT'")),
        sa.Column('equipment', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'AVAILABLE'")),
        sa.Column('contact', sa.String(length=50), nullable=True),
    )
    op.create_index('ix_rescue_teams_id', 'rescue_teams', ['id'], unique=False)
    op.create_index('ix_rescue_teams_spatial', 'rescue_teams', ['latitude', 'longitude'], unique=False)

    # 12. Rescue Assignments
    op.create_table(
        'rescue_assignments',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('incident_id', sa.Integer(), sa.ForeignKey('incidents.id'), nullable=False),
        sa.Column('rescue_team_id', sa.Integer(), sa.ForeignKey('rescue_teams.id'), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True, server_default=sa.text('1')),
        sa.Column('estimated_distance', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default=sa.text("'DISPATCHED'")),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )
    op.create_index('ix_rescue_assignments_id', 'rescue_assignments', ['id'], unique=False)

def downgrade() -> None:
    op.drop_table('rescue_assignments')
    op.drop_table('rescue_teams')
    op.drop_table('hospitals')
    op.drop_table('shelters')
    op.drop_table('alerts')
    op.drop_table('sos_reports')
    op.drop_table('incidents')
    op.drop_table('risk_zones')
    op.drop_table('flood_predictions')
    op.drop_table('rainfall_predictions')
    op.drop_table('weather_observations')
    op.drop_table('users')
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS userrole CASCADE;")
