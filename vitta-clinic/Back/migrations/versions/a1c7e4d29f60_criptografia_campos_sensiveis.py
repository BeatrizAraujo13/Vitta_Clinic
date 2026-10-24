"""Criptografa campos pessoais e clínicos existentes."""

from alembic import op
import sqlalchemy as sa

from app.utils.criptografia import cifrar_valor


revision = "a1c7e4d29f60"
down_revision = "0b56a78edb0c"
branch_labels = None
depends_on = None


_COLUNAS = {
    "patients": {
        "birth_date": ("patients.birth_date", sa.Date()),
        "phone": ("patients.phone", sa.String(length=32)),
        "email": ("patients.email", sa.String(length=254)),
        "address": ("patients.address", sa.String(length=300)),
        "insurance": ("patients.insurance", sa.String(length=120)),
        "notes": ("patients.notes", sa.Text()),
    },
    "doctors": {
        "email": ("doctors.email", sa.String(length=254)),
        "phone": ("doctors.phone", sa.String(length=32)),
    },
    "appointments": {
        "notes": ("appointments.notes", sa.Text()),
    },
    "medical_records": {
        "complaint": ("medical_records.complaint", sa.Text()),
        "diagnosis": ("medical_records.diagnosis", sa.Text()),
        "prescription": ("medical_records.prescription", sa.Text()),
        "notes": ("medical_records.notes", sa.Text()),
    },
}


def upgrade():
    conexao = op.get_bind()
    banco_sqlite = conexao.dialect.name == "sqlite"

    for tabela, colunas in _COLUNAS.items():
        alteracoes = {
            coluna: tipo_existente
            for coluna, (_, tipo_existente) in colunas.items()
            if not isinstance(tipo_existente, sa.Text)
        }
        if not alteracoes:
            continue
        if banco_sqlite:
            with op.batch_alter_table(tabela) as alteracao:
                for coluna, tipo_existente in alteracoes.items():
                    alteracao.alter_column(
                        coluna,
                        existing_type=tipo_existente,
                        type_=sa.Text(),
                    )
        else:
            for coluna, tipo_existente in alteracoes.items():
                op.alter_column(
                    tabela,
                    coluna,
                    existing_type=tipo_existente,
                    type_=sa.Text(),
                )

    for tabela, colunas in _COLUNAS.items():
        definicao = sa.table(
            tabela,
            sa.column("id", sa.Integer()),
            *(sa.column(coluna, sa.Text()) for coluna in colunas),
        )
        for registro in conexao.execute(sa.select(definicao.c.id, *(
            definicao.c[coluna] for coluna in colunas
        ))):
            atualizacoes = {}
            for coluna, (contexto, _) in colunas.items():
                valor = registro._mapping[coluna]
                if valor is not None and not valor.startswith("v1:"):
                    atualizacoes[coluna] = cifrar_valor(str(valor), _chave(), contexto)
            if atualizacoes:
                conexao.execute(
                    definicao.update().where(definicao.c.id == registro.id).values(**atualizacoes)
                )


def _chave():
    from flask import current_app

    return current_app.config["CHAVE_CIFRAGEM"]


def downgrade():
    pass
