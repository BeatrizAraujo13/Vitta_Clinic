"""JWT account lookup and reusable role-protection decorator."""

from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import User
from app.utils.errors import ApiError


def current_user() -> User:
    identity = get_jwt_identity()
    try:
        user = db.session.get(User, int(identity))
    except (TypeError, ValueError):
        user = None
    if user is None or not user.active:
        raise ApiError("Usuário autenticado não encontrado ou inativo.", 401)
    return user


def roles_required(*roles: str):
    """Require a valid access token and one of the listed account roles."""

    def decorator(view):
        @wraps(view)
        @jwt_required()
        def wrapped(*args, **kwargs):
            user = current_user()
            if user.role.value not in roles:
                raise ApiError("Você não tem permissão para esta operação.", 403)
            return view(*args, **kwargs)

        return wrapped

    return decorator
