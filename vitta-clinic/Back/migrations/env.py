import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# Este é o objeto de configuração do Alembic, que fornece
# acesso aos valores do arquivo .ini em uso.
config = context.config

# Interpreta o arquivo de configuração do registro de eventos do Python.
# Esta linha configura os registradores.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def obter_mecanismo():
    try:
        # Compatível com Flask-SQLAlchemy anterior à versão 3 e Alchemical.
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # Compatível com Flask-SQLAlchemy 3 ou superior.
        return current_app.extensions['migrate'].db.engine


def obter_url_mecanismo():
    try:
        return obter_mecanismo().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(obter_mecanismo().url).replace('%', '%%')


# Adicione aqui o objeto MetaData dos modelos para gerar migrações automaticamente.
# from meu_app import meu_modelo
# target_metadata = meu_modelo.BaseDeclarativa.metadata
config.set_main_option('sqlalchemy.url', obter_url_mecanismo())
target_db = current_app.extensions['migrate'].db

# Outros valores de configuração necessários podem ser obtidos assim:
# minha_opcao = config.get_main_option("minha_opcao")
# ...


def obter_metadados():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def executar_migracoes_desconectadas():
    """Executa migrações no modo desconectado.

    Configura o contexto apenas com uma URL, sem mecanismo de banco.
    Ao não criar o mecanismo, não é necessário ter uma DBAPI disponível.

    As chamadas a context.execute() emitem a instrução para a saída do script.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=obter_metadados(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def executar_migracoes_conectadas():
    """Executa migrações no modo conectado.

    Neste modo, cria um mecanismo de banco e associa uma conexão ao contexto.

    """

    # Evita gerar uma migração automática quando não há mudanças no esquema.
    # Referência: https://alembic.sqlalchemy.org/en/latest/cookbook.html
    def processar_diretivas_de_revisao(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('Nenhuma alteração de esquema detectada.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = processar_diretivas_de_revisao

    connectable = obter_mecanismo()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=obter_metadados(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    executar_migracoes_desconectadas()
else:
    executar_migracoes_conectadas()
