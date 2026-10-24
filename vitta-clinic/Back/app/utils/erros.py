"""Exceções e tratadores de resposta consistentes da API."""

from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType


class ErroApi(Exception):
    """Um erro previsto da API com um código de resposta HTTP."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def registrar_tratadores_de_erro(app):
    """Registra respostas JSON de erro para falhas da aplicação."""

    @app.errorhandler(ErroApi)
    def tratar_erro_api(error):
        return {"error": error.message}, error.status_code

    @app.errorhandler(ValidationError)
    def tratar_erro_validacao(error):
        return {"error": "Dados inválidos.", "details": error.messages}, 400

    @app.errorhandler(BadRequest)
    def tratar_requisicao_invalida(_error):
        return {"error": "Requisição inválida. Verifique o JSON enviado."}, 400

    @app.errorhandler(UnsupportedMediaType)
    def tratar_tipo_de_midia_nao_suportado(_error):
        return {"error": "Envie o corpo da requisição com Content-Type application/json."}, 415

    @app.errorhandler(404)
    def tratar_nao_encontrado(_error):
        return {"error": "Recurso não encontrado."}, 404

    @app.errorhandler(405)
    def tratar_metodo_nao_permitido(_error):
        return {"error": "Método não permitido."}, 405
