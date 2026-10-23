"""Relatórios agregados restritos a administradores."""

from sqlalchemy import func

from app.extensoes import db
from app.models import Consulta, StatusConsulta, Medico, Paciente
from app.utils.erros import ErroApi


def relatorio_consultas(date_from=None, date_to=None, doctor_id=None):
    if date_from and date_to and date_from > date_to:
        raise ErroApi("A data inicial deve ser anterior ou igual à data final.", 400)
    query = Consulta.query
    if date_from:
        query = query.filter(Consulta.appointment_date >= date_from)
    if date_to:
        query = query.filter(Consulta.appointment_date <= date_to)
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    return [item.para_dicionario() for item in query.order_by(Consulta.appointment_date, Consulta.appointment_time).all()]


def relatorio_pacientes():
    return [item.para_dicionario() for item in Paciente.query.filter(Paciente.deleted_at.is_(None)).order_by(Paciente.name).all()]


def relatorio_medicos(date_from=None, date_to=None):
    query = db.session.query(
        Medico.id,
        Medico.name,
        Medico.crm,
        func.count(Consulta.id).label("appointment_count"),
    ).outerjoin(Consulta, Consulta.doctor_id == Medico.id)
    if date_from:
        query = query.filter(db.or_(Consulta.id.is_(None), Consulta.appointment_date >= date_from))
    if date_to:
        query = query.filter(db.or_(Consulta.id.is_(None), Consulta.appointment_date <= date_to))
    query = query.group_by(Medico.id).order_by(Medico.name)
    return [
        {"doctor_id": row.id, "doctor_name": row.name, "crm": row.crm, "appointment_count": row.appointment_count}
        for row in query.all()
    ]
