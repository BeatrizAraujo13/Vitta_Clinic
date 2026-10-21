"""Consistent API exceptions and response handlers."""

from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType


class ApiError(Exception):
    """An expected API error with an HTTP response status."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    """Install JSON error responses for application-level failures."""

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return {"error": error.message}, error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return {"error": "Dados inválidos.", "details": error.messages}, 400

    @app.errorhandler(BadRequest)
    def handle_bad_request(_error):
        return {"error": "Requisição inválida. Verifique o JSON enviado."}, 400

    @app.errorhandler(UnsupportedMediaType)
    def handle_unsupported_media_type(_error):
        return {"error": "Envie o corpo da requisição com Content-Type application/json."}, 415

    @app.errorhandler(404)
    def handle_not_found(_error):
        return {"error": "Recurso não encontrado."}, 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return {"error": "Método não permitido."}, 405
