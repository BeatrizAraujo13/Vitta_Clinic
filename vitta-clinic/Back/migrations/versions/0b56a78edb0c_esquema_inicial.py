"""Esquema inicial.

Revision ID: 0b56a78edb0c
Revises: 
Create Date: 2026-10-20 21:08:43.596760

"""
from alembic import op
import sqlalchemy as sa


# Identificadores de revisão usados pelo Alembic.
revision = '0b56a78edb0c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### comandos gerados automaticamente pelo Alembic; ajuste se necessário. ###
    op.create_table('patients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('cpf', sa.String(length=11), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=False),
    sa.Column('phone', sa.String(length=32), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=True),
    sa.Column('address', sa.String(length=300), nullable=True),
    sa.Column('insurance', sa.String(length=120), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('patients', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_patients_cpf'), ['cpf'], unique=True)
        batch_op.create_index(batch_op.f('ix_patients_name'), ['name'], unique=False)

    op.create_table('specialties',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('specialties', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_specialties_name'), ['name'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('role', sa.Enum('admin', 'medico', 'recepcionista', name='userrole'), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)

    op.create_table('doctors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('specialty_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('crm', sa.String(length=12), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('phone', sa.String(length=32), nullable=False),
    sa.Column('schedule', sa.String(length=200), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['specialty_id'], ['specialties.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    with op.batch_alter_table('doctors', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_doctors_crm'), ['crm'], unique=True)
        batch_op.create_index(batch_op.f('ix_doctors_name'), ['name'], unique=False)

    op.create_table('appointments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('appointment_date', sa.Date(), nullable=False),
    sa.Column('appointment_time', sa.Time(), nullable=False),
    sa.Column('status', sa.Enum('agendada', 'realizada', 'cancelada', name='appointmentstatus'), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_appointments_appointment_date'), ['appointment_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_appointments_doctor_id'), ['doctor_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_appointments_patient_id'), ['patient_id'], unique=False)
        batch_op.create_index('uq_appointment_doctor_active_slot', ['doctor_id', 'appointment_date', 'appointment_time'], unique=True, sqlite_where=sa.text("status != 'cancelada'"), postgresql_where=sa.text("status != 'cancelada'"))
        batch_op.create_index('uq_appointment_patient_active_slot', ['patient_id', 'appointment_date', 'appointment_time'], unique=True, sqlite_where=sa.text("status != 'cancelada'"), postgresql_where=sa.text("status != 'cancelada'"))

    op.create_table('medical_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('record_date', sa.Date(), nullable=False),
    sa.Column('complaint', sa.Text(), nullable=False),
    sa.Column('diagnosis', sa.Text(), nullable=False),
    sa.Column('prescription', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('appointment_id')
    )
    with op.batch_alter_table('medical_records', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_medical_records_patient_id'), ['patient_id'], unique=False)

    # ### fim dos comandos do Alembic ###


def downgrade():
    # ### comandos gerados automaticamente pelo Alembic; ajuste se necessário. ###
    with op.batch_alter_table('medical_records', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_medical_records_patient_id'))

    op.drop_table('medical_records')
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.drop_index('uq_appointment_patient_active_slot', sqlite_where=sa.text("status != 'cancelada'"), postgresql_where=sa.text("status != 'cancelada'"))
        batch_op.drop_index('uq_appointment_doctor_active_slot', sqlite_where=sa.text("status != 'cancelada'"), postgresql_where=sa.text("status != 'cancelada'"))
        batch_op.drop_index(batch_op.f('ix_appointments_patient_id'))
        batch_op.drop_index(batch_op.f('ix_appointments_doctor_id'))
        batch_op.drop_index(batch_op.f('ix_appointments_appointment_date'))

    op.drop_table('appointments')
    with op.batch_alter_table('doctors', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_doctors_name'))
        batch_op.drop_index(batch_op.f('ix_doctors_crm'))

    op.drop_table('doctors')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    with op.batch_alter_table('specialties', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_specialties_name'))

    op.drop_table('specialties')
    with op.batch_alter_table('patients', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_patients_name'))
        batch_op.drop_index(batch_op.f('ix_patients_cpf'))

    op.drop_table('patients')
    # ### fim dos comandos do Alembic ###
