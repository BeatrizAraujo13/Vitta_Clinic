"""Development seed data for users and clinic operations."""

from datetime import date, time, timedelta

from app.extensions import db
from app.models import (
    Appointment,
    AppointmentStatus,
    Doctor,
    MedicalRecord,
    Patient,
    Specialty,
    User,
    UserRole,
)


def seed_database():
    """Create the requested demo records if the database is empty."""
    if User.query.first():
        return False

    admin = User(name="Marina Costa", email="admin@vitta.com", role=UserRole.ADMIN)
    doctor_user = User(name="Dr. Rafael Mendes", email="medico@vitta.com", role=UserRole.MEDICO)
    reception = User(name="Camila Rocha", email="recepcao@vitta.com", role=UserRole.RECEPCIONISTA)
    for user in (admin, doctor_user, reception):
        user.set_password("123456")
        db.session.add(user)

    cardiology = Specialty(name="Cardiologia", description="Prevenção e tratamento das doenças do coração.")
    dermatology = Specialty(name="Dermatologia", description="Cuidados clínicos com pele, cabelos e unhas.")
    general = Specialty(name="Clínica geral", description="Atendimento integral e acompanhamento de saúde.")
    db.session.add_all((cardiology, dermatology, general))
    db.session.flush()

    doctors = [
        Doctor(user=doctor_user, specialty=cardiology, name="Rafael Mendes", crm="SP 123456", email="rafael@vitta.com", phone="(11) 98888-1200", schedule="Seg a qui, 08:00–17:00"),
        Doctor(specialty=dermatology, name="Luciana Freitas", crm="SP 234567", email="luciana@vitta.com", phone="(11) 97777-3400", schedule="Seg a sex, 09:00–16:00"),
        Doctor(specialty=general, name="André Oliveira", crm="SP 345678", email="andre@vitta.com", phone="(11) 96666-5600", schedule="Ter a sex, 08:00–18:00"),
    ]
    db.session.add_all(doctors)
    patients = [
        Patient(name="Ana Beatriz Lima", cpf="52998224725", birth_date=date(1988, 4, 12), phone="(11) 99911-2233", email="ana.lima@email.com", address="Rua das Flores, 120 — São Paulo/SP", insurance="Vida Plena"),
        Patient(name="Bruno Carvalho", cpf="11144477735", birth_date=date(1976, 11, 3), phone="(11) 99822-3344", email="bruno.c@email.com", address="Av. Central, 45 — São Paulo/SP", insurance="Particular"),
        Patient(name="Carolina Nunes", cpf="12345678909", birth_date=date(1993, 7, 25), phone="(11) 99733-4455", email="carolina.n@email.com", address="Rua Aurora, 88 — Guarulhos/SP", insurance="Bem Saúde"),
        Patient(name="Diego Martins", cpf="93541134780", birth_date=date(1982, 2, 14), phone="(11) 99644-5566", email="diego.m@email.com", address="Alameda Sul, 310 — São Paulo/SP", insurance="Vida Plena"),
        Patient(name="Elisa Ferreira", cpf="98765432100", birth_date=date(2001, 9, 8), phone="(11) 99555-6677", email="elisa.f@email.com", address="Rua do Lago, 72 — Osasco/SP", insurance="Bem Saúde"),
    ]
    db.session.add_all(patients)
    db.session.flush()

    today = date.today()
    appointments = [
        Appointment(patient=patients[0], doctor=doctors[0], appointment_date=today - timedelta(days=1), appointment_time=time(9, 0), status=AppointmentStatus.REALIZADA, notes="Consulta de rotina."),
        Appointment(patient=patients[1], doctor=doctors[2], appointment_date=today + timedelta(days=1), appointment_time=time(10, 30), status=AppointmentStatus.AGENDADA),
        Appointment(patient=patients[2], doctor=doctors[1], appointment_date=today + timedelta(days=2), appointment_time=time(14, 0), status=AppointmentStatus.AGENDADA),
        Appointment(patient=patients[3], doctor=doctors[0], appointment_date=today + timedelta(days=3), appointment_time=time(11, 0), status=AppointmentStatus.AGENDADA),
        Appointment(patient=patients[4], doctor=doctors[2], appointment_date=today + timedelta(days=4), appointment_time=time(8, 30), status=AppointmentStatus.AGENDADA, notes="Primeira consulta."),
    ]
    db.session.add_all(appointments)
    db.session.flush()

    db.session.add(
        MedicalRecord(
            patient=patients[0],
            appointment=appointments[0],
            doctor=doctors[0],
            record_date=today - timedelta(days=1),
            complaint="Acompanhamento de rotina.",
            diagnosis="Paciente estável, sem sinais de alerta.",
            prescription="Manter hábitos saudáveis e retorno de rotina.",
            notes="Prontuário demonstrativo.",
        )
    )
    db.session.commit()
    return True
